"""Tests for the repository fact-source validator."""

import importlib.util
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "validate_project.py"
SPEC = importlib.util.spec_from_file_location("validate_project", MODULE_PATH)
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = VALIDATOR
SPEC.loader.exec_module(VALIDATOR)


TIMESTAMP = "2026-07-21T07:14:12Z"


def valid_task(task_id="D01-T01"):
    return {
        "id": task_id,
        "title": "示例任务",
        "type": "writing",
        "phase": "foundation",
        "status": "ready",
        "priority": "must",
        "owner": "author",
        "day": int(task_id[1:3]),
        "planned_date": "2026-07-21",
        "dependencies": [],
        "artifacts": [{"path": "README.md", "required": True}],
        "acceptance": [{"text": "示例验收", "passed": False}],
        "blocker_reason": "",
        "unblock_action": "",
        "updated": TIMESTAMP,
    }


def valid_chapter():
    return {
        "id": "CH-01",
        "number": 1,
        "title": "示例章",
        "question": "唯一问题是什么？",
        "reader_outcome": "读者可以完成一个动作",
        "stages": [
            {"name": name, "status": "pending"}
            for name in VALIDATOR.CHAPTER_STAGE_NAMES
        ],
        "evidence_links": [],
        "updated": TIMESTAMP,
    }


def valid_ship():
    return {
        "id": "EXP-01-01",
        "name": "仓库实验",
        "chapter": "CH-01",
        "triage": "SHIP",
        "effort": "S",
        "inputs": ["input"],
        "outputs": ["output"],
        "metrics": ["metric"],
        "command": "python3 quickstart.py",
        "acceptance": ["生成输出"],
        "status": "planned",
        "updated": TIMESTAMP,
        "repository_path": "experiments/exp-01-01",
        "readme_path": "experiments/exp-01-01/README.md",
        "sample_input": "experiments/exp-01-01/input.json",
        "sample_output": "experiments/exp-01-01/output.json",
        "test_path": "experiments/exp-01-01/test_demo.py",
    }


def valid_keep_ext():
    return {
        "id": "EXP-01-02",
        "name": "外部实验",
        "chapter": "CH-01",
        "triage": "KEEP-EXT",
        "effort": "M",
        "inputs": ["input"],
        "outputs": ["output"],
        "metrics": ["metric"],
        "command": "See reproduction_steps",
        "acceptance": ["复现输出"],
        "status": "planned",
        "updated": TIMESTAMP,
        "external_source": "https://example.com/docs",
        "pinned_version": "snapshot-1",
        "configuration": "config.example",
        "reproduction_steps": ["step 1"],
        "sample_result": "sample-result.md",
    }


def valid_already():
    return {
        "id": "EXP-01-03",
        "name": "复用实验",
        "chapter": "CH-01",
        "triage": "ALREADY",
        "effort": "S",
        "inputs": ["input"],
        "outputs": ["output"],
        "metrics": ["metric"],
        "command": "open existing.html",
        "acceptance": ["打开现有实现"],
        "status": "ready",
        "updated": TIMESTAMP,
        "reused_implementation": "existing.html",
        "cross_chapter_references": ["CH-01"],
    }


