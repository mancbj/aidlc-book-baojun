"""Executable contract tests for EXP-04-01."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
QUICKSTART = EXPERIMENT_ROOT / "quickstart.py"
VALID_INPUT = EXPERIMENT_ROOT / "samples" / "input.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class QuickstartContractTest(unittest.TestCase):
    def run_quickstart(self, output_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(QUICKSTART),
                "--input",
                str(VALID_INPUT),
                "--output",
                str(output_path),
            ],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )

    def test_valid_sample_generates_ab_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "sample.json"
            completed = self.run_quickstart(output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(100.0, report["metrics"]["with_memory_bank"]["context_recovery_accuracy_percent"])
        self.assertEqual(0.0, report["metrics"]["without_memory_bank"]["context_recovery_accuracy_percent"])
        self.assertFalse(report["metrics"]["with_memory_bank"]["first_action_error"])
        self.assertTrue(report["metrics"]["without_memory_bank"]["first_action_error"])
        self.assertEqual(100.0, report["metrics"]["delta"]["accuracy_gain_percent"])
        self.assertEqual(3, report["metrics"]["delta"]["clarification_reduction"])

    def test_sample_flag_writes_default_output(self):
        completed = subprocess.run(
            [sys.executable, str(QUICKSTART), "--sample"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )
        report = load_json(EXPERIMENT_ROOT / "output" / "sample.json")

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])

    def test_repeated_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp_name:
            first = Path(temp_name) / "first.json"
            second = Path(temp_name) / "second.json"

            first_run = self.run_quickstart(first)
            second_run = self.run_quickstart(second)
            first_digest = hashlib.sha256(first.read_bytes()).hexdigest()
            second_digest = hashlib.sha256(second.read_bytes()).hexdigest()

        self.assertEqual(0, first_run.returncode, first_run.stderr)
        self.assertEqual(0, second_run.returncode, second_run.stderr)
        self.assertEqual(first_digest, second_digest)

    def test_missing_input_returns_cli_error_without_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "missing.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(QUICKSTART),
                    "--input",
                    str(Path(temp_name) / "nope.json"),
                    "--output",
                    str(output),
                ],
                cwd=str(REPO_ROOT),
                text=True,
                capture_output=True,
            )

        self.assertEqual(1, completed.returncode)
        self.assertIn("[ERROR]", completed.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
