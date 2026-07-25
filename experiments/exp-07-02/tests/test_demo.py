"""Executable contract tests for EXP-07-02."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ID = "EXP-07-02"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
QUICKSTART = EXPERIMENT_ROOT / "quickstart.py"
VALID_INPUT = EXPERIMENT_ROOT / "samples" / "input.json"
INVALID_ROOT = EXPERIMENT_ROOT / "samples" / "invalid"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class QuickstartContractTest(unittest.TestCase):
    def run_quickstart(
        self, input_path: Path, output_path: Path
    ) -> subprocess.CompletedProcess[str]:
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
            check=False,
        )

    def test_valid_sample_generates_matrix_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual("CAND-07-02-SAMPLE", report["delivery_candidate_id"])
        self.assertEqual(66.67, report["metrics"]["review_agreement_rate"])
        self.assertEqual(1, report["metrics"]["new_risk_count"])
        self.assertEqual(0.0, report["metrics"]["human_override_rate"])
        self.assertEqual(5, len(report["disagreement_matrix"]))
        self.assertIn("不证明模型评审可以替代人工判断", report["limitation"])
        self.assertEqual("CH-07 delivery candidate verification", report["verification_framing"])

    def test_rubric_row_captures_model_split(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        row = next(
            item for item in report["disagreement_matrix"] if item["dimension_id"] == "RB-002"
        )
        self.assertEqual(0, completed.returncode)
        self.assertFalse(row["aligned"])
        self.assertIn("MODEL_MODEL_DISAGREEMENT", row["attribution_codes"])
        self.assertEqual("pass", row["parties"]["test_evidence"]["signal"])
        self.assertEqual("fail", row["parties"]["MODEL-B"]["signal"])

    def test_new_risk_row_marked_and_counted(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        row = next(
            item for item in report["disagreement_matrix"] if item["dimension_id"] == "RISK-NEW-02"
        )
        self.assertEqual(0, completed.returncode)
        self.assertTrue(row["is_new_risk"])
        self.assertIn("MODEL_ONLY_RISK", row["attribution_codes"])
        self.assertIn("HUMAN_DEFERS_RISK", row["attribution_codes"])

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

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
            "missing-model-reviews.json": "E_REQUIRED_COLLECTION",
            "duplicate-reviewer-id.json": "E_DUPLICATE_ID",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, error_code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.output.json"
                    completed = self.run_quickstart(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[ERROR {error_code}]", completed.stderr)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
