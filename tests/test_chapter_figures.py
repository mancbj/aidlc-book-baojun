"""Checks chapter SVG registry: presence, references, and strict skill audit."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "book" / "images" / "chapter-figures.json"
AUDITOR = (
    REPO_ROOT
    / ".codex"
    / "skills"
    / "svg-technical-diagram"
    / "scripts"
    / "audit_svg.py"
)
CHAPTER_FILES = {
    "CH-01": REPO_ROOT / "book" / "chapters" / "ch01-ai-native-sdlc.md",
    "CH-02": REPO_ROOT / "book" / "chapters" / "ch02-human-judgment.md",
    "CH-03": REPO_ROOT / "book" / "chapters" / "ch03-inception.md",
    "CH-04": REPO_ROOT / "book" / "chapters" / "ch04-memory-bank-standards.md",
    "CH-05": REPO_ROOT / "book" / "chapters" / "ch05-bolts.md",
    "CH-06": REPO_ROOT / "book" / "chapters" / "ch06-exsecutio.md",
    "CH-07": REPO_ROOT / "book" / "chapters" / "ch07-verification.md",
    "CH-08": REPO_ROOT / "book" / "chapters" / "ch08-operations.md",
    "CH-09": REPO_ROOT / "book" / "chapters" / "ch09-adaptive-engineering.md",
    "CH-10": REPO_ROOT / "book" / "chapters" / "ch10-organization-metrics.md",
}


def load_registry() -> dict:
    return json.loads(REGISTRY.read_text(encoding="utf-8"))


class ChapterFiguresTest(unittest.TestCase):
    def test_registry_covers_ten_chapters(self):
        data = load_registry()
        chapters = [item["chapter"] for item in data["chapter_figures"]]
        self.assertEqual(
            [
                "CH-01",
                "CH-02",
                "CH-03",
                "CH-04",
                "CH-05",
                "CH-06",
                "CH-07",
                "CH-08",
                "CH-09",
                "CH-10",
            ],
            chapters,
        )
        self.assertEqual("book/images/fig0-1.svg", data["core_figure"])

    def test_each_figure_exists_and_is_referenced(self):
        data = load_registry()
        for item in data["chapter_figures"]:
            path = REPO_ROOT / item["path"]
            self.assertTrue(path.is_file(), f"missing figure: {item['path']}")
            chapter_path = CHAPTER_FILES[item["chapter"]]
            body = chapter_path.read_text(encoding="utf-8")
            if item.get("reuse"):
                self.assertIn("fig0-1.svg", body)
                continue
            relative = Path(item["path"]).name
            self.assertTrue(
                f"(images/{relative})" in body or f"(../images/{relative})" in body,
                f"{item['chapter']} must embed {relative}",
            )
            self.assertIn(item["path"], body)

    def test_each_figure_passes_strict_audit(self):
        data = load_registry()
        for item in data["chapter_figures"]:
            path = REPO_ROOT / item["path"]
            command = ["python3", str(AUDITOR), str(path), "--strict"]
            for required in item.get("required_text", []):
                command.extend(["--required-text", required])
            if item.get("reuse"):
                command.extend(["--required-text", "𝓔 = Engineering with Exsecutio"])
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(
                0,
                result.returncode,
                f"{item['path']}\n{result.stdout}\n{result.stderr}",
            )

    def test_ch06_and_ch08_preserve_terminology_boundaries(self):
        ch06 = (REPO_ROOT / "book/images/ch06-exsecutio-loop.svg").read_text(encoding="utf-8")
        ch08 = (REPO_ROOT / "book/images/ch08-operations-loop.svg").read_text(encoding="utf-8")
        self.assertIn("Exsecutio", ch06)
        self.assertNotIn("Engineering with Execution", ch06)
        self.assertIn("Runtime Verify", ch08)
        self.assertIn("CH-07", ch08)


if __name__ == "__main__":
    unittest.main()
