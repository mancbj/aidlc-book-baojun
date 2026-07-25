"""Executable contract tests for EXP-07-01 (composition mode only)."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ID = "EXP-07-01"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
QUICKSTART = EXPERIMENT_ROOT / "quickstart.py"
VALID_INPUT = EXPERIMENT_ROOT / "samples" / "input.json"
INVALID_ROOT = EXPERIMENT_ROOT / "samples" / "invalid"

CORE_CHECKS = [
    "facts",
    "continuity",
    "github-config",
    "tests",
    "verified-experiments",
    "generation-dry-run",
    "internal-links",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class QuickstartContractTest(unittest.TestCase):
    def run_quickstart(
        self, input_path: Path, output_path: Path, *, extra_args: list[str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        command = [
            sys.executable,
            str(QUICKSTART),
            "--input",
            str(input_path),
            "--output",
            str(output_path),
        ]
        if extra_args:
            command.extend(extra_args)
        return subprocess.run(
            command,
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_valid_sample_matches_ci_check_composition(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual("scripts/ci_check.py", report["reused_implementation"])
        self.assertEqual(CORE_CHECKS, report["configured_checks"])
        self.assertEqual(CORE_CHECKS, report["expected_checks"])
        self.assertEqual([], report["composition"]["missing_checks"])
        self.assertEqual([], report["composition"]["extra_checks"])
        self.assertEqual(7, report["metrics"]["configured_check_count"])
        self.assertEqual(7, report["metrics"]["passed_check_count"])
        self.assertEqual(0, report["metrics"]["failed_check_count"])
        self.assertIn("不证明书稿内容质量", report["limitation"])
        self.assertEqual("composition", report["mode"])

    def test_sample_flag_writes_default_output(self):
        completed = subprocess.run(
            [sys.executable, str(QUICKSTART), "--sample"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
            check=False,
        )
        report = load_json(EXPERIMENT_ROOT / "output" / "sample.json")

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(7, report["metrics"]["configured_check_count"])

    def test_repeated_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp_name:
            first = Path(temp_name) / "first.json"
            second = Path(temp_name) / "second.json"
            first_run = self.run_quickstart(VALID_INPUT, first)
            second_run = self.run_quickstart(VALID_INPUT, second)
            first_digest = hashlib.sha256(first.read_bytes()).hexdigest()
            second_digest = hashlib.sha256(second.read_bytes()).hexdigest()

        self.assertEqual(0, first_run.returncode, first_run.stderr)
        self.assertEqual(0, second_run.returncode, second_run.stderr)
        self.assertEqual(first_digest, second_digest)

    def test_composition_mismatch_fails_without_writing_valid_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "bad.json"
            completed = self.run_quickstart(INVALID_ROOT / "composition-mismatch.json", output)
            report = load_json(output)

        self.assertEqual(1, completed.returncode)
        self.assertIn("E_COMPOSITION_MISMATCH", completed.stderr)
        self.assertFalse(report["valid"])
        self.assertIn("nonexistent-gate", report["composition"]["missing_checks"])

    def test_invalid_samples_return_stable_error_codes(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
            "missing-expected-checks.json": "E_REQUIRED_FIELD",
            "duplicate-check-name.json": "E_DUPLICATE_ID",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, error_code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.output.json"
                    completed = self.run_quickstart(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[ERROR {error_code}]", completed.stderr)
                    self.assertFalse(output.exists())

    def test_contract_does_not_invoke_live_ci(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            self.assertEqual(0, completed.returncode, completed.stderr)
            report = load_json(output)
            self.assertNotIn("live_run", report)


if __name__ == "__main__":
    unittest.main()
