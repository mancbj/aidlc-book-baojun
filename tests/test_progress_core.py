"""Unit tests for deterministic aggregation and key-event detection."""

import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import progress_core as core  # noqa: E402


TIMESTAMP = "2026-07-21T07:14:12Z"


def task(
    task_id,
    day=1,
    status="ready",
    priority="must",
    dependencies=None,
    title=None,
):
    return {
        "id": task_id,
        "title": title or task_id,
        "type": "writing",
        "phase": "foundation",
        "status": status,
        "priority": priority,
        "owner": "author",
        "day": day,
        "planned_date": f"2026-07-{20 + day:02d}",
        "dependencies": dependencies or [],
        "artifacts": [{"path": "README.md", "required": True}],
        "acceptance": [{"text": "完成", "passed": status == "done"}],
        "blocker_reason": "等待输入" if status == "blocked" else "",
        "unblock_action": "补充输入" if status == "blocked" else "",
        "updated": TIMESTAMP,
    }


def chapter(stage_statuses=None):
    statuses = stage_statuses or ["pending"] * 6
    return {
        "id": "CH-01",
        "number": 1,
        "title": "示例章",
        "question": "问题是什么？",
        "reader_outcome": "完成动作",
        "stages": [
            {"name": name, "status": status}
            for name, status in zip(core.CHAPTER_STAGE_NAMES, statuses)
        ],
        "evidence_links": [],
        "updated": TIMESTAMP,
    }


def experiment(status="planned", triage="SHIP"):
    return {
        "id": "EXP-01-01",
        "name": "示例实验",
        "chapter": "CH-01",
        "triage": triage,
        "effort": "S",
        "status": status,
        "updated": TIMESTAMP,
    }


def facts(tasks=None, chapters=None, experiments=None):
    return {
        "tasks": {"updated": TIMESTAMP, "tasks": tasks or []},
        "chapters": {"updated": TIMESTAMP, "chapters": chapters or []},
        "experiments": {"updated": TIMESTAMP, "experiments": experiments or []},
    }


class AggregateProgressTests(unittest.TestCase):
    def aggregate(self, value, generated_at="2026-07-22T01:00:00Z"):
        return core.aggregate_progress(value, "source-1", generated_at)

    def test_empty_tasks_are_zero_and_prompt_initialization(self):
        result = self.aggregate(facts())

        self.assertEqual(0.0, result["tasks"]["percent"])
        self.assertEqual(0.0, result["tasks"]["weighted_percent"])
        self.assertEqual([], result["next_actions"])
        self.assertIn("初始化", result["release_message"])

    def test_total_priority_and_weighted_percentages(self):
        value = facts(
            tasks=[
                task("D01-T01", status="done", priority="must"),
                task("D01-T02", status="ready", priority="must"),
                task("D01-T03", status="done", priority="should"),
                task("D01-T04", status="ready", priority="could"),
            ]
        )

        result = self.aggregate(value)

        self.assertEqual(50.0, result["tasks"]["percent"])
        self.assertEqual(55.6, result["tasks"]["weighted_percent"])
        self.assertEqual(50.0, result["tasks"]["priority"]["must"]["percent"])
        self.assertEqual(100.0, result["tasks"]["priority"]["should"]["percent"])

    def test_next_actions_filter_dependencies_and_use_stable_order(self):
        value = facts(
            tasks=[
                task("D01-T01", status="done"),
                task("D01-T02", status="ready", dependencies=["D01-T01"]),
                task("D01-T03", status="in-progress", dependencies=["D01-T01"]),
                task("D01-T04", status="review", dependencies=["D01-T01"]),
                task("D01-T05", status="ready", priority="should"),
                task("D01-T06", status="ready", dependencies=["D99-T99"]),
            ]
        )

        result = self.aggregate(value)

        self.assertEqual(
            ["D01-T04", "D01-T03", "D01-T02", "D01-T05"],
            [item["id"] for item in result["next_actions"]],
        )

    def test_blocked_tasks_expose_reason_and_unblock_action(self):
        result = self.aggregate(facts(tasks=[task("D01-T01", status="blocked")]))

        self.assertEqual(1, len(result["blockers"]))
        self.assertEqual("等待输入", result["blockers"][0]["reason"])
        self.assertEqual("补充输入", result["blockers"][0]["unblock_action"])
        self.assertEqual([], result["next_actions"])

    def test_all_done_moves_to_release_cycle(self):
        result = self.aggregate(facts(tasks=[task("D14-T01", day=14, status="done")]))

        self.assertTrue(result["goal"]["all_tasks_done"])
        self.assertEqual(14, result["goal"]["current_day"])
        self.assertIn("发布", result["release_message"])

    def test_chapter_gaps_and_experiment_distributions(self):
        value = facts(
            tasks=[task("D01-T01")],
            chapters=[chapter(["done", "done", "in-progress", "pending", "pending", "pending"])],
            experiments=[
                experiment("planned", "SHIP"),
                {**experiment("ready", "KEEP-EXT"), "id": "EXP-01-02"},
                {**experiment("verified", "ALREADY"), "id": "EXP-01-03"},
            ],
        )

        result = self.aggregate(value)

        self.assertEqual("example", result["chapters"]["rows"][0]["next_gap"])
        self.assertEqual(33.3, result["chapters"]["rows"][0]["percent"])
        self.assertEqual({"SHIP": 1, "KEEP-EXT": 1, "ALREADY": 1}, result["experiments"]["triage_counts"])
        self.assertEqual(1, result["experiments"]["status_counts"]["verified"])

    def test_metrics_are_deterministic_except_generation_time(self):
        value = facts(tasks=[task("D01-T01")], chapters=[chapter()], experiments=[experiment()])
        first = self.aggregate(value, "2026-07-22T01:00:00Z")
        second = self.aggregate(value, "2026-07-22T02:00:00Z")

        del first["generated_at"]
        del second["generated_at"]
        self.assertEqual(first, second)


