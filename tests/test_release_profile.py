"""Tests for release-profile hygiene filtering."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
HAS_PANDOC = shutil.which("pandoc") is not None
HAS_MERMAID = shutil.which("mmdc") is not None
HAS_PDFTOTEXT = shutil.which("pdftotext") is not None


class ReleaseProfileTest(unittest.TestCase):
    def test_lua_filter_strips_metadata_and_gate(self):
        if not HAS_PANDOC:
            self.skipTest("pandoc required")
        sample = """# 第 X 章

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-08 |
| Writing Sprint Card | D22-T03 |

## 01 · Question

正文问题。

### Gate

- [x] 核心问题只有一个

## 02 · Framework

框架正文。

## 10 · Review Notes for D15-T03

审校备注。

## References

- 保留引用
"""
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.md"
            output = Path(directory) / "out.md"
            source.write_text(sample, encoding="utf-8")
            result = subprocess.run(
                [
                    "pandoc",
                    str(source),
                    "--from=markdown",
                    "--to=markdown",
                    f"--lua-filter={REPO_ROOT / 'book/filters/release-profile.lua'}",
                    f"--output={output}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("框架正文", text)
            self.assertIn("保留引用", text)
            self.assertNotIn("Writing Sprint Card", text)
            self.assertNotIn("Chapter ID", text)
            self.assertNotIn("核心问题只有一个", text)
            self.assertNotIn("Review Notes", text)
            self.assertNotIn("审校备注", text)

    def test_lua_filter_keeps_content_gates_heading(self):
        if not HAS_PANDOC:
            self.skipTest("pandoc required")
        sample = "## 02 · Framework\n\n### 2.3 Gates：阶段门禁防止错误级联\n\n门禁内容应保留。\n"
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "sample.md"
            output = Path(directory) / "out.md"
            source.write_text(sample, encoding="utf-8")
            result = subprocess.run(
                [
                    "pandoc",
                    str(source),
                    "--from=markdown",
                    "--to=markdown",
                    f"--lua-filter={REPO_ROOT / 'book/filters/release-profile.lua'}",
                    f"--output={output}",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            text = output.read_text(encoding="utf-8")
            self.assertIn("阶段门禁防止错误级联", text)
            self.assertIn("门禁内容应保留", text)

    @unittest.skipUnless(HAS_PANDOC and HAS_MERMAID, "release build requires pandoc and mmdc")
    def test_release_html_passes_content_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "release"
            result = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "build_release_book.py"),
                    "--root",
                    str(REPO_ROOT),
                    "--output",
                    str(output),
                    "--format",
                    "html",
                    "--generated-at",
                    "2026-07-25T00:10:00Z",
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
                env=dict(os.environ),
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            html = output / "deep-understanding-ai-dlc.html"
            audit = subprocess.run(
                [
                    "python3",
                    str(REPO_ROOT / "scripts" / "audit_release_content.py"),
                    "--html",
                    str(html),
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(0, audit.returncode, audit.stdout + audit.stderr)
            manifest = json.loads((output / "build-manifest.json").read_text(encoding="utf-8"))
            self.assertEqual("release", manifest["profile"])


if __name__ == "__main__":
    unittest.main()
