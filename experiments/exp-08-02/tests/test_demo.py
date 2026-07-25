"""Executable contract tests for EXP-08-02."""

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

    def test_valid_sample_generates_timeline_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(10.5, report["metrics"]["detect_to_rollback_minutes"])
        self.assertEqual(25.0, report["metrics"]["data_loss_window_minutes"])
        self.assertEqual(1, report["metrics"]["runbook_gap_count"])
        self.assertEqual(
            ["detect", "decide", "rollback", "recover"],
            [item["phase"] for item in report["drill_timeline"]],
        )

    def test_detect_anchored_on_earliest_monitoring_signal(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        detect = report["drill_timeline"][0]
        self.assertEqual(0, completed.returncode)
        self.assertEqual("detect", detect["phase"])
        self.assertEqual(["MON-01", "MON-02"], detect["monitoring_signal_ids"])
        self.assertIn("DETECT_FROM_MONITORING", detect["codes"])
        self.assertEqual("2026-07-22T14:06:30Z", detect["started_at"])

    def test_runbook_gap_lists_uncovered_worker_component(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode)
        self.assertEqual(1, len(report["runbook_gaps"]))
        self.assertEqual("UNCOVERED_AFFECTED_COMPONENT", report["runbook_gaps"][0]["code"])

    def test_data_impact_false_yields_null_loss_window(self):
        with tempfile.TemporaryDirectory() as temp_name:
            temp_root = Path(temp_name)
            input_path = temp_root / "input.json"
            output = temp_root / "report.json"
            data = load_json(VALID_INPUT)
            data["fault_scenario"]["data_impact"] = False
            input_path.write_text(
                json.dumps(data, ensure_ascii=False, sort_keys=True), encoding="utf-8"
            )
            completed = self.run_quickstart(input_path, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode)
        self.assertIsNone(report["metrics"]["data_loss_window_minutes"])

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
            "missing-fault-scenario.json": "E_REQUIRED_FIELD",
            "duplicate-signal-id.json": "E_DUPLICATE_ID",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
            "unknown-fault-reference.json": "E_UNKNOWN_FAULT_ID",
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
