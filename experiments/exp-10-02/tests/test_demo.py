"""Executable contract tests for EXP-10-02."""

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
EXPERIMENT_ID = "EXP-10-02"


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

    def test_valid_sample_generates_scorecard_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            {"cycle_time", "quality", "review_burden", "business_result"},
            set(report["scorecard"].keys()),
        )
        self.assertEqual(-20.83, report["metrics"]["cycle_time_change_percent"])
        self.assertEqual(0.25, report["metrics"]["defect_escape_rate"])
        self.assertEqual(1.3333, report["metrics"]["human_review_burden"])
        self.assertEqual(5.0, report["metrics"]["business_result_change"])
        self.assertEqual("shrink", report["scale_decision"]["decision"])
        self.assertIn("因果", report["limitation"])

    def test_scale_decision_lists_mixed_signals_on_sample(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        codes = set(report["scale_decision"]["reason_codes"])
        self.assertIn("EXPAND_CYCLE_IMPROVED", codes)
        self.assertIn("SHRINK_ELEVATED_DEFECT_ESCAPE", codes)
        self.assertIn("SHRINK_REVIEW_BURDEN_HIGH", codes)

    def test_business_null_rules_when_outcomes_omitted(self):
        base = load_json(VALID_INPUT)
        base.pop("business_outcomes")
        with tempfile.TemporaryDirectory() as temp_name:
            input_path = Path(temp_name) / "input.json"
            output = Path(temp_name) / "report.json"
            input_path.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
            completed = self.run_case(input_path, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIsNone(report["metrics"]["business_result_change"])
        self.assertEqual("not_provided", report["scorecard"]["business_result"]["status"])

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
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "missing-runs.json": "E_REQUIRED_COLLECTION",
            "unknown-run.json": "E_UNKNOWN_RUN",
            "invalid-baseline.json": "E_INVALID_NUMBER",
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
