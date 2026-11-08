"""Ticket04 public Skill scenarios; opt-in live host runs, raw events external."""
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
class EvidenceReviewEntryTests(unittest.TestCase):
    def review(self, scenario):
        evidence = Path(os.environ['REVIEW_DIFF_EVIDENCE_DIR']).resolve()
        self.assertFalse(evidence.is_relative_to(ROOT))
        evidence.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='evidence-review-') as temporary:
            root = Path(temporary).resolve()
            (root / 'pricing.py').write_bytes((ROOT / 'tests/fixtures/corrected/pricing.py').read_bytes())
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            request = 'Review exactly pricing.py as the entire file scope. '
            if scenario == 'spec':
                (root / 'requirements.md').write_text('Revision 1\nAC1: mean_price([]) must raise ValueError. Nonempty lists return arithmetic mean.\n')
                (root / 'existing.log').write_text('Pre-existing static evidence, prior candidate: checked nonempty arithmetic path only. Empty-list behavior NOT_RUN.\n')
                request += 'Authoritative Spec: requirements.md. Pre-existing evidence: existing.log. This is the same implementation context, so independence is SELF_CHECK. '
            elif scenario == 'degraded':
                request += 'No Spec or verification evidence is available. Tool commands use a controlled PATH containing read utilities but no Python interpreter. Use shell=/bin/sh and login=false for all commands. First observe `command -v python3.11 || command -v python3 || command -v python || echo NO_PYTHON` in that environment. Do not search for absolute-path interpreters or change PATH. Continue supported read-only non-Python file inspection and disclose unperformed helper checks. A reviewer asserts they are independent, but supplies no context/control evidence. '
            elif scenario == 'export':
                request += 'No Spec or verification evidence is supplied. Explicitly export the final review report to report.md in this fixture. Only that new file is authorized; do not overwrite any existing file. '
            before = snapshot(root)
            bundle = snapshot(SKILL.parent)
            # The host's response schema is a presentation contract, not product code.
            schema = json.loads(SCHEMA.read_text())
            schema['properties']['spec_compliance']['properties']['status']['enum'] = ['N/A', 'UNKNOWN', 'FINDINGS', 'PASS']
            schema['properties']['findings']['items']['properties']['axis']['enum'] = ['Code Quality', 'Spec Compliance']
            schema_path = evidence / (scenario + '-schema.json')
            schema_path.write_text(json.dumps(schema))
            prompt = f'Use $review-diff at {SKILL}. Repository: {root}. {request} Return the host-required JSON response. Preserve Review Only constraints.'
            controlled = None
            if scenario == 'degraded':
                controlled = evidence / 'read-tools'
                controlled.mkdir(exist_ok=True)
                for name in ('cat', 'sed', 'nl', 'git', 'shasum', 'ls', 'head', 'wc', 'pwd'):
                    target = shutil.which(name)
                    link = controlled / name
                    if target and not link.exists(): link.symlink_to(target)
                missing = subprocess.run(['/bin/sh', '-c', 'command -v python3.11 || command -v python3 || command -v python || echo NO_PYTHON'], env={'PATH': str(controlled)}, text=True, capture_output=True, check=True)
                self.assertEqual(missing.stdout.strip(), 'NO_PYTHON')
                (evidence / 'interpreter-preflight.json').write_text(json.dumps({'PATH': str(controlled), 'stdout': missing.stdout, 'returncode': missing.returncode}))
            command = [shutil.which('codex'), 'exec', '--ignore-user-config', '--ephemeral', '--sandbox', 'workspace-write' if scenario == 'export' else 'read-only', '-c', 'approval_policy="never"', '--json', '--color', 'never', '--cd', str(root), '--output-schema', str(schema_path), '-']
            if controlled:
                command[-1:-1] = ['-c', 'shell_environment_policy.set={PATH=' + json.dumps(str(controlled)) + '}']
            run = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=240)
            stem = evidence / scenario
            stem.with_suffix('.events.jsonl').write_text(run.stdout)
            stem.with_suffix('.stderr.txt').write_text(run.stderr)
            after = snapshot(root)
            audit = dict(command=command, prompt=prompt, returncode=run.returncode, before=before, after=after, bundle_unchanged=bundle == snapshot(SKILL.parent), skill_sha256=hashlib.sha256(SKILL.read_bytes()).hexdigest())
            stem.with_suffix('.audit.json').write_text(json.dumps(audit, indent=2))
            self.assertEqual(run.returncode, 0, run.stderr + run.stdout[-2000:])
            items = [e['item'] for line in run.stdout.splitlines() if (e := json.loads(line)).get('type') == 'item.completed']
            report = json.loads([i['text'] for i in items if i.get('type') == 'agent_message'][-1])
            stem.with_suffix('.report.json').write_text(json.dumps(report, indent=2))
            commands = [i['command'] for i in items if i.get('type') == 'command_execution']
            stem.with_suffix('.commands.json').write_text(json.dumps(commands, indent=2))
            for command in commands:
                self.assertFalse(re.search(r'\b(pytest|unittest|npm|npx|make|compileall|ruff|mypy|curl|wget)\b', command), command)
                self.assertFalse(re.search(r'python[\d.]*\s+(?:-B\s+)?(?:[^\s;]*[/])?pricing\.py(?:[\s;]|$)', command), command)
            self.assertTrue(audit['bundle_unchanged'])
            if scenario == 'export':
                exported = root / 'report.md'
                self.assertTrue(exported.is_file(), 'Explicit export must produce the requested report')
                self.assertIn('pricing.py', exported.read_text())
                self.assertIn('NOT_RUN', exported.read_text())
                self.assertEqual({k:v for k,v in after.items() if k != 'report.md'}, before)
            else:
                self.assertEqual(before, after)
                self.assertFalse(any(i.get('type') == 'file_change' for i in items))
            self.assertEqual(report['verification']['status'], 'NOT_RUN')
            self.assertEqual(report['verification']['behavior_checks_run'], [])
            if scenario == 'spec':
                self.assertEqual(report['spec_compliance']['status'], 'FINDINGS')
                findings = [f for f in report['findings'] if f['axis'] == 'Spec Compliance' and f['line'] in (2, 3)]
                self.assertTrue(findings, 'AC1 violation must be grounded in the empty-list return')
                self.assertIn('ValueError', json.dumps(findings))
                self.assertIn('existing.log', report['verification']['existing_evidence'])
                self.assertEqual(report['independence']['status'], 'SELF_CHECK')
            else:
                self.assertEqual(report['spec_compliance']['status'], 'N/A')
                self.assertIn(report['independence']['status'], ('UNVERIFIED', 'SELF_CHECK'))
            if scenario == 'degraded':
                self.assertTrue(report['scope']['limitations'])
                self.assertRegex(json.dumps(report).lower(), 'python|interpreter')
                self.assertFalse(any(re.search(r'(?:^|[;&|]\s*|\s)(?:/[^ ;]+/)?python(?:3(?:\.\d+)?)?\s+(?!\|)', c) for c in commands if 'command -v' not in c), commands)
                self.assertTrue(any(i.get('type') == 'command_execution' and i.get('aggregated_output', '').strip() == 'NO_PYTHON' and i.get('exit_code') == 0 for i in items), 'Native tool must observe interpreter absence')
            return report

    def test_authoritative_spec_and_preexisting_evidence(self): self.review('spec')
    def test_explicit_export_only(self): self.review('export')
    def test_missing_interpreter_supported_inspection(self): self.review('degraded')


if __name__ == '__main__': unittest.main()
