"""Documentation-level contract for immutable progress snapshots."""

import json
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_README = REPO_ROOT / "progress" / "snapshots" / "README.md"
CURRENT = REPO_ROOT / "progress" / "generated" / "current.json"


class SnapshotContractTest(unittest.TestCase):
    def test_snapshot_readme_documents_source_and_failure_safety(self):
        text = SNAPSHOT_README.read_text(encoding="utf-8")

        for required in (
            "source_id",
            "commit SHA",
            "working-tree-*",
            "不得覆盖历史文件",
            "last-successful-facts.json",
            "返回非零状态",
            "tests/test_generate_progress.py",
        ):
            self.assertIn(required, text)

    def test_current_projection_points_to_existing_snapshot(self):
        current = json.loads(CURRENT.read_text(encoding="utf-8"))
        latest = current["latest_snapshot"]
        self.assertTrue(latest.startswith("../progress/snapshots/"))
        snapshot = REPO_ROOT / latest.removeprefix("../")
        self.assertTrue(snapshot.is_file(), snapshot)


if __name__ == "__main__":
    unittest.main()
