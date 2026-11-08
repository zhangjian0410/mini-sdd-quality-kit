"""Real default public Skill checks; raw host evidence stays outside the kit."""
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_review_diff import ROOT, SKILL, SCHEMA, snapshot


@unittest.skipUnless(os.environ.get('REVIEW_DIFF_LIVE') == '1', 'real Skill NOT_RUN; set REVIEW_DIFF_LIVE=1')
class DefaultReviewEntryTests(unittest.TestCase):
    def review(self, scenario):
        evidence = Path(os.environ['REVIEW_DIFF_EVIDENCE_DIR']).resolve()
        self.assertFalse(evidence.is_relative_to(ROOT))
        evidence.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='default-review-') as temp:
            root = Path(temp).resolve()
            def git(*args):
                subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True)
            git('init', '-q')
            for name in ('pricing.py', 'other.py'):
                (root / name).write_bytes((ROOT / 'tests/fixtures/corrected/pricing.py').read_bytes())
            git('add', '.')
            git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'baseline')
            request = 'Review current workspace changes. '
            selected = 'pricing.py'
            if scenario in ('staged', 'unstaged', 'unrelated', 'ambiguous'):
                (root / selected).write_bytes((ROOT / 'tests/fixtures/logic_bug/pricing.py').read_bytes())
            if scenario in ('staged', 'canceled'):
                if scenario == 'canceled':
                    (root / selected).write_bytes((ROOT / 'tests/fixtures/logic_bug/pricing.py').read_bytes())
                git('add', selected)
                if scenario == 'canceled':
                    (root / selected).write_bytes((ROOT / 'tests/fixtures/corrected/pricing.py').read_bytes())
            if scenario == 'untracked':
                selected = 'new pricing.py'
                (root / selected).write_bytes((ROOT / 'tests/fixtures/logic_bug/pricing.py').read_bytes())
            if scenario == 'unrelated':
                (root / 'other.py').write_text('unrelated private draft\n')
                request += 'other.py is unrelated pre-existing work; exclude it. '
            if scenario == 'ambiguous':
                request += 'The ownership of pricing.py is unknown; do not attribute it to my task. '
            elif scenario != 'clean':
                request += f'{selected} is my only current task change and relevant to this review. '
            if scenario == 'unsupported':
                request = 'Review from an ambiguous base: either previous release or main, whichever you guess. '
            head = subprocess.run(['git', '-C', str(root), 'rev-parse', 'HEAD'], check=True, capture_output=True, text=True).stdout.strip()
            layer_hashes = []
            for layer in (['--cached', 'HEAD'], []):
                patch = subprocess.run(['git', '-C', str(root), 'diff', '--no-ext-diff', '--no-textconv', '--no-renames', '--ignore-submodules=dirty', '--binary', *layer, '--', ':(literal)' + selected], check=True, capture_output=True).stdout
                if patch:
                    layer_hashes.append(hashlib.sha256(patch).hexdigest())
            index_blob = subprocess.run(['git', '-C', str(root), 'show', ':' + selected], capture_output=True)
            index_sha256 = hashlib.sha256(index_blob.stdout).hexdigest() if index_blob.returncode == 0 else None
            before = snapshot(root)
            bundle_before = snapshot(SKILL.parent)
            prompt = f'Use $review-diff at {SKILL}. Repository root: {root}. {request} No authoritative Spec or existing verification evidence is supplied. Return the host-required JSON report. Keep Review Only read-only.'
            command = [shutil.which('codex'), 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'read-only', '-c', 'approval_policy="never"', '--json', '--color', 'never', '--cd', str(root), '--output-schema', str(SCHEMA), '-']
            run = subprocess.run(command, input=prompt, capture_output=True, text=True, timeout=240)
            stem = evidence / ('default-' + scenario)
            stem.with_suffix('.events.jsonl').write_text(run.stdout)
            stem.with_suffix('.stderr.txt').write_text(run.stderr)
            after = snapshot(root)
            audit = dict(command=command, prompt=prompt, returncode=run.returncode, before=before, after=after, unchanged=before == after, bundle_unchanged=bundle_before == snapshot(SKILL.parent), skill_sha256=hashlib.sha256(SKILL.read_bytes()).hexdigest())
            stem.with_suffix('.audit.json').write_text(json.dumps(audit, indent=2))
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout[-2000:])
            self.assertEqual(before, after)
            self.assertTrue(audit['bundle_unchanged'])
            items = [e['item'] for line in run.stdout.splitlines() if (e := json.loads(line)).get('type') == 'item.completed']
            self.assertFalse(any(i.get('type') == 'file_change' for i in items))
            report = json.loads([i['text'] for i in items if i.get('type') == 'agent_message'][-1])
            stem.with_suffix('.report.json').write_text(json.dumps(report, indent=2))
            commands = [i['command'] for i in items if i.get('type') == 'command_execution']
            stem.with_suffix('.commands.json').write_text(json.dumps(commands, indent=2))
            for command in commands:
                self.assertFalse(re.search(r'\b(pytest|unittest|npm|npx|make|compileall|ruff|mypy|curl|wget)\b', command), command)
                self.assertFalse(re.search(r'python[\d.]*\s+(?:-B\s+)?(?:[^\s;]*[/])?(?:pricing|other)\.py(?:[\s;]|$)', command), command)

            self.assertEqual(report['spec_compliance']['status'], 'N/A')
            self.assertEqual(report['verification']['status'], 'NOT_RUN')
            self.assertEqual(report['verification']['behavior_checks_run'], [])
            self.assertIn(report['independence']['status'], ('SELF_CHECK', 'UNVERIFIED'))
            if scenario in ('clean', 'ambiguous', 'unsupported'):
                self.assertEqual(report['scope']['files'], [])
                self.assertEqual(report['findings'], [])
                if scenario != 'clean':
                    self.assertEqual(report['code_quality']['status'], 'LIMITED')
                    self.assertTrue(report['scope']['limitations'] or report['scope']['excluded'])
            else:
                scope_text = json.dumps(report['scope'])
                self.assertIn(head, scope_text)
                for digest in layer_hashes:
                    self.assertIn(digest, scope_text, 'Report must retain actual layer patch identity')
                self.assertRegex(scope_text.lower(), r'own|task|attribut')
                self.assertEqual(report['scope']['kind'], 'default-workspace')
                current_sha256 = hashlib.sha256((root / selected).read_bytes()).hexdigest()
                current_seen = False
                for reviewed in report['scope']['files']:
                    # One logical file can have separate worktree/index coverage
                    # rows. A layer qualifier is presentation, not an extra file.
                    qualifier = re.search(r'\s*[\[(](?:index|staged)[^()\[\]/\\]*[\])]$', reviewed['path'], re.I)
                    logical_path = reviewed['path'][:qualifier.start()] if qualifier else reviewed['path']
                    self.assertEqual((root / logical_path).resolve(), root / selected, 'Unexpected logical file in scope')
                    if qualifier:
                        self.assertIsNotNone(index_sha256, 'An untracked file has no index input')
                        self.assertEqual(reviewed['sha256'], index_sha256)
                    elif reviewed['sha256'] == current_sha256:
                        current_seen = True
                    else:
                        self.assertIsNotNone(index_sha256)
                        self.assertEqual(reviewed['sha256'], index_sha256)
                        self.assertRegex(reviewed['lines_reviewed'].lower(), r'index|staged')
                self.assertTrue(current_seen, 'Current file identity must still be reported')
                self.assertTrue(any((root / f['file']).resolve() == root / selected and f['line'] == 4 and 'prices - 1' in f['evidence'] for f in report['findings']))
            if scenario == 'unrelated':
                self.assertIn('other.py', json.dumps(report['scope']['excluded']))
            return report

    def test_staged_defect_hidden_by_unstaged_correction(self): self.review('canceled')
    def test_staged(self): self.review('staged')
    def test_unstaged(self): self.review('unstaged')
    def test_owned_untracked(self): self.review('untracked')
    def test_unrelated_exclusion(self): self.review('unrelated')
    def test_ambiguous_ownership(self): self.review('ambiguous')
    def test_clean(self): self.review('clean')
    def test_unsupported_comparison(self): self.review('unsupported')
