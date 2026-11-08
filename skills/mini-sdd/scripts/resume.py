"""Inspect a local task checkpoint without granting review or Completion approval."""
import json
import importlib.util
from pathlib import Path
import re
import review


def text(value):
    return isinstance(value, str) and bool(value.strip())


def sha(value):
    return isinstance(value, str) and re.fullmatch(r'[0-9a-f]{64}', value) is not None


def strings(value):
    return isinstance(value, list) and all(text(item) for item in value)


def schema(state):
    """Validate the index shape before reading referenced records or permitting writes."""
    if not text(state['next_action']) or not (state['unresolved_blocker'] is None or text(state['unresolved_blocker'])):
        raise ValueError('Malformed task next action or blocker')
    phase = state['phase']
    consent = state.get('consent_reference')
    if consent is not None and not text(consent):
        raise ValueError('Malformed implementation consent reference')
    if phase != 'AWAITING_CONSENT' and not text(consent):
        raise ValueError('Current scope consent is missing')
    if phase in ('IMPLEMENTING', 'REVIEW_READY', 'BLOCKED_VERIFICATION', 'COMPLETE') and state.get('implementation_started') is not True:
        raise ValueError('Implementation checkpoint lacks its original base binding')
    candidate = state['candidate']
    if candidate is not None:
        if (not isinstance(candidate, dict) or not {'id', 'head', 'scope'}.issubset(candidate) or
                set(candidate) - {'id', 'head', 'scope', 'manifest'} or not sha(candidate['id']) or
                not isinstance(candidate['head'], str) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', candidate['head']) or
                not strings(candidate['scope']) or not candidate['scope'] or candidate['scope'] != sorted(set(candidate['scope'])) or
                ('manifest' in candidate and candidate['manifest'] != 'candidate-' + candidate['id'] + '.json')):
            raise ValueError('Malformed candidate index')
    if phase in ('REVIEW_READY', 'BLOCKED_VERIFICATION', 'COMPLETE') and candidate is None:
        raise ValueError('Implementation checkpoint requires an actual candidate')
    if candidate is not None and phase not in ('REVIEW_READY', 'BLOCKED_VERIFICATION', 'COMPLETE'):
        raise ValueError('Candidate is inconsistent with task phase')
    verification = state.get('verification')
    if verification is not None:
        if (not isinstance(verification, dict) or set(verification) != {'status', 'references', 'assessment_reference', 'missing'} or
                verification['status'] not in ('SUFFICIENT', 'INCOMPLETE') or not strings(verification['references']) or
                not text(verification['assessment_reference']) or not strings(verification['missing']) or
                (verification['status'] == 'SUFFICIENT' and (not verification['references'] or verification['missing'])) or
                (verification['status'] == 'INCOMPLETE' and not verification['missing'])):
            raise ValueError('Malformed verification evidence index')
    if candidate is not None and (verification is None or (phase in ('REVIEW_READY', 'COMPLETE') and verification['status'] != 'SUFFICIENT')):
        raise ValueError('Candidate verification is missing or inconsistent')
    latest = state['latest_review']
    if latest is not None and (not isinstance(latest, str) or not re.fullmatch(r'reviews/(spec|code)-\d{2,}\.md', latest)):
        raise ValueError('Malformed latest review reference')
    pending = state.get('review')
    if pending is not None:
        if (not isinstance(pending, dict) or pending.get('status') not in ('PENDING', 'REVIEWED') or
                not isinstance(pending.get('packet'), str) or not re.fullmatch(r'review-launch-[0-9a-f]{64}\.json', pending['packet']) or
                not sha(pending.get('packet_sha256'))):
            raise ValueError('Malformed review checkpoint')
        if candidate is None or phase not in ('REVIEW_READY', 'COMPLETE'):
            raise ValueError('Review checkpoint is stale for the current task phase')
    if latest and latest.startswith('reviews/code-') and pending is None:
        raise ValueError('Latest code review lacks its launch packet binding')
    completion = state.get('completion')
    if completion is not None and (not isinstance(completion, dict) or phase != 'COMPLETE' or
            set(completion) != {'assessment_reference', 'assessment_sha256', 'candidate_id', 'spec_sha256', 'report_sha256'} or
            not text(completion.get('assessment_reference')) or not all(sha(completion.get(key)) for key in
                ('assessment_sha256', 'candidate_id', 'spec_sha256', 'report_sha256'))):
        raise ValueError('Malformed Completion assessment index')
    if pending and pending['status'] == 'REVIEWED' and (latest is None or not latest.startswith('reviews/code-')):
        raise ValueError('Reviewed index has no actual code-review report')
    if pending and latest and latest.startswith('reviews/code-'):
        if (pending.get('candidate_id') != candidate['id'] or pending.get('spec_sha256') != state['spec']['sha256'] or
                not sha(pending.get('report_sha256'))):
            raise ValueError('Latest report index has a mismatched candidate, Spec or digest')


