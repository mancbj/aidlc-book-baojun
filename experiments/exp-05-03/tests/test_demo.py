"""Executable contract tests for EXP-05-03."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


EXPERIMENT_ID = "EXP-05-03"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = EXPERIMENT_ROOT.parents[1]
QUICKSTART = EXPERIMENT_ROOT / "quickstart.py"
VALID_INPUT = EXPERIMENT_ROOT / "samples" / "input.json"
INVALID_ROOT = EXPERIMENT_ROOT / "samples" / "invalid"
EXPECTED_PIN = (
    "sha256:32d73fc5231f81eabaf9c881e1c64f3353882c605c729bfbbca9f5bb4aa0b481"
)


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

    def test_valid_sample_reports_full_adherence(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_case(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(EXPERIMENT_ID, report["experiment_id"])
        self.assertEqual(EXPECTED_PIN, report["pinned_version"])
        self.assertEqual(100.0, report["metrics"]["stage_completeness_percent"])
        self.assertEqual(100.0, report["metrics"]["checkpoint_adherence_percent"])
        self.assertEqual(100.0, report["tracks"]["simple"]["stage_completeness_percent"])
        self.assertEqual(100.0, report["tracks"]["ddd"]["stage_completeness_percent"])
        self.assertIn("不能替代人工 Bolt 类型选择", report["limitation"])
        self.assertTrue(report["guide_digest"].startswith("sha256:"))

    def test_partial_simple_track_lowers_overall_metrics(self):
        payload = load_json(VALID_INPUT)
        payload["stage_records"]["simple"]["stages"] = payload["stage_records"]["simple"][
            "stages"
        ][:2]
        with tempfile.TemporaryDirectory() as temp_name:
            input_path = Path(temp_name) / "input.json"
            output_path = Path(temp_name) / "output.json"
            input_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            completed = self.run_case(input_path, output_path)
            report = load_json(output_path)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertEqual(
            round(100.0 * 2 / 3, 2),
            report["tracks"]["simple"]["stage_completeness_percent"],
        )
        self.assertLess(report["metrics"]["stage_completeness_percent"], 100.0)

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
        self.assertEqual(100.0, report["metrics"]["checkpoint_adherence_percent"])

    def test_invalid_samples_return_stable_error_codes_without_output(self):
        cases = {
            "malformed-json.json": "E_INVALID_JSON",
            "pin-mismatch.json": "E_PIN_MISMATCH",
            "missing-track-ddd.json": "E_MISSING_TRACK",
            "unknown-stage-simple.json": "E_UNKNOWN_STAGE",
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
