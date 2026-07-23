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
    triage = {name: sum(item["triage"] == name for item in experiments) for name in ("SHIP", "KEEP-EXT", "ALREADY")}
    gaps = readiness.get("gaps", [])
    gap_lines = [f"- **{item['priority']} · {item['code']}** — `{item['object']}`：{item['fix']}" for item in gaps]
    if not gap_lines:
        gap_lines = ["- 无发布阻断缺口。"]
    return "\n".join(
        [
            f"# {readiness['version']} Release Notes Candidate",
            "",
            f"> Readiness: **{readiness['status'].upper()}** · Source `{readiness['source_id']}` · Generated `{readiness['generated_at']}`",
            "",
            "## 新增内容",
            "",
            "- GitHub 原生写作事实、进度、事件、快照和鸟瞰驾驶舱。",
            "- Issue/PR、CI、Pages、Release 与 Projects 自动化入口。",
            "- 五类审校、反馈决策、发布门禁和下一周期机制。",
            "",
            "## 关键指标",
            "",
            f"- 任务：{current['tasks']['done']}/{current['tasks']['total']}（{current['tasks']['percent']:.1f}%）",
            f"- Must：{current['tasks']['priority']['must']['done']}/{current['tasks']['priority']['must']['total']}",
            f"- 章节：{current['chapters']['total']}",
            f"- 实验：SHIP {triage['SHIP']} · KEEP-EXT {triage['KEEP-EXT']} · ALREADY {triage['ALREADY']}",
            "",
            "## 已知缺口",
            "",
            *gap_lines,
            "",
            "## 产物与来源",
            "",
            f"- Source commit/fingerprint：`{readiness['source_id']}`",
            "- HTML：候选 manifest 生成后填写文件名和 SHA-256。",
            "- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。",
            "- 驾驶舱：`site/index.html`",
            "- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form",
            "",
            "## 下一版本目标",
            "",
            "v0.2 draft 保持每周一节、一次实验、一次构建/审校和每月可读 Release；只有真实 v0.1 published receipt 后才激活。",
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
