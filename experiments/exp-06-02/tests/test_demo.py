"""Executable contract tests for EXP-06-02."""

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

    def test_valid_sample_generates_chain_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(2, report["metrics"]["repair_round_count"])
        self.assertEqual(50.0, report["metrics"]["regression_pass_rate"])
        self.assertEqual(66.67, report["metrics"]["evidence_completeness_percent"])
        self.assertEqual(3, len(report["evidence_chain"]))
        self.assertEqual(
            ["FAIL-01", "FAIL-02", "FAIL-03"],
            [round_item["failure_id"] for round_item in report["evidence_chain"]],
        )

    def test_complete_round_has_chain_complete_code(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        first = report["evidence_chain"][0]
        self.assertEqual(0, completed.returncode)
        self.assertTrue(first["evidence_complete"])
        self.assertIn("CHAIN_COMPLETE", first["codes"])
        self.assertEqual("COMMIT-01", first["fix_commit"]["id"])
        self.assertEqual("TEST-01", first["retest"]["id"])

    def test_missing_fix_and_retest_codes(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        third = report["evidence_chain"][2]
        self.assertEqual(0, completed.returncode)
        self.assertFalse(third["evidence_complete"])
        self.assertIn("MISSING_FIX_COMMIT", third["codes"])
        self.assertIsNone(third["fix_commit"])
        self.assertIsNone(third["retest"])

    def test_implicit_commit_links_after_failure_timestamp(self):
        with tempfile.TemporaryDirectory() as temp_name:
            temp_root = Path(temp_name)
            input_path = temp_root / "input.json"
            output = temp_root / "report.json"
            data = {
                "experiment_id": "EXP-06-02",
                "failures": [
                    {
                        "id": "FAIL-01",
                        "summary": "单失败",
                        "timestamp": "2026-07-20T10:00:00Z",
                    }
                ],
                "commits": [
                    {
                        "id": "COMMIT-01",
                        "message": "隐式绑定",
                        "timestamp": "2026-07-20T10:30:00Z",
                    }
                ],
                "tests": [
                    {
                        "id": "TEST-01",
                        "failure_id": "FAIL-01",
                        "passed": True,
                        "timestamp": "2026-07-20T11:00:00Z",
                    }
                ],
            }
            input_path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
            completed = self.run_quickstart(input_path, output)
            report = load_json(output)

        round_item = report["evidence_chain"][0]
        self.assertEqual(0, completed.returncode)
        self.assertEqual("COMMIT-01", round_item["fix_commit"]["id"])
        self.assertTrue(round_item["evidence_complete"])
        self.assertEqual(100.0, report["metrics"]["evidence_completeness_percent"])

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
            "invalid-json.json": "E_INVALID_JSON",
            "missing-failures.json": "E_REQUIRED_FIELD",
            "duplicate-failure-id.json": "E_DUPLICATE_ID",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
            "unknown-failure-reference.json": "E_UNKNOWN_FAILURE_ID",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, error_code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.output.json"
                    completed = self.run_quickstart(
                        INVALID_ROOT / filename, output
                    )
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[ERROR {error_code}]", completed.stderr)
                    self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
