#!/usr/bin/env python3
"""Generate the complete visual progress and audit projection."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from progress_core import (
    ProgressError,
    actor_identity,
    aggregate_progress,
    canonical_json,
    detect_events,
    load_facts,
    load_json,
    merge_events,
    read_events,
    serialize_events,
    source_identity,
    utc_now,
)
from progress_render import (
    append_changelog,
    render_current_markdown,
    render_dashboard,
    render_details,
    render_progress_page,
)
from validate_project import ProjectValidator
from validate_feedback import run_validation as validate_continuity


EXPLICIT_EVENT_TYPES = (
    "milestone_reached",
    "build_completed",
    "release_published",
    "feedback_decided",
    "cycle_opened",
)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="从版本化事实源生成进度、关键事件、快照和静态驾驶舱。"
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
    parser.add_argument("--event-summary", help="显式里程碑、构建或版本事件摘要。")
    parser.add_argument(
        "--dry-run", action="store_true", help="完成校验和计算，但不写入任何文件。"
    )
    return parser.parse_args(argv)


def _pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _safe_source_id(source_id: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", source_id).strip("-.")
    return (cleaned or "unknown")[-32:]


def _safe_timestamp(timestamp: str) -> str:
    return re.sub(r"[^0-9TZ]+", "", timestamp)


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


def _validate_generated_json(label: str, content: str) -> None:
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise ProgressError(f"生成的 {label} 不是有效 JSON: {exc}") from exc


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


def generate(args: argparse.Namespace) -> Dict[str, Any]:
    root = args.root.resolve()
    generated_at = args.generated_at or utc_now()
    explicit_event = _explicit_event(args)

    report = ProjectValidator(root).validate()
    if not report.ok:
        rendered = "\n".join(issue.render() for issue in report.errors)
        raise ProgressError(f"事实源校验失败，未写入生成文件：\n{rendered}")
    continuity = validate_continuity(root)
    if not continuity.ok:
        rendered = "\n".join(issue.render() for issue in continuity.issues)
        raise ProgressError(f"反馈/周期事实校验失败，未写入生成文件：\n{rendered}")

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
        explicit_event,
    )

    events_path = root / "progress" / "events" / "events.jsonl"
    existing_events_content = (
        events_path.read_text(encoding="utf-8") if events_path.exists() else ""
    )
    existing_events = read_events(events_path)
    all_events, new_events = merge_events(existing_events, candidates)
    projection = aggregate_progress(facts, source_id, generated_at)
    projection["recent_events"] = all_events[-10:]

    snapshots_dir = root / "progress" / "snapshots"
    source_suffix = _safe_source_id(source_id)
    matching_snapshots = sorted(snapshots_dir.glob(f"*-{source_suffix}.json")) if snapshots_dir.exists() else []
    should_snapshot = previous_facts is None or bool(new_events) or not matching_snapshots
    snapshot_name = matching_snapshots[-1].name if matching_snapshots else ""
    snapshot_content = ""
    if should_snapshot and not matching_snapshots:
        snapshot_name = f"{_safe_timestamp(generated_at)}-{source_suffix}.json"
        snapshot = {
            "schema_version": "1.0.0",
            "source_id": source_id,
            "captured_at": generated_at,
            "metrics": projection,
            "events": new_events,
        }
        snapshot_content = _pretty_json(snapshot)
    elif matching_snapshots:
        existing_snapshot = load_json(matching_snapshots[-1])
        if existing_snapshot.get("source_id") != source_id:
            raise ProgressError(f"快照 {matching_snapshots[-1]} 的来源身份冲突，拒绝覆盖")

    projection["latest_snapshot"] = (
        f"../progress/snapshots/{snapshot_name}" if snapshot_name else ""
    )
    current_json = _pretty_json(projection)
    current_markdown = render_current_markdown(projection, all_events)
    dashboard_html = render_dashboard(projection, all_events)
    progress_html = render_progress_page(facts, projection, root, all_events)
    details_html = render_details(facts, projection, root)
    events_content = existing_events_content
    if new_events:
        if events_content and not events_content.endswith("\n"):
            events_content += "\n"
        events_content += serialize_events(new_events)
    changelog_path = root / "progress" / "CHANGELOG.md"
    old_changelog = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else ""
    changelog = append_changelog(
        old_changelog,
        new_events,
        snapshot_name,
        source_id,
    )
    baseline = _pretty_json(
        {"schema_version": "1.0.0", "source_id": source_id, "facts": facts}
    )

    _validate_generated_json("current.json", current_json)
    _validate_generated_json("site/data/progress.json", current_json)
    if snapshot_content:
        _validate_generated_json(snapshot_name, snapshot_content)
    if "<main id=\"main\">" not in dashboard_html or "下一动作" not in dashboard_html:
        raise ProgressError("驾驶舱缺少核心语义区域，拒绝发布")
    required_progress_markers = (
        'id="progress-timeline"',
        'id="chapter-production"',
        'id="experiment-production"',
        'id="blocker-production"',
        'id="task-drilldown"',
        'id="artifact-drilldown"',
        'id="github-drilldown"',
        'id="event-production"',
    )
    if any(marker not in progress_html for marker in required_progress_markers):
        raise ProgressError("生产线页缺少时间线、章节、实验、阻塞或事件语义区域，拒绝发布")
    if "id=\"task-D01-T01\"" not in details_html or "id=\"chapter-CH-01\"" not in details_html:
        raise ProgressError("对象下钻页缺少稳定锚点，拒绝发布")

    result = {
        "source_id": source_id,
        "actor": actor,
        "task_count": report.task_count,
        "chapter_count": report.chapter_count,
        "experiment_count": report.experiment_count,
        "new_event_count": len(new_events),
        "total_event_count": len(all_events),
        "snapshot": snapshot_name or None,
        "dry_run": args.dry_run,
    }
    if args.dry_run:
        return result

    # History first: reruns are idempotent through stable event IDs and source IDs.
    if snapshot_content:
        target = snapshots_dir / snapshot_name
        if target.exists():
            if canonical_json(load_json(target)) != canonical_json(json.loads(snapshot_content)):
                raise ProgressError(f"快照 {target} 已存在且内容冲突，拒绝覆盖")
        else:
            _atomic_write(target, snapshot_content)
    _atomic_write(events_path, events_content)
    _atomic_write(changelog_path, changelog)

    # Replaceable projections are published only after all candidates validate.
    _atomic_write(root / "progress" / "generated" / "current.json", current_json)
    _atomic_write(root / "progress" / "generated" / "current.md", current_markdown)
    _atomic_write(root / "site" / "data" / "progress.json", current_json)
    _atomic_write(root / "site" / "index.html", dashboard_html)
    _atomic_write(root / "site" / "progress.html", progress_html)
    _atomic_write(root / "site" / "details.html", details_html)

    # The comparison baseline is the final success marker.
    _atomic_write(baseline_path, baseline)
    return result


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        result = generate(args)
    except (ProgressError, OSError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    mode = "DRY-RUN" if result["dry_run"] else "OK"
    print(
        f"[{mode}] source={result['source_id']} tasks={result['task_count']} "
        f"chapters={result['chapter_count']} experiments={result['experiment_count']} "
        f"new_events={result['new_event_count']} total_events={result['total_event_count']} "
        f"snapshot={result['snapshot'] or 'none'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
