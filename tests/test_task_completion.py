"""Synthetic public-CLI validation only; fixtures establish no real Independent Review."""
import hashlib
import json
import unittest
import test_task_review as review_tests


class TaskCompletionTests(unittest.TestCase):
    git = review_tests.TaskReviewTests.git
    call = review_tests.TaskReviewTests.call
    approve = review_tests.TaskReviewTests.approve
    freeze = review_tests.TaskReviewTests.freeze
    report = review_tests.TaskReviewTests.report
    def proof(self, report):
        path, receipt = review_tests.TaskReviewTests.proof(self, report)
        self._cleanups.pop()
        unique = path.with_name(path.stem + '-' + report['packet_sha256'] + '.json')
        path.rename(unique)
        self.addCleanup(unique.unlink)
        report['evidence'][0]['path'] = str(unique)
        return unique, receipt
    submit = review_tests.TaskReviewTests.submit
    setUp = review_tests.TaskReviewTests.setUp

    def test_repair_checks_original_inputs_then_preserves_history_and_consent(self):
        report = self.report()
        self.assertEqual(self.submit(report).returncode, 0)
        folder = self.repo / '.specdd/prices'
        before = json.loads((folder / 'state.json').read_text())
        history = (folder / before['latest_review']).read_bytes()
        source = self.repo / 'pricing.py'
        old = source.read_bytes()
        source.write_text('candidate drift\n')
        blocked = self.call('repair', '--task', 'prices', '--reason', 'Confirmed AC1 violation')
        self.assertEqual(blocked.returncode, 2, blocked.stdout + blocked.stderr)
        self.assertIn('Candidate drift', blocked.stdout)
        source.write_bytes(old)
        repaired = self.call('repair', '--task', 'prices', '--reason', 'Confirmed AC1 violation')
        self.assertEqual(repaired.returncode, 0, repaired.stdout + repaired.stderr)
        state = json.loads(repaired.stdout)
        self.assertEqual(state['phase'], 'IMPLEMENTING')
        self.assertEqual(state['consent_reference'], before['consent_reference'])
        self.assertIsNone(state['candidate'])
        self.assertNotIn('review', state)
        self.assertIsNone(state['latest_review'])
        self.assertEqual((folder / before['latest_review']).read_bytes(), history)
        resumed = self.call('resume', '--task', 'prices')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)

    def reviewed(self, finding=False):
        # Readable files permit byte-binding; their claims remain synthetic here.
        evidence = self.repo / 'verification.log'
        evidence.write_text('Fixture observation: empty input raises ValueError; mean([2,4]) == 3. exit 0\n')
        self.assertEqual(self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
            '--verification-status', 'SUFFICIENT', '--assessment-reference', str(evidence),
            '--evidence-reference', str(evidence)).returncode, 0)
        report = self.report()
        if finding:
            report['findings'] = [{'id': 'F1', 'axis': 'Spec Compliance', 'severity': 'P1',
                'file': 'pricing.py', 'line': 2, 'expected': 'AC1 empty input rejected',
                'actual': 'Known failing implementation', 'evidence': 'Static source path',
                'impact': 'AC1 violation', 'remedy': 'Raise ValueError', 'verification': 'NOT_RUN'}]
        if finding == 'suggestion':
            report['findings'][0].update(axis='Code Quality', severity='low', expected='Optional explanatory docstring', actual='No docstring', evidence='Source inspection', impact='Readability suggestion only; no AC violation or material defect', remedy='Consider a docstring later')
        self.proof(report)
        result = self.submit(report)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def assessment(self, state):
        folder = self.repo / '.specdd/prices'
        reports = {p.relative_to(folder).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
                   for p in sorted((folder / 'reviews').glob('code-*.md'))}
        return {'version': 1, 'candidate_id': state['candidate']['id'],
            'spec_sha256': state['spec']['sha256'], 'consent_reference': state['consent_reference'],
            'reviews': reports, 'implementation': 'Inspected accepted AC1 behavior and scope against current source.',
            'verification': 'Inspected actual fixture command/result and assessed proportional adequacy for AC1.',
            'review_authenticity': 'Inspected separate context, enforced controls, exact inputs and no-write observer receipt.',
            'axes': {'Spec Compliance': {'status': 'SATISFIED', 'rationale': 'AC1 implemented in inspected pricing.py.'},
                     'Code Quality': {'status': 'SATISFIED', 'rationale': 'Inspected error path and preserved arithmetic behavior.'}},
            'findings': [], 'disclosed': ['Synthetic helper fixture; no actual independent review occurred']}

    def complete(self, assessment):
        path = self.repo / 'completion-assessment.json'
        path.write_text(json.dumps(assessment))
        return self.call('complete', '--task', 'prices', '--assessment-reference', str(path))

    def test_completion_needs_inspected_assessment_and_valid_current_review(self):
        # An axis string or empty findings list cannot grant Completion.
        state = self.reviewed()
        bad = self.complete({'status': 'PASS'})
        self.assertEqual(bad.returncode, 2, bad.stdout + bad.stderr)
        assessment = self.assessment(state)
        good = self.complete(assessment)
        self.assertEqual(good.returncode, 0, good.stdout + good.stderr)
        self.assertEqual(json.loads(good.stdout)['phase'], 'COMPLETE')
        resumed = self.call('resume', '--task', 'prices')
        self.assertEqual(resumed.returncode, 0, resumed.stdout + resumed.stderr)
        self.assertEqual(json.loads(resumed.stdout)['completion']['status'], 'ATTRIBUTABLE')
        self.assertNotEqual(json.loads(resumed.stdout)['status'], 'PASS')
        (self.repo / 'pricing.py').write_text('subsequent drift\n')
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 2)

    def test_unresolved_findings_fail_and_same_candidate_cannot_claim_repaired(self):
        state = self.reviewed(finding='suggestion')
        assessment = self.assessment(state)
        self.assertEqual(self.complete(assessment).returncode, 2)
        finding = {'review': state['latest_review'], 'id': 'F1', 'disposition': 'UNRESOLVED',
                   'rationale': 'Finding has not yet been assessed; no Completion judgment.'}
        assessment['findings'] = [finding]
        self.assertEqual(self.complete(assessment).returncode, 2)
        finding['disposition'] = 'REPAIRED'
        self.assertEqual(self.complete(assessment).returncode, 2)
        finding.update(disposition='NON_BLOCKING', rationale='Inspected optional docstring suggestion; no AC violation or material defect.')
        self.assertEqual(self.complete(assessment).returncode, 0)

    def test_repair_new_candidate_requires_new_review_and_preserves_attempts(self):
        state = self.reviewed(finding=True)
        folder = self.repo / '.specdd/prices'
        old_report = (folder / state['latest_review']).read_bytes()
        self.assertEqual(self.call('repair', '--task', 'prices', '--reason', 'Fix confirmed F1 within AC1').returncode, 0)
        (self.repo / 'pricing.py').write_text('def mean_price(prices):\n    if not prices:\n        raise ValueError("empty")\n    return sum(prices) / len(prices)\n')
        self.assertEqual(self.freeze('pricing.py').returncode, 0)
        self.assertEqual(self.complete(self.assessment(state)).returncode, 2)
        latest = self.reviewed()
        self.assertNotEqual(latest['candidate']['id'], state['candidate']['id'])
        assessment = self.assessment(latest)
        assessment['findings'] = [{'review': state['latest_review'], 'id': 'F1', 'disposition': 'REPAIRED',
            'rationale': 'Affected check repeated and code-02 independently inspected the new candidate.'}]
        self.assertEqual(self.complete(assessment).returncode, 0)
        self.assertEqual((folder / state['latest_review']).read_bytes(), old_report)
        self.assertEqual(latest['latest_review'], 'reviews/code-02.md')

    def test_malformed_assessment_fails_closed_without_task_or_git_writes(self):
        state = self.reviewed()
        assessment = self.assessment(state)
        # A nonhashable finding identity must yield the public BLOCKED contract.
        assessment['findings'] = [{'review': [], 'id': 'F1', 'disposition': 'NON_BLOCKING', 'rationale': 'bad input'}]
        folder = self.repo / '.specdd/prices'
        before = {p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}
        index = (self.repo / '.git/index').read_bytes()
        run = self.complete(assessment)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertEqual(json.loads(run.stdout)['status'], 'BLOCKED')
        self.assertEqual({p.relative_to(folder).as_posix(): p.read_bytes() for p in folder.rglob('*') if p.is_file()}, before)
        self.assertEqual((self.repo / '.git/index').read_bytes(), index)

    def test_missing_checks_pending_review_and_partial_coverage_never_complete(self):
        state = json.loads(self.call('resume', '--task', 'prices').stdout)
        # A checkpoint alone has no real review, even with caller SUFFICIENT.
        self.assertEqual(self.complete({'status': 'PASS'}).returncode, 2)
        report = self.report()
        pending = json.loads(self.submit(report).stdout)
        self.assertEqual(self.complete(self.assessment(pending)).returncode, 2)
        path = self.repo / 'new.py'
        path.write_text('NEW = 7\n')
        self.assertEqual(self.freeze('pricing.py', 'new.py').returncode, 0)
        report = self.report()
        self.proof(report)
        partial = json.loads(self.submit(report).stdout)
        self.assertEqual(self.complete(self.assessment(partial)).returncode, 2)
        blocked = self.call('checkpoint', '--task', 'prices', '--owned', 'pricing.py',
            '--verification-status', 'INCOMPLETE', '--assessment-reference', 'Necessary integration NOT_RUN',
            '--missing', 'Actual integration check NOT_RUN')
        self.assertEqual(blocked.returncode, 0)
        self.assertEqual(self.complete(self.assessment(partial)).returncode, 2)

    def test_completed_record_rechecks_assessment_history_spec_report_and_verification_drift(self):
        state = self.reviewed()
        self.assertEqual(self.complete(self.assessment(state)).returncode, 0)
        folder = self.repo / '.specdd/prices'
        paths = [self.repo / 'completion-assessment.json', self.repo / 'verification.log',
                 folder / 'spec.md', folder / state['latest_review']]
        for path in paths:
            saved = path.read_bytes()
            path.write_bytes(saved + b'\nchanged\n')
            index = (folder / 'state.json').read_bytes()
            run = self.call('resume', '--task', 'prices', '--update-state')
            self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
            self.assertEqual((folder / 'state.json').read_bytes(), index)
            path.write_bytes(saved)
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 0)

    def test_material_revision_discards_review_approval_and_requires_renewed_consent(self):
        from test_task_start import SPEC
        state = self.reviewed()
        folder = self.repo / '.specdd/prices'
        original = (folder / state['latest_review']).read_bytes()
        revised = SPEC.replace('Revision: 1', 'Revision: 2').replace('Reject empty prices.', 'Reject empty prices and reject None.')
        run = self.call('revise', '--task', 'prices', '--previous-sha256', state['spec']['sha256'], content=revised)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        pending = json.loads(run.stdout)
        self.assertEqual(pending['phase'], 'AWAITING_CONSENT')
        self.assertNotIn('review', pending)
        self.assertNotIn('consent_reference', pending)
        self.assertEqual(self.call('begin', '--task', 'prices').returncode, 2)
        self.assertEqual((folder / state['latest_review']).read_bytes(), original)
        self.assertEqual(self.call('resume', '--task', 'prices').returncode, 0)

    def test_local_completion_preserves_issue_unrelated_files_git_and_task_history(self):
        state = self.reviewed()
        issue = self.repo / 'ISSUE.md'
        issue.write_text('Status: open; team-owned issue\n')
        legacy = self.repo / 'legacy.txt'
        legacy.write_text('unrelated pre-existing issue disclosed\n')
        git_before = {p.relative_to(self.repo / '.git').as_posix(): p.read_bytes()
                      for p in (self.repo / '.git').rglob('*') if p.is_file()}
        folder = self.repo / '.specdd/prices'
        history = {p.relative_to(folder).as_posix(): p.read_bytes()
                   for p in folder.rglob('*') if p.is_file() and p.name != 'state.json'}
        result = self.complete(self.assessment(state))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual({p.relative_to(self.repo / '.git').as_posix(): p.read_bytes()
                          for p in (self.repo / '.git').rglob('*') if p.is_file()}, git_before)
        self.assertEqual({p.relative_to(folder).as_posix(): p.read_bytes()
                          for p in folder.rglob('*') if p.is_file() and p.name != 'state.json'}, history)
        self.assertEqual(issue.read_text(), 'Status: open; team-owned issue\n')
        self.assertEqual(legacy.read_text(), 'unrelated pre-existing issue disclosed\n')

    def test_attributable_complete_resume_persists_the_returned_action_without_stale_outstanding_limit(self):
        state = self.reviewed()
        self.assertEqual(self.complete(self.assessment(state)).returncode, 0)
        run = self.call('resume', '--task', 'prices', '--update-state')
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        result = json.loads(run.stdout)
        stored = json.loads((self.repo / '.specdd/prices/state.json').read_text())
        self.assertEqual(result['completion']['status'], 'ATTRIBUTABLE')
        self.assertEqual(stored['next_action'], result['next_action'])
        self.assertNotIn('Necessary verification or Completion assessment remains outstanding', result['limitations'])


if __name__ == '__main__':
    unittest.main()
