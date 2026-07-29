"""Infographic asset builder."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

import build_infographic_assets as builder  # noqa: E402


class InfographicAssetsTest(unittest.TestCase):
    def test_manifest_lists_eleven_pngs(self) -> None:
        manifest = json.loads((REPO_ROOT / "assets/infographics/en/manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(11, len(manifest["items"]))
        en_dir = REPO_ROOT / "assets/infographics/en"
        for item in manifest["items"]:
            path = en_dir / item["file"]
            self.assertTrue(path.is_file(), msg=item["file"])
            self.assertGreater(path.stat().st_size, 5000)

    def test_build_pngs_idempotent_without_force(self) -> None:
        entries = builder.build_pngs(REPO_ROOT, width=1920, force=False)
        self.assertEqual(11, len(entries))


if __name__ == "__main__":
    unittest.main()
