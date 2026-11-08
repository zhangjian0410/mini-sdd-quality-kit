"""Synthetic validation at public CLI; these records prove no native independence."""
import json
from pathlib import Path
import sys
import unittest
import test_task_candidate as candidate_tests


class TaskReviewTests(unittest.TestCase):
    git = candidate_tests.TaskCandidateTests.git
    call = candidate_tests.TaskCandidateTests.call
    approve = candidate_tests.TaskCandidateTests.approve
    freeze = candidate_tests.TaskCandidateTests.freeze
    # Reuse disposable fixture setup, not its inherited test suite.
    def setUp(self):
        candidate_tests.TaskCandidateTests.setUp(self)
        self.approve()
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 0)
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    if not prices: raise ValueError("empty")\n    return sum(prices) / len(prices)\n')
        self.assertEqual(self.freeze('pricing.py').returncode, 0)

    def test_pending_packet_is_reusable_and_does_not_create_fake_attempt(self):
        before = (self.repo / 'pricing.py').read_bytes()
        result = self.call('review-packet', '--task', 'prices', '--limitation', 'Host read-only controls unavailable')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        state = json.loads(result.stdout)
        self.assertEqual(state['review']['status'], 'PENDING')
        self.assertIsNone(state['latest_review'])
        packet = json.loads((self.repo / '.specdd/prices' / state['review']['packet']).read_text())
        self.assertEqual(packet['candidate']['files'][0]['path'], 'pricing.py')
        self.assertIn('AC1', packet['spec']['content'])
        self.assertIn('review-diff', packet['review_entry'])
        self.assertEqual(packet['verification']['status'], 'SUFFICIENT')
        self.assertEqual(packet['result_contract']['verification'], 'NOT_RUN')
        self.assertEqual(packet['limitations'], ['Host read-only controls unavailable'])
        self.assertFalse((self.repo / '.specdd/prices/reviews').exists())
        again = self.call('review-packet', '--task', 'prices', '--limitation', 'Host read-only controls unavailable')
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertEqual((self.repo / 'pricing.py').read_bytes(), before)
        (self.repo / 'pricing.py').write_text('drift\n')
        self.assertEqual(self.call('review-packet', '--task', 'prices').returncode, 2)


    def report(self):
        launch = self.call('review-packet', '--task', 'prices', '--implementation-context', 'implementation-session')
        self.assertEqual(launch.returncode, 0, launch.stdout + launch.stderr)
        state = json.loads(launch.stdout)
        packet = json.loads((self.repo / '.specdd/prices' / state['review']['packet']).read_text())
        return {'version': 1, 'candidate_id': packet['candidate']['id'],
                'spec_sha256': packet['spec']['sha256'], 'base': packet['base'],
                'packet_sha256': state['review']['packet_sha256'],
                'reviewer': 'fixture-reviewer', 'review_context': 'review-session',
                'coverage': ['pricing.py'], 'axes': {'Spec Compliance': 'PASS', 'Code Quality': 'No high-confidence findings'},
                'limitations': ['Synthetic helper fixture; no actual independent review occurred'],
                'verification': 'NOT_RUN', 'findings': [],
                'report': 'Inspected pricing.py lines 1-3 against AC1; empty input raises ValueError. No high-confidence findings.',
                'evidence': []}

    def submit(self, report):
        return self.call('code-review', '--task', 'prices', content=json.dumps(report))

    def test_actual_reports_are_numbered_but_self_check_cannot_satisfy_independence(self):
        report = self.report()
        report['review_context'] = 'implementation-session'
        first = self.submit(report)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        state = json.loads(first.stdout)
        self.assertEqual(state['review']['status'], 'PENDING')
        self.assertEqual(state['review']['independence'], 'SELF_CHECK')
        self.assertEqual(state['latest_review'], 'reviews/code-01.md')
        old = (self.repo / '.specdd/prices/reviews/code-01.md').read_bytes()
        report['review_context'] = 'unknown-review-session'
        second = self.submit(report)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertEqual(json.loads(second.stdout)['latest_review'], 'reviews/code-02.md')
        self.assertEqual((self.repo / '.specdd/prices/reviews/code-01.md').read_bytes(), old)
        report['candidate_id'] = 'wrong-candidate'
        self.assertEqual(self.submit(report).returncode, 2)
        report['candidate_id'] = json.loads(first.stdout)['candidate']['id']
        report['report'] = ''
        self.assertEqual(self.submit(report).returncode, 2)
        self.assertFalse((self.repo / '.specdd/prices/reviews/code-03.md').exists())

    def proof(self, report, source='manual'):
        import hashlib
        receipt = {'candidate_id': report['candidate_id'], 'packet_sha256': report['packet_sha256'],
                   'implementation_context': 'implementation-session', 'review_context': 'review-session',
                   'observer': 'fixture-independent-observer', 'provenance': source,
                   'separate_context': 'Observed separate process launch and isolated prompt input',
                   'input_identity': 'Observed candidate digests before and after review',
                   'read_only_controls': {'enforcement': 'sandbox-read-only', 'observation': 'Observed effective read-only sandbox configuration'},
                   'no_writes': 'Observed repository, Git and task records unchanged during reviewer process'}
        path = self.repo.parent / (self.repo.name + '-receipt.json')
        path.write_text(json.dumps(receipt))
        self.addCleanup(path.unlink)
        report['evidence'] = [{'source': source, 'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}]
        return path, receipt

    def test_manual_and_host_receipts_remain_distinct_and_unsupported_claims_stay_pending(self):
        for source in ('manual', 'host-captured'):
            report = self.report()
            path, receipt = self.proof(report, source)
            result = self.submit(report)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            state = json.loads(result.stdout)
            self.assertEqual(state['review']['status'], 'REVIEWED')
            self.assertEqual(state['review']['independence'], 'INDEPENDENT')
            self.assertEqual(state['review']['evidence_source'], source)
            self.assertNotEqual(state['phase'], 'COMPLETE')
            # The records above are synthetic validation, not actual independence evidence.
            receipt['read_only_controls']['enforcement'] = 'instruction-only'
            path.write_text(json.dumps(receipt))
            import hashlib
            report['evidence'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            pending = self.submit(report)
            self.assertEqual(pending.returncode, 0, pending.stdout + pending.stderr)
            self.assertEqual(json.loads(pending.stdout)['review']['status'], 'PENDING')
            path.unlink()
            # Avoid duplicate cleanup callbacks for a shared fixture receipt.
            self._cleanups.pop()

    def test_oral_self_declared_tampered_or_same_observer_receipts_do_not_establish_independence(self):
        import hashlib
        for provenance in ('user-oral', 'reviewer-self-declaration', 'manual'):
            report = self.report()
            path, receipt = self.proof(report)
            receipt['provenance'] = provenance
            if provenance == 'manual':
                receipt['observer'] = report['reviewer']
            path.write_text(json.dumps(receipt))
            report['evidence'][0]['sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
            result = self.submit(report)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)['review']['status'], 'PENDING')
            report['evidence'][0]['sha256'] = '0' * 64
            self.assertEqual(json.loads(self.submit(report).stdout)['review']['status'], 'PENDING')
            path.unlink()
            self._cleanups.pop()

    def test_changed_verification_file_cannot_be_imported_as_the_reviewed_evidence(self):
        evidence = self.repo / 'actual-verification.log'
        evidence.write_text('AC1 observed: empty input ValueError and mean([2,4]) == 3; exit 0\n')
        run = self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
                        '--verification-status', 'SUFFICIENT', '--assessment-reference', 'actual observation',
                        '--evidence-reference', str(evidence))
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        report = self.report()
        first = self.submit(report)
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        preserved = (self.repo / '.specdd/prices/reviews/code-01.md').read_bytes()
        evidence.write_text('Replaced evidence: checks failed; exit 1\n')
        refused = self.submit(report)
        self.assertEqual(refused.returncode, 2, refused.stdout + refused.stderr)
        self.assertIn('Verification evidence changed', refused.stdout)
        self.assertEqual((self.repo / '.specdd/prices/reviews/code-01.md').read_bytes(), preserved)
        self.assertFalse((self.repo / '.specdd/prices/reviews/code-02.md').exists())

if __name__ == '__main__':
    unittest.main()
