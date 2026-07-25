"""Executable contract tests for EXP-08-01."""

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

    def test_valid_sample_passes_source_and_asset_checks(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode, completed.stderr)
        self.assertTrue(report["valid"])
        self.assertEqual(100.0, report["metrics"]["source_completeness_percent"])
        self.assertEqual(0, report["metrics"]["hash_mismatch_count"])
        self.assertEqual(2, report["summary"]["present_required_asset_count"])
        self.assertIn("limitation", report)

    def test_manifest_assets_sorted_by_name(self):
        with tempfile.TemporaryDirectory() as temp_name:
            output = Path(temp_name) / "report.json"
            completed = self.run_quickstart(VALID_INPUT, output)
            report = load_json(output)

        self.assertEqual(0, completed.returncode)
        names = [item["name"] for item in report["manifest_assets"]]
        self.assertEqual(["release-manifest.json", "site.zip"], names)

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
            "source-mismatch.json": "E_SOURCE_MISMATCH",
            "missing-asset.json": "E_MISSING_ASSET",
            "bad-hash.json": "E_INVALID_HASH",
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
