"""Fixed comparison public CLI, real disposable Git histories."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

import test_workspace_scope
from test_review_diff import snapshot

HELPER = Path(__file__).resolve().parents[1] / 'skills/review-diff/scripts/fixed_scope.py'


class FixedScopeTests(unittest.TestCase):
    setUp = test_workspace_scope.WorkspaceScopeTests.setUp
    git = test_workspace_scope.WorkspaceScopeTests.git
    def fixed(self, *args, success=True):
        before = snapshot(self.root)
        result = subprocess.run([sys.executable, '-B', str(HELPER), '--root', str(self.root), *args], capture_output=True, text=True)
        self.assertEqual(snapshot(self.root), before)
        self.assertEqual(result.returncode, 0 if success else 2, result.stderr)
        return json.loads(result.stdout)

    def test_committed_patch_excludes_dirty_and_attributes_workspace(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        (self.root / 'both.py').write_text('committed\n')
        self.git('add', 'both.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'change')
        (self.root / 'both.py').write_text('dirty\n')
        (self.root / 'new.py').write_text('new\n')
        report = self.fixed('--base', base, '--owned', 'both.py')
        self.assertEqual(report['comparison']['merge_base'], base)
        entry = report['comparison']['files'][0]
        self.assertEqual(entry['path'], 'both.py')
        self.assertIn('+committed', entry['diff'])
        self.assertNotIn('+dirty', entry['diff'])
        self.assertEqual(entry['tip_content'], 'committed\n')
        workspace = {e['path']: e for e in report['workspace']['files']}
        self.assertTrue(workspace['both.py']['selected'])
        self.assertFalse(workspace['new.py']['selected'])
        equivalent = self.fixed('--base', base[:12], '--owned', 'both.py')
        self.assertEqual(report['comparison'], equivalent['comparison'])

    def test_committed_metadata_case_aliases_expose_no_content_or_hashes(self):
        metadata = ['.SPECDD/task/state.json', 'nested/.SpEcDd/task/state.json', 'lower/.specdd/task/state.json']
        ordinary = ['owned.py', '.specdd-backup/notes.txt', 'nested/specdd/notes.txt', '.specdd.py']
        for name in metadata + ordinary:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('PRIVATE_METADATA_BEFORE' if name in metadata else 'ordinary before\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'comparison baseline')
        base = self.git('rev-parse', 'HEAD').decode().strip()
        for name in metadata + ordinary:
            (self.root / name).write_text('PRIVATE_METADATA_AFTER' if name in metadata else 'ordinary after\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'comparison change')
        report = self.fixed('--base', base)
        entries = {entry['path']: entry for entry in report['comparison']['files']}
        for name in metadata:
            with self.subTest(path=name):
                self.assertEqual(entries[name], dict(path=name, selected=False, reason='protected task metadata'))
        self.assertNotIn('PRIVATE_METADATA_', json.dumps(report))
        for name in ordinary:
            with self.subTest(path=name):
                self.assertTrue(entries[name]['selected'])
                self.assertEqual(entries[name]['base_content'], 'ordinary before\n')
                self.assertEqual(entries[name]['tip_content'], 'ordinary after\n')
                self.assertIn('+ordinary after', entries[name]['diff'])
                self.assertIn('diff_sha256', entries[name])

    def test_single_commit_matches_parent_base(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        (self.root / 'both.py').write_text('one commit\n')
        self.git('add', 'both.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'change')
        tip = self.git('rev-parse', 'HEAD').decode().strip()
        single = self.fixed('--commit', tip)
        pair = self.fixed('--base', base, '--tip', tip)
        self.assertEqual(single['comparison'], pair['comparison'])

    def test_invalid_base_and_unknown_pr_do_not_guess(self):
        for ref in ('missing-ref', 'https://example.invalid/pull/3', '--all', 'HEAD...main'):
            report = self.fixed('--base=' + ref, success=False)
            self.assertEqual(report['kind'], 'limited')
            self.assertTrue(report['limitations'])

    def test_deletions_symlinks_and_metadata_are_attributed(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        (self.root / 'both.py').unlink()
        (self.root / 'link').symlink_to('/etc/passwd')
        (self.root / '.specdd').mkdir()
        (self.root / '.specdd/task').write_text('private')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'change')
        entries = {e['path']: e for e in self.fixed('--base', base)['comparison']['files']}
        self.assertEqual(entries['both.py']['base_content'], 'original\n')
        self.assertIsNone(entries['both.py']['tip_content'])
        self.assertFalse(entries['link']['selected'])
        self.assertFalse(entries['.specdd/task']['selected'])

    def test_dirty_staged_untracked_and_configured_programs(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        (self.root / 'both.py').write_text('committed\n')
        self.git('add', 'both.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'change')
        (self.root / 'staged.py').write_text('staged\n')
        self.git('add', 'staged.py')
        (self.root / 'unstaged.py').write_text('dirty\n')
        (self.root / 'new.py').write_text('owned\n')
        script = self.root / 'trap.sh'
        script.write_text('#!/bin/sh\ntouch "' + str(self.root / 'MARKER') + '"\ncat\n')
        script.chmod(0o755)
        for key in ('core.fsmonitor', 'filter.fixture.clean', 'filter.fixture.process', 'diff.external', 'diff.fixture.textconv'):
            self.git('config', key, str(script))
        (self.root / '.gitattributes').write_text('*.py filter=fixture diff=fixture\n')
        report = self.fixed('--base', base, '--owned', 'staged.py', '--owned', 'unstaged.py', '--owned', 'new.py')
        self.assertFalse((self.root / 'MARKER').exists())
        self.assertEqual([e['path'] for e in report['comparison']['files']], ['both.py'])
        workspace = {e['path']: e for e in report['workspace']['files']}
        self.assertTrue(workspace['staged.py']['staged'])
        self.assertTrue(workspace['unstaged.py']['unstaged'])
        self.assertTrue(workspace['new.py']['untracked'])

    def test_ambiguous_branch_and_tag_is_limited_but_qualified_ref_works(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('tag', 'collision', base)
        (self.root / 'both.py').write_text('next\n')
        self.git('add', 'both.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'next')
        self.git('branch', 'collision', 'HEAD')
        self.git('config', 'core.warnAmbiguousRefs', 'false')
        report = self.fixed('--base', 'collision', success=False)
        self.assertEqual(report['kind'], 'limited')
        self.assertEqual(self.fixed('--base', 'refs/tags/collision')['comparison']['merge_base'], base)
        self.assertEqual(self.fixed('--base', 'refs/heads/collision')['comparison']['files'], [])

    def test_committed_gitlink_is_visible_as_excluded_without_traversal(self):
        base = self.git('rev-parse', 'HEAD').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '160000,' + base + ',module')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'gitlink')
        entries = {e['path']: e for e in self.fixed('--base', base)['comparison']['files']}
        self.assertIn('module', entries)
        self.assertFalse(entries['module']['selected'])
        self.assertIn('submodule', entries['module']['reason'])
