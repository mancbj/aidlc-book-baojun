"""Integration and failure-safety tests for the progress generator."""

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = REPO_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import generate_progress as generator  # noqa: E402
from progress_core import ProgressError  # noqa: E402
from test_validate_project import TIMESTAMP, valid_already, valid_chapter, valid_task  # noqa: E402


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GeneratorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "progress").mkdir(parents=True)
        (self.root / "feedback").mkdir(parents=True)
        (self.root / "README.md").write_text("# Fixture\n", encoding="utf-8")
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
                "experiments": [valid_already()],
            },
        }
        self.write_documents()
        (self.root / "feedback/decisions.json").write_text(
            json.dumps(
                {"schema_version": "1.0.0", "updated": TIMESTAMP, "readers": [], "decisions": []},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "progress/cycles.json").write_text(
            json.dumps(
                {"schema_version": "1.0.0", "updated": TIMESTAMP, "active_cycle": None, "cycles": []},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp_dir.cleanup()

    def write_documents(self):
        for filename, value in self.documents.items():
            (self.root / "progress" / filename).write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def args(self, timestamp="2026-07-22T01:00:00Z", **overrides):
        values = {
            "root": self.root,
            "actor": "tester",
            "generated_at": timestamp,
            "event_type": None,
            "event_object": None,
            "event_summary": None,
            "dry_run": False,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def test_initial_run_generates_complete_projection(self):
        result = generator.generate(self.args())

        self.assertEqual(1, result["new_event_count"])
        self.assertTrue((self.root / "progress/generated/current.json").is_file())
        self.assertTrue((self.root / "progress/generated/current.md").is_file())
        self.assertTrue((self.root / "progress/events/events.jsonl").is_file())
        self.assertTrue((self.root / "progress/CHANGELOG.md").is_file())
        self.assertTrue((self.root / "site/index.html").is_file())
        self.assertTrue((self.root / "site/progress.html").is_file())
        self.assertTrue((self.root / "site/details.html").is_file())
        self.assertEqual(1, len(list((self.root / "progress/snapshots").glob("*.json"))))

        current = json.loads((self.root / "progress/generated/current.json").read_text())
        self.assertEqual("D01-T01", current["next_actions"][0]["id"])
        self.assertEqual(1, current["tasks"]["total"])

    def test_repeat_run_preserves_event_log_changelog_and_snapshot(self):
        generator.generate(self.args())
        events = self.root / "progress/events/events.jsonl"
        changelog = self.root / "progress/CHANGELOG.md"
        events_before = events.read_bytes()
        changelog_before = changelog.read_bytes()

        result = generator.generate(self.args("2026-07-22T02:00:00Z"))

        self.assertEqual(0, result["new_event_count"])
        self.assertEqual(events_before, events.read_bytes())
        self.assertEqual(changelog_before, changelog.read_bytes())
        self.assertEqual(1, len(list((self.root / "progress/snapshots").glob("*.json"))))

    def test_repeat_run_preserves_current_projection_with_fixed_time(self):
        generator.generate(self.args())
        current = self.root / "progress/generated/current.json"
        current_before = current.read_bytes()

        result = generator.generate(self.args())

        self.assertEqual(0, result["new_event_count"])
        self.assertEqual(current_before, current.read_bytes())

    def test_status_change_appends_one_event_and_new_snapshot(self):
        generator.generate(self.args())
        events_path = self.root / "progress/events/events.jsonl"
        old_bytes = events_path.read_bytes()
        task = self.documents["tasks.json"]["tasks"][0]
        task["status"] = "blocked"
        task["blocker_reason"] = "等待确认"
        task["unblock_action"] = "获得确认"
        task["updated"] = "2026-07-22T02:00:00Z"
        self.documents["tasks.json"]["updated"] = task["updated"]
        self.write_documents()

        result = generator.generate(self.args("2026-07-22T02:00:00Z"))

        self.assertEqual(1, result["new_event_count"])
        self.assertTrue(events_path.read_bytes().startswith(old_bytes))
        events = [json.loads(line) for line in events_path.read_text().splitlines()]
        self.assertEqual("task_status_changed", events[-1]["type"])
        self.assertEqual(2, len(list((self.root / "progress/snapshots").glob("*.json"))))

    def test_invalid_facts_leave_last_successful_outputs_untouched(self):
        generator.generate(self.args())
        current = self.root / "progress/generated/current.json"
        baseline = self.root / "progress/generated/last-successful-facts.json"
        before = (digest(current), digest(baseline))
        self.documents["tasks.json"]["tasks"][0]["status"] = "invalid"
        self.write_documents()

        with self.assertRaises(ProgressError):
            generator.generate(self.args("2026-07-22T02:00:00Z"))

        self.assertEqual(before, (digest(current), digest(baseline)))

    def test_conflicting_snapshot_is_not_overwritten(self):
        result = generator.generate(self.args())
        snapshot = self.root / "progress/snapshots" / result["snapshot"]
        value = json.loads(snapshot.read_text())
        value["source_id"] = "different-source"
        snapshot.write_text(json.dumps(value), encoding="utf-8")
        before = snapshot.read_bytes()

        with self.assertRaises(ProgressError):
            generator.generate(self.args("2026-07-22T02:00:00Z"))

        self.assertEqual(before, snapshot.read_bytes())

    def test_dry_run_has_no_filesystem_side_effects(self):
        result = generator.generate(self.args(dry_run=True))

        self.assertTrue(result["dry_run"])
        self.assertFalse((self.root / "progress/generated").exists())
        self.assertFalse((self.root / "site").exists())

    def test_dashboard_has_no_javascript_fallback_and_stable_drilldowns(self):
        generator.generate(self.args())
        dashboard = (self.root / "site/index.html").read_text(encoding="utf-8")
        progress = (self.root / "site/progress.html").read_text(encoding="utf-8")
        details = (self.root / "site/details.html").read_text(encoding="utf-8")

        for text in (
            "总体进度",
            "Day 进度",
            "倒计时",
            "章节阶段",
            "下一动作",
            "任务时间线",
            "十章六阶段生产线",
            "实验治理队列",
            "阻塞中心",
            "可立即执行",
            "D01-T01",
        ):
            self.assertIn(text, dashboard)
        self.assertIn('<main id="main">', dashboard)
        self.assertIn('class="skip-link"', dashboard)
        for text in (
            "时间线与",
            "生产线鸟瞰",
            "任务时间线",
            "章节生产线",
            "实验生产线",
            "阻塞中心",
            "最近事件",
            'id="progress-timeline"',
            'id="chapter-production"',
            'id="experiment-production"',
            'id="blocker-production"',
            'id="task-drilldown"',
            'id="artifact-drilldown"',
            'id="github-drilldown"',
            'id="event-production"',
            "任务下钻",
            "产物下钻",
            "GitHub 链接",
            "打开任务下钻",
            "打开产物下钻",
        ):
            self.assertIn(text, progress)
        self.assertIn('id="task-D01-T01"', details)
        self.assertIn('id="chapter-writing-cards"', details)
        self.assertIn('id="chapter-CH-01"', details)
        self.assertIn('id="experiment-EXP-01-03"', details)

    def test_explicit_event_requires_complete_arguments(self):
        with self.assertRaises(ProgressError):
            generator.generate(self.args(event_type="release_published"))


if __name__ == "__main__":
    unittest.main()
