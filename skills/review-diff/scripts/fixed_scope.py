"""Read-only local fixed Git comparison, separately attributed workspace additions."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

from workspace_scope import inspect


def compare(root: Path, base: str, tip: str, owned: list[str]) -> dict:
    # The existing protected enumerator identifies workspace layers independently.
    workspace = inspect(root, owned)
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_NO_LAZY_FETCH'] = '1'

    def git(*args: str) -> bytes:
        run = subprocess.run(['git', '--no-lazy-fetch', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                              '-c', 'core.untrackedCache=false', '-c', 'core.warnAmbiguousRefs=true', '-C', str(root), *args],
                             env=env, capture_output=True)
        if run.returncode or (args[0] == 'rev-parse' and run.stderr):
            raise ValueError('Comparison unavailable: ' + run.stderr.decode(errors='replace').strip())
        return run.stdout

    def commit(ref: str) -> str:
        if not ref or ref.startswith('-') or any(c in ref for c in ('\0', '\n', '\r')):
            raise ValueError('Supply one unambiguous local commit reference')
        return git('rev-parse', '--verify', '--end-of-options', ref + '^{commit}').decode().strip()

    base_id, tip_id = commit(base), commit(tip)
    ancestors = git('merge-base', '--all', base_id, tip_id).decode().splitlines()
    if len(ancestors) != 1:
        raise ValueError('Comparison requires one unambiguous merge base')
    ancestor = ancestors[0]
    diff_flags = ('--no-ext-diff', '--no-textconv', '--no-renames', '--ignore-submodules=dirty')
    names = git('diff', *diff_flags, '--name-only', '-z', ancestor, tip_id, '--').split(b'\0')
    files = []
    for raw_name in names:
        if not raw_name:
            continue
        name = os.fsdecode(raw_name)
        entry = dict(path=name, selected=not any(part.casefold() == '.specdd' for part in Path(name).parts))
        if not entry['selected']:
            entry['reason'] = 'protected task metadata'
            files.append(entry)
            continue
        patch = git('diff', *diff_flags, '--binary', ancestor, tip_id, '--', ':(literal)' + name)
        entry.update(diff=patch.decode('utf-8', errors='replace'), diff_sha256=hashlib.sha256(patch).hexdigest())
        for label, revision in (('base', ancestor), ('tip', tip_id)):
            tree = git('ls-tree', '-z', revision, '--', ':(literal)' + name)
            if not tree:
                entry[label + '_sha256'] = None
                entry[label + '_content'] = None
                continue
            mode, kind, oid = tree.split(b'\t', 1)[0].split()
            if kind != b'blob' or mode not in (b'100644', b'100755'):
                entry.update(selected=False, reason='symlink/submodule/non-regular committed input requires separate explicit scope')
                continue
            content = git('cat-file', 'blob', oid.decode())
            entry[label + '_sha256'] = hashlib.sha256(content).hexdigest()
            entry[label + '_content'] = content.decode('utf-8', errors='replace')
        files.append(entry)
    return dict(kind='fixed-comparison', root=str(root),
                comparison=dict(base=base_id, tip=tip_id, merge_base=ancestor, semantics='merge-base...tip committed objects only', files=files),
                workspace=workspace,
                limitations=['No remote lookup or PR resolution; supply verified local base and tip references.',
                             'Workspace additions are separate from the committed comparison, even on the same path.',
                             'Submodule internal contents are not reviewed; recheck identities after inspection.'])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument('--base')
    selection.add_argument('--commit', help='single non-root commit; compare its first parent to it')
    parser.add_argument('--tip', default='HEAD')
    parser.add_argument('--owned', action='append', default=[])
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 11):
            raise ValueError('Python 3.11+ required; no installation performed')
        if args.commit and args.tip != 'HEAD':
            raise ValueError('--commit cannot be combined with --tip')
        # Root commits have no parent and remain an explicit limitation.
        base = args.commit + '^' if args.commit else args.base
        report = compare(args.root.resolve(), base, args.commit or args.tip, args.owned)
    except (OSError, ValueError) as error:
        print(json.dumps(dict(kind='limited', limitations=[str(error)])))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
