"""Executable contract tests for EXP-09-02."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ID = "EXP-09-02"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
QUICKSTART = EXPERIMENT_ROOT / "quickstart.py"
VALID_INPUT = EXPERIMENT_ROOT / "samples" / "input.json"
INVALID_ROOT = EXPERIMENT_ROOT / "samples" / "invalid"


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

    def test_valid_sample_budget_covers_critical_with_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual(3, report["checkpoint_count"])
        self.assertEqual(100.0, report["metrics"]["critical_risk_coverage_percent"])
        self.assertEqual(1, report["metrics"]["nonessential_checkpoint_count"])
        self.assertEqual(4.25, report["metrics"]["estimated_review_cost"])
        self.assertEqual(4.25, report["cost_benefit_estimate"]["estimated_review_cost_hours"])
        self.assertIn("R-CP-MANDATORY-CRITICAL", report["fired_rule_ids"])
        self.assertIn("被预算公式穷尽", report["limitation"])

        phases = [item["phase"] for item in report["checkpoint_placements"]]
        self.assertEqual(["implement", "verify", "release"], phases)

    def test_cost_benefit_ratio_matches_reduction_over_cost(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        estimate = report["cost_benefit_estimate"]
        self.assertEqual(5.0, estimate["estimated_risk_reduction_score"])
        self.assertEqual(
            round(estimate["estimated_risk_reduction_score"] / estimate["estimated_review_cost_hours"], 2),
            estimate["benefit_cost_ratio"],
        )
        self.assertEqual(1.18, estimate["benefit_cost_ratio"])

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
            "missing-reversibility.json": "E_INVALID_ENUM",
            "invalid-severity.json": "E_INVALID_ENUM",
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
