"""Tests for the Pandoc-based minimal book build."""

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BUILD = REPO_ROOT / "scripts" / "build_book.sh"
FIXED_TIME = "2026-07-22T09:20:00Z"
HAS_PANDOC = shutil.which("pandoc") is not None
HAS_MERMAID = shutil.which("mmdc") is not None
HAS_TECTONIC = shutil.which("tectonic") is not None


class CandidateParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.images = []
        self.text_parts = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "img" and values.get("src"):
            self.images.append(values["src"])

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_data(self, data):
        self.text_parts.append(data)


@unittest.skipUnless(HAS_PANDOC and HAS_MERMAID, "build integration requires pandoc and mmdc")
class BuildBookTest(unittest.TestCase):
    def run_build(self, output: Path, build_format="html"):
        environment = dict(os.environ)
        environment["BOOK_BUILD_GENERATED_AT"] = FIXED_TIME
        return subprocess.run(
            [str(BUILD), str(output), build_format], cwd=REPO_ROOT, env=environment,
            capture_output=True, text=True, check=False,
        )

    def test_one_command_builds_self_contained_html_candidate(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            result = self.run_build(output)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            candidate = output / "deep-understanding-ai-dlc.html"
            text = candidate.read_text(encoding="utf-8")
            parser = CandidateParser()
            parser.feed(text)
            visible_text = re.sub(r"\s+", " ", " ".join(parser.text_parts))
            self.assertIn("AI-DLC = 𝓔（人的判断 + AI 能力）", visible_text)
            self.assertIn("𝓔 = Engineering with Exsecutio", visible_text)
            self.assertIn("Part 00 · 鸟瞰 AI-DLC", visible_text)
            self.assertIn("第 1 章 · AI 原生 SDLC", visible_text)
            self.assertIn("第 2 章 · 人的判断与反向对话", visible_text)
            self.assertIn("第 3 章 · Inception", visible_text)
            self.assertIn("第 4 章 · 上下文工程", visible_text)
            self.assertIn("第 5 章 · Bolts", visible_text)
            self.assertIn("第 6 章 · Exsecutio", visible_text)
            self.assertIn("第 10 章", visible_text)
            self.assertIn("TOC", parser.ids)
            self.assertGreaterEqual(len(parser.images), 5)
            self.assertTrue(all(source.startswith("data:image/") for source in parser.images))

    def test_manifest_links_every_source_and_output_by_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            result = self.run_build(output)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(FIXED_TIME, manifest["generated_at"])
            self.assertEqual("html", manifest["format"])
            self.assertTrue(manifest["pandoc"].startswith("pandoc "))
            self.assertEqual("11.16.0", manifest["diagram_engine"])
            self.assertEqual(14, len(manifest["sources"]))
            self.assertEqual({"deep-understanding-ai-dlc.html"}, {item["path"] for item in manifest["outputs"]})
            self.assertTrue(all(len(item["sha256"]) == 64 for item in manifest["sources"] + manifest["outputs"]))

    def test_build_refuses_to_replace_unmarked_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            output.mkdir()
            human_file = output / "human.txt"
            human_file.write_text("preserve", encoding="utf-8")
            result = self.run_build(output)
            self.assertNotEqual(0, result.returncode)
            self.assertEqual("preserve", human_file.read_text(encoding="utf-8"))
            self.assertIn("拒绝覆盖", result.stdout)

    @unittest.skipUnless(
        HAS_TECTONIC and os.environ.get("RUN_PDF_BUILD_TESTS") == "1",
        "set RUN_PDF_BUILD_TESTS=1 for the Tectonic integration test",
    )
    def test_all_format_builds_structurally_valid_pdf_without_missing_glyphs(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "candidate"
            result = self.run_build(output, "all")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            pdf = (output / "deep-understanding-ai-dlc.pdf").read_bytes()
            self.assertTrue(pdf.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf[-4096:])
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
            self.assertTrue(manifest["pdf_engine"].lower().startswith("tectonic "))
            self.assertEqual(
                {"deep-understanding-ai-dlc.html", "deep-understanding-ai-dlc.pdf"},
                {item["path"] for item in manifest["outputs"]},
            )


if __name__ == "__main__":
    unittest.main()
