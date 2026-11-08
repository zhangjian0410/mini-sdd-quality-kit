"""Full Task creation and consent through the public helper CLI."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / 'skills/mini-sdd/scripts/task.py'
SPEC = '''# Mean price
Revision: 1

## Goal
Reject empty prices.
## Current Behavior
mean_price([]) returns zero.
## Change / Scope
Change only pricing.py empty-list behavior.
## Acceptance Criteria
AC1: Empty prices raise ValueError; nonempty arithmetic is unchanged.
## Constraints / Non-goals
No API redesign or Git publishing.
## Verification
Run existing public mean_price tests including empty-list regression.
'''


class TaskStartTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='task-start-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.git('init', '-q')
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    return sum(prices) / len(prices) if prices else 0\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'baseline')

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], capture_output=True, text=True, check=True).stdout.strip()

    def call(self, *args, content=None):
        return subprocess.run([sys.executable, '-B', str(HELPER), '--root', str(self.repo), *args], input=content, text=True, capture_output=True)

    def test_create_keeps_product_untouched_and_waits_for_consent(self):
        head = self.git('rev-parse', 'HEAD')
        source = (self.repo / 'pricing.py').read_bytes()
        run = self.call('create', '--task', 'empty-prices', content=SPEC)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        state = json.loads((self.repo / '.specdd/empty-prices/state.json').read_text())
        self.assertEqual(state['phase'], 'AWAITING_CONSENT')
        self.assertEqual(state['base'], head)
        self.assertEqual(state['spec']['sha256'], hashlib.sha256(SPEC.encode()).hexdigest())
        self.assertEqual(state['spec']['revision'], '1')
        self.assertIsNone(state['candidate'])
        self.assertIsNone(state['latest_review'])
        self.assertEqual(sorted(p.name for p in (self.repo / '.specdd/empty-prices').iterdir()), ['spec.md', 'state.json'])
        self.assertEqual((self.repo / 'pricing.py').read_bytes(), source)
        self.assertEqual(self.git('rev-parse', 'HEAD'), head)
        self.assertEqual(self.git('diff', '--name-only'), '')
        self.assertEqual(self.git('ls-files', '.specdd'), '')

    def test_consent_binds_exact_spec_and_preserves_the_spec(self):
        self.assertEqual(self.call('create', '--task', 'empty-prices', content=SPEC).returncode, 0)
        digest = hashlib.sha256(SPEC.encode()).hexdigest()
        run = self.call('confirm', '--task', 'empty-prices', '--spec-sha256', digest,
                        '--consent-reference', 'user-message:fixture-approved-revision-1')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        state = json.loads(run.stdout)
        self.assertEqual(state['phase'], 'READY_TO_IMPLEMENT')
        self.assertEqual(state['consent_reference'], 'user-message:fixture-approved-revision-1')
        self.assertEqual((self.repo / '.specdd/empty-prices/spec.md').read_text(), SPEC)
        self.assertIsNone(state['candidate'])
        self.assertIsNone(state['latest_review'])
        self.assertEqual(self.git('diff', '--name-only'), '')

    def test_colliding_and_active_tasks_are_preserved(self):
        self.assertEqual(self.call('create', '--task', 'empty-prices', content=SPEC).returncode, 0)
        folder = self.repo / '.specdd/empty-prices'
        before = {p.name: p.read_bytes() for p in folder.iterdir()}
        for task in ('empty-prices', 'second-task', '../escape'):
            run = self.call('create', '--task', task, content=SPEC)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in folder.iterdir()}, before)
        self.assertFalse((self.repo / '.specdd/second-task').exists())
        self.assertFalse((self.repo / 'escape').exists())

    def test_tracked_and_symlink_storage_is_protected(self):
        storage = self.repo / '.specdd'
        storage.mkdir()
        (storage / 'old.txt').write_text('retain\n')
        self.git('add', '.specdd/old.txt')
        self.assertEqual(self.call('create', '--task', 'new', content=SPEC).returncode, 2)
        self.assertEqual((storage / 'old.txt').read_text(), 'retain\n')
        self.assertFalse((storage / 'new').exists())
        with tempfile.TemporaryDirectory(prefix='task-symlink-') as temporary:
            other = Path(temporary)
            self.repo = other / 'repo'
            self.repo.mkdir()
            self.git('init', '-q')
            (self.repo / '.specdd').symlink_to(storage, target_is_directory=True)
            self.assertEqual(self.call('create', '--task', 'new', content=SPEC).returncode, 2)
            self.assertFalse((storage / 'new').exists())

    def test_invalid_spec_or_stale_consent_writes_nothing(self):
        self.assertEqual(self.call('create', '--task', 'broken', content='no Mini Spec').returncode, 2)
        self.assertFalse((self.repo / '.specdd').exists())
        self.assertEqual(self.call('create', '--task', 'empty-prices', content=SPEC).returncode, 0)
        index = self.repo / '.specdd/empty-prices/state.json'
        before = index.read_bytes()
        run = self.call('confirm', '--task', 'empty-prices', '--spec-sha256', '0' * 64,
                        '--consent-reference', 'user-message:stale')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(index.read_bytes(), before)
        (index.parent / 'spec.md').write_text(SPEC.replace('Revision: 1', 'Revision: 2'))
        run = self.call('confirm', '--task', 'empty-prices', '--spec-sha256', hashlib.sha256(SPEC.encode()).hexdigest(),
                        '--consent-reference', 'user-message:stale')
        self.assertEqual(run.returncode, 2)
        self.assertEqual(index.read_bytes(), before)

    def test_revise_requires_new_consent_and_keeps_optional_review(self):
        self.assertEqual(self.call('create', '--task', 'empty-prices', content=SPEC).returncode, 0)
        folder = self.repo / '.specdd/empty-prices'
        (folder / 'reviews').mkdir()
        (folder / 'reviews/spec-01.md').write_text('Actual supplied review of revision 1; fixture data.\n')
        revised = SPEC.replace('Revision: 1', 'Revision: 2').replace('Reject empty prices.', 'Reject empty price collections.')
        run = self.call('revise', '--task', 'empty-prices', '--previous-sha256', hashlib.sha256(SPEC.encode()).hexdigest(), content=revised)
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)
        state = json.loads(run.stdout)
        self.assertEqual(state['phase'], 'AWAITING_CONSENT')
        self.assertEqual(state['spec']['revision'], '2')
        self.assertEqual((folder / 'spec.md').read_text(), revised)
        self.assertEqual((folder / 'reviews/spec-01.md').read_text(), 'Actual supplied review of revision 1; fixture data.\n')

    def test_consent_digest_is_exact_file_bytes(self):
        content = SPEC.replace('\n', '\r\n')
        self.assertEqual(self.call('create', '--task', 'crlf', content=content).returncode, 0)
        folder = self.repo / '.specdd/crlf'
        digest = hashlib.sha256((folder / 'spec.md').read_bytes()).hexdigest()
        run = self.call('confirm', '--task', 'crlf', '--spec-sha256', digest,
                        '--consent-reference', 'user-message:approve-exact-bytes')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_optional_review_is_numbered_and_referenced_only_when_recorded(self):
        self.assertEqual(self.call('create', '--task', 'empty-prices', content=SPEC).returncode, 0)
        folder = self.repo / '.specdd/empty-prices'
        digest = hashlib.sha256(SPEC.encode()).hexdigest()
        self.assertFalse((folder / 'reviews').exists())
        body = 'SELF_CHECK: supplied synthetic fixture report of revision 1; no independent approval.\n'
        first = self.call('spec-review', '--task', 'empty-prices', '--spec-sha256', digest, content=body)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(json.loads(first.stdout)['latest_review'], 'reviews/spec-01.md')
        saved = (folder / 'reviews/spec-01.md').read_bytes()
        second = self.call('spec-review', '--task', 'empty-prices', '--spec-sha256', digest, content=body)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(json.loads(second.stdout)['latest_review'], 'reviews/spec-02.md')
        self.assertEqual((folder / 'reviews/spec-01.md').read_bytes(), saved)
        self.assertEqual(json.loads(second.stdout)['phase'], 'AWAITING_CONSENT')

    def test_unrecognized_complete_record_cannot_bypass_one_writer_guard(self):
        folder = self.repo / '.specdd/foreign'
        folder.mkdir(parents=True)
        index = folder / 'state.json'
        index.write_text('{"phase":"COMPLETE"}')
        original = index.read_bytes()
        run = self.call('create', '--task', 'new', content=SPEC)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual(index.read_bytes(), original)
        self.assertFalse((self.repo / '.specdd/new').exists())

    def test_only_locally_bound_historical_record_is_exempt_from_active_writer_guard(self):
        self.assertEqual(self.call('create', '--task', 'old', content=SPEC).returncode, 0)
        index = self.repo / '.specdd/old/state.json'
        state = json.loads(index.read_text())
        # Synthetic historical input tests record recognition, not Completion.
        state.update(phase='COMPLETE', next_action='Historical fixture', unresolved_blocker=None)
        bad = dict(state, worktree={'root': '/foreign/worktree', 'git_dir': '/foreign/.git'})
        index.write_text(json.dumps(bad))
        self.assertEqual(self.call('create', '--task', 'new', content=SPEC).returncode, 2)
        index.write_text(json.dumps(state))
        spec_file = index.parent / 'spec.md'
        spec_file.write_text(SPEC + 'drift\n')
        self.assertEqual(self.call('create', '--task', 'new', content=SPEC).returncode, 2)
        spec_file.write_text(SPEC)
        self.assertEqual(self.call('create', '--task', 'new', content=SPEC).returncode, 0)


if __name__ == '__main__':
    unittest.main()
