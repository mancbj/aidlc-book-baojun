"""Release notes title helper tests."""

from __future__ import annotations

import unittest

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import render_release_notes as notes  # noqa: E402


class ReleaseTitleTest(unittest.TestCase):
    def test_v09006_title_includes_summary(self) -> None:
        title = notes.release_title({"version": "v0.9.006"})
        self.assertIn("v0.9.006", title)
        self.assertIn("Markdown", title)

    def test_unknown_version_falls_back_to_tag(self) -> None:
        self.assertEqual("v9.9.9", notes.release_title({"version": "v9.9.9"}))


if __name__ == "__main__":
    unittest.main()
