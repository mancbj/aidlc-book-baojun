"""README release download block and updater."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import update_readme_release_downloads as updater  # noqa: E402
from release_book_assets import asset_filenames  # noqa: E402


class ReadmeReleaseDownloadsTest(unittest.TestCase):
    def test_markers_present_in_both_readmes(self) -> None:
        for name in ("README.md", "README.en.md"):
            text = (REPO_ROOT / name).read_text(encoding="utf-8")
            self.assertIn(updater.BEGIN, text)
            self.assertIn(updater.END, text)

    def test_block_contains_six_download_urls(self) -> None:
        names = asset_filenames("v9.9.9")
        block = updater.block_zh("owner/repo", "v9.9.9", names, infographics=False)
        self.assertEqual(block.count("/releases/download/v9.9.9/"), 6)

    def test_block_includes_infographic_zip_when_enabled(self) -> None:
        names = asset_filenames("v0.9.007")
        block = updater.block_zh(updater.DEFAULT_REPO, "v0.9.007", names, infographics=True)
        self.assertIn("en-infographics.zip", block)

    def test_patch_is_idempotent(self) -> None:
        names = asset_filenames("v0.9.006")
        block = updater.block_zh(updater.DEFAULT_REPO, "v0.9.006", names, infographics=False)
        sample = f"pre\n{block}\npost"
        pattern = __import__("re").compile(
            __import__("re").escape(updater.BEGIN) + r".*?" + __import__("re").escape(updater.END),
            __import__("re").DOTALL,
        )
        once = pattern.sub(block, sample, count=1)
        twice = pattern.sub(block, once, count=1)
        self.assertEqual(once, twice)


if __name__ == "__main__":
    unittest.main()
