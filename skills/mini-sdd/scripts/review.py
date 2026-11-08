"""Candidate-bound launch packets and attributed reports; never launch a reviewer."""
import hashlib
import json
import os
import tempfile
from pathlib import Path
import re


def digest(data):
    return hashlib.sha256(data).hexdigest()


def current(api, root, task):
    folder, state = api.load_draft(root, task, allow_implementation=True)
    if state['phase'] != 'REVIEW_READY' or not state.get('candidate') or not state.get('consent_reference'):
        raise ValueError('Review requires a consented REVIEW_READY candidate with sufficient verification')
    candidate = api.capture(root, state['base'], state['candidate']['scope'])
    if candidate['id'] != state['candidate']['id']:
        raise ValueError('Candidate changed; checkpoint and verify the actual inputs before review')
    return folder, state, candidate


def publish(path, content):
    # Exclusive publication; an identical packet is reusable, reports never replace attempts.
    if path.is_symlink() or (path.exists() and (not path.is_file() or path.read_bytes() != content)):
        raise ValueError('Existing review artifact collision; preserve it')
    if not path.exists():
        with tempfile.NamedTemporaryFile('wb', dir=path.parent, prefix='.review-', delete=False) as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
            temporary = stream.name
        try:
            os.link(temporary, path)
        finally:
            os.unlink(temporary)


def verification_inputs(root, verification):
    inputs = []
    for reference in [verification['assessment_reference'], *verification['references']]:
        path = Path(reference)
        if not path.is_absolute():
            path = root / path
        if path.resolve() == path and path.is_file():
            inputs.append({'reference': reference, 'path': str(path), 'sha256': digest(path.read_bytes()), 'status': 'AVAILABLE'})
        else:
            inputs.append({'reference': reference, 'status': 'UNAVAILABLE',
                           'limitation': 'No ordinary canonical evidence file at this exact reference; inspect accessible source separately, never infer verification PASS'})
    return inputs


def packet(api, root, task, rules, limitations, implementation_context):
    folder, state, candidate = current(api, root, task)
    rule_inputs = []
    for name in rules:
        path = root / name
        relative = Path(name)
        if relative.is_absolute() or '..' in relative.parts or any(root.joinpath(*relative.parts[:i]).is_symlink() for i in range(1, len(relative.parts) + 1)) or not path.is_file():
            raise ValueError('Repository rules must be ordinary root-relative files')
        data = path.read_bytes()
        rule_inputs.append({'path': name, 'sha256': digest(data), 'content': data.decode('utf-8')})
    if any(not item.strip() for item in limitations):
        raise ValueError('State actual limitations, not empty placeholders')
    core = Path(__file__).resolve().parents[2] / 'review-diff' / 'SKILL.md'
    contract = core.parent / 'references' / 'report.md'
    payload = {'version': 1, 'task_id': task, 'implementation_context': implementation_context, 'worktree': state['worktree'],
               'base': state['base'], 'candidate': candidate,
               'spec': {**state['spec'], 'content': (folder / 'spec.md').read_text()},
               'accepted_scope': state['candidate']['scope'], 'repository_rules': rule_inputs,
               'verification': state['verification'], 'verification_inputs': verification_inputs(root, state['verification']), 'limitations': limitations,
               'review_entry': str(core), 'review_entry_sha256': digest(core.read_bytes()),
               'requirements': contract.read_text(), 'requirements_sha256': digest(contract.read_bytes()),
               'read_only_expectations': 'Separate context; inspect only. No tests, corrective tools, product/task/Git writes, publishing or remote comments. Return report to coordinator.',
               'result_contract': {'candidate_id': candidate['id'], 'spec_sha256': state['spec']['sha256'],
                                   'base': state['base'], 'verification': 'NOT_RUN',
                                   'axes': ['Spec Compliance', 'Code Quality'],
                                   'independence_evidence': 'Inspectable observer/host evidence of separate context, exact inputs, enforced read-only controls and no writes. Reviewer self-declaration alone is insufficient.'}}
    identifier = digest(json.dumps(payload, sort_keys=True).encode())
    filename = 'review-launch-' + identifier + '.json'
    publish(folder / filename, (json.dumps(payload, indent=2) + '\n').encode())
    state['review'] = {'status': 'PENDING', 'packet': filename, 'packet_sha256': digest((folder / filename).read_bytes())}
    state['next_action'] = 'Launch canonical review-diff in a verifiable separate read-only context using ' + filename
    api.atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def validated_packet(root, folder, state, candidate):
    pending = state.get('review', {})
    name = pending.get('packet', '')
    if not re.fullmatch(r'review-launch-[0-9a-f]{64}\.json', name):
        raise ValueError('Prepare the current review packet before recording an actual attempt')
    path = folder / name
    if path.is_symlink() or not path.is_file() or digest(path.read_bytes()) != pending.get('packet_sha256'):
        raise ValueError('Review packet input changed')
    packet = json.loads(path.read_text())
    if not isinstance(packet, dict) or packet.get('worktree') != state['worktree']:
        raise ValueError('Review packet worktree identity is invalid')
    identifier = digest(json.dumps(packet, sort_keys=True).encode())
    if (name != 'review-launch-' + identifier + '.json' or type(packet.get('version')) is not int or packet['version'] != 1 or
            packet.get('task_id') != state['task_id'] or packet.get('candidate') != candidate or
            packet.get('base') != state['base'] or packet.get('accepted_scope') != state['candidate']['scope'] or
            packet.get('spec') != {**state['spec'], 'content': (folder / 'spec.md').read_text()} or
            packet.get('verification') != state['verification'] or not isinstance(packet.get('repository_rules'), list)):
        raise ValueError('Review packet must bind the actual candidate, Spec, base and verification')
    for item in packet['repository_rules']:
        rule = root / item['path']
        if rule.resolve() != rule or not rule.is_file() or digest(rule.read_bytes()) != item['sha256']:
            raise ValueError('Repository rules changed; prepare current review inputs')
    core = Path(__file__).resolve().parents[2] / 'review-diff' / 'SKILL.md'
    contract = core.parent / 'references' / 'report.md'
    if digest(core.read_bytes()) != packet.get('review_entry_sha256') or digest(contract.read_bytes()) != packet.get('requirements_sha256'):
        raise ValueError('Canonical review requirements changed; prepare current review inputs')
    if verification_inputs(root, state['verification']) != packet.get('verification_inputs'):
        raise ValueError('Verification evidence changed; recheck observations and prepare a new review packet')
    return packet