class EventDetectionTests(unittest.TestCase):
    def setUp(self):
        self.current = facts(
            tasks=[task("D01-T01")],
            chapters=[chapter()],
            experiments=[experiment()],
        )

    def detect(self, previous, current=None):
        return core.detect_events(
            previous,
            current or self.current,
            "source-1",
            "tester",
            "2026-07-22T01:00:00Z",
        )

    def test_first_run_creates_one_initialization_event(self):
        events = self.detect(None)

        self.assertEqual(1, len(events))
        self.assertEqual("system_initialized", events[0]["type"])

    def test_identical_facts_create_no_events(self):
        self.assertEqual([], self.detect(deepcopy(self.current)))

    def test_task_chapter_and_experiment_changes_are_detected(self):
        previous = deepcopy(self.current)
        self.current["tasks"]["tasks"][0]["status"] = "in-progress"
        self.current["chapters"]["chapters"][0]["stages"][0]["status"] = "done"
        self.current["experiments"]["experiments"][0]["status"] = "ready"

        events = self.detect(previous)

        self.assertEqual(
            {"task_status_changed", "chapter_stage_changed", "experiment_changed"},
            {event["type"] for event in events},
        )

    def test_event_ids_are_stable_and_merge_deduplicates(self):
        previous = deepcopy(self.current)
        self.current["tasks"]["tasks"][0]["status"] = "in-progress"
        first = self.detect(previous)
        second = self.detect(previous)

        self.assertEqual(first[0]["id"], second[0]["id"])
        merged, additions = core.merge_events(first, second)
        self.assertEqual(1, len(merged))
        self.assertEqual([], additions)

    def test_explicit_release_event_is_supported(self):
        events = core.detect_events(
            deepcopy(self.current),
            self.current,
            "source-1",
            "tester",
            "2026-07-22T01:00:00Z",
            ("release_published", "v0.1", "v0.1 已发布"),
        )

        self.assertEqual("release_published", events[0]["type"])
        self.assertEqual("v0.1", events[0]["object_id"])

    def test_source_identity_falls_back_to_fact_fingerprint_without_git(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = core.source_identity(Path(directory), self.current)

        self.assertRegex(identity, r"^working-tree-[0-9a-f]{12}$")


if __name__ == "__main__":
    unittest.main()
