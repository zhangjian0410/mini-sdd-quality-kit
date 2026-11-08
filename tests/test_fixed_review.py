"""Opt-in actual fixed-comparison Skill invocation; fixture observations outside repo."""
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from test_review_diff import ROOT, SKILL, SCHEMA, snapshot


@unittest.skipUnless(os.environ.get('REVIEW_DIFF_LIVE') == '1', 'actual Skill NOT_RUN')
class FixedReviewEntryTests(unittest.TestCase):
    def test_committed_bug_with_dirty_correction_and_unknown_pr(self):
        evidence = Path(os.environ['REVIEW_DIFF_EVIDENCE_DIR']).resolve()
        self.assertFalse(evidence.is_relative_to(ROOT))
        evidence.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='fixed-review-') as temp:
            root = Path(temp).resolve()
            def git(*args):
                return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout
            git('init', '-q')
            (root / 'pricing.py').write_bytes((ROOT / 'tests/fixtures/corrected/pricing.py').read_bytes())
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'baseline')
            base = git('rev-parse', 'HEAD').decode().strip()
            bug = (ROOT / 'tests/fixtures/logic_bug/pricing.py').read_bytes()
            (root / 'pricing.py').write_bytes(bug)
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=x@y', 'commit', '-qm', 'change')
            tip = git('rev-parse', 'HEAD').decode().strip()
            (root / 'pricing.py').write_bytes((ROOT / 'tests/fixtures/corrected/pricing.py').read_bytes())
            (root / 'unrelated.txt').write_text('unrelated existing draft\n')
            requests = [('fixed', f'Review only the committed comparison from base {base} to tip {tip}. Workspace correction in pricing.py and unrelated.txt are extra workspace work; exclude those from committed review and disclose them.'),
                        ('pr', 'Review PR https://example.invalid/pull/3. No local comparison information is supplied. Do not perform network lookup or guess a comparison.')]
            for name, request in requests:
                before = snapshot(root)
                bundle_before = snapshot(SKILL.parent)
                prompt = f'Use $review-diff at {SKILL}. Repository root: {root}. {request} No authoritative Spec or existing verification evidence. Return host-required JSON; keep Review Only read-only.'
                command = [shutil.which('codex'), 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'read-only', '-c', 'approval_policy="never"', '--json', '--color', 'never', '--cd', str(root), '--output-schema', str(SCHEMA), '-']
                run = subprocess.run(command, input=prompt, capture_output=True, text=True, timeout=240)
                stem = evidence / name
                stem.with_suffix('.events.jsonl').write_text(run.stdout)
                stem.with_suffix('.stderr.txt').write_text(run.stderr)
                after = snapshot(root)
                stem.with_suffix('.audit.json').write_text(json.dumps(dict(command=command, prompt=prompt, returncode=run.returncode, unchanged=before == after, bundle_unchanged=bundle_before == snapshot(SKILL.parent)), indent=2))
                self.assertEqual(run.returncode, 0, run.stderr + run.stdout[-2000:])
                self.assertEqual(before, after)
                self.assertEqual(bundle_before, snapshot(SKILL.parent))
                items = [e['item'] for line in run.stdout.splitlines() if (e := json.loads(line)).get('type') == 'item.completed']
                self.assertFalse(any(i.get('type') == 'file_change' for i in items))
                commands = [i['command'] for i in items if i.get('type') == 'command_execution']
                stem.with_suffix('.commands.json').write_text(json.dumps(commands, indent=2))
                for command in commands:
                    self.assertFalse(re.search(r'\b(pytest|unittest|npm|npx|make|compileall|ruff|mypy|curl|wget)\b', command), command)
                report = json.loads([i['text'] for i in items if i.get('type') == 'agent_message'][-1])
                stem.with_suffix('.report.json').write_text(json.dumps(report, indent=2))
                self.assertEqual(report['verification']['behavior_checks_run'], [])
                self.assertEqual(report['spec_compliance']['status'], 'N/A')
                self.assertIn(report['independence']['status'], ('SELF_CHECK', 'UNVERIFIED'))
                if name == 'fixed':
                    scope = json.dumps(report['scope'])
                    self.assertEqual(report['scope']['kind'], 'fixed-comparison')
                    self.assertIn(base, scope)
                    self.assertIn(tip, scope)
                    self.assertIn(hashlib.sha256(bug).hexdigest(), scope)
                    self.assertIn('unrelated.txt', json.dumps(report['scope']['excluded']))
                    self.assertTrue(any(f['line'] == 4 and 'prices - 1' in f['evidence'] for f in report['findings']))
                else:
                    self.assertEqual(report['code_quality']['status'], 'LIMITED')
                    self.assertEqual(report['findings'], [])
                    self.assertEqual(report['scope']['files'], [])
