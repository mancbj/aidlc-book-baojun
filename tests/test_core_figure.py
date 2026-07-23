"""Checks for the editable AI-DLC core figure and its SVG skill contract."""

import re
import subprocess
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
FIGURE = REPO_ROOT / "book" / "images" / "fig0-1.svg"
AUDITOR = (
    REPO_ROOT
    / ".codex"
    / "skills"
    / "svg-technical-diagram"
    / "scripts"
    / "audit_svg.py"
)
SVG_NS = "http://www.w3.org/2000/svg"


class CoreFigureTest(unittest.TestCase):
    def test_core_figure_is_valid_editable_svg(self):
        root = ET.parse(FIGURE).getroot()

        self.assertEqual(f"{{{SVG_NS}}}svg", root.tag)
        self.assertEqual("0 0 960 540", root.attrib["viewBox"])
        self.assertEqual("img", root.attrib["role"])
        self.assertTrue(root.findall(f".//{{{SVG_NS}}}text"))

    def test_core_figure_explains_formula_and_loop(self):
        text = FIGURE.read_text(encoding="utf-8")
        compact = re.sub(r"\s+", "", text)

        for required in (
            "AI-DLC=𝓔",
            "人的判断+AI能力",
            "𝓔=EngineeringwithExsecutio",
            "人的判断",
            "AI能力",
            "工程化执行",
            "确定性交付",
            "反馈更新判断与工程约束",
        ):
            self.assertIn(required, compact)
        self.assertNotIn("Engineering with Execution", text)

    def test_core_figure_uses_semantic_svg_engineering(self):
        root = ET.parse(FIGURE).getroot()
        text = FIGURE.read_text(encoding="utf-8")
        groups = root.findall(f".//{{{SVG_NS}}}g")
        roles = {group.attrib.get("data-role") for group in groups}
        feedback = next(group for group in groups if group.attrib.get("data-role") == "feedback")

        self.assertTrue({"thesis", "inputs", "shared-input", "process", "output", "feedback"} <= roles)
        self.assertEqual("shared-input-rail", feedback.attrib["data-target"])
        self.assertIn("<style>", text)
        self.assertIn('vector-effect="non-scaling-stroke"', text)
        self.assertNotIn("<circle", text)
        self.assertNotIn("<foreignObject", text)
        self.assertNotIn("<image", text)

    def test_core_figure_passes_skill_audit_in_strict_mode(self):
        result = subprocess.run(
            [
                "python3",
                str(AUDITOR),
                str(FIGURE),
                "--strict",
                "--required-text",
                "𝓔 = Engineering with Exsecutio",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_skill_audit_rejects_execution_normalization(self):
        bad_svg = FIGURE.read_text(encoding="utf-8").replace("Exsecutio", "Execution")
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "bad.svg"
            candidate.write_text(bad_svg, encoding="utf-8")
            result = subprocess.run(
                ["python3", str(AUDITOR), str(candidate)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("preserve Exsecutio", result.stdout)


if __name__ == "__main__":
    unittest.main()
