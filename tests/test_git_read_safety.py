"""Public CLIs never fetch missing promisor objects or execute a remote helper."""
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tempfile
import unittest

from test_task_start import SPEC

ROOT = Path(__file__).resolve().parents[1]
TASK = ROOT / 'skills/mini-sdd/scripts/task.py'


class GitReadSafetyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='git-no-lazy-fetch-')
        self.addCleanup(temporary.cleanup)
        self.area = Path(temporary.name).resolve()
        self.bin = self.area / 'bin'
        self.bin.mkdir()
        self.env = dict(os.environ, PATH=str(self.bin) + os.pathsep + os.environ['PATH'],
                        GIT_NO_LAZY_FETCH='1')
        self.observations = []

    def command(self, *args, content=None):
        return subprocess.run(args, env=self.env, input=content, text=True, capture_output=True, timeout=15)

    def git(self, root, *args):
        run = self.command('git', '-C', str(root), *args)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        return run.stdout.strip()

    def task(self, root, *args, content=None):
        return self.command(sys.executable, '-B', str(TASK), '--root', str(root), *args, content=content)

    def snapshot(self, root):
        return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in root.rglob('*') if p.is_file()}

    def test_missing_local_objects_stay_unresolved_without_any_remote_helper_execution(self):
        for entry in ('workspace', 'fixed', 'task', 'candidate', 'resume'):
            with self.subTest(entry=entry):
                root = self.area / entry
                root.mkdir()
                self.git(root, 'init', '-q', '--template=')
                self.git(root, 'config', 'user.name', 'Fixture')
                self.git(root, 'config', 'user.email', 'fixture@example.invalid')
                self.git(root, 'config', 'commit.gpgsign', 'false')
                self.git(root, 'config', 'core.hooksPath', str(self.area / 'no-hooks'))
                source = root / 'pricing.py'
                source.write_text('old fixture bytes\n')
                self.git(root, 'add', 'pricing.py')
                self.git(root, 'commit', '-qm', 'fixture baseline')
                base = self.git(root, 'rev-parse', 'HEAD')
                old_blob = self.git(root, 'rev-parse', 'HEAD:pricing.py')
                source.write_text('new fixture bytes\n')
                self.git(root, 'add', 'pricing.py')
                self.git(root, 'commit', '-qm', 'fixture tip')
                tip = self.git(root, 'rev-parse', 'HEAD')
                head_blob = self.git(root, 'rev-parse', 'HEAD:pricing.py')
                protocol = 'sddlazysafety' + entry
                marker = self.area / (entry + '-remote-executed')
                helper = self.bin / ('git-remote-' + protocol)
                helper.write_text('#!/bin/sh\nprintf invoked >> ' + shlex.quote(str(marker)) + '\nexit 1\n')
                helper.chmod(0o700)
                for name, value in (('remote.origin.url', protocol + '::local-fixture-only'),
                                    ('remote.origin.promisor', 'true'), ('remote.origin.partialclonefilter', 'blob:none'),
                                    ('extensions.partialClone', 'origin'), ('protocol.' + protocol + '.allow', 'always')):
                    self.git(root, 'config', name, value)
                if entry in ('candidate', 'resume'):
                    created = self.task(root, 'create', '--task', 'prices', content=SPEC)
                    self.assertEqual(created.returncode, 0, created.stdout + created.stderr)
                    state = json.loads(created.stdout)
                    self.assertEqual(self.task(root, 'confirm', '--task', 'prices', '--spec-sha256', state['spec']['sha256'],
                        '--consent-reference', 'controlled fixture scope authorization').returncode, 0)
                    self.assertEqual(self.task(root, 'begin', '--task', 'prices').returncode, 0)
                    source.write_text('dirty owned fixture bytes\n')
                    checkpoint = ('checkpoint', '--task', 'prices', '--owned', 'pricing.py', '--verification-status',
                                  'INCOMPLETE', '--assessment-reference', 'fixture missing checks', '--missing', 'runtime check NOT_RUN')
                    if entry == 'resume':
                        frozen = self.task(root, *checkpoint)
                        self.assertEqual(frozen.returncode, 0, frozen.stdout + frozen.stderr)
                if entry == 'workspace':
                    source.write_text('dirty owned fixture bytes\n')
                missing = tip if entry == 'task' else old_blob if entry == 'fixed' else head_blob
                object_file = root / '.git/objects' / missing[:2] / missing[2:]
                self.assertTrue(object_file.is_file())
                object_file.unlink()  # Only a toy object created above, never existing work.
                before = self.snapshot(root)
                marker_before = marker.exists()
                if entry in ('workspace', 'fixed'):
                    script = ROOT / ('skills/review-diff/scripts/' + ('workspace_scope.py' if entry == 'workspace' else 'fixed_scope.py'))
                    args = ('--owned', 'pricing.py') if entry == 'workspace' else ('--base', base)
                    run = self.command(sys.executable, '-B', str(script), '--root', str(root), *args)
                elif entry == 'task':
                    run = self.task(root, 'create', '--task', 'prices', content=SPEC)
                elif entry == 'candidate':
                    run = self.task(root, *checkpoint)
                else:
                    run = self.task(root, 'resume', '--task', 'prices', '--update-state')
                observation = {'entry': entry, 'marker_before': marker_before, 'marker_after': marker.exists(),
                    'returncode': run.returncode, 'records_unchanged': self.snapshot(root) == before,
                    'object_restored': object_file.exists()}
                self.observations.append(observation)
                self.assertFalse(marker.exists(), json.dumps(observation))
                self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                self.assertEqual(self.snapshot(root), before)
                self.assertFalse(object_file.exists())
                report = json.loads(run.stdout)
                self.assertIn(report.get('status', report.get('kind')), ('BLOCKED', 'limited'))


if __name__ == '__main__':
    unittest.main()
