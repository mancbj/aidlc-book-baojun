"""Tests for the verified SHIP experiment CI gate."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "run_verified_experiments.py"
SPEC = importlib.util.spec_from_file_location("run_verified_experiments", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class VerifiedExperimentGateTest(unittest.TestCase):
    def test_filters_only_verified_ship(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "progress").mkdir()
            (root / "progress/experiments.json").write_text(
                json.dumps(
                    {
                        "experiments": [
                            {
                                "id": "EXP-01",
                                "triage": "SHIP",
                                "status": "verified",
                                "repository_path": "experiments/exp-01",
                                "readme_path": "experiments/exp-01/README.md",
                                "sample_input": "experiments/exp-01/samples/input.json",
                                "sample_output": "experiments/exp-01/output/sample.json",
                                "test_path": "experiments/exp-01/tests/test_demo.py",
                            },
                            {"id": "EXP-02", "triage": "SHIP", "status": "planned"},
                            {
                                "id": "EXP-03",
                                "triage": "ALREADY",
                                "status": "verified",
                                "repository_path": "experiments/exp-03",
                                "readme_path": "experiments/exp-03/README.md",
                                "sample_input": "experiments/exp-03/samples/input.json",
                                "sample_output": "experiments/exp-03/output/sample.json",
                                "test_path": "experiments/exp-03/tests/test_demo.py",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )

            experiments = MODULE.verified_ship_experiments(root)

        self.assertEqual(["EXP-01"], [item["id"] for item in experiments])

    def test_contract_filter_includes_already_and_keepext_with_paths(self):
        paths = {
            "repository_path": "experiments/x",
            "readme_path": "experiments/x/README.md",
            "sample_input": "experiments/x/samples/input.json",
            "sample_output": "experiments/x/output/sample.json",
            "test_path": "experiments/x/tests/test_demo.py",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "progress").mkdir()
            (root / "progress/experiments.json").write_text(
                json.dumps(
                    {
                        "experiments": [
                            {"id": "EXP-SHIP", "triage": "SHIP", "status": "verified", **paths},
                            {"id": "EXP-ALREADY", "triage": "ALREADY", "status": "verified", **paths},
                            {"id": "EXP-KEEP", "triage": "KEEP-EXT", "status": "verified", **paths},
                            {"id": "EXP-ALREADY-BARE", "triage": "ALREADY", "status": "verified"},
                        ]
                    }
                ),
                encoding="utf-8",
            )
            experiments = MODULE.verified_contract_experiments(root)
        self.assertEqual(
            ["EXP-SHIP", "EXP-ALREADY", "EXP-KEEP"],
            [item["id"] for item in experiments],
        )

    def test_artifact_errors_report_missing_paths(self):
        experiment = {
            "id": "EXP-01",
            "repository_path": "experiments/exp-01",
            "readme_path": "experiments/exp-01/README.md",
            "sample_input": "experiments/exp-01/samples/input.json",
            "sample_output": "experiments/exp-01/output/sample.json",
            "test_path": "experiments/exp-01/tests/test_demo.py",
        }
        with tempfile.TemporaryDirectory() as directory:
            errors = MODULE.artifact_errors(Path(directory), experiment)

        self.assertEqual(5, len(errors))
        self.assertTrue(all("EXP-01" in error for error in errors))

    def test_artifact_errors_accept_complete_contract(self):
        experiment = {
            "id": "EXP-01",
            "repository_path": "experiments/exp-01",
            "readme_path": "experiments/exp-01/README.md",
            "sample_input": "experiments/exp-01/samples/input.json",
            "sample_output": "experiments/exp-01/output/sample.json",
            "test_path": "experiments/exp-01/tests/test_demo.py",
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "experiments/exp-01/samples").mkdir(parents=True)
            (root / "experiments/exp-01/output").mkdir()
            (root / "experiments/exp-01/tests").mkdir()
            for relative in (
                "experiments/exp-01/README.md",
                "experiments/exp-01/samples/input.json",
                "experiments/exp-01/output/sample.json",
                "experiments/exp-01/tests/test_demo.py",
            ):
                (root / relative).write_text("x", encoding="utf-8")

            errors = MODULE.artifact_errors(root, experiment)

        self.assertEqual([], errors)


if __name__ == "__main__":
    unittest.main()
