#!/usr/bin/env python3
"""Report roadmap evidence without changing any task state."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

from progress_core import load_facts, source_identity


EQUIVALENT_EVIDENCE = {
    "D06-T01": ["scripts/progress_core.py", "docs/PROGRESS-AUTOMATION.md"],
    "D06-T02": ["scripts/progress_core.py", "scripts/generate_progress.py"],
    "D07-T01": ["progress/snapshots", "progress/CHANGELOG.md"],
    "D08-T03": ["site/details.html"],
    "D09-T01": ["site/details.html"],
    "D09-T02": ["memory-bank/bolts/002-github-writing-system-ui/test-walkthrough.md"],
    "D09-T03": ["memory-bank/bolts/002-github-writing-system-ui/test-walkthrough.md"],
    "D10-T01": [".github/pull_request_template.md", ".github/ISSUE_TEMPLATE"],
    "D10-T02": [".github/labels.yml", "planning/github-milestones.md"],
    "D10-T03": ["planning/github-project.json", "docs/GITHUB-PROJECTS.md"],
    "D11-T03": [".github/workflows/release.yml", "scripts/prepare_release.py", "planning/reviews/tag-release-gate.md"],
}


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_report(root: Path, generated_at: Optional[str] = None) -> Dict[str, Any]:
    root = root.resolve()
    facts = load_facts(root)
    rows = []
    counts = {"verified": 0, "artifact-present-review-required": 0, "missing": 0, "path-divergence": 0}
    for task in facts["tasks"].get("tasks", []):
        declared = [item["path"] for item in task.get("artifacts", []) if item.get("required")]
        missing = [path for path in declared if not (root / path).exists()]
        equivalents = [path for path in EQUIVALENT_EVIDENCE.get(task["id"], []) if (root / path).exists()]
        if task.get("status") == "done":
            classification = "verified"
            action = "保持历史状态；变更需形成新事件。"
        elif not missing:
            classification = "artifact-present-review-required"
            action = "人工核对验收后，再通过 tasks.json 正常状态流更新。"
        elif equivalents:
            classification = "path-divergence"
            action = "确认等价实现后更新声明路径或补兼容入口；不得静默 done。"
        else:
            classification = "missing"
            action = "完成声明产物与验收。"
        counts[classification] += 1
        rows.append(
            {
                "id": task["id"],
                "priority": task["priority"],
                "status": task["status"],
                "classification": classification,
                "declared_artifacts": declared,
                "missing_artifacts": missing,
                "equivalent_evidence": equivalents,
                "next_action": action,
            }
        )
    return {
        "schema_version": "1.0.0",
        "generated_at": generated_at or now_utc(),
        "source_id": source_identity(root, facts),
        "authority": "report-only-no-task-write",
        "counts": counts,
        "tasks": rows,
    }


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# Roadmap Evidence Audit",
        "",
        "> 本报告只比较事实与证据，不自动修改 `progress/tasks.json`。",
        "",
        f"- Source: `{report['source_id']}`",
        f"- Generated: `{report['generated_at']}`",
        "",
        "| Task | Priority | State | Evidence class | Next action |",
        "|---|---|---|---|---|",
    ]
    for item in report["tasks"]:
        lines.append(
            f"| {item['id']} | {item['priority']} | {item['status']} | {item['classification']} | {item['next_action']} |"
        )
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="审计 42 个路线任务的现有证据，不改状态。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json-report", type=Path)
    parser.add_argument("--markdown-report", type=Path, default=Path("planning/releases/roadmap-evidence.md"))
    parser.add_argument("--generated-at")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    report = build_report(root, args.generated_at)
    markdown_path = args.markdown_report if args.markdown_report.is_absolute() else root / args.markdown_report
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    if args.json_report:
        json_path = args.json_report if args.json_report.is_absolute() else root / args.json_report
        json_path.parent.mkdir(parents=True, exist_ok=True)
        json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("[INFO] roadmap evidence: " + ", ".join(f"{key}={value}" for key, value in report["counts"].items()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