def validate_report(report, packet, state, candidate):
    pending = state['review']
    if (not isinstance(report, dict) or type(report.get('version')) is not int or report['version'] != 1 or
            report.get('candidate_id') != candidate['id'] or report.get('spec_sha256') != state['spec']['sha256'] or
            report.get('base') != state['base'] or report.get('packet_sha256') != pending['packet_sha256'] or
            packet['candidate'] != candidate or packet['spec']['sha256'] != state['spec']['sha256'] or
            packet['verification'] != state['verification']):
        raise ValueError('Review must bind the actual candidate, Spec, base, verification and launch packet')
    for field in ('reviewer', 'review_context', 'report'):
        if not isinstance(report.get(field), str) or not report[field].strip() or report[field].strip().upper() in ('TODO', 'PENDING', 'TEMPLATE'):
            raise ValueError('Actual attributable report required: ' + field)
    if (not isinstance(report.get('coverage'), list) or not report['coverage'] or
            any(p not in state['candidate']['scope'] for p in report['coverage']) or
            not isinstance(report.get('limitations'), list) or
            report.get('verification') != 'NOT_RUN' or
            not isinstance(report.get('axes'), dict) or set(report['axes']) != {'Spec Compliance', 'Code Quality'} or
            any(not isinstance(value, str) or not value.strip() for value in report['axes'].values()) or
            not isinstance(report.get('findings'), list) or not isinstance(report.get('evidence'), list)):
        raise ValueError('Actual coverage, both review axes, limitations, findings and NOT_RUN verification are required')
    required = {'id', 'axis', 'severity', 'file', 'line', 'expected', 'actual', 'evidence', 'impact', 'remedy', 'verification'}
    seen = set()
    for finding in report['findings']:
        if (not isinstance(finding, dict) or not required.issubset(finding) or
                any(not isinstance(finding[key], str) or not finding[key].strip() for key in required - {'line'}) or
                type(finding['line']) is not int or finding['line'] < 1 or
                finding['file'] not in report['coverage'] or finding['axis'] not in report['axes'] or
                finding['verification'] != 'NOT_RUN' or finding['id'] in seen):
            raise ValueError('Each finding needs grounded location, expected/actual, evidence, impact, remedy and verification')
        seen.add(finding['id'])


