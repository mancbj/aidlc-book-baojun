#!/usr/bin/env python3
"""Create a v0.2 preview or activate it from a real GitHub release.published event."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from check_release_readiness import build_report as build_readiness_report
from validate_feedback import validate_cycle_document


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def receipt_from_event(path: Path, source_sha: str) -> Dict[str, Any]:
    event = json.loads(path.read_text(encoding="utf-8"))
    if event.get("action") != "published" or not isinstance(event.get("release"), dict):
        raise ValueError("只接受 GitHub release.published event")
    release = event["release"]
    if release.get("tag_name") != "v0.1" or release.get("draft") is True:
        raise ValueError("只允许已发布且非 draft 的 v0.1 激活下一周期")
    published_at = release.get("published_at")
    if not isinstance(published_at, str) or not published_at:
        raise ValueError("release event 缺少 published_at")
    return {
        "schema_version": "1.0.0",
        "version": "v0.1",
        "status": "published",
        "tag": release["tag_name"],
        "source_sha": source_sha,
        "published_at": published_at,
        "url": release.get("html_url", ""),
        "release_id": release.get("id"),
    }


def same_published_release(existing: Dict[str, Any], incoming: Dict[str, Any]) -> bool:
    return all(
        existing.get(field) == incoming.get(field)
        for field in ("version", "tag", "source_sha", "published_at", "release_id")
    )


def activate_cycle(
    root: Path,
    receipt: Dict[str, Any],
    generated_at: str,
    readiness: Dict[str, Any],
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    cycles_path = root / "progress/cycles.json"
    cycles = json.loads(cycles_path.read_text(encoding="utf-8"))
    feedback = json.loads((root / "feedback/decisions.json").read_text(encoding="utf-8"))
    tasks = json.loads((root / "progress/tasks.json").read_text(encoding="utf-8"))
    target = next((item for item in cycles.get("cycles", []) if item.get("id") == "v0.2-draft"), None)
    if target is None:
        raise ValueError("progress/cycles.json 缺少 v0.2-draft preview")
    target["status"] = "active"
    target["origin_release"] = receipt
    accepted = [item for item in feedback.get("decisions", []) if item.get("decision") == "accepted"]
    target["accepted_feedback"] = sorted(item["id"] for item in accepted)
    target["carried_tasks"] = [
        {
            "id": item["id"],
            "title": item["title"],
            "priority": item["priority"],
            "status": item["status"],
        }
        for item in tasks.get("tasks", [])
        if item.get("status") != "done"
    ]
    target["carried_gaps"] = [
        {"code": item["code"], "object": item["object"], "priority": item["priority"]}
        for item in readiness.get("gaps", [])
        if item.get("priority") == "known-gap"
    ]
    existing_ids = {task["id"] for task in target.get("tasks", [])}
    next_number = max((int(task_id.split("T")[1]) for task_id in existing_ids), default=0) + 1
    for item in accepted:
        linked = item.get("linked_task", "")
        if linked.startswith("C02-") and linked not in existing_ids:
            task_id = linked
        elif linked.startswith("C02-"):
            continue
        else:
            task_id = f"C02-T{next_number:02d}"
            next_number += 1
        target.setdefault("tasks", []).append(
            {
                "id": task_id,
                "title": f"处理 {item['id']} · {item['object']}",
                "kind": "content",
                "priority": "must",
                "status": "backlog",
                "dependencies": ["C02-T03"],
                "acceptance": list(item.get("acceptance", [])),
                "feedback_id": item["id"],
            }
        )
        existing_ids.add(task_id)
    cycles["active_cycle"] = target["id"]
    cycles["updated"] = generated_at
    issues = validate_cycle_document(cycles, "progress/cycles.json")
    if issues:
        raise ValueError("\n".join(issue.render() for issue in issues))
    return cycles, target


def render_markdown(cycle: Dict[str, Any]) -> str:
    origin = cycle.get("origin_release") or {}
    lines = [
        "# v0.2 Draft · Continuous Update Cycle",
        "",
        f"- Status: `{cycle['status']}`",
        f"- Origin release: `{origin.get('version', 'waiting-for-v0.1')}`",
        f"- Source: `{origin.get('source_sha', 'pending')}`",
        f"- Monthly target: {cycle['monthly_target']}",
        "",
        "## Cadence",
        "",
        "- 每周至少一节可读内容。",
        "- 每周至少一次实验运行与结果更新。",
        "- 每周至少一次构建或审校。",
        "- 每月至少一个可读 Release。",
        "",
        "## Tasks",
        "",
    ]
    for task in cycle.get("tasks", []):
        lines.append(f"- [{task['status']}] **{task['id']} · {task['title']}** — {task['priority']} / {task['kind']}")
    lines.extend(["", "## Accepted feedback", ""])
    lines.extend(f"- `{item}`" for item in cycle.get("accepted_feedback", []))
    if not cycle.get("accepted_feedback"):
        lines.append("- 当前没有 accepted feedback；使用默认节奏和公开缺口。")
    lines.extend(["", "## Carried unfinished tasks", ""])
    lines.extend(
        f"- `{item['id']}` · {item['title']} — {item['priority']} / {item['status']}"
        for item in cycle.get("carried_tasks", [])
    )
    if not cycle.get("carried_tasks"):
        lines.append("- 当前没有需要带入的 v0.1 未完成项。")
    lines.extend(["", "## Carried known gaps", ""])
    lines.extend(
        f"- `{item['code']}` · {item['object']} — {item['priority']}"
        for item in cycle.get("carried_gaps", [])
    )
    if not cycle.get("carried_gaps"):
        lines.append("- 当前没有需要带入的公开缺口。")
    lines.append("")
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="预览或从真实 v0.1 发布事件激活下一周期。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release-event", type=Path)
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--generated-at")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--markdown", type=Path, default=Path("planning/releases/v0.2-draft.md"))
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    generated_at = args.generated_at or now_utc()
    try:
        cycles = json.loads((root / "progress/cycles.json").read_text(encoding="utf-8"))
        target = next(item for item in cycles["cycles"] if item["id"] == "v0.2-draft")
        receipt = None
        if args.release_event:
            if not args.source_sha:
                raise ValueError("真实 release event 必须提供 source SHA")
            receipt = receipt_from_event(args.release_event, args.source_sha)
            receipt_path = root / "releases/v0.1/release.json"
            existing_receipt = (
                json.loads(receipt_path.read_text(encoding="utf-8"))
                if receipt_path.is_file()
                else None
            )
            already_active = (
                args.apply
                and isinstance(existing_receipt, dict)
                and same_published_release(existing_receipt, receipt)
                and target.get("status") == "active"
                and isinstance(target.get("origin_release"), dict)
                and same_published_release(target["origin_release"], receipt)
            )
            if already_active:
                receipt = existing_receipt
            else:
                readiness = build_readiness_report(
                    root,
                    root / "planning/releases/v0.1-policy.json",
                    generated_at,
                )
                if readiness.get("status") != "ready":
                    raise ValueError(
                        f"v0.1 readiness 仍为 blocked（{readiness['summary']['blockers']} blockers），拒绝激活周期"
                    )
                if readiness.get("source_id") != args.source_sha:
                    raise ValueError("release source SHA 与实时 readiness source 不一致")
                receipt["readiness_source_id"] = readiness["source_id"]
                cycles, target = activate_cycle(root, receipt, generated_at, readiness)
        if args.apply and receipt is None:
            raise ValueError("没有真实 release.published receipt 时不能 --apply 激活周期")
        if args.apply:
            atomic_json(root / "progress/cycles.json", cycles)
            atomic_json(root / "releases/v0.1/release.json", receipt)
        markdown = args.markdown if args.markdown.is_absolute() else root / args.markdown
        markdown.parent.mkdir(parents=True, exist_ok=True)
        markdown.write_text(render_markdown(target), encoding="utf-8")
    except (OSError, ValueError, StopIteration, json.JSONDecodeError) as exc:
        print(f"[ERROR] next cycle failed: {exc}")
        return 1
    mode = "ACTIVE" if args.apply else "PREVIEW"
    print(f"[{mode}] cycle={target['id']} tasks={len(target['tasks'])} origin={target.get('origin_release') or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
