#!/usr/bin/env python3
"""Record progress state-difference events without regenerating projections."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from progress_core import (
    ProgressError,
    actor_identity,
    detect_events,
    load_facts,
    load_json,
    merge_events,
    read_events,
    serialize_events,
    source_identity,
    utc_now,
)
from validate_feedback import run_validation as validate_continuity
from validate_project import ProjectValidator


EXPLICIT_EVENT_TYPES = (
    "milestone_reached",
    "build_completed",
    "release_published",
    "feedback_decided",
    "cycle_opened",
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="比较当前事实源与最后成功基线，并只追加关键事件账本。"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="仓库根目录；默认从脚本位置推断。",
    )
    parser.add_argument("--actor", help="事件操作者；默认读取 CI/Git/系统身份。")
    parser.add_argument("--generated-at", help="带时区 ISO 8601 时间；测试时可固定。")
    parser.add_argument("--event-type", choices=EXPLICIT_EVENT_TYPES)
    parser.add_argument("--event-object", help="显式事件的稳定对象 ID。")
    parser.add_argument("--event-summary", help="显式事件摘要。")
    parser.add_argument("--dry-run", action="store_true", help="只计算，不写入事件账本。")
    parser.add_argument("--report", type=Path, help="可选 JSON 报告路径。")
    return parser.parse_args(argv)


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent)
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(str(temporary_path), str(path))
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


def _load_previous_facts(path: Path) -> Optional[Dict[str, Dict[str, Any]]]:
    if not path.exists():
        return None
    document = load_json(path)
    facts = document.get("facts")
    if not isinstance(facts, dict):
        raise ProgressError(f"{path} 缺少 facts object")
    return facts


def _explicit_event(args: argparse.Namespace) -> Optional[Tuple[str, str, str]]:
    supplied = [args.event_type, args.event_object, args.event_summary]
    if any(supplied) and not all(supplied):
        raise ProgressError(
            "显式事件必须同时提供 --event-type、--event-object 和 --event-summary"
        )
    if not args.event_type:
        return None
    return args.event_type, args.event_object.strip(), args.event_summary.strip()


def record(args: argparse.Namespace) -> Dict[str, Any]:
    root = args.root.resolve()
    generated_at = args.generated_at or utc_now()

    report = ProjectValidator(root).validate()
    if not report.ok:
        rendered = "\n".join(issue.render() for issue in report.errors)
        raise ProgressError(f"事实源校验失败，未写入事件：\n{rendered}")
    continuity = validate_continuity(root)
    if not continuity.ok:
        rendered = "\n".join(issue.render() for issue in continuity.issues)
        raise ProgressError(f"反馈/周期事实校验失败，未写入事件：\n{rendered}")

    facts = load_facts(root)
    source_id = source_identity(root, facts)
    actor = actor_identity(root, args.actor)
    baseline_path = root / "progress" / "generated" / "last-successful-facts.json"
    previous_facts = _load_previous_facts(baseline_path)
    candidates = detect_events(
        previous_facts,
        facts,
        source_id,
        actor,
        generated_at,
        _explicit_event(args),
    )

    events_path = root / "progress" / "events" / "events.jsonl"
    existing_content = events_path.read_text(encoding="utf-8") if events_path.exists() else ""
    existing_events = read_events(events_path)
    all_events, new_events = merge_events(existing_events, candidates)
    next_content = existing_content
    if new_events:
        if next_content and not next_content.endswith("\n"):
            next_content += "\n"
        next_content += serialize_events(new_events)

    result = {
        "schema_version": "1.0.0",
        "source_id": source_id,
        "actor": actor,
        "generated_at": generated_at,
        "candidate_event_count": len(candidates),
        "new_event_count": len(new_events),
        "total_event_count": len(all_events),
        "dry_run": args.dry_run,
        "events_path": str(events_path.relative_to(root)),
    }
    if not args.dry_run:
        _atomic_write(events_path, next_content)
    if args.report:
        report_path = args.report if args.report.is_absolute() else root / args.report
        _atomic_write(report_path, json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        result = record(args)
    except (ProgressError, OSError) as exc:
        print(f"[ERROR] {exc}", file=os.sys.stderr)
        return 1
    mode = "DRY-RUN" if result["dry_run"] else "OK"
    print(
        f"[{mode}] source={result['source_id']} candidates={result['candidate_event_count']} "
        f"new_events={result['new_event_count']} total_events={result['total_event_count']} "
        f"path={result['events_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
