"""Executable contract tests for EXP-09-01."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ID = "EXP-09-01"
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

    def test_valid_sample_recommends_fire_with_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual("FIRE", report["flow_recommendation"])
        self.assertGreaterEqual(len(report["reasons"]), 1)
        self.assertGreaterEqual(len(report["inapplicable_conditions"]), 1)
        self.assertEqual(100.0, report["metrics"]["expert_agreement_rate"])
        self.assertEqual(100.0, report["metrics"]["reason_completeness_rate"])
        self.assertIn("不构成强制选型法令", report["limitation"])
        self.assertIn("R-FIRE-BROWNFIELD", report["fired_rule_ids"])

    def test_inapplicable_conditions_cover_other_flows(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        flows = {item["flow"] for item in report["inapplicable_conditions"]}
        self.assertIn("Simple", flows)
        self.assertIn("AI-DLC", flows)

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

    def test_expert_agreement_null_without_label(self):
        payload = load_json(VALID_INPUT)
        payload.pop("expert_label", None)
        with tempfile.TemporaryDirectory() as temp_name:
            input_path = Path(temp_name) / "input.json"
            output_path = Path(temp_name) / "output.json"
            input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            completed = self.run_case(input_path, output_path)
            report = load_json(output_path)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertIsNone(report["metrics"]["expert_agreement_rate"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "missing-task-complexity.json": "E_INVALID_ENUM",
            "invalid-complexity.json": "E_INVALID_ENUM",
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