def ordinary(folder, relative):
    path = folder / relative
    if path.resolve() != path or not path.is_file():
        raise ValueError('Missing or unsafe referenced record: ' + relative)
    return path


def inspect(api, root, task, update_state=False):
    try:
        return inspect_checkpoint(api, root, task, update_state)
    except (KeyError, TypeError, AttributeError) as error:
        raise ValueError('Malformed referenced task record: ' + str(error)) from error


def inspect_checkpoint(api, root, task, update_state):
    worktree = api.identity(root)
    folder = api.task_path(root, task)
    for name in ('state.json', 'spec.md'):
        path = folder / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Resume requires existing ordinary task records')
    state = json.loads((folder / 'state.json').read_text())
    api.recognized_record(root, folder, state, worktree)
    schema(state)
    for other in folder.parent.iterdir():
        if other == folder:
            continue
        index = other / 'state.json'
        if other.is_symlink() or not other.is_dir() or index.is_symlink() or not index.is_file():
            raise ValueError('Unrecognized sibling task; inspect before resuming a writer')
        previous = json.loads(index.read_text())
        api.recognized_record(root, other, previous, worktree)
        if previous['phase'] != 'COMPLETE':
            raise ValueError('One Full Task writer per worktree; another task remains active')
    if state.get('implementation_started'):
        api.git(root, 'merge-base', '--is-ancestor', state['base'], 'HEAD')
    elif state['base'] != api.git(root, 'rev-parse', '--verify', 'HEAD^{commit}'):
        raise ValueError('Fixed Git base changed before implementation')
    candidate = state['candidate']
    if candidate is not None:
        actual = api.capture(root, state['base'], candidate['scope'])
        if actual['id'] != candidate['id'] or actual['head'] != candidate['head']:
            raise ValueError('Candidate drift; verify the actual inputs and obtain appropriate re-review')
        dirty = any(item['head'] != item['index'] or item['index'] != item['worktree'] for item in actual['files'])
        if dirty and 'manifest' not in candidate:
            raise ValueError('Dirty or untracked candidate requires its preserved manifest')
        if 'manifest' in candidate and json.loads(ordinary(folder, candidate['manifest']).read_text()) != actual:
            raise ValueError('Candidate manifest is malformed or mismatched')
    if state['latest_review'] is not None:
        ordinary(folder, state['latest_review'])
    # Reuse canonical raw workspace enumeration: even name-only worktree diffs
    # otherwise execute configured clean/process filters. Empty ownership reads
    # no patches; committed-to-committed names need no worktree conversion.
    source = Path(__file__).resolve().parents[2] / 'review-diff/scripts/workspace_scope.py'
    module_spec = importlib.util.spec_from_file_location('mini_sdd_workspace_scope', source)
    workspace = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(workspace)
    changed = {entry['path'] for entry in workspace.inspect(root, [])['files']}
    changed.update(name for name in api.git(root, 'diff', '--no-ext-diff', '--no-textconv',
                   '--no-renames', '--ignore-submodules=dirty', '--name-only', '-z', state['base'], 'HEAD', '--').split('\0') if name)
    changed = {name for name in changed if not any(part.casefold() in ('.specdd', '.git') for part in Path(name).parts)}
    owned = set(candidate['scope']) if candidate else set()
    status = 'READY'
    limitations = ['Structural validation is not evidence of user consent, verification sufficiency or review authenticity']
    latest = state['latest_review']
    if latest and latest.startswith('reviews/spec-'):
        body = ordinary(folder, latest).read_text()
        match = re.fullmatch(r'# Spec review attempt\n\nSpec: spec\.md\nRevision: ([^\n]+)\nSHA-256: ([0-9a-f]{64})\n\n(\s*\S[\s\S]*)', body)
        if match is None:
            raise ValueError('Latest optional Spec Review is malformed or lacks its revision/digest')
        if match.group(1) != state['spec']['revision'] or match.group(2) != state['spec']['sha256']:
            limitations.append('Optional Spec Review belongs to an earlier revision; it supplies no current approval')
        else:
            limitations.append('Optional Spec Review record is bound to this revision; inspect actual observations, not the pointer alone')
    if changed - owned:
        limitations.append('Changed paths outside the recorded candidate are excluded; inspect ownership before expanding scope')
    if state['phase'] == 'AWAITING_CONSENT':
        status = 'PENDING'
    elif state['phase'] in ('BLOCKED_VERIFICATION', 'COMPLETE'):
        status = 'UNKNOWN'
        limitations.append('Necessary verification or Completion assessment remains outstanding')
    review_result = None
    if state.get('review'):
        packet = review.validated_packet(root, folder, state, actual)
        review_result = {'status': 'PENDING', 'packet': state['review']['packet'], 'independence': 'UNVERIFIED'}
        status = 'PENDING'
        latest = state['latest_review']
        if latest is not None and latest.startswith('reviews/code-'):
            report_path = ordinary(folder, latest)
            if review.digest(report_path.read_bytes()) != state['review'].get('report_sha256'):
                raise ValueError('Latest review report digest is missing or changed')
            body = report_path.read_text()
            prefix, suffix = '# Code review attempt\n\n```json\n', '\n```\n'
            if not body.startswith(prefix) or not body.endswith(suffix):
                raise ValueError('Latest review report is malformed')
            envelope = json.loads(body[len(prefix):-len(suffix)])
            if not isinstance(envelope, dict) or not isinstance(envelope.get('actual_report'), dict):
                raise ValueError('Latest review report lacks the actual attributed report')
            report = envelope['actual_report']
            review.validate_report(report, packet, state, actual)
            classification, reasons, source = review.independence(report, packet)
            review_result.update(independence=classification, evidence_source=source)
            limitations.extend(reasons)
            if classification == 'INDEPENDENT':
                status = 'UNKNOWN'
                review_result['status'] = 'REVIEWED'
                limitations.append('Observer authenticity, actual findings and verification sufficiency require inspection by the resuming session')
        if status == 'PENDING':
            next_action = 'Obtain verifiable separate-context read-only review using ' + state['review']['packet']
        else:
            next_action = 'Inspect the actual report, observer evidence and verification before relying on prior results; Completion remains outstanding'
    else:
        next_action = state['next_action']
    result = {'status': status, 'task_id': task, 'phase': state['phase'],
              'spec': state['spec'], 'base': state['base'], 'candidate': candidate,
              'latest_review': state['latest_review'], 'next_action': next_action,
              'unresolved_blocker': state['unresolved_blocker'], 'limitations': limitations,
              'current_diff': {'owned_paths': sorted(changed & owned), 'excluded_paths': sorted(changed - owned)}}
    if state.get('verification'):
        result['verification_inputs'] = review.verification_inputs(root, state['verification'])
    if review_result:
        result['review'] = review_result
    if state['phase'] == 'COMPLETE':
        if state.get('completion') is None:
            limitations.append('Historical COMPLETE index has no inspected Completion assessment; no approval follows')
        else:
            import completion
            binding = completion.validate(api, root, folder, state, state['completion']['assessment_reference'])
            if binding != state['completion']:
                raise ValueError('Completion assessment or its inputs changed')
            result['completion'] = {'status': 'ATTRIBUTABLE', **binding}
            limitations.remove('Necessary verification or Completion assessment remains outstanding')
            next_action = 'Inspect attributable Completion judgments and current limitations before relying on them; no Git, Issue, release or business authority follows'
            result['next_action'] = next_action
    if update_state:
        state['next_action'] = next_action
        if status == 'PENDING' and review_result:
            state['unresolved_blocker'] = 'Independent Review remains pending; inspect the current resume result'
            result['unresolved_blocker'] = state['unresolved_blocker']
        api.atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return result
