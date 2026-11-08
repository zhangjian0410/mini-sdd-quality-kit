"""Read-only default workspace enumeration; Python 3.11+, standard library only."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
from pathlib import Path
import subprocess
import sys


def inspect(root: Path, owned: list[str]) -> dict:
    env = os.environ.copy()
    # Caller Git overrides must not redirect inspection to a different repository.
    for key in list(env):
        if key.startswith('GIT_'):
            del env[key]
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_NO_LAZY_FETCH'] = '1'

    config = ['-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false']

    def git(*args: str) -> bytes:
        result = subprocess.run(
            ['git', '--no-lazy-fetch', '--no-optional-locks', *config, '-C', str(root), *args],
            env=env, capture_output=True,
        )
        if result.returncode:
            raise ValueError('Git inspection unavailable: ' + result.stderr.decode(errors='replace').strip())
        return result.stdout

    # Git worktree comparisons normally run configured clean/process filters.
    # Query names without reading the index, then neutralize every configured
    # driver before any enumeration or patch read. No repository code is run.
    names = subprocess.run(
        ['git', '--no-lazy-fetch', *config, '-C', str(root), 'config', '--name-only', '--get-regexp',
         r'^filter\..*\.(clean|process|required)$'], env=env, capture_output=True,
    )
    if names.returncode not in (0, 1):
        raise ValueError('Cannot establish safe Git filter configuration')
    drivers = {os.fsdecode(name).rsplit('.', 1)[0] for name in names.stdout.splitlines()}
    # Unlike -c key=value, --config-env preserves '=' inside a driver name.
    env['REVIEW_DIFF_FILTER_DISABLED'] = ''
    env['REVIEW_DIFF_FILTER_REQUIRED'] = 'false'
    for driver in sorted(drivers):
        config.extend([f'--config-env={driver}.clean=REVIEW_DIFF_FILTER_DISABLED',
                       f'--config-env={driver}.process=REVIEW_DIFF_FILTER_DISABLED',
                       f'--config-env={driver}.required=REVIEW_DIFF_FILTER_REQUIRED'])

    actual = Path(os.fsdecode(git('rev-parse', '--show-toplevel')).rstrip('\n')).resolve()
    if root != actual:
        raise ValueError('--root must identify the Git worktree root')
    head = git('rev-parse', '--verify', 'HEAD^{commit}').decode().strip()

    def paths(*args: str) -> set[str]:
        return {os.fsdecode(p) for p in git(*args).split(b'\0') if p}

    diff_args = ('--no-ext-diff', '--no-textconv', '--no-renames', '--ignore-submodules=dirty')
    staged = paths('diff', *diff_args, '--cached', '--name-only', '-z', head, '--')
    unstaged = paths('diff', *diff_args, '--name-only', '-z', '--')
    untracked = paths('ls-files', '--others', '--exclude-standard', '-z')
    files = []
    for name in sorted(staged | unstaged | untracked):
        path = root / name
        protected = any(part.casefold() == '.specdd' for part in Path(name).parts)
        selected = name in owned and not protected
        reason = 'explicit ownership supplied' if selected else 'ownership/relevance unestablished or unrelated'
        if protected:
            reason = 'protected task metadata'
        entry = dict(path=name, staged=name in staged, unstaged=name in unstaged,
                     untracked=name in untracked, selected=selected, reason=reason)
        if selected:
            # Never follow symlinks, including a replaced parent directory.
            parents = [root.joinpath(*Path(name).parts[:i]) for i in range(1, len(Path(name).parts) + 1)]
            mode = git('ls-files', '--stage', '-z', '--', ':(literal)' + name)
            if any(p.is_symlink() for p in parents) or mode.startswith(b'160000 ') or (path.exists() and not stat.S_ISREG(path.stat().st_mode)):
                entry.update(selected=False, reason='symlink/submodule/non-regular file requires separate explicit scope')
            else:
                try:
                    entry['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None
                    # Preserve index-only changes even if the worktree cancels them.
                    for layer, args in (('staged', ('--cached', head)), ('unstaged', ())):
                        patch = git('diff', *diff_args, '--binary', *args, '--', ':(literal)' + name)
                        entry[layer + '_diff_sha256'] = hashlib.sha256(patch).hexdigest()
                        entry[layer + '_diff'] = patch.decode('utf-8', errors='replace')
                except OSError as error:
                    entry.update(selected=False, reason=f'unreadable input: {error}')
        files.append(entry)
    unknown = sorted(set(owned) - {entry['path'] for entry in files})
    return dict(kind='default-workspace', root=str(root), head=head, files=files,
                limitations=['Committed history, ignored files and submodule internal dirtiness are not reviewed.',
                             'Enumeration is not an atomic snapshot; recheck identity after reading.',
                             'Git clean/process filters are disabled; raw worktree bytes are inspected.'] +
                [f'Owned path is not an enumerated change: {name}' for name in unknown])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--owned', action='append', default=[], help='exact root-relative path whose relevance/ownership the caller established; repeatable')
    args = parser.parse_args()
    try:
        if sys.version_info < (3, 11):
            raise ValueError('Python 3.11+ is required; supply an interpreter, no installation is performed')
        report = inspect(args.root.resolve(), args.owned)
    except (OSError, ValueError) as error:
        print(json.dumps(dict(kind='limited', limitations=[str(error)])))
        return 2
    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0


if __name__ == '__main__':
    sys.exit(main())
