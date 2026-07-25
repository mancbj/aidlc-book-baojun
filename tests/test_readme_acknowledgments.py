"""Contract: README opening acknowledgments for upstream projects."""

from __future__ import annotations

import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class ReadmeAcknowledgmentsTest(unittest.TestCase):
    def test_opening_thanks_ai_agent_book_and_specsmd(self) -> None:
        text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("## 致谢", text)
        self.assertLess(text.index("## 致谢"), text.index("## 核心公式"))
        self.assertIn("https://github.com/bojieli/ai-agent-book", text)
        self.assertIn("https://specs.md", text)
        self.assertIn("v0.2", text)


if __name__ == "__main__":
    unittest.main()
