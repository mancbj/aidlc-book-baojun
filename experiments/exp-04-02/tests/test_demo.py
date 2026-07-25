"""Executable contract tests for EXP-04-02."""

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

    def test_valid_sample_reports_violations_diffs_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertFalse(report["compliant"])
        self.assertEqual(
            [
                "STD-EVIDENCE:release-manifest:evidence",
                "STD-STATUS:release-manifest:status",
            ],
            [item["key"] for item in report["violations"]],
        )
        self.assertEqual(["STD-EVIDENCE"], report["version_diff"]["standards"]["rules"]["added"])
        self.assertEqual(["STD-STATUS"], report["version_diff"]["standards"]["rules"]["changed"])
        self.assertEqual(100.0, report["metrics"]["rule_coverage_percent"])
        self.assertEqual(0.0, report["metrics"]["false_positive_rate_percent"])
        self.assertEqual(2, report["metrics"]["drift_item_count"])
        self.assertIn("不证明", report["disclaimer"])

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
        self.assertEqual("EXP-04-02", report["experiment_id"])

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
            "unsupported-rule.json": "E_UNSUPPORTED_RULE",
            "duplicate-artifact.json": "E_DUPLICATE_ID",
            "wrong-schema-version.json": "E_SCHEMA_VERSION",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.output"
                    completed = self.run_quickstart(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[{code}]", completed.stderr)
                    self.assertFalse(output.exists())

    def test_false_positive_metric_uses_only_benchmark_labels(self):
        data = load_json(VALID_INPUT)
        data["benchmark"]["expected_violation_keys"] = [
            "STD-STATUS:release-manifest:status"
        ]
        with tempfile.TemporaryDirectory() as temp_name:
            input_path = Path(temp_name) / "input.json"
            output = Path(temp_name) / "output.json"
            input_path.write_text(json.dumps(data), encoding="utf-8")
            completed = self.run_quickstart(input_path, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertFalse(report["valid"])
        self.assertEqual(1, report["metrics"]["false_positive_count"])
        self.assertEqual(50.0, report["metrics"]["false_positive_rate_percent"])
        self.assertEqual(
            "仅基于输入 benchmark.expected_violation_keys 标注",
            report["benchmark_evaluation"]["basis"],
        )


if __name__ == "__main__":
    unittest.main()
