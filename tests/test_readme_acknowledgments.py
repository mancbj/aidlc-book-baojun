"""Contract: README opening acknowledgments for upstream projects."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReadmeAcknowledgmentsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

    def test_readme_thanks_ai_agent_book_and_specsmd(self) -> None:
        self.assertIn("## 致谢", self.text)
        self.assertGreater(self.text.index("## 致谢"), self.text.index("## 当前状态"))
        self.assertIn("https://github.com/bojieli/ai-agent-book", self.text)
        self.assertIn("https://specs.md", self.text)
        self.assertIn("v0.2", self.text)

    def test_first_screen_has_trust_and_action_signals(self) -> None:
        first_screen = self.text[:3000]
        self.assertIn("Open-source AI-DLC book", first_screen)
        self.assertIn("actions/workflows/validate.yml/badge.svg", first_screen)
        self.assertIn("releases/latest", first_screen)
        self.assertIn('alt="License: Apache-2.0"', first_screen)
        self.assertIn("book/images/star-this-repo.gif", first_screen)
        self.assertIn("## 3 分钟开始", first_screen)

    def test_readme_has_agent_community_and_honest_license_sections(self) -> None:
        for heading in ("## AI Agent / Cursor 使用", "## 贡献", "## 社区与支持", "## 许可"):
            self.assertIn(heading, self.text)
        self.assertIn("[Apache License 2.0](LICENSE)", self.text)
        self.assertIn("Copyright 2026 mancbj", self.text)
        self.assertNotIn("尚未声明 SPDX 开源许可证", self.text)
        self.assertNotIn("## 两周 v0.1 目标", self.text)

    def test_readme_lists_official_ai_dlc_sources(self) -> None:
        for url in (
            "https://prod.d13rzhkk8cj2z0.amplifyapp.com",
            "https://aws.amazon.com/cn/blogs/devops/ai-driven-development-life-cycle/",
            "https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md",
        ):
            self.assertIn(url, self.text)
        self.assertIn("docs/WORKING-WITH-AIDLC-MAP.md", self.text)
        self.assertIn("## 官方来源与两条路径", self.text)

    def test_english_readme_lists_official_sources(self) -> None:
        en = (REPO_ROOT / "README.en.md").read_text(encoding="utf-8")
        self.assertIn("## Official sources and two paths", en)
        self.assertIn("https://prod.d13rzhkk8cj2z0.amplifyapp.com", en)
        self.assertIn("WORKING-WITH-AIDLC-MAP.md", en)

    def test_english_readme_is_pure_english_entrypoint(self) -> None:
        en = (REPO_ROOT / "README.en.md").read_text(encoding="utf-8")
        self.assertIn("## Get started in 3 minutes", en)
        self.assertIn("[Apache License 2.0](LICENSE)", en)
        self.assertIn("README.md", en)
        self.assertIn("https://github.com/bojieli/ai-agent-book", en)
        self.assertIn("https://specs.md", en)
        self.assertNotIn("## 3 分钟开始", en)
        self.assertIn('href="README.md"', en)
        self.assertIn("中文 README", en)
        self.text.index("README.en.md")


if __name__ == "__main__":
    unittest.main()
