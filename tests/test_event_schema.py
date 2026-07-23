"""Contract tests for the progress event schema document."""

import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EVENT_SCHEMA = REPO_ROOT / "progress" / "schemas" / "event-schema.md"
PROGRESS_CORE = REPO_ROOT / "scripts" / "progress_core.py"
GENERATE_PROGRESS = REPO_ROOT / "scripts" / "generate_progress.py"


class EventSchemaTest(unittest.TestCase):
    def test_schema_documents_all_emitted_event_types(self):
        schema = EVENT_SCHEMA.read_text(encoding="utf-8")
        core = PROGRESS_CORE.read_text(encoding="utf-8")
        generator = GENERATE_PROGRESS.read_text(encoding="utf-8")

        automatic_types = set(re.findall(r'_event\(\s*"([^"]+)"', core))
        explicit_types = set(re.findall(r'"([a-z_]+)",', generator.split("EXPLICIT_EVENT_TYPES =", 1)[1].split(")", 1)[0]))

        for event_type in sorted(automatic_types | explicit_types):
            self.assertIn(f"`{event_type}`", schema)

    def test_schema_documents_required_event_fields(self):
        schema = EVENT_SCHEMA.read_text(encoding="utf-8")
        for field in (
            "id",
            "occurred_at",
            "type",
            "object_type",
            "object_id",
            "before",
            "after",
            "source_id",
            "actor",
            "summary",
        ):
            self.assertIn(f"`{field}`", schema)

    def test_schema_covers_day6_acceptance_categories(self):
        schema = EVENT_SCHEMA.read_text(encoding="utf-8")
        for event_type in (
            "task_status_changed",
            "chapter_stage_changed",
            "experiment_changed",
            "build_completed",
            "milestone_reached",
            "release_published",
        ):
            self.assertIn(f"`{event_type}`", schema)


if __name__ == "__main__":
    unittest.main()
