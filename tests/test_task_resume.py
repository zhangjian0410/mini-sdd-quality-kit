"""Resume validation through public CLI; synthetic reports are not native reviews."""
import json
import unittest
import test_task_review as review_tests
import test_task_start as start_tests


class TaskResumeTests(unittest.TestCase):
    setUp = review_tests.TaskReviewTests.setUp
    git = review_tests.TaskReviewTests.git
    call = review_tests.TaskReviewTests.call
    approve = review_tests.TaskReviewTests.approve
    freeze = review_tests.TaskReviewTests.freeze
    report = review_tests.TaskReviewTests.report
    submit = review_tests.TaskReviewTests.submit
    proof = review_tests.TaskReviewTests.proof
    def test_resume_continues_real_consent_and_implementation_checkpoints(self):
        # setUp supplies an implemented/verified fixture from the earlier CLI slices.
        before = self.snapshot()
        run = self.call('resume', '--task', 'prices')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        self.assertEqual(result['status'], 'READY')
        self.assertEqual(result['phase'], 'REVIEW_READY')
        self.assertEqual(result['candidate']['scope'], ['pricing.py'])
        self.assertEqual(self.snapshot(), before)
        # A second, separate Git fixture holds the agreed-Spec checkpoint.
        original = self.repo
        start_tests.TaskStartTests.setUp(self)
        self.assertEqual(self.call('create', '--task', 'agreed', content=start_tests.SPEC).returncode, 0)
        state = json.loads((self.repo / '.specdd/agreed/state.json').read_text())
        self.assertEqual(self.call('confirm', '--task', 'agreed', '--spec-sha256', state['spec']['sha256'],
                                   '--consent-reference', 'fixture actual consent').returncode, 0)
        resumed = self.call('resume', '--task', 'agreed')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)['phase'], 'READY_TO_IMPLEMENT')
        self.repo = original

    def snapshot(self):
        return {p.relative_to(self.repo).as_posix(): p.read_bytes()
                for p in self.repo.rglob('*') if p.is_file() and '.git' not in p.relative_to(self.repo).parts}

    def test_drift_and_malformed_indices_are_blocked_without_overwriting_records(self):
        folder = self.repo / '.specdd/prices'
        index = folder / 'state.json'
        original = index.read_bytes()
        state = json.loads(original)
        mutations = [dict(state, version=True), dict(state, candidate={}),
                     dict(state, verification=[]), dict(state, next_action=None),
                     dict(state, worktree={'root': '/foreign', 'git_dir': '/foreign/.git'}),
                     dict(state, base='0' * 40), dict(state, latest_review='../outside.md'),
                     dict(state, phase='COMPLETE', candidate=None)]
        for changed in mutations:
            with self.subTest(index=changed):
                index.write_text(json.dumps(changed))
                before = self.snapshot()
                run = self.call('resume', '--task', 'prices', '--update-state')
                self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                self.assertEqual(json.loads(run.stdout)['status'], 'BLOCKED')
                self.assertEqual(self.snapshot(), before)
        index.write_bytes(original)
        spec = folder / 'spec.md'
        spec.write_bytes(spec.read_bytes().replace(b'Revision: 1', b'Revision: 2'))
        before = self.snapshot()
        self.assertEqual(self.call('resume', '--task', 'prices', '--update-state').returncode, 2)
        self.assertEqual(self.snapshot(), before)

    def test_dirty_untracked_staged_and_manifest_drift_never_reuses_approval(self):
        (self.repo / 'new.py').write_text('owned untracked input\n')
        self.assertEqual(self.freeze('pricing.py', 'new.py').returncode, 0)
        folder = self.repo / '.specdd/prices'
        state = json.loads((folder / 'state.json').read_text())
        manifest = folder / state['candidate']['manifest']
        saved = manifest.read_bytes()
        manifest.write_text('{}')
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 2)
        manifest.write_bytes(saved)
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 0)
        for name in ('pricing.py', 'new.py'):
            path = self.repo / name
            original = path.read_bytes()
            path.write_text('drift\n')
            before = self.snapshot()
            self.assertEqual(self.call('resume', '--task', 'prices', '--update-state').returncode, 2)
            self.assertEqual(self.snapshot(), before)
            path.write_bytes(original)
        self.git('add', 'pricing.py')
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 2)

    def test_pending_packet_and_self_check_remain_pending_without_history_changes(self):
        report = self.report()
        folder = self.repo / '.specdd/prices'
        before = self.snapshot()
        pending = self.call('resume', '--task', 'prices', '--update-state')
        self.assertEqual(pending.returncode, 0, pending.stdout + pending.stderr)
        result = json.loads(pending.stdout)
        self.assertEqual(result['status'], 'PENDING')
        self.assertTrue((folder / result['review']['packet']).is_file())
        self.assertIsNone(result['latest_review'])
        self.assertEqual({k: v for k, v in self.snapshot().items() if not k.endswith('state.json')},
                         {k: v for k, v in before.items() if not k.endswith('state.json')})
        report['review_context'] = 'implementation-session'
        self.assertEqual(self.submit(report).returncode, 0)
        old_report = (folder / 'reviews/code-01.md').read_bytes()
        resumed = json.loads(self.call('resume', '--task', 'prices').stdout)
        self.assertEqual(resumed['status'], 'PENDING')
        self.assertEqual(resumed['review']['independence'], 'SELF_CHECK')
        self.assertEqual((folder / 'reviews/code-01.md').read_bytes(), old_report)

    def test_stale_report_packet_evidence_and_provenance_cannot_survive_resume(self):
        evidence = self.repo / 'verification.log'
        evidence.write_text('Actual fixture test output: empty ValueError; mean([2,4]) == 3\n')
        self.assertEqual(self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
            '--verification-status', 'SUFFICIENT', '--assessment-reference', str(evidence),
            '--evidence-reference', str(evidence)).returncode, 0)
        report = self.report()
        receipt, _ = self.proof(report)
        self.assertEqual(self.submit(report).returncode, 0)
        folder = self.repo / '.specdd/prices'
        state = json.loads((folder / 'state.json').read_text())
        # Synthetic provenance relationships can be validated, but this is no real Independent Review.
        good = self.call('resume', '--task', 'prices')
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertEqual(json.loads(good.stdout)['status'], 'UNKNOWN')
        for path in (folder / state['latest_review'], folder / state['review']['packet'], evidence):
            original = path.read_bytes()
            path.write_bytes(original + b'drift\n')
            before = self.snapshot()
            blocked = self.call('resume', '--task', 'prices', '--update-state')
            self.assertEqual(blocked.returncode, 2, blocked.stdout + blocked.stderr)
            self.assertEqual(self.snapshot(), before)
            path.write_bytes(original)
        receipt.write_text('replaced observer evidence\n')
        unverified = self.call('resume', '--task', 'prices', '--update-state')
        self.assertEqual(unverified.returncode, 0, unverified.stdout + unverified.stderr)
        result = json.loads(unverified.stdout)
        self.assertEqual(result['status'], 'PENDING')
        self.assertEqual(result['review']['independence'], 'UNVERIFIED')
        self.assertEqual(json.loads((folder / 'state.json').read_text())['review']['status'], 'REVIEWED')
        self.assertIn('review', result['next_action'].lower())

    def test_malformed_packet_review_binding_and_protected_records_are_not_rewritten(self):
        import hashlib
        report = self.report()
        self.assertEqual(self.submit(report).returncode, 0)
        folder = self.repo / '.specdd/prices'
        index = folder / 'state.json'
        original = index.read_bytes()
        state = json.loads(original)
        packet_path = folder / state['review']['packet']
        original_packet = packet_path.read_bytes()
        for review_change in ({'candidate_id': '0' * 64}, {'spec_sha256': '0' * 64}, {'report_sha256': None}):
            changed = json.loads(original)
            changed['review'].update(review_change)
            index.write_text(json.dumps(changed))
            before = self.snapshot()
            result = self.call('resume', '--task', 'prices', '--update-state')
            self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
            self.assertEqual(self.snapshot(), before)
        index.write_bytes(original)
        packet_path.write_text('[]')
        changed = json.loads(original)
        changed['review']['packet_sha256'] = hashlib.sha256(packet_path.read_bytes()).hexdigest()
        index.write_text(json.dumps(changed))
        before = self.snapshot()
        result = self.call('resume', '--task', 'prices', '--update-state')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED')
        self.assertEqual(self.snapshot(), before)
        packet_path.write_bytes(original_packet)
        index.write_bytes(original)
        self.git('add', '.specdd/prices/state.json')
        before = index.read_bytes()
        self.assertEqual(self.call('resume', '--task', 'prices', '--update-state').returncode, 2)
        self.assertEqual(index.read_bytes(), before)

    def test_one_writer_and_explicit_update_preserve_unrelated_files_and_git(self):
        other = self.repo / '.specdd/other'
        other.mkdir()
        (other / 'state.json').write_text('{"phase":"COMPLETE"}')
        before = self.snapshot()
        self.assertEqual(self.call('resume', '--task', 'prices', '--update-state').returncode, 2)
        self.assertEqual(self.snapshot(), before)

    def test_current_diff_discloses_unowned_paths_without_attributing_or_touching_them(self):
        (self.repo / 'unrelated.txt').write_text('another person owns this\n')
        before = self.snapshot()
        result = self.call('resume', '--task', 'prices')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        resumed = json.loads(result.stdout)
        self.assertIn('unrelated.txt', resumed['current_diff']['excluded_paths'])
        self.assertFalse(any('.specdd' in name for name in resumed['current_diff']['excluded_paths']))
        self.assertEqual(resumed['candidate']['scope'], ['pricing.py'])
        self.assertEqual(self.snapshot(), before)

    def test_optional_spec_review_is_inspected_as_a_record_not_approval(self):
        original = self.repo
        start_tests.TaskStartTests.setUp(self)
        self.assertEqual(self.call('create', '--task', 'draft', content=start_tests.SPEC).returncode, 0)
        folder = self.repo / '.specdd/draft'
        state = json.loads((folder / 'state.json').read_text())
        self.assertEqual(self.call('spec-review', '--task', 'draft', '--spec-sha256', state['spec']['sha256'],
                                   content='SELF_CHECK: inspect AC1 against fixture behavior; not approval.').returncode, 0)
        first = self.call('resume', '--task', 'draft')
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(json.loads(first.stdout)['status'], 'PENDING')
        report = folder / 'reviews/spec-01.md'
        report.write_text('malformed report without revision binding\n')
        before = self.snapshot()
        self.assertEqual(self.call('resume', '--task', 'draft', '--update-state').returncode, 2)
        self.assertEqual(self.snapshot(), before)
        self.repo = original

    def test_resume_never_executes_repository_clean_or_process_filters(self):
        marker = self.repo / 'configured-program-ran'
        script = self.repo / 'configured-filter.sh'
        (self.repo / '.gitattributes').write_text('*.py filter=fixture\n')
        for mode in ('clean', 'process'):
            with self.subTest(filter=mode):
                script.write_text('#!/bin/sh\nprintf invoked > "' + str(marker) + '"\n' + ('cat\n' if mode == 'clean' else 'exit 1\n'))
                script.chmod(0o755)
                if marker.exists():
                    marker.unlink()  # Controlled regression setup only, never product cleanup.
                self.git('config', 'filter.fixture.' + mode, str(script))
                before = marker.exists()
                index_before = (self.repo / '.git/index').read_bytes()
                result = self.call('resume', '--task', 'prices')
                self.assertFalse(marker.exists(), json.dumps({'filter': mode, 'before_marker': before,
                    'after_marker': marker.exists(), 'returncode': result.returncode}))
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertEqual((self.repo / '.git/index').read_bytes(), index_before)

    def test_case_alias_of_tracked_task_storage_cannot_be_overwritten(self):
        self.report()
        (self.repo / '.specdd').rename(self.repo / '.SPECDD')
        self.git('add', '.SPECDD')
        state_path = self.repo / '.SPECDD/prices/state.json'
        before = state_path.read_bytes()
        result = self.call('resume', '--task', 'prices', '--update-state')
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)['status'], 'BLOCKED')
        self.assertEqual(state_path.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
