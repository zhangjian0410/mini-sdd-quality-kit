"""Public CLI behavior against disposable Git workspaces."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_diff import snapshot

HELPER = Path(__file__).resolve().parents[1] / 'skills/review-diff/scripts/workspace_scope.py'


class WorkspaceScopeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.git('init', '-q')
        for name in ('staged.py', 'unstaged.py', 'both.py', 'unrelated.py'):
            (self.root / name).write_text('original\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'baseline')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.root), *args], check=True, capture_output=True).stdout

    def scope(self, *args, success=True):
        before = snapshot(self.root)
        result = subprocess.run([sys.executable, '-B', str(HELPER), '--root', str(self.root), *args], capture_output=True, text=True, timeout=30)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return json.loads(result.stdout)

    def test_layers_owned_untracked_and_exclusions(self):
        for name in ('staged.py', 'both.py'):
            (self.root / name).write_text('staged\n')
        self.git('add', 'staged.py', 'both.py')
        for name in ('unstaged.py', 'both.py', 'unrelated.py', 'new file.py'):
            (self.root / name).write_text('working\n')
        (self.root / '.specdd').mkdir()
        (self.root / '.specdd/secret').write_text('task metadata')
        report = self.scope('--owned', 'staged.py', '--owned', 'unstaged.py', '--owned', 'both.py', '--owned', 'new file.py')
        files = {entry['path']: entry for entry in report['files']}
        self.assertEqual(set(files), {'staged.py', 'unstaged.py', 'both.py', 'new file.py', 'unrelated.py', '.specdd/secret'})
        self.assertTrue(files['staged.py']['staged'])
        self.assertTrue(files['unstaged.py']['unstaged'])
        self.assertTrue(files['both.py']['staged'] and files['both.py']['unstaged'])
        self.assertTrue(files['new file.py']['selected'] and files['new file.py']['untracked'])
        self.assertFalse(files['unrelated.py']['selected'])
        self.assertFalse(files['.specdd/secret']['selected'])
        self.assertEqual(len(report['head']), 40)

    def test_metadata_case_aliases_are_excluded_even_when_owned(self):
        metadata_dirs = ('.SPECDD/task', 'nested/.SpEcDd/task', 'lower/.specdd/task')
        staged = [directory + '/staged.json' for directory in metadata_dirs]
        untracked = [directory + '/untracked.json' for directory in metadata_dirs]
        ordinary = ['owned.py', '.specdd-backup/notes.txt', 'nested/specdd/notes.txt', '.specdd.py']
        for name in staged + untracked + ordinary:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('PRIVATE_METADATA_SENTINEL' if name in staged + untracked else 'ordinary change\n')
        self.git('add', '--', *staged)
        owned = [argument for name in staged + untracked + ordinary for argument in ('--owned', name)]
        report = self.scope(*owned)
        files = {entry['path']: entry for entry in report['files']}
        for name in staged + untracked:
            with self.subTest(path=name):
                self.assertEqual(files[name], dict(
                    path=name, staged=name in staged, unstaged=False,
                    untracked=name in untracked, selected=False, reason='protected task metadata'))
        self.assertNotIn('PRIVATE_METADATA_SENTINEL', json.dumps(report))
        for name in ordinary:
            with self.subTest(path=name):
                self.assertTrue(files[name]['selected'])
                self.assertIn('sha256', files[name])

    def test_clean_and_unknown_ownership_are_not_approval(self):
        self.assertEqual(self.scope()['files'], [])
        (self.root / 'unstaged.py').write_text('changed\n')
        result = self.scope()
        self.assertFalse(result['files'][0]['selected'])
        self.assertIn('ownership', result['files'][0]['reason'])

    def test_canceled_staged_change_remains_visible(self):
        (self.root / 'both.py').write_text('index-only\n')
        self.git('add', 'both.py')
        (self.root / 'both.py').write_text('original\n')
        entry = self.scope('--owned', 'both.py')['files'][0]
        self.assertTrue(entry['staged'] and entry['unstaged'])
        self.assertNotEqual(entry['staged_diff_sha256'], entry['unstaged_diff_sha256'])

    def test_deletion_rename_literal_names_and_symlinks(self):
        (self.root / 'staged.py').unlink()
        self.git('mv', 'both.py', 'renamed.py')
        (self.root / '[x].py').write_text('literal\n')
        (self.root / 'link.py').symlink_to('/etc/passwd')
        result = self.scope('--owned', 'staged.py', '--owned', 'both.py', '--owned', 'renamed.py', '--owned', '[x].py', '--owned', 'link.py')
        files = {e['path']: e for e in result['files']}
        self.assertIsNone(files['staged.py']['sha256'])
        self.assertIsNone(files['both.py']['sha256'])
        self.assertTrue(files['renamed.py']['selected'])
        self.assertTrue(files['[x].py']['selected'])
        self.assertFalse(files['link.py']['selected'])

    def test_unsupported_base_and_unborn_head_are_limitations(self):
        result = subprocess.run([sys.executable, '-B', str(HELPER), '--root', str(self.root), '--base', 'guess'], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b'unrecognized arguments', result.stderr)
        with tempfile.TemporaryDirectory() as temp:
            self.root = Path(temp).resolve()
            self.git('init', '-q')
            self.assertEqual(self.scope(success=False)['kind'], 'limited')

    def test_repository_configured_programs_are_never_executed(self):
        script = self.root / 'trap.sh'
        script.write_text('#!/bin/sh\nprintf invoked > "' + str(self.root / 'marker') + '"\ncat\n')
        script.chmod(0o755)
        self.git('config', 'core.fsmonitor', str(script))
        self.git('config', 'filter.fixture.clean', str(script))
        self.git('config', 'filter.fixture.process', str(script))
        self.git('config', 'filter.fixture.required', 'true')
        self.git('config', 'diff.external', str(script))
        self.git('config', 'diff.fixture.textconv', str(script))
        (self.root / '.gitattributes').write_text('*.py filter=fixture diff=fixture\n')
        (self.root / 'unstaged.py').write_text('changed\n')
        result = self.scope('--owned', 'unstaged.py')
        self.assertFalse((self.root / 'marker').exists())
        self.assertTrue(any(e['path'] == 'unstaged.py' and e['selected'] for e in result['files']))

    def test_submodule_internal_filters_are_not_executed(self):
        child = self.root / 'child'
        child.mkdir()
        def git(*args):
            return subprocess.run(['git', '-C', str(child), *args], check=True, capture_output=True)
        git('init', '-q')
        (child / 'a.txt').write_text('old\n')
        git('add', '.')
        git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'child')
        self.git('add', 'child')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'gitlink')
        script = child / 'trap.sh'
        script.write_text('#!/bin/sh\nprintf invoked > "' + str(self.root / 'marker') + '"\ncat\n')
        script.chmod(0o755)
        git('config', 'filter.child.clean', str(script))
        (child / '.gitattributes').write_text('*.txt filter=child\n')
        (child / 'a.txt').write_text('new\n')
        report = self.scope()
        self.assertFalse((self.root / 'marker').exists())
        self.assertIn('submodule', ' '.join(report['limitations']))
