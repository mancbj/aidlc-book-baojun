"""Executable contract tests for EXP-02-01."""

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

    def test_valid_sample_generates_checklist_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(6, len(report["human_judgment_checkpoints"]))
        self.assertEqual(100.0, report["metrics"]["judgment_point_coverage_percent"])
        self.assertEqual(1, report["metrics"]["unassigned_responsibility_count"])
        self.assertIn("不证明已覆盖", report["limitation"])
        self.assertEqual(
            ["CONSTRAINT_EXCEPTION", "GOAL_APPROVAL", "RISK_ACCEPTANCE"],
            report["coverage_basis"],
        )

    def test_boundaries_connect_roles_to_checkpoints(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        boundaries = {
            item["role"]["id"]: item["accountable_checkpoint_ids"]
            for item in report["responsibility_boundaries"]
        }
        self.assertEqual(["J-001", "J-002"], boundaries["product_owner"])
        unassigned = [
            item
            for item in report["human_judgment_checkpoints"]
            if item["responsibility_status"] == "unassigned"
        ]
        self.assertEqual(["R-02"], [item["source"]["id"] for item in unassigned])

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
        self.assertEqual(EXPERIMENT_ROOT / "output" / "sample.json", Path(completed.stdout.strip().split(": ", 1)[1]))
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "missing-goals.json": "E_REQUIRED_COLLECTION",
            "unknown-role.json": "E_UNKNOWN_ROLE",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, code in cases.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.out"
                    completed = self.run_case(INVALID_ROOT / filename, output)
                    self.assertEqual(1, completed.returncode)
                    self.assertIn(f"[ERROR {code}]", completed.stderr)
                    self.assertFalse(output.exists())


EXPERIMENT_ID = "EXP-02-01"


if __name__ == "__main__":
    unittest.main()
