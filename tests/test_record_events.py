"""Integration tests for the standalone event recorder."""

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

import record_events  # noqa: E402
from progress_core import canonical_json  # noqa: E402
from test_validate_project import TIMESTAMP, valid_already, valid_chapter, valid_task  # noqa: E402


class RecordEventsTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "progress" / "generated").mkdir(parents=True)
        (self.root / "feedback").mkdir(parents=True)
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
        (self.root / "feedback" / "decisions.json").write_text(
            json.dumps(
                {"schema_version": "1.0.0", "updated": TIMESTAMP, "readers": [], "decisions": []},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (self.root / "progress" / "cycles.json").write_text(
            json.dumps(
                {"schema_version": "1.0.0", "updated": TIMESTAMP, "active_cycle": None, "cycles": []},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self.write_baseline()

    def tearDown(self):
        self.temp_dir.cleanup()

    def args(self, **overrides):
        values = {
            "root": self.root,
            "actor": "tester",
            "generated_at": "2026-07-22T03:00:00Z",
            "event_type": None,
            "event_object": None,
            "event_summary": None,
            "dry_run": False,
            "report": None,
        }
        values.update(overrides)
        return SimpleNamespace(**values)

    def current_facts(self):
        return {
            "tasks": self.documents["tasks.json"],
            "chapters": self.documents["chapters.json"],
            "experiments": self.documents["experiments.json"],
            "feedback": json.loads((self.root / "feedback" / "decisions.json").read_text(encoding="utf-8")),
            "cycles": json.loads((self.root / "progress" / "cycles.json").read_text(encoding="utf-8")),
        }

    def write_documents(self):
        for filename, value in self.documents.items():
            (self.root / "progress" / filename).write_text(
                json.dumps(value, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )

    def write_baseline(self):
        facts = self.current_facts()
        baseline = {"schema_version": "1.0.0", "source_id": "baseline", "facts": facts}
        (self.root / "progress" / "generated" / "last-successful-facts.json").write_text(
            json.dumps(baseline, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def event_lines(self):
        path = self.root / "progress" / "events" / "events.jsonl"
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]

    def test_real_status_change_appends_event_once(self):
        task = self.documents["tasks.json"]["tasks"][0]
        task["status"] = "in-progress"
        task["updated"] = "2026-07-22T03:00:00Z"
        self.documents["tasks.json"]["updated"] = task["updated"]
        self.write_documents()

        first = record_events.record(self.args())
        events_before = (self.root / "progress" / "events" / "events.jsonl").read_bytes()
        second = record_events.record(self.args(generated_at="2026-07-22T04:00:00Z"))

        self.assertEqual(1, first["new_event_count"])
        self.assertEqual(0, second["new_event_count"])
        self.assertEqual(events_before, (self.root / "progress" / "events" / "events.jsonl").read_bytes())
        self.assertEqual("task_status_changed", self.event_lines()[0]["type"])

    def test_dry_run_does_not_write_event_log(self):
        task = self.documents["tasks.json"]["tasks"][0]
        task["status"] = "in-progress"
        task["updated"] = "2026-07-22T03:00:00Z"
        self.documents["tasks.json"]["updated"] = task["updated"]
        self.write_documents()

        result = record_events.record(self.args(dry_run=True))

        self.assertEqual(1, result["candidate_event_count"])
        self.assertEqual(1, result["new_event_count"])
        self.assertFalse((self.root / "progress" / "events" / "events.jsonl").exists())

    def test_explicit_event_is_recorded_once(self):
        args = self.args(
            event_type="milestone_reached",
            event_object="v0.0.1",
            event_summary="Day 7 可读版本完成",
        )

        first = record_events.record(args)
        second = record_events.record(args)

        self.assertEqual(1, first["new_event_count"])
        self.assertEqual(0, second["new_event_count"])
        self.assertEqual("milestone_reached", self.event_lines()[0]["type"])

    def test_explicit_event_requires_complete_arguments(self):
        with self.assertRaises(Exception):
            record_events.record(self.args(event_type="release_published"))


if __name__ == "__main__":
    unittest.main()
