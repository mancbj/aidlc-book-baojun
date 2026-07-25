"""Executable contract tests for EXP-01-02."""

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
EXPERIMENT_ID = "EXP-01-02"


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

    def test_valid_sample_generates_comparison_and_metrics(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual(9, report["metrics"]["ai_assisted"]["human_roundtrips"])
        self.assertEqual(4, report["metrics"]["ai_driven"]["human_roundtrips"])
        self.assertEqual(-5, report["metrics"]["delta"]["human_roundtrip_delta"])
        self.assertEqual(-2, report["metrics"]["delta"]["escaped_defect_delta"])
        self.assertEqual(44.0, report["metrics"]["delta"]["end_to_end_minutes_delta"])
        self.assertEqual(2, report["comparison"]["ai_assisted"]["evidence_link_count"])
        self.assertEqual(5, report["comparison"]["ai_driven"]["evidence_link_count"])
        self.assertIn("不证明", report["limitation"])

    def test_comparison_preserves_evidence_links(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        driven_links = report["comparison"]["ai_driven"]["evidence_links"]
        self.assertIn("progress/tasks.json#D12-T03", driven_links)
        self.assertIn("progress/events.jsonl#evt-20260721-complete", driven_links)

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

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "wrong-experiment-id.json": "E_EXPERIMENT_ID",
            "missing-workflow-mode.json": "E_REQUIRED_COLLECTION",
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