def record(api, root, task, body):
    folder, state, candidate = current(api, root, task)
    packet = validated_packet(root, folder, state, candidate)
    pending = state['review']
    name = pending['packet']
    report = json.loads(body)
    validate_report(report, packet, state, candidate)
    classification, reasons, source = independence(report, packet)
    reviews = folder / 'reviews'
    if reviews.is_symlink() or (reviews.exists() and not reviews.is_dir()):
        raise ValueError('Review storage must be an ordinary directory')
    numbers = []
    if reviews.exists():
        for existing in reviews.iterdir():
            match = re.fullmatch(r'code-(\d{2,})\.md', existing.name)
            if match:
                if existing.is_symlink() or not existing.is_file():
                    raise ValueError('Existing reports are protected')
                numbers.append(int(match.group(1)))
    reviews.mkdir(exist_ok=True)
    filename = 'code-%02d.md' % (max(numbers, default=0) + 1)
    result = {'independence': classification, 'evidence_source': source, 'limitations': reasons, 'actual_report': report}
    publish(reviews / filename, ('# Code review attempt\n\n```json\n' + json.dumps(result, indent=2) + '\n```\n').encode())
    state['latest_review'] = 'reviews/' + filename
    state['review'].update(candidate_id=candidate['id'], spec_sha256=state['spec']['sha256'], status='REVIEWED' if classification == 'INDEPENDENT' else 'PENDING',
                           independence=classification, evidence_source=source,
                           report_sha256=digest((reviews / filename).read_bytes()))
    state['next_action'] = ('Assess findings against the accepted scope; Completion remains outstanding' if classification == 'INDEPENDENT'
                            else 'Obtain verifiable separate-context read-only review using ' + name)
    api.atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def independence(report, packet):
    """Validate supplied relationships, not authenticity or the truth of observations."""
    implementation = packet.get('implementation_context')
    context = report['review_context']
    if context == implementation:
        return 'SELF_CHECK', ['Review shares the recorded implementation context'], None
    reasons = []
    sources = set()
    for reference in report['evidence']:
        try:
            if not isinstance(reference, dict) or reference.get('source') not in ('manual', 'host-captured'):
                raise ValueError('Evidence source must be manual or host-captured observer evidence')
            path = Path(reference['path'])
            if not path.is_absolute() or path.resolve() != path or not path.is_file() or digest(path.read_bytes()) != reference.get('sha256'):
                raise ValueError('Observer evidence path or digest is unavailable or changed')
            receipt = json.loads(path.read_text())
            if (not isinstance(receipt, dict) or receipt.get('candidate_id') != report['candidate_id'] or receipt.get('packet_sha256') != report['packet_sha256'] or
                    receipt.get('implementation_context') != implementation or receipt.get('review_context') != context or
                    implementation in (None, '', 'unavailable') or receipt.get('provenance') != reference['source'] or
                    receipt.get('observer') in (None, '', report['reviewer'], context)):
                raise ValueError('Observer receipt does not establish the distinct contexts and exact inputs')
            for key in ('separate_context', 'input_identity', 'no_writes'):
                if not isinstance(receipt.get(key), str) or not receipt[key].strip():
                    raise ValueError('Missing inspectable observer observation: ' + key)
            controls = receipt.get('read_only_controls', {})
            if (not isinstance(controls, dict) or controls.get('enforcement') not in ('sandbox-read-only', 'tool-policy-read-only', 'mount-read-only') or
                    not isinstance(controls.get('observation'), str) or not controls['observation'].strip()):
                raise ValueError('Enforced read-only controls are not established; instructions alone are insufficient')
            sources.add(reference['source'])
        except (OSError, ValueError, KeyError, TypeError) as error:
            reasons.append(str(error))
    if sources and not reasons:
        return 'INDEPENDENT', ['Caller must inspect receipt authenticity and observations; relationship validation alone proves no real review'], '+'.join(sorted(sources))
    return 'UNVERIFIED', reasons or ['Separate context and enforced read-only controls need inspected observer/host evidence'], None
