"""Executable contract tests for EXP-06-01."""

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

    def test_valid_sample_generates_required_table_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(100.0, report["metrics"]["deliverable_coverage_percent"])
        self.assertEqual(1, report["metrics"]["undeclared_change_count"])
        self.assertEqual(2, report["metrics"]["deviation_count"])
        self.assertEqual(0, report["metrics"]["failure_count"])
        self.assertEqual(5, len(report["audit_table"]))

    def test_undeclared_change_is_deviation_not_failure(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        row = next(
            item
            for item in report["audit_table"]
            if item["path"] == "config/example.json"
        )
        self.assertEqual(0, completed.returncode)
        self.assertEqual("deviation", row["classification"])
        self.assertIn("UNDECLARED_CHANGE", row["codes"])
        self.assertNotEqual("failure", row["classification"])

    def test_missing_planned_delivery_is_failure(self):
        with tempfile.TemporaryDirectory() as temp_name:
            temp_root = Path(temp_name)
            input_path = temp_root / "input.json"
            output = temp_root / "report.json"
            data = load_json(VALID_INPUT)
            data["actual_changes"] = [
                change
                for change in data["actual_changes"]
                if change["path"] != "src/audit.py"
            ]
            data["walkthrough"]["changes"] = [
                change
                for change in data["walkthrough"]["changes"]
                if change["path"] != "src/audit.py"
            ]
            input_path.write_text(
                json.dumps(data, ensure_ascii=False), encoding="utf-8"
            )
            completed = self.run_quickstart(input_path, output)
            report = load_json(output)

        self.assertEqual(2, completed.returncode)
        self.assertFalse(report["valid"])
        self.assertEqual(1, report["metrics"]["failure_count"])
        self.assertEqual(
            66.67, report["metrics"]["deliverable_coverage_percent"]
        )

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
            "missing-plan.json": "E_REQUIRED_FIELD",
            "duplicate-actual-path.json": "E_DUPLICATE_PATH",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
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
