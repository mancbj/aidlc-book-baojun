#!/usr/bin/env python3
"""Render v0.1 Release Notes from readiness and progress facts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Optional, Sequence


def render(root: Path, readiness: dict) -> str:
    current = json.loads((root / "progress/generated/current.json").read_text(encoding="utf-8"))
    experiments = json.loads((root / "progress/experiments.json").read_text(encoding="utf-8"))["experiments"]
    chapters = json.loads((root / "progress/chapters.json").read_text(encoding="utf-8"))["chapters"]
    triage = {name: sum(item["triage"] == name for item in experiments) for name in ("SHIP", "KEEP-EXT", "ALREADY")}
    gaps = readiness.get("gaps", [])
    gap_lines = [f"- **{item['priority']} · {item['code']}** — `{item['object']}`：{item['fix']}" for item in gaps]
    if not gap_lines:
        gap_lines = ["- 无发布阻断缺口。"]
    version = str(readiness.get("version", "v0.1"))
    done_chapters = sum(
        1
        for chapter in chapters
        if all(stage.get("status") == "done" for stage in chapter.get("stages", []))
    )
    if version.startswith("v0.2"):
        highlights = [
            "- 正式十章生产线可读稿与五类审校全部完成（CH-01～CH-10）。",
            "- CH-08 Operations、CH-09 适配性工程、CH-10 组织与度量闭合交付闭环到规模化。",
            "- 进度事实源、事件、快照与驾驶舱同步到十章完成状态。",
            "- 书稿 HTML / PDF 与 Pages 候选一并进入 Release 资产。",
        ]
        next_goal = "v0.3 draft：推进 planned 实验实现、独立章节 SVG，并消化 Reader 反馈缺口。"
    else:
        highlights = [
            "- GitHub 原生写作事实、进度、事件、快照和鸟瞰驾驶舱。",
            "- Issue/PR、CI、Pages、Release 与 Projects 自动化入口。",
            "- 五类审校、反馈决策、发布门禁和下一周期机制。",
        ]
        next_goal = "v0.2 draft 保持每周一节、一次实验、一次构建/审校和每月可读 Release；只有真实 v0.1 published receipt 后才激活。"
    return "\n".join(
        [
            f"# {version} Release Notes Candidate",
            "",
            f"> Readiness: **{readiness['status'].upper()}** · Source `{readiness['source_id']}` · Generated `{readiness['generated_at']}`",
            "",
            "## 新增内容",
            "",
            *highlights,
            "",
            "## 关键指标",
            "",
            f"- 任务：{current['tasks']['done']}/{current['tasks']['total']}（{current['tasks']['percent']:.1f}%）",
            f"- Must：{current['tasks']['priority']['must']['done']}/{current['tasks']['priority']['must']['total']}",
            f"- 章节：{done_chapters}/{current['chapters']['total']} 六阶段完成",
            f"- 实验：SHIP {triage['SHIP']} · KEEP-EXT {triage['KEEP-EXT']} · ALREADY {triage['ALREADY']}",
            "",
            "## 已知缺口",
            "",
            *gap_lines,
            "",
            "## 产物与来源",
            "",
            f"- Source commit/fingerprint：`{readiness['source_id']}`",
            "- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。",
            "- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。",
            "- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。",
            "- 驾驶舱：`site/index.html`",
            "- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form",
            "",
            "## 下一版本目标",
            "",
            next_goal,
            "",
        ]
    )


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="从 readiness 与 progress 生成 Release Notes。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--readiness", type=Path, default=Path("releases/v0.1-rc/readiness.json"))
    parser.add_argument("--output", type=Path, default=Path("releases/v0.1-rc/release-notes.md"))
    parser.add_argument("--require-ready", action="store_true")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    readiness_path = args.readiness if args.readiness.is_absolute() else root / args.readiness
    output = args.output if args.output.is_absolute() else root / args.output
    try:
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        if args.require_ready and readiness.get("status") != "ready":
            raise ValueError("readiness 不是 ready，拒绝生成可发布 Notes")
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(render(root, readiness), encoding="utf-8")
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Release Notes failed: {exc}")
        return 1
    print(f"[INFO] Release Notes: status={readiness['status']}, output={output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
