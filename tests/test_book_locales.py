"""Contract tests for zh/en book locale layout and build spine."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD_PY = REPO_ROOT / "scripts" / "build_book.py"
FIXED_TIME = "2026-07-27T06:00:00Z"
HAS_PANDOC = shutil.which("pandoc") is not None
HAS_MERMAID = shutil.which("mmdc") is not None

EN_REQUIRED_PATHS = (
    "book/en/build-frontmatter.md",
    "book/en/manifesto.md",
    "book/en/part-00-overview.md",
    "book/en/toc.md",
    "book/en/glossary.md",
    "book/en/chapters/README.md",
    "docs/BOOK-LOCALES.md",
)


class BookLocaleLayoutTest(unittest.TestCase):
    def test_english_spine_files_exist(self) -> None:
        for relative in EN_REQUIRED_PATHS:
            path = REPO_ROOT / relative
            self.assertTrue(path.is_file(), relative)

    def test_build_book_exposes_locale_config(self) -> None:
        source = BUILD_PY.read_text(encoding="utf-8")
        self.assertIn("SUPPORTED_LOCALES", source)
        self.assertIn('html_name="deep-understanding-ai-dlc-en.html"', source)
        self.assertIn("SOURCE_FILES_EN", source)

    def test_v09001_policy_defers_en_pdf_release(self) -> None:
        policy = json.loads(
            (REPO_ROOT / "planning/releases/v0.9.001-policy.json").read_text(encoding="utf-8")
        )
        self.assertEqual("v0.9.001", policy["version"])
        self.assertFalse(policy["pdf_required"])
        self.assertEqual("v0.9.002-draft", policy["next_version"])


@unittest.skipUnless(HAS_PANDOC and HAS_MERMAID, "English build smoke requires pandoc and mmdc")
class EnglishBuildSmokeTest(unittest.TestCase):
    def test_en_locale_builds_html_with_locale_manifest(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "en"
            environment = dict(os.environ)
            environment["BOOK_BUILD_GENERATED_AT"] = FIXED_TIME
            result = subprocess.run(
                [
                    "python3",
                    str(BUILD_PY),
                    "--output",
                    str(output),
                    "--format",
                    "html",
                    "--locale",
                    "en",
                    "--generated-at",
                    FIXED_TIME,
                ],
                cwd=REPO_ROOT,
                env=environment,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("en", manifest["locale"])
            self.assertEqual(
                "deep-understanding-ai-dlc-en.html",
                manifest["outputs"][0]["path"],
            )
            html = (output / "deep-understanding-ai-dlc-en.html").read_text(encoding="utf-8")
            self.assertIn("Part 00 · Bird", html)
            self.assertIn("Engineering with Exsecutio", html)


if __name__ == "__main__":
    unittest.main()
