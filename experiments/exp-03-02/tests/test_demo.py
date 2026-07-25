"""Executable contract tests for EXP-03-02."""

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
INVALID_DIR = EXPERIMENT_ROOT / "samples" / "invalid"


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
        )

    def test_valid_sample_reports_graph_metrics_and_warnings(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "sample.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["structural_valid"])
        self.assertFalse(report["plan_optimal"])
        self.assertEqual(
            {
                "cycle_count": 0,
                "cross_unit_coupling_edge_count": 1,
                "unmet_prerequisite_count": 1,
            },
            report["metrics"],
        )
        codes = {item["code"] for item in report["anomalies"]}
        self.assertIn("W_CROSS_UNIT_COUPLING", codes)
        self.assertIn("W_UNMET_PREREQUISITE", codes)
        self.assertEqual(2, len(report["dependency_graph"]["edges"]))
        self.assertEqual(3, len(report["dependency_graph"]["nodes"]))

    def test_invalid_samples_return_stable_error_codes(self):
        fixtures = {
            "cycle.json": "E_CYCLE",
            "duplicate-id.json": "E_DUPLICATE_ID",
            "unknown-bolt.json": "E_UNKNOWN_BOLT",
            "unknown-unit.json": "E_UNKNOWN_UNIT",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, expected_code in fixtures.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.out.json"
                    completed = self.run_quickstart(INVALID_DIR / filename, output)
                    report = load_json(output)
                    self.assertEqual(2, completed.returncode, completed.stderr)
                    self.assertFalse(report["structural_valid"])
                    self.assertIn(
                        expected_code,
                        {item["code"] for item in report["anomalies"]},
                    )

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

    def test_sample_flag_writes_default_output(self):
        completed = subprocess.run(
            [sys.executable, str(QUICKSTART), "--sample"],
            cwd=str(REPO_ROOT),
            text=True,
            capture_output=True,
        )
        output = EXPERIMENT_ROOT / "output" / "sample.json"
        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(output.is_file())
        report = load_json(output)
        self.assertEqual("EXP-03-02", report["experiment_id"])

    def test_missing_input_returns_cli_error_without_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "missing.json"
            completed = self.run_quickstart(Path(temp_name) / "nope.json", output)
        self.assertEqual(1, completed.returncode)
        self.assertIn("[ERROR]", completed.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
