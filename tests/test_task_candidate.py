"""Implementation checkpoints through the public task helper, in disposable Git repos."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_task_start import SPEC, HELPER


class TaskCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='task-candidate-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name).resolve()
        self.git('init', '-q')
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    return sum(prices) / len(prices) if prices else 0\n')
        self.git('add', '.')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'baseline')
        self.assertEqual(self.call('create', '--task', 'prices', content=SPEC).returncode, 0)

    def git(self, *args):
        return subprocess.run(['git', '-C', str(self.repo), *args], check=True, text=True, capture_output=True).stdout.strip()

    def call(self, *args, content=None):
        return subprocess.run([sys.executable, '-B', str(HELPER), '--root', str(self.repo), *args], input=content, text=True, capture_output=True)

    def approve(self):
        run = self.call('confirm', '--task', 'prices', '--spec-sha256', hashlib.sha256(SPEC.encode()).hexdigest(), '--consent-reference', 'fixture-user-approved')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_begin_requires_current_scope_consent(self):
        source = (self.repo / 'pricing.py').read_bytes()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 2)
        self.approve()
        run = self.call('begin', '--task', 'prices')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        state = json.loads(run.stdout)
        self.assertEqual(state['phase'], 'IMPLEMENTING')
        self.assertIsNone(state['candidate'])
        self.assertEqual((self.repo / 'pricing.py').read_bytes(), source)
        self.assertEqual(self.git('diff', '--name-only'), '')

    def test_checkpoint_identifies_dirty_and_untracked_owned_content(self):
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    if not prices: raise ValueError("empty")\n    return sum(prices) / len(prices)\n')
        (self.repo / 'new.py').write_text('VALUE = 7\n')
        (self.repo / 'unrelated.txt').write_text('Pre-existing unrelated draft\n')
        run = self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py', '--owned', 'new.py',
                        '--verification-status', 'SUFFICIENT', '--assessment-reference', 'fixture-assessment:AC1-tested',
                        '--evidence-reference', 'fixture-log:unittest-exit0')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        state = json.loads(run.stdout)
        self.assertEqual(state['phase'], 'REVIEW_READY')
        self.assertNotEqual(state['candidate']['id'], self.git('rev-parse', 'HEAD'))
        manifest = json.loads((self.repo / '.specdd/prices' / state['candidate']['manifest']).read_text())
        self.assertEqual({f['path'] for f in manifest['files']}, {'pricing.py', 'new.py'})
        new = next(f for f in manifest['files'] if f['path'] == 'new.py')
        self.assertEqual(new['worktree']['sha256'], hashlib.sha256(b'VALUE = 7\n').hexdigest())
        self.assertIsNone(new['index'])
        self.assertIsNone(new['head'])
        self.assertEqual(state['verification']['references'], ['fixture-log:unittest-exit0'])
        self.assertIsNone(state['latest_review'])
        self.assertEqual((self.repo / 'unrelated.txt').read_text(), 'Pre-existing unrelated draft\n')

    def test_unavailable_verification_retains_candidate_and_handoff(self):
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    if not prices: raise ValueError("empty")\n    return sum(prices) / len(prices)\n')
        run = self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
                        '--verification-status', 'INCOMPLETE', '--assessment-reference', 'fixture-assessment:missing-integration-service',
                        '--missing', 'Real integration service verification NOT_RUN')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        state = json.loads(run.stdout)
        self.assertEqual(state['phase'], 'BLOCKED_VERIFICATION')
        self.assertTrue(state['candidate']['id'])
        self.assertIn('NOT_RUN', state['unresolved_blocker'])
        self.assertTrue(state['next_action'])
        self.assertIsNone(state['latest_review'])
        blocked = self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
                            '--verification-status', 'SUFFICIENT', '--assessment-reference', 'unsupported-claim')
        self.assertEqual(blocked.returncode, 2)

    def freeze(self, *owned):
        paths = [arg for name in owned for arg in ('--owned', name)]
        return self.call('checkpoint', '--task', 'prices', *paths, '--verification-status', 'SUFFICIENT',
                         '--assessment-reference', 'fixture-static-assessment', '--evidence-reference', 'fixture-static-observation')

    def test_index_layer_and_unrelated_work_have_distinct_identity_effects(self):
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        original = (self.repo / 'pricing.py').read_bytes()
        (self.repo / 'pricing.py').write_text('staged accepted version\n')
        self.git('add', 'pricing.py')
        (self.repo / 'pricing.py').write_bytes(original)
        first = self.freeze('pricing.py')
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        old = json.loads(first.stdout)['candidate']
        manifest = json.loads((self.repo / '.specdd/prices' / old['manifest']).read_text())
        self.assertNotEqual(manifest['files'][0]['index'], manifest['files'][0]['worktree'])
        (self.repo / 'unrelated.txt').write_text('not owned\n')
        self.assertEqual(json.loads(self.freeze('pricing.py').stdout)['candidate']['id'], old['id'])
        (self.repo / 'pricing.py').write_text('new current accepted version\n')
        latest = json.loads(self.freeze('pricing.py').stdout)['candidate']
        self.assertNotEqual(latest['id'], old['id'])
        self.assertTrue((self.repo / '.specdd/prices' / old['manifest']).is_file())

    def test_clean_committed_candidate_needs_no_extra_manifest(self):
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        (self.repo / 'pricing.py').write_text('committed accepted version\n')
        self.git('add', 'pricing.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'accepted change')
        run = self.freeze('pricing.py')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        state = json.loads(run.stdout)
        self.assertNotIn('manifest', state['candidate'])
        self.assertEqual(state['candidate']['head'], self.git('rev-parse', 'HEAD'))
        self.assertEqual(sorted(p.name for p in (self.repo / '.specdd/prices').iterdir()), ['spec.md', 'state.json'])

    def test_protected_metadata_escape_symlink_and_unconfirmed_checkpoint_are_rejected(self):
        self.assertEqual(self.freeze('pricing.py').returncode, 2)
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        state_path = self.repo / '.specdd/prices/state.json'
        state_before = state_path.read_bytes()
        (self.repo / 'link.py').symlink_to(self.repo / 'pricing.py')
        for alias, content in (('.GIT/config', 'reserved Git alias'), ('.SPECDD/prices/spec.md', 'reserved task alias')):
            path = self.repo / alias
            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
        for name in ('.specdd/prices/spec.md', '../escape', '.git/config', 'link.py', '.GIT/config', '.SPECDD/prices/spec.md'):
            run = self.freeze(name)
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertEqual(state_path.read_bytes(), state_before)

    def test_material_revision_after_implementation_requires_new_consent(self):
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        (self.repo / 'pricing.py').write_text('accepted implementation version\n')
        checkpoint = self.freeze('pricing.py')
        self.assertEqual(checkpoint.returncode, 0, checkpoint.stdout + checkpoint.stderr)
        old_state = json.loads(checkpoint.stdout)
        old_manifest = self.repo / '.specdd/prices' / old_state['candidate']['manifest']
        old_manifest_bytes = old_manifest.read_bytes()
        # This explicit fixture commit is test setup, never product behavior.
        self.git('add', 'pricing.py')
        self.git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'accepted fixture implementation')
        revised = SPEC.replace('Revision: 1', 'Revision: 2').replace('Reject empty prices.', 'Reject empty prices and None.').replace('AC1: Empty prices raise ValueError;', 'AC1: Empty prices or None raise ValueError;')
        revision = self.call('revise', '--task', 'prices', '--previous-sha256', old_state['spec']['sha256'], content=revised)
        self.assertEqual(revision.returncode, 0, revision.stdout + revision.stderr)
        pending = json.loads(revision.stdout)
        self.assertEqual(pending['phase'], 'AWAITING_CONSENT')
        self.assertIsNone(pending['candidate'])
        self.assertNotIn('verification', pending)
        self.assertNotIn('consent_reference', pending)
        self.assertEqual(old_manifest.read_bytes(), old_manifest_bytes)
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 2)
        confirmation = self.call('confirm', '--task', 'prices', '--spec-sha256', hashlib.sha256(revised.encode()).hexdigest(), '--consent-reference', 'fixture-user-approved-revision-2')
        self.assertEqual(confirmation.returncode, 0, confirmation.stdout + confirmation.stderr)
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)


if __name__ == '__main__':
    unittest.main()
