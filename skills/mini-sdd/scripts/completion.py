"""Narrow repair and Completion checks; assessments remain the coordinator's judgment."""
import json
import resume


def repair(api, root, task, reason):
    # Validate the original checkpoint before invalidating approval for new work.
    resume.inspect(api, root, task)
    folder = api.task_path(root, task)
    state = json.loads((folder / 'state.json').read_text())
    if state['phase'] not in ('REVIEW_READY', 'BLOCKED_VERIFICATION', 'COMPLETE') or not reason.strip():
        raise ValueError('Repair requires an existing candidate and a confirmed in-scope repair reason')
    state.update(phase='IMPLEMENTING', candidate=None, latest_review=None,
                 next_action='Repair within current consent, then verify a new candidate and obtain Independent Review: ' + reason.strip(),
                 unresolved_blocker='Repair and affected verification/re-review remain outstanding')
    for key in ('verification', 'review', 'completion'):
        state.pop(key, None)
    api.atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def report_inputs(folder):
    """Bind actual numbered history without rewriting its original observations."""
    import re
    import review
    records = {}
    findings = {}
    directory = folder / 'reviews'
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError('Actual code-review history is required')
    for path in sorted(directory.iterdir()):
        if not re.fullmatch(r'code-\d{2,}\.md', path.name):
            continue
        relative = path.relative_to(folder).as_posix()
        body = resume.ordinary(folder, relative).read_text()
        prefix, suffix = '# Code review attempt\n\n```json\n', '\n```\n'
        if not body.startswith(prefix) or not body.endswith(suffix):
            raise ValueError('Malformed actual review history')
        envelope = json.loads(body[len(prefix):-len(suffix)])
        report = envelope['actual_report']
        if not isinstance(report, dict) or not isinstance(report.get('findings'), list):
            raise ValueError('Malformed actual report history')
        records[relative] = review.digest(path.read_bytes())
        for finding in report['findings']:
            key = (relative, finding['id'])
            if key in findings:
                raise ValueError('Duplicate historical finding identity')
            findings[key] = report
    return records, findings


def validate(api, root, folder, state, assessment_path):
    try:
        return validate_assessment(api, root, folder, state, assessment_path)
    except (KeyError, TypeError, AttributeError, IndexError) as error:
        raise ValueError("Malformed Completion assessment or report: " + str(error)) from error


def validate_assessment(api, root, folder, state, assessment_path):
    """Validate evidence bindings and explicit judgments, never their truth."""
    from pathlib import Path
    import review
    path = Path(assessment_path)
    if not path.is_absolute() or path.resolve() != path or not path.is_file():
        raise ValueError('Completion requires an ordinary canonical assessment reference')
    assessment = json.loads(path.read_text())
    if (not isinstance(assessment, dict) or type(assessment.get('version')) is not int or assessment['version'] != 1 or
            assessment.get('candidate_id') != state['candidate']['id'] or
            assessment.get('spec_sha256') != state['spec']['sha256'] or
            assessment.get('consent_reference') != state['consent_reference']):
        raise ValueError('Completion assessment must bind current candidate, Spec and actual consent')
    candidate = api.capture(root, state['base'], state['candidate']['scope'])
    packet = review.validated_packet(root, folder, state, candidate)
    latest = state['latest_review']
    if latest is None or not latest.startswith('reviews/code-'):
        raise ValueError('Completion requires an actual latest Independent Review')
    report_path = resume.ordinary(folder, latest)
    if review.digest(report_path.read_bytes()) != state['review'].get('report_sha256'):
        raise ValueError('Latest review report changed')
    body = report_path.read_text()
    prefix, suffix = '# Code review attempt\n\n```json\n', '\n```\n'
    if not body.startswith(prefix) or not body.endswith(suffix):
        raise ValueError('Latest review report is malformed')
    report = json.loads(body[len(prefix):-len(suffix)])['actual_report']
    review.validate_report(report, packet, state, candidate)
    independence, _, _ = review.independence(report, packet)
    if independence != 'INDEPENDENT' or state['verification']['status'] != 'SUFFICIENT':
        raise ValueError('Completion requires valid Independent Review and sufficient actual verification')
    if sorted(set(report['coverage'])) != state['candidate']['scope']:
        raise ValueError('Latest review coverage is incomplete; obtain appropriate review')
    for field in ('implementation', 'verification', 'review_authenticity'):
        if not resume.text(assessment.get(field)):
            raise ValueError('Explicit inspected coordinator judgment required: ' + field)
    axes = assessment.get('axes')
    if not isinstance(axes, dict) or set(axes) != {'Spec Compliance', 'Code Quality'}:
        raise ValueError('Assess both applicable review axes against actual requirements and observations')
    for value in axes.values():
        if (not isinstance(value, dict) or value.get('status') != 'SATISFIED' or
                not resume.text(value.get('rationale'))):
            raise ValueError('Applicable axes need satisfied judgments and inspected reasons, not report strings')
    # Historical findings must have explicit dispositions. A change cannot be
    # approved by relabeling its old report or suppressing an earlier blocker.
    records, findings = report_inputs(folder)
    if assessment.get('reviews') != records:
        raise ValueError('Completion assessment must preserve and bind all actual code-review attempts')
    dispositions = assessment.get('findings')
    if not isinstance(dispositions, list) or not resume.strings(assessment.get('disclosed')):
        raise ValueError('Finding dispositions and disclosed remaining limitations are required')
    if any(item not in assessment['disclosed'] for item in report['limitations']):
        raise ValueError('Preserve every latest review limitation in the disclosed handoff')
    seen = set()
    for item in dispositions:
        if not isinstance(item, dict):
            raise ValueError('Malformed finding disposition')
        key = (item.get('review'), item.get('id'))
        if key not in findings or key in seen or not resume.text(item.get('rationale')):
            raise ValueError('Each actual finding requires exactly one grounded disposition')
        seen.add(key)
        disposition = item.get('disposition')
        if disposition == 'REPAIRED':
            original = findings[key]
            old_number = int(key[0].split('-')[-1].split('.')[0])
            new_number = int(latest.split('-')[-1].split('.')[0])
            if original['candidate_id'] == candidate['id'] or old_number >= new_number:
                raise ValueError('A repaired finding requires a new candidate and a later actual Independent Review')
        elif disposition not in ('NON_BLOCKING', 'PRE_EXISTING'):
            raise ValueError('Unresolved Blocking Findings prevent Completion; repair or hand off')
    if seen != set(findings):
        raise ValueError('Unassessed findings prevent Completion')
    return {'assessment_reference': str(path), 'assessment_sha256': review.digest(path.read_bytes()),
            'candidate_id': candidate['id'], 'spec_sha256': state['spec']['sha256'],
            'report_sha256': state['review']['report_sha256']}


def complete(api, root, task, assessment_path):
    resume.inspect(api, root, task)
    folder = api.task_path(root, task)
    state = json.loads((folder / 'state.json').read_text())
    if state['phase'] != 'REVIEW_READY':
        raise ValueError('Completion requires the latest reviewed, sufficiently verified candidate')
    binding = validate(api, root, folder, state, assessment_path)
    state.update(phase='COMPLETE', completion=binding, unresolved_blocker=None,
                 next_action='Local Completion only; preserve evidence and follow the team workflow for Issue, Git, merge, release or business acceptance')
    api.atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state