class ValidatorTestCase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "progress").mkdir()
        self.documents = {
            "tasks.json": {
                "schema_version": "1.0.0",
                "updated": TIMESTAMP,
                "tasks": [valid_task()],
            },
            "chapters.json": {
                "schema_version": "1.0.0",
                "updated": TIMESTAMP,
                "chapters": [valid_chapter()],
            },
            "experiments.json": {
                "schema_version": "1.0.0",
                "updated": TIMESTAMP,
                "experiments": [
                    valid_ship(),
                    valid_keep_ext(),
                    valid_already(),
                ],
            },
        }
        self.write_documents()

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_documents(self):
        for filename, document in self.documents.items():
            path = self.root / "progress" / filename
            path.write_text(
                json.dumps(document, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def report(self):
        self.write_documents()
        return VALIDATOR.run_validation(self.root)

    def assert_error_field(self, report, field):
        self.assertIn(field, {issue.field for issue in report.errors})

    def test_valid_documents_pass(self):
        report = self.report()

        self.assertTrue(report.ok)
        self.assertEqual(1, report.task_count)
        self.assertEqual(1, report.chapter_count)
        self.assertEqual(3, report.experiment_count)

    def test_duplicate_task_id_fails(self):
        self.documents["tasks.json"]["tasks"].append(valid_task())

        report = self.report()

        self.assert_error_field(report, "id")

    def test_broken_dependency_link_fails(self):
        self.documents["tasks.json"]["tasks"][0]["dependencies"] = ["D14-T99"]

        report = self.report()

        self.assert_error_field(report, "dependencies")

    def test_dependency_cycle_fails_with_chain(self):
        first = self.documents["tasks.json"]["tasks"][0]
        second = valid_task("D01-T02")
        first["dependencies"] = ["D01-T02"]
        second["dependencies"] = ["D01-T01"]
        self.documents["tasks.json"]["tasks"].append(second)

        report = self.report()

        cycles = [
            issue for issue in report.errors
            if issue.field == "dependencies" and "循环" in issue.message
        ]
        self.assertEqual(1, len(cycles))
        self.assertIn("D01-T01", str(cycles[0].value))
        self.assertIn("D01-T02", str(cycles[0].value))

    def test_illegal_task_status_fails(self):
        self.documents["tasks.json"]["tasks"][0]["status"] = "started"

        report = self.report()

        self.assert_error_field(report, "status")

    def test_blocked_task_requires_reason_and_action(self):
        task = self.documents["tasks.json"]["tasks"][0]
        task["status"] = "blocked"
        task["blocker_reason"] = ""
        task["unblock_action"] = ""

        report = self.report()

        fields = {issue.field for issue in report.errors}
        self.assertIn("blocker_reason", fields)
        self.assertIn("unblock_action", fields)

    def test_false_done_task_requires_acceptance_and_artifact(self):
        task = self.documents["tasks.json"]["tasks"][0]
        task["status"] = "done"
        task["acceptance"][0]["passed"] = False
        task["artifacts"][0]["path"] = "missing.md"

        report = self.report()

        fields = {issue.field for issue in report.errors}
        self.assertIn("acceptance", fields)
        self.assertIn("artifacts", fields)

    def test_false_done_task_rejects_unfinished_dependency(self):
        dependency = self.documents["tasks.json"]["tasks"][0]
        completed = valid_task("D01-T02")
        completed["status"] = "done"
        completed["dependencies"] = [dependency["id"]]
        completed["artifacts"] = [
            {"path": "progress/tasks.json", "required": True}
        ]
        completed["acceptance"][0]["passed"] = True
        self.documents["tasks.json"]["tasks"].append(completed)

        report = self.report()

        issues = [
            issue for issue in report.errors
            if issue.object_id == completed["id"]
            and issue.field == "dependencies"
            and "未完成" in issue.message
        ]
        self.assertEqual(1, len(issues))

    def test_timestamp_without_timezone_fails(self):
        self.documents["tasks.json"]["tasks"][0]["updated"] = (
            "2026-07-21T07:14:12"
        )

        report = self.report()

        self.assert_error_field(report, "updated")

    def test_document_timestamp_without_timezone_fails(self):
        self.documents["tasks.json"]["updated"] = "2026-07-21T07:14:12"

        report = self.report()

        issues = [
            issue for issue in report.errors
            if issue.source == "progress/tasks.json"
            and issue.object_id == "document"
            and issue.field == "updated"
        ]
        self.assertEqual(1, len(issues))

    def test_chapter_next_gap_returns_first_unfinished_stage(self):
        chapter = valid_chapter()
        chapter["stages"][0]["status"] = "done"
        chapter["stages"][1]["status"] = "done"

        self.assertEqual("example", VALIDATOR.chapter_next_gap(chapter))

        for stage in chapter["stages"]:
            stage["status"] = "done"
        self.assertIsNone(VALIDATOR.chapter_next_gap(chapter))

    def test_chapter_stage_order_is_fixed(self):
        chapter = self.documents["chapters.json"]["chapters"][0]
        chapter["stages"][0], chapter["stages"][1] = (
            chapter["stages"][1],
            chapter["stages"][0],
        )

        report = self.report()

        self.assert_error_field(report, "stages")

    def test_each_experiment_triage_requires_conditional_fields(self):
        triage_fields = {
            "SHIP": "repository_path",
            "KEEP-EXT": "external_source",
            "ALREADY": "reused_implementation",
        }
        originals = deepcopy(self.documents["experiments.json"]["experiments"])

        for index, (triage, field) in enumerate(triage_fields.items()):
            with self.subTest(triage=triage):
                experiments = deepcopy(originals)
                del experiments[index][field]
                self.documents["experiments.json"]["experiments"] = experiments

                report = self.report()

                self.assert_error_field(report, field)


if __name__ == "__main__":
    unittest.main()
