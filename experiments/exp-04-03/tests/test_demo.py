"""Executable contract tests for EXP-04-03."""

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
    def run_quickstart(self, input_path: Path, output_path: Path) -> subprocess.CompletedProcess[str]:
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

    def test_valid_sample_reports_full_structure_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertTrue(report["loadable_minimal_memory_bank"])
        self.assertEqual(100.0, report["metrics"]["required_file_completeness_percent"])
        self.assertEqual(100.0, report["metrics"]["reference_validity_percent"])
        self.assertEqual([], report["required_path_check"]["missing"])
        self.assertIn("不验证实时 specs.md", report["limitation"])

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
        self.assertEqual("EXP-04-03", report["experiment_id"])

    def test_repeated_runs_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp_name:
            first = Path(temp_name) / "first.json"
            second = Path(temp_name) / "second.json"
            first_run = self.run_quickstart(VALID_INPUT, first)
            second_run = self.run_quickstart(VALID_INPUT, second)

            self.assertEqual(0, first_run.returncode, first_run.stderr)
            self.assertEqual(0, second_run.returncode, second_run.stderr)
            self.assertEqual(
                hashlib.sha256(first.read_bytes()).hexdigest(),
                hashlib.sha256(second.read_bytes()).hexdigest(),
            )

    def test_invalid_samples_return_stable_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_JSON_INVALID",
            "wrong-schema-version.json": "E_SCHEMA_VERSION",
            "pin-mismatch.json": "E_PIN_MISMATCH",
            "missing-bank-root.json": "E_BANK_ROOT",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.output"
                    completed = self.run_quickstart(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[{code}]", completed.stderr)
                    self.assertFalse(output.exists())

    def test_missing_required_path_lowers_completeness(self):
        data = load_json(VALID_INPUT)
        data["required_paths"] = list(data["required_paths"]) + ["intents/001-demo-intent/missing.md"]
        with tempfile.TemporaryDirectory() as temp_name:
            input_path = Path(temp_name) / "input.json"
            output = Path(temp_name) / "output.json"
            input_path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
            completed = self.run_quickstart(input_path, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertFalse(report["valid"])
        self.assertLess(report["metrics"]["required_file_completeness_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
