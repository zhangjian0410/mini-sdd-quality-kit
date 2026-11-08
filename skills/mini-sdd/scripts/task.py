"""Local Full Task consent, implementation and candidate index (Python 3.11+)."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

from candidate import capture


SECTIONS = ('Goal', 'Current Behavior', 'Change / Scope', 'Acceptance Criteria',
            'Constraints / Non-goals', 'Verification')


def git(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_NO_LAZY_FETCH'] = '1'
    run = subprocess.run(['git', '--no-lazy-fetch', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                          '-c', 'core.untrackedCache=false', '-C', str(root), *args],
                         env=env, capture_output=True, text=True)
    if run.returncode:
        raise ValueError('Git worktree unavailable: ' + run.stderr.strip())
    return run.stdout.strip()


def identity(root: Path) -> dict:
    if git(root, 'rev-parse', '--show-toplevel') != str(root):
        raise ValueError('Use the actual Git worktree root')
    return {'root': str(root), 'git_dir': git(root, 'rev-parse', '--absolute-git-dir')}


def task_path(root: Path, task: str) -> Path:
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', task):
        raise ValueError('SAFE-TASK-ID must be 1-64 ASCII letters, digits, underscores or hyphens')
    storage = root / '.specdd'
    if storage.is_symlink() or (storage.exists() and not storage.is_dir()):
        raise ValueError('Task storage must be an ordinary directory')
    folder = storage / task
    if folder.is_symlink():
        raise ValueError('Task directory cannot be a symlink')
    # Git pathspecs remain case-sensitive on case-insensitive volumes. Inspect
    # indexed spellings so aliases cannot hide tracked records from any writer.
    if any(name.split('/', 1)[0].casefold() == '.specdd'
           for name in git(root, 'ls-files', '-z').split('\0') if name):
        raise ValueError('Tracked task storage, including case aliases, is protected; leave it unchanged')
    return folder


def spec_identity(content: str) -> dict:
    revision = re.search(r'^Revision:[ \t]*(\S[^\r\n]*)\r?$', content, re.M)
    if not revision:
        raise ValueError('Mini Spec requires a nonempty Revision: line')
    for section in SECTIONS:
        match = re.search(r'^## ' + re.escape(section) + r'\s*\n(.*?)(?=^## |\Z)', content, re.M | re.S)
        if not match or not match.group(1).strip():
            raise ValueError('Mini Spec requires nonempty section: ' + section)
    return {'path': 'spec.md', 'revision': revision.group(1).strip(),
            'sha256': hashlib.sha256(content.encode('utf-8')).hexdigest()}


def atomic_write(path: Path, content: str) -> None:
    # Only called on paths owned by this task after collision/schema checks.
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='',
                                     dir=path.parent, prefix='.' + path.name + '-', delete=False) as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    os.replace(temporary, path)


def recognized_record(root: Path, folder: Path, state: dict, worktree: dict) -> None:
    """Recognize historical storage, without certifying Completion or review."""
    fields = {'version', 'task_id', 'worktree', 'phase', 'spec', 'base',
              'candidate', 'latest_review', 'next_action', 'unresolved_blocker'}
    spec_file = folder / 'spec.md'
    if (not isinstance(state, dict) or not fields.issubset(state) or
            type(state['version']) is not int or state['version'] != 1 or
            state['task_id'] != folder.name or state['worktree'] != worktree or
            state['phase'] not in ('AWAITING_CONSENT', 'READY_TO_IMPLEMENT', 'IMPLEMENTING',
                                   'REVIEW_READY', 'BLOCKED_VERIFICATION', 'COMPLETE') or
            ('implementation_started' in state and type(state['implementation_started']) is not bool) or
            spec_file.is_symlink() or not spec_file.is_file() or
            not isinstance(state['base'], str) or not re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', state['base'])):
        raise ValueError('Existing task record is unrecognized; inspect before starting')
    if state['spec'] != spec_identity(spec_file.read_bytes().decode('utf-8')):
        raise ValueError('Existing task Mini Spec binding is invalid; inspect before starting')
    if git(root, 'rev-parse', '--verify', state['base'] + '^{commit}') != state['base']:
        raise ValueError('Existing task base is unavailable; inspect before starting')


def create(root: Path, task: str, content: str) -> dict:
    worktree = identity(root)
    folder = task_path(root, task)
    spec = spec_identity(content)
    if folder.exists():
        raise ValueError('Task directory already exists; no overwrite or cleanup performed')
    storage = folder.parent
    if storage.exists():
        for other in storage.iterdir():
            if other.is_symlink() or not other.is_dir():
                raise ValueError('Unrecognized task storage; inspect it before starting another task')
            index = other / 'state.json'
            if index.is_symlink() or not index.is_file():
                raise ValueError('Existing task has no safe state index; inspect before starting')
            try:
                prior = json.loads(index.read_text())
            except (ValueError, KeyError, TypeError):
                raise ValueError('Existing task state is malformed; inspect before starting')
            recognized_record(root, other, prior, worktree)
            if prior['phase'] != 'COMPLETE':
                raise ValueError('One Full Task writer per worktree; existing task remains active')
    base = git(root, 'rev-parse', '--verify', 'HEAD^{commit}')
    state = {'version': 1, 'task_id': task, 'worktree': worktree,
             'phase': 'AWAITING_CONSENT', 'spec': spec, 'base': base,
             'candidate': None, 'latest_review': None,
             'next_action': 'Confirm Mini Spec revision and implementation scope',
             'unresolved_blocker': 'Implementation consent is pending'}
    storage.mkdir(exist_ok=True)
    folder.mkdir()  # Exclusive creation: never reuse a colliding directory.
    atomic_write(folder / 'spec.md', content)
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def load_draft(root: Path, task: str, allow_implementation: bool = False) -> tuple[Path, dict]:
    worktree = identity(root)
    folder = task_path(root, task)
    for name in ('spec.md', 'state.json'):
        path = folder / name
        if path.is_symlink() or not path.is_file():
            raise ValueError('Task records must be existing ordinary files')
    state = json.loads((folder / 'state.json').read_text())
    actual = spec_identity((folder / 'spec.md').read_bytes().decode('utf-8'))
    phases = ('AWAITING_CONSENT', 'READY_TO_IMPLEMENT')
    if allow_implementation:
        phases += ('IMPLEMENTING', 'REVIEW_READY', 'BLOCKED_VERIFICATION')
    if (not isinstance(state, dict) or state.get('version') != 1 or
            state.get('task_id') != task or state.get('worktree') != worktree or
            state.get('phase') not in phases or state.get('spec') != actual or
            ('implementation_started' in state and type(state['implementation_started']) is not bool)):
        raise ValueError('Task identity or Mini Spec changed; inspect before consent')
    if state.get('implementation_started') is True:
        recognized_record(root, folder, state, worktree)
        git(root, 'merge-base', '--is-ancestor', state['base'], 'HEAD')
    elif state.get('base') != git(root, 'rev-parse', '--verify', 'HEAD^{commit}'):
        raise ValueError('Git base changed; inspect before consent')
    return folder, state


def confirm(root: Path, task: str, digest: str, reference: str) -> dict:
    folder, state = load_draft(root, task)
    actual = state['spec']
    if state['phase'] != 'AWAITING_CONSENT':
        raise ValueError('Only an awaiting-consent task can be confirmed')
    if digest != actual['sha256'] or not reference.strip():
        raise ValueError('Consent must reference the exact Mini Spec digest and actual user approval')
    state.update(phase='READY_TO_IMPLEMENT', consent_reference=reference.strip(),
                 next_action='Implement only the confirmed Mini Spec scope', unresolved_blocker=None)
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def begin(root: Path, task: str) -> dict:
    folder, state = load_draft(root, task)
    if state['phase'] != 'READY_TO_IMPLEMENT' or not state.get('consent_reference'):
        raise ValueError('Implementation requires current Mini Spec scope consent')
    state.update(phase='IMPLEMENTING', implementation_started=True,
                 next_action='Implement and verify only the consented scope')
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def checkpoint(root: Path, task: str, owned: list[str], status: str,
               assessment: str, references: list[str], missing: list[str]) -> dict:
    folder = task_path(root, task)
    for name in ('spec.md', 'state.json'):
        if (folder / name).is_symlink() or not (folder / name).is_file():
            raise ValueError('Implementation task records must be ordinary existing files')
    state = json.loads((folder / 'state.json').read_text())
    recognized_record(root, folder, state, identity(root))
    if state['phase'] not in ('IMPLEMENTING', 'REVIEW_READY', 'BLOCKED_VERIFICATION') or not state.get('consent_reference'):
        raise ValueError('Checkpoint requires consented implementation')
    if not assessment.strip() or any(not ref.strip() for ref in references + missing):
        raise ValueError('Verification requires an actual sufficiency assessment and nonempty references')
    if status == 'SUFFICIENT' and (not references or missing):
        raise ValueError('Sufficient verification requires actual evidence and no necessary missing checks')
    if status == 'INCOMPLETE' and not missing:
        raise ValueError('Incomplete verification must identify its missing evidence')
    manifest = capture(root, state['base'], owned)
    dirty = any(entry['head'] != entry['index'] or entry['index'] != entry['worktree'] for entry in manifest['files'])
    candidate = {'id': manifest['id'], 'head': manifest['head'], 'scope': sorted(set(owned))}
    if dirty:
        filename = 'candidate-' + manifest['id'] + '.json'
        path = folder / filename
        content = json.dumps(manifest, sort_keys=True, indent=2) + '\n'
        if path.is_symlink() or (path.exists() and path.read_bytes() != content.encode()):
            raise ValueError('Candidate manifest collision; preserve existing evidence')
        if not path.exists():
            # Publish complete bytes atomically and never replace an old manifest.
            with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=folder,
                                             prefix='.candidate-', delete=False) as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                temporary = stream.name
            try:
                os.link(temporary, path)
            finally:
                os.unlink(temporary)
        candidate['manifest'] = filename
    for key in ('review', 'completion'):
        state.pop(key, None)
    if state['latest_review'] and state['latest_review'].startswith('reviews/code-'):
        state['latest_review'] = None
    state.update(candidate=candidate,
                 verification={'status': status, 'references': references,
                               'assessment_reference': assessment.strip(), 'missing': missing},
                 phase='REVIEW_READY' if status == 'SUFFICIENT' else 'BLOCKED_VERIFICATION',
                 next_action='Obtain Independent Review of this candidate' if status == 'SUFFICIENT' else 'Complete the missing verification or hand off unresolved work',
                 unresolved_blocker=None if status == 'SUFFICIENT' else '; '.join(missing))
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def revise(root: Path, task: str, previous: str, content: str) -> dict:
    folder, state = load_draft(root, task, allow_implementation=True)
    replacement = spec_identity(content)
    if previous != state['spec']['sha256'] or replacement['revision'] == state['spec']['revision']:
        raise ValueError('Revision requires the current digest and a new revision identity')
    state.update(spec=replacement, phase='AWAITING_CONSENT',
                 next_action='Confirm revised Mini Spec and implementation scope',
                 unresolved_blocker='Implementation consent is pending')
    state.pop('consent_reference', None)
    state['candidate'] = None
    for key in ('verification', 'review', 'completion'):
        state.pop(key, None)
    if state['latest_review'] and state['latest_review'].startswith('reviews/code-'):
        state['latest_review'] = None
    # Two atomic file writes, not a multi-file transaction. An interrupted pair
    # fails the next digest check; it never grants approval from a stale index.
    atomic_write(folder / 'spec.md', content)
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def spec_review(root: Path, task: str, digest: str, body: str) -> dict:
    folder, state = load_draft(root, task)
    if digest != state['spec']['sha256'] or not body.strip():
        raise ValueError('An actual nonempty review must reference the current Mini Spec digest')
    reviews = folder / 'reviews'
    if reviews.is_symlink() or (reviews.exists() and not reviews.is_dir()):
        raise ValueError('Review storage must be an ordinary directory')
    reviews.mkdir(exist_ok=True)
    numbers = []
    for path in reviews.iterdir():
        match = re.fullmatch(r'spec-(\d{2,})\.md', path.name)
        if match:
            if path.is_symlink() or not path.is_file():
                raise ValueError('Existing review records are protected')
            numbers.append(int(match.group(1)))
    report = reviews / ('spec-%02d.md' % (max(numbers, default=0) + 1))
    content = ('# Spec review attempt\n\nSpec: spec.md\nRevision: ' + state['spec']['revision'] +
               '\nSHA-256: ' + digest + '\n\n' + body)
    # Publish a complete new report atomically without overwriting an attempt.
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', newline='', dir=reviews,
                                     prefix='.spec-review-', delete=False) as stream:
        stream.write(content)
        stream.flush()
        os.fsync(stream.fileno())
        temporary = stream.name
    try:
        os.link(temporary, report)
    finally:
        os.unlink(temporary)
    state['latest_review'] = report.relative_to(folder).as_posix()
    atomic_write(folder / 'state.json', json.dumps(state, indent=2) + '\n')
    return state


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    start = sub.add_parser('create', help='Create a task from a Mini Spec supplied on stdin')
    start.add_argument('--task', required=True)
    consent = sub.add_parser('confirm', help='Record an actual user approval reference for this exact Mini Spec')
    consent.add_argument('--task', required=True)
    consent.add_argument('--spec-sha256', required=True)
    consent.add_argument('--consent-reference', required=True)
    revision = sub.add_parser('revise', help='Replace a draft Mini Spec from stdin and require renewed consent')
    revision.add_argument('--task', required=True)
    revision.add_argument('--previous-sha256', required=True)
    review = sub.add_parser('spec-review', help='Record an actual optional Spec Review supplied on stdin')
    review.add_argument('--task', required=True)
    review.add_argument('--spec-sha256', required=True)
    implement = sub.add_parser('begin', help='Enter implementation only after current scope consent')
    implement.add_argument('--task', required=True)
    freeze = sub.add_parser('checkpoint', help='Identify accepted candidate inputs and reference actual verification')
    freeze.add_argument('--task', required=True)
    freeze.add_argument('--owned', action='append', default=[])
    freeze.add_argument('--verification-status', choices=('SUFFICIENT', 'INCOMPLETE'), required=True)
    freeze.add_argument('--assessment-reference', required=True)
    freeze.add_argument('--evidence-reference', action='append', default=[])
    freeze.add_argument('--missing', action='append', default=[])
    launch = sub.add_parser('review-packet', help='Prepare reusable pending review inputs; never launch a reviewer')
    launch.add_argument('--task', required=True)
    launch.add_argument('--rule', action='append', default=[])
    launch.add_argument('--limitation', action='append', default=[])
    launch.add_argument('--implementation-context', default='unavailable')
    attempt = sub.add_parser('code-review', help='Record an actual canonical review report supplied as JSON on stdin')
    attempt.add_argument('--task', required=True)
    recovery = sub.add_parser('resume', help='Validate actual checkpoint inputs; never infer PASS from the index')
    recovery.add_argument('--task', required=True)
    recovery.add_argument('--update-state', action='store_true', help='Explicitly authorize only next-action/blocker updates after validation')
    repairs = sub.add_parser('repair', help='Validate a checkpoint before starting an ordinary consented repair')
    repairs.add_argument('--task', required=True)
    repairs.add_argument('--reason', required=True)
    finish = sub.add_parser('complete', help='Record local Completion after inspecting a candidate-bound coordinator assessment')
    finish.add_argument('--task', required=True)
    finish.add_argument('--assessment-reference', required=True)
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 11):
            raise ValueError('Python 3.11+ required; no installation or state write performed')
        if args.command == 'create':
            result = create(args.root.resolve(), args.task, sys.stdin.read())
        elif args.command == 'confirm':
            result = confirm(args.root.resolve(), args.task, args.spec_sha256, args.consent_reference)
        elif args.command == 'revise':
            result = revise(args.root.resolve(), args.task, args.previous_sha256, sys.stdin.read())
        elif args.command == 'begin':
            result = begin(args.root.resolve(), args.task)
        elif args.command == 'checkpoint':
            result = checkpoint(args.root.resolve(), args.task, args.owned, args.verification_status,
                                args.assessment_reference, args.evidence_reference, args.missing)
        elif args.command == 'review-packet':
            import review
            result = review.packet(sys.modules[__name__], args.root.resolve(), args.task, args.rule, args.limitation, args.implementation_context)
        elif args.command == 'code-review':
            import review
            result = review.record(sys.modules[__name__], args.root.resolve(), args.task, sys.stdin.read())
        elif args.command == 'complete':
            import completion
            result = completion.complete(sys.modules[__name__], args.root.resolve(), args.task, args.assessment_reference)
        elif args.command == 'repair':
            import completion
            result = completion.repair(sys.modules[__name__], args.root.resolve(), args.task, args.reason)
        elif args.command == 'resume':
            import resume
            result = resume.inspect(sys.modules[__name__], args.root.resolve(), args.task, args.update_state)
        else:
            result = spec_review(args.root.resolve(), args.task, args.spec_sha256, sys.stdin.read())
    except (OSError, ValueError) as error:
        print(json.dumps({'status': 'BLOCKED', 'reason': str(error)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
