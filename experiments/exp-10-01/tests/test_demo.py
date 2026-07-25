"""Executable contract tests for EXP-10-01."""

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
EXPERIMENT_ID = "EXP-10-01"


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

    def test_valid_sample_generates_raci_matrix_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(6, len(report["raci_matrix"]))
        self.assertEqual(1, report["metrics"]["unassigned_accountable_decisions_count"])
        self.assertEqual(1, report["metrics"]["responsibility_conflict_count"])
        self.assertIn("不得为 Agent", report["accountable_rule"])
        self.assertIn("不证明", report["limitation"])
        self.assertEqual(
            sorted(
                [
                    "BOLT_EXECUTION",
                    "INDEPENDENT_REVIEW",
                    "INTENT_DECOMPOSITION",
                    "RELEASE_ROLLBACK",
                    "STAGE_ROUTING",
                ]
            ),
            report["pattern_basis"],
        )

    def test_accountable_is_never_agent_in_output(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        for row in report["raci_matrix"]:
            for cell in row["assignments"]:
                if "A" in cell["letters"]:
                    self.assertEqual("human", cell["participant"]["kind"])
            for agent_cell in row["assignments"]:
                if agent_cell["participant"]["kind"] == "agent":
                    self.assertNotIn("A", agent_cell["letters"])

    def test_sample_exercises_unassigned_and_conflict_rows(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        by_id = {row["activity"]["id"]: row for row in report["raci_matrix"]}
        self.assertEqual("unassigned", by_id["ACT-06"]["accountable_status"])
        self.assertEqual(["MISSING_ACCOUNTABLE"], by_id["ACT-06"]["conflict_codes"])
        self.assertEqual("conflict", by_id["ACT-05"]["accountable_status"])
        self.assertEqual(["MULTIPLE_ACCOUNTABLE"], by_id["ACT-05"]["conflict_codes"])

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
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "missing-activities.json": "E_REQUIRED_COLLECTION",
            "unknown-role.json": "E_UNKNOWN_ROLE",
            "agent-accountable.json": "E_ACCOUNTABLE_AGENT",
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
