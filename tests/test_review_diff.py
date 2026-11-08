"""Real Skill-entry checks; model calls require explicit REVIEW_DIFF_LIVE=1."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "review-diff" / "SKILL.md"
SCHEMA = ROOT / "tests" / "review_report.schema.json"


def snapshot(root: Path) -> dict[str, dict[str, str | int]]:
    """Observe the reviewed filesystem, including Git metadata, without writes."""
    result = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        entry: dict[str, str | int] = {"mode": stat.S_IMODE(info.st_mode)}
        if path.is_symlink():
            entry["link"] = os.readlink(path)
        elif path.is_file():
            entry["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            entry["kind"] = "directory"
        result[path.relative_to(root).as_posix()] = entry
    return result


@unittest.skipUnless(os.environ.get("REVIEW_DIFF_LIVE") == "1", "real Codex run NOT_RUN; set REVIEW_DIFF_LIVE=1")
class ReviewDiffEntryTests(unittest.TestCase):
    def review(self, variant: str) -> dict:
        self.assertTrue(SKILL.is_file(), "The public review-diff Skill entry does not exist")
        executable = shutil.which("codex")
        self.assertIsNotNone(executable, "Codex CLI is required for this development-host check")
        evidence = Path(os.environ["REVIEW_DIFF_EVIDENCE_DIR"]).resolve()
        self.assertFalse(evidence.is_relative_to(ROOT), "Keep raw host events outside the kit: they may contain private host context")
        evidence.mkdir(parents=True, exist_ok=True)
        skill_before = snapshot(SKILL.parent)
        with tempfile.TemporaryDirectory(prefix="review-fixture-") as temporary:
            fixture = Path(temporary).resolve()
            source = (ROOT / "tests" / "fixtures" / variant / "pricing.py").read_bytes()
            (fixture / "pricing.py").write_bytes(source)
            subprocess.run(["git", "init", "--quiet", str(fixture)], check=True, capture_output=True)
            before = snapshot(fixture)
            prompt = (
                f"Use $review-diff at {SKILL} to review exactly {fixture / 'pricing.py'}. "
                "The complete scope of this proposed change is this entire explicitly named file. "
                "No authoritative Spec, existing verification evidence, or externally attested "
                "review independence is supplied. Keep this a read-only Review Only request. "
                "Use the host-required JSON response format without changing the review contract."
            )
            command = [
                executable, "exec", "--ignore-user-config", "--ephemeral",
                "--sandbox", "read-only", "-c", 'approval_policy="never"',
                "--json", "--color", "never", "--cd", str(fixture),
                "--output-schema", str(SCHEMA), "-",
            ]
            completed = subprocess.run(command, input=prompt, text=True, capture_output=True, timeout=180)
            after = snapshot(fixture)
            skill_after = snapshot(SKILL.parent)
            (evidence / f"{variant}-events.jsonl").write_text(completed.stdout, encoding="utf-8")
            (evidence / f"{variant}-stderr.txt").write_text(completed.stderr, encoding="utf-8")
            audit = {
                "command": command, "prompt": prompt, "returncode": completed.returncode,
                "skill_sha256": hashlib.sha256(SKILL.read_bytes()).hexdigest(),
                "skill_before": skill_before, "skill_after": skill_after,
                "selected_input": {"path": "pricing.py", "content": source.decode("utf-8"), "sha256": hashlib.sha256(source).hexdigest()},
                "before": before, "after": after, "unchanged": before == after,
            }
            (evidence / f"{variant}-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout[-4000:])
            self.assertEqual(before, after, "The reviewed repository changed during Review Only")
            self.assertEqual(skill_before, skill_after, "The Skill changed during its live check")
            events = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
            items = [event["item"] for event in events if event.get("type") == "item.completed"]
            self.assertFalse(any(item.get("type") == "file_change" for item in items), "Reviewer attempted file edits")
            messages = [item["text"] for item in items if item.get("type") == "agent_message"]
            self.assertTrue(messages, "No actual Skill report returned")
            report = json.loads(messages[-1])
            (evidence / f"{variant}-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            self.assertEqual(report["scope"]["kind"], "explicit-files")
            self.assertEqual(Path(report["scope"]["root"]).resolve(), fixture)
            self.assertEqual(len(report["scope"]["files"]), 1)
            reviewed = report["scope"]["files"][0]
            self.assertEqual((fixture / reviewed["path"]).resolve(), fixture / "pricing.py")
            self.assertEqual(reviewed["sha256"], hashlib.sha256(source).hexdigest())
            self.assertTrue(reviewed["lines_reviewed"])
            self.assertEqual(report["spec_compliance"]["status"], "N/A")
            self.assertIn(report["independence"]["status"], ["SELF_CHECK", "UNVERIFIED"])
            self.assertEqual(report["verification"]["status"], "NOT_RUN")
            self.assertEqual(report["verification"]["behavior_checks_run"], [])
            for finding in report["findings"]:
                for field in ("id", "axis", "severity", "file", "line", "expected", "actual", "evidence", "impact", "remedy", "verification_status"):
                    self.assertTrue(finding[field], f"Missing finding value: {field}")
                self.assertEqual(finding["axis"], "Code Quality")
                self.assertEqual((fixture / finding["file"]).resolve(), fixture / "pricing.py")
                self.assertEqual(finding["verification_status"], "NOT_RUN")
            return report

    def test_known_logic_defect_is_grounded_in_the_selected_file(self):
        report = self.review("logic_bug")
        self.assertEqual(report["code_quality"]["status"], "FINDINGS")
        grounded = [finding for finding in report["findings"] if finding["line"] == 4]
        self.assertTrue(grounded, "The known failing expression must be identified at line 4")
        self.assertTrue(any("prices - 1" in finding["evidence"] for finding in grounded))

    def test_corrected_counterpart_does_not_repeat_the_removed_defect(self):
        report = self.review("corrected")
        self.assertEqual(report["code_quality"]["status"], "NO_HIGH_CONFIDENCE_FINDINGS")
        self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
