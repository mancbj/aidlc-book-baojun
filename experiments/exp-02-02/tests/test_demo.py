"""Executable contract tests for EXP-02-02."""

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
INVALID_ROOT = EXPERIMENT_ROOT / "samples" / "invalid"
EXPERIMENT_ID = "EXP-02-02"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class QuickstartContractTest(unittest.TestCase):
    def run_case(self, input_path: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(QUICKSTART),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
            ],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )

    def test_valid_sample_generates_logs_diff_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual(1, len(report["decision_log_by_arm"]["no_clarify"]))
        self.assertEqual(4, len(report["decision_log_by_arm"]["with_clarify"]))
        no_metrics = report["metrics"]["by_arm"]["no_clarify"]
        with_metrics = report["metrics"]["by_arm"]["with_clarify"]
        self.assertEqual(0, no_metrics["clarification_rounds"])
        self.assertEqual(3, with_metrics["clarification_rounds"])
        self.assertEqual(4, no_metrics["post_impl_requirement_change_count"])
        self.assertEqual(5, with_metrics["post_impl_requirement_change_count"])
        self.assertEqual(3, no_metrics["critical_omission_count"])
        self.assertEqual(1, with_metrics["critical_omission_count"])
        delta = report["metrics"]["delta_no_clarify_minus_with_clarify"]
        self.assertEqual(-1, delta["post_impl_requirement_change_count"])
        self.assertEqual(2, delta["critical_omission_count"])
        self.assertIn("不证明澄清", report["limitation"])

    def test_implementation_difference_report_splits_arms(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        diff = report["implementation_difference_report"]
        self.assertEqual([], diff["shared_implementations"])
        self.assertEqual(
            {"I-N-01", "I-N-02", "I-N-03"},
            {item["id"] for item in diff["no_clarify_only"]},
        )
        self.assertEqual(
            {"I-W-01", "I-W-02", "I-W-03", "I-W-04", "I-W-05"},
            {item["id"] for item in diff["with_clarify_only"]},
        )
        self.assertEqual(8, diff["unique_implementation_count"])

    def test_repeated_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp_name:
            first = Path(temp_name) / "first.json"
            second = Path(temp_name) / "second.json"
            first_run = self.run_case(VALID_INPUT, first)
            second_run = self.run_case(VALID_INPUT, second)

            self.assertEqual(0, first_run.returncode, first_run.stderr)
            self.assertEqual(0, second_run.returncode, second_run.stderr)
            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )

    def test_sample_flag_writes_default_output(self):
        completed = subprocess.run(
            [sys.executable, str(QUICKSTART), "--sample"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )
        report = load_json(EXPERIMENT_ROOT / "output" / "sample.json")

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            EXPERIMENT_ROOT / "output" / "sample.json",
            Path(completed.stdout.strip().split(": ", 1)[1]),
        )
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "missing-with-clarify-arm.json": "E_MISSING_SESSION_ARM",
            "invalid-clarification-rounds.json": "E_INVALID_CLARIFICATION_ROUNDS",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.out"
                    completed = self.run_case(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[ERROR {code}]", completed.stderr)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
