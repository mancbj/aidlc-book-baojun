"""Executable contract tests for EXP-03-01."""

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

    def test_valid_sample_generates_success_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "sample.json"

            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual([], report["errors"])
        self.assertEqual(
            {
                "requirement_coverage_percent": 100.0,
                "orphan_story_count": 0,
                "acceptance_completeness_percent": 100.0,
                "invalid_reference_count": 0,
            },
            report["metrics"],
        )

    def test_invalid_samples_return_stable_error_codes(self):
        fixtures = {
            "missing-nfr.json": "E_MISSING_NFR",
            "duplicate-id.json": "E_DUPLICATE_ID",
            "unknown-reference.json": "E_UNKNOWN_REF",
            "orphan-story.json": "E_ORPHAN_STORY",
            "empty-acceptance.json": "E_ACCEPTANCE",
        }
        with tempfile.TemporaryDirectory() as temp_name:
            for filename, expected_code in fixtures.items():
                with self.subTest(filename=filename):
                    output = Path(temp_name) / f"{filename}.out.json"

                    completed = self.run_quickstart(INVALID_DIR / filename, output)
                    report = load_json(output)

                    self.assertEqual(2, completed.returncode, completed.stderr)
                    self.assertFalse(report["valid"])
                    self.assertIn(expected_code, {error["code"] for error in report["errors"]})

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

    def test_missing_input_returns_cli_error_without_report(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "missing.json"

            completed = self.run_quickstart(Path(temp_name) / "nope.json", output)

        self.assertEqual(1, completed.returncode)
        self.assertIn("[ERROR]", completed.stderr)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
