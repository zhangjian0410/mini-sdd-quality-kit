"""Identify explicitly owned raw Git/worktree inputs; never execute repository code."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess


def capture(root: Path, base: str, owned: list[str]) -> dict:
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    env['GIT_OPTIONAL_LOCKS'] = '0'
    env['GIT_NO_LAZY_FETCH'] = '1'

    def git(*args):
        run = subprocess.run(['git', '--no-lazy-fetch', '--no-optional-locks', '-c', 'core.fsmonitor=false',
                              '-c', 'core.untrackedCache=false', '-C', str(root), *args],
                             env=env, capture_output=True)
        if run.returncode:
            raise ValueError('Candidate Git input unavailable: ' + run.stderr.decode(errors='replace').strip())
        return run.stdout

    head = git('rev-parse', '--verify', 'HEAD^{commit}').decode().strip()
    git('merge-base', '--is-ancestor', base, head)

    def blob(record):
        if not record:
            return None
        mode, kind, oid = record.split(b'\t', 1)[0].split()
        if kind != b'blob' or mode not in (b'100644', b'100755'):
            raise ValueError('Candidate requires regular files; symlink/submodule scope is unsupported')
        content = git('cat-file', 'blob', oid.decode())
        return {'mode': mode.decode(), 'sha256': hashlib.sha256(content).hexdigest()}

    files = []
    for name in sorted(set(owned)):
        relative = Path(name)
        if (not name or relative.is_absolute() or relative.as_posix() != name or
                any(part in ('.', '..') or part.casefold() in ('.git', '.specdd') for part in relative.parts)):
            raise ValueError('Owned candidate paths must be exact relative product paths, excluding task/Git metadata')
        path = root / relative
        if any(root.joinpath(*relative.parts[:i]).is_symlink() for i in range(1, len(relative.parts) + 1)):
            raise ValueError('Candidate paths cannot follow symlinks')
        worktree = None
        if path.exists():
            mode = path.stat().st_mode
            if not stat.S_ISREG(mode):
                raise ValueError('Candidate requires ordinary files')
            worktree = {'mode': '100755' if mode & stat.S_IXUSR else '100644',
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        index_rows = [row for row in git('ls-files', '--stage', '-z', '--', ':(literal)' + name).split(b'\0') if row]
        if len(index_rows) > 1:
            raise ValueError('Unmerged index input is not a fixed candidate')
        index = None
        if index_rows:
            mode, oid, stage = index_rows[0].split(b'\t', 1)[0].split()
            if stage != b'0':
                raise ValueError('Unmerged index input is not a fixed candidate')
            index = blob(mode + b' blob ' + oid + b'\t' + os.fsencode(name))
        before = blob(git('ls-tree', '-z', base, '--', ':(literal)' + name))
        committed = blob(git('ls-tree', '-z', head, '--', ':(literal)' + name))
        if before == committed == index == worktree:
            raise ValueError('Owned path has no candidate change: ' + name)
        files.append({'path': name, 'base': before, 'head': committed, 'index': index, 'worktree': worktree})
    if not files:
        raise ValueError('Identify at least one owned changed product path')
    inputs = {'base': base, 'head': head, 'files': files}
    identifier = hashlib.sha256(json.dumps(inputs, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'version': 1, 'id': identifier, **inputs}
