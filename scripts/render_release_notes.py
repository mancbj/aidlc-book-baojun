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
    if version.startswith("v0.8.002") or version.startswith("v0.8.00") and not version.startswith("v0.8.001"):
        # Prefer exact patch notes for v0.8.002+; fall through carefully below for 001.
        pass
    if version.startswith("v0.8.002"):
        highlights = [
            "- 四个 KEEP-EXT 收尾转 verified：`EXP-07-03`、`EXP-08-03`、`EXP-09-03`、`EXP-10-03`（triage 不改写为 SHIP）。",
            "- 全部实验 verified=30/30；CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT。",
            "- CH-07 / CH-08 / CH-09 / CH-10 证据边界收紧；明确 CH-07 Verify ≠ CH-08 Runtime Verify。",
            "- Reader 无真实回复时保留 `READER-RESPONSES` known-gap；下一版默认 `v0.8.003`。",
        ]
        next_goal = "v0.8.003：消化真实 Reader 反馈，或开启新内容/度量周期。"
    elif version.startswith("v0.8.001"):
        highlights = [
            "- 版本颗粒度改为 patch-grain：`v0.8.001`（见 `planning/releases/VERSIONING.md`）。",
            "- 四个 KEEP-EXT 冻结复现转 verified：`EXP-01-03`、`EXP-02-03`、`EXP-03-03`、`EXP-06-03`（triage 不改写为 SHIP）。",
            "- CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT；SHIP 仍为 18/18。",
            "- CH-01 / CH-02 / CH-03 / CH-06 证据边界收紧；Reader 无真实回复时保留 `READER-RESPONSES` known-gap。",
        ]
        next_goal = "v0.8.002：消化真实 Reader 反馈，并推进剩余 KEEP-EXT（07-03 / 08-03 / 09-03 / 10-03）。"
    elif version.startswith("v0.8.") :
        highlights = [
            "- 继续 patch-grain 发布（见 `planning/releases/VERSIONING.md`）。",
            "- 推进 KEEP-EXT / Reader 反馈治理，并保持合同测试可复现。",
            "- 章节证据边界与过宣称条款保持收紧。",
            "- Reader 无真实回复时保留 `READER-RESPONSES` known-gap。",
        ]
        next_goal = "下一 patch：消化真实 Reader 反馈或开启新内容周期。"
    elif version.startswith("v0.8"):
        highlights = [
            "- 两个 ALREADY 实验转 verified：`EXP-07-01`、`EXP-08-01`（triage 保持 ALREADY，不改写为 SHIP）。",
            "- 两个 KEEP-EXT 冻结复现转 verified：`EXP-04-03`、`EXP-05-03`（仅消费仓库内 pin 夹具，CI 不抓外网）。",
            "- CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT；SHIP 仍为 18/18。",
            "- CH-04 / CH-05 / CH-07 / CH-08 证据边界收紧；Reader 无真实回复时保留 `READER-RESPONSES` known-gap。",
        ]
        next_goal = "v0.8.001：改用 patch-grain 版本号，继续推进剩余 KEEP-EXT 冻结复现。"
    elif version.startswith("v0.7"):
        highlights = [
            "- 四个冻结证据实验转 verified：`EXP-01-01`、`EXP-01-02`、`EXP-02-02`、`EXP-07-02`（无在线模型调用）。",
            "- SHIP verified 达到 18/18；CI 合同测试覆盖全部 SHIP。",
            "- CH-01 / CH-02 / CH-07 证据边界收紧，明确冻结夹具不等于生产模型保证。",
            "- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。",
        ]
        next_goal = "v0.8：消化真实 Reader 反馈，并按需推进 KEEP-EXT / ALREADY 实验或新内容周期。"
    elif version.startswith("v0.6"):
        highlights = [
            "- 四个目标实验转 verified：`EXP-05-02`、`EXP-08-02`、`EXP-09-02`、`EXP-10-02`，并由 CI 执行合同测试。",
            "- SHIP verified 达到 14/18；剩余 planned 主要为需冻结会话/模型证据的批次。",
            "- CH-05 / CH-08 / CH-09 / CH-10 证据边界收紧，过宣称条款明确。",
            "- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。",
        ]
        next_goal = "v0.7：推进剩余 planned 实验（冻结会话/模型评审夹具），并在收到真实 Reader 回复后关闭反馈缺口。"
    elif version.startswith("v0.5"):
        highlights = [
            "- 四个目标实验转 verified：`EXP-05-01`、`EXP-09-01`、`EXP-10-01`、`EXP-06-02`，并由 CI 执行合同测试。",
            "- SHIP verified 达到 10/18；继续保持确定性可复现边界，不伪装模型方差实验。",
            "- CH-05 / CH-06 / CH-09 / CH-10 证据边界收紧，过宣称条款明确。",
            "- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。",
        ]
        next_goal = "v0.6：继续推进剩余 planned 实验（含需冻结会话/模型证据的批次），并在收到真实 Reader 回复后关闭反馈缺口。"
    elif version.startswith("v0.4"):
        highlights = [
            "- 四个目标实验转 verified：`EXP-03-02`、`EXP-06-01`、`EXP-02-01`、`EXP-04-02`，并由 CI 执行合同测试。",
            "- CH-02～CH-10 九张独立可审计章节 SVG；CH-01 继续复用核心图 `fig0-1.svg`。",
            "- 章节图注册表、构建哈希与 strict audit 门禁进入主线。",
            "- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。",
        ]
        next_goal = "v0.5：继续推进剩余 planned 实验，并在收到真实 Reader 回复后关闭反馈缺口。"
    elif version.startswith("v0.3"):
        highlights = [
            "- 出版质量 Loop：release profile 剥离 Metadata / Gate / Review Notes 等写作脚手架。",
            "- 书稿 HTML 设计系统升级（品牌级标题、衬线字体、青绿强调与可读动效）。",
            "- 书稿 PDF 章节分页与页边距优化；十章正式可读稿保持完整。",
            "- 内容边界收紧：Runtime Verify 与 CH-07 验证区分；ready/planned 实验不再过宣称。",
        ]
        next_goal = "v0.4：推进 planned 实验实现、独立章节 SVG，并消化 Reader 反馈缺口。"
    elif version.startswith("v0.2"):
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
