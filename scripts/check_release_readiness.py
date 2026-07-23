#!/usr/bin/env python3
"""Evaluate the real repository against the machine-readable v0.1 policy."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from progress_core import load_facts, source_identity
from validate_feedback import run_validation as validate_continuity
from validate_project import ProjectValidator


GAP_ORDER = {"must-blocker": 0, "must-missing": 1, "review-required": 2, "known-gap": 3}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def meaningful_markdown(path: Path, minimum: int, markers: Sequence[str]) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    return len(text.strip()) >= minimum and not any(marker.lower() in text.lower() for marker in markers)


def build_report(root: Path, policy_path: Path, generated_at: Optional[str] = None) -> Dict[str, Any]:
    root = root.resolve()
    policy_path = policy_path.resolve()
    policy = json.loads(policy_path.read_text(encoding="utf-8"))
    facts = load_facts(root)
    source_id = source_identity(root, facts)
    gaps: List[Dict[str, str]] = []

    def gap(code: str, priority: str, object_id: str, evidence: str, fix: str, owner: str = "author") -> None:
        gaps.append({"code": code, "priority": priority, "object": object_id, "evidence": evidence, "fix": fix, "owner": owner})

    project = ProjectValidator(root).validate()
    for issue in project.errors:
        gap("FACT-INVALID", "must-blocker", issue.object_id, issue.render(), issue.fix, "maintainer")
    continuity = validate_continuity(root)
    for issue in continuity.issues:
        gap("CONTINUITY-INVALID", "must-blocker", issue.object_id, issue.render(), issue.fix, "maintainer")

    tasks = facts["tasks"].get("tasks", [])
    for task in tasks:
        if task.get("priority") != "must" or task.get("status") == "done":
            continue
        code = "MUST-BLOCKED" if task.get("status") == "blocked" else "MUST-NOT-DONE"
        priority = "must-blocker" if task.get("status") == "blocked" else "must-missing"
        gap(code, priority, task["id"], f"status={task.get('status')}", "完成依赖、产物与全部二元验收后设为 done。")

    chapters = facts["chapters"].get("chapters", [])
    questions = [str(item.get("question", "")).strip() for item in chapters]
    if len(chapters) < int(policy["minimum_chapters"]) or len(set(questions)) != len(questions) or any(not value for value in questions):
        gap("CHAPTER-STRUCTURE", "must-missing", "chapters", f"count={len(chapters)}, unique_questions={len(set(questions))}", "保持十章且每章核心问题非空、唯一。")

    sample = root / policy["sample_chapter"]
    if not meaningful_markdown(sample, int(policy["sample_minimum_characters"]), policy["placeholder_markers"]):
        gap("SAMPLE-NOT-READABLE", "must-missing", policy["sample_chapter"], "文件缺失、过短或仍含占位标记。", "完成非模板样章并达到最小结构/长度门禁。")

    experiment_ready = False
    for experiment in facts["experiments"].get("experiments", []):
        if experiment.get("triage") != "SHIP" or experiment.get("status") not in policy["validated_experiment_statuses"]:
            continue
        paths = [experiment.get(name) for name in ("repository_path", "readme_path", "sample_input", "sample_output", "test_path")]
        if all(isinstance(path, str) and (root / path).exists() for path in paths):
            experiment_ready = True
            break
    if not experiment_ready:
        gap("SHIP-NOT-VERIFIED", "must-missing", "experiments", "没有 SHIP 同时满足 verified 和 README/输入/输出/测试。", "完成一个 10 分钟可复现实验并把事实状态设为 verified。")

    figure = root / policy["core_figure"]
    if not figure.is_file():
        gap("CORE-FIGURE-MISSING", "must-missing", policy["core_figure"], "核心图不存在。", "创建图并在样章记录源文件与再生成方法。")
    elif sample.is_file() and policy["core_figure"] not in sample.read_text(encoding="utf-8"):
        gap("CORE-FIGURE-UNREFERENCED", "review-required", policy["core_figure"], "样章未引用核心图路径。", "在样章引用并解释核心图。")

    review = root / policy["sample_review"]
    review_text = review.read_text(encoding="utf-8") if review.is_file() else ""
    categories_present = all(category in review_text for category in policy["required_review_categories"])
    if not categories_present or review_text.count("- 结论：pass") < len(policy["required_review_categories"]):
        gap("REVIEW-INCOMPLETE", "review-required", policy["sample_review"], "五类审校尚未全部明确 pass。", "逐类记录结论、问题、影响、建议和关闭证据。")

    for key in ("learning_guide", "reader_guide", "feedback_template", "feedback_facts"):
        relative = policy[key]
        if not (root / relative).is_file():
            gap("ENTRY-MISSING", "must-missing", relative, f"{key} 不存在。", "创建非占位入口。")
    if not (root / "site/index.html").is_file():
        gap("HTML-MISSING", "must-missing", "site/index.html", "HTML 驾驶舱不存在。", "运行进度生成和 Pages 构建。")

    feedback = facts.get("feedback", {}).get("readers", [])
    responded = sum(reader.get("status") == "responded" for reader in feedback)
    if responded < 3:
        gap("READER-RESPONSES", "known-gap", "Reader-A/B/C", f"responded={responded}/3", "保留反馈入口；真实邀请/响应后更新匿名槽位。")

    if policy.get("pdf_required") and not (root / "releases/v0.1-rc/ai-dlc-book-v0.1.pdf").is_file():
        gap("PDF-REQUIRED", "must-blocker", "v0.1.pdf", "policy 要求 PDF，但文件不存在。", "生成并验证 PDF，或经批准修改 policy。")

    gaps.sort(key=lambda item: (GAP_ORDER[item["priority"]], item["code"], item["object"]))
    blockers = [item for item in gaps if item["priority"] in {"must-blocker", "must-missing", "review-required"}]
    return {
        "schema_version": "1.0.0",
        "version": policy["version"],
        "status": "ready" if not blockers else "blocked",
        "generated_at": generated_at or now_utc(),
        "source_id": source_id,
        "policy": str(policy_path.relative_to(root)) if root in policy_path.parents else str(policy_path),
        "summary": {"blockers": len(blockers), "known_gaps": len(gaps) - len(blockers), "total_gaps": len(gaps)},
        "checks": {
            "tasks_total": len(tasks),
            "must_total": sum(task.get("priority") == "must" for task in tasks),
            "must_done": sum(task.get("priority") == "must" and task.get("status") == "done" for task in tasks),
            "chapters": len(chapters),
            "responded_readers": responded,
            "html_required": bool(policy["html_required"]),
            "pdf_required": bool(policy["pdf_required"]),
        },
        "gaps": gaps,
        "next_action": blockers[0]["fix"] if blockers else "构造同源候选并执行人工发布审阅。",
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        f"# {report['version']} Release Readiness",
        "",
        f"**Status: {report['status'].upper()}**",
        "",
        f"- Source: `{report['source_id']}`",
        f"- Generated: `{report['generated_at']}`",
        f"- Blockers: {report['summary']['blockers']}",
        f"- Known gaps: {report['summary']['known_gaps']}",
        "",
        "| Priority | Code | Object | Evidence | Fix |",
        "|---|---|---|---|---|",
    ]
    for item in report["gaps"]:
        lines.append(f"| {item['priority']} | {item['code']} | `{item['object']}` | {item['evidence']} | {item['fix']} |")
    if not report["gaps"]:
        lines.append("| — | READY | v0.1 | 全部门禁通过 | 构造同源候选 |")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="执行真实 v0.1 发布门禁。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--policy", type=Path, default=Path("planning/releases/v0.1-policy.json"))
    parser.add_argument("--json-report", type=Path, default=Path("releases/v0.1-rc/readiness.json"))
    parser.add_argument("--markdown-report", type=Path, default=Path("releases/v0.1-rc/readiness.md"))
    parser.add_argument("--generated-at")
    parser.add_argument("--allow-blocked", action="store_true", help="仍写报告，但 blocked 时返回 0；只用于诊断。")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    policy = args.policy if args.policy.is_absolute() else root / args.policy
    report = build_report(root, policy, args.generated_at)
    json_path = args.json_report if args.json_report.is_absolute() else root / args.json_report
    md_path = args.markdown_report if args.markdown_report.is_absolute() else root / args.markdown_report
    json_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    print(f"[INFO] v0.1 readiness: status={report['status']}, blockers={report['summary']['blockers']}, known_gaps={report['summary']['known_gaps']}, source={report['source_id']}")
    return 0 if report["status"] == "ready" or args.allow_blocked else 1


if __name__ == "__main__":
    raise SystemExit(main())
