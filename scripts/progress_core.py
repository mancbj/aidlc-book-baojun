#!/usr/bin/env python3
"""Pure progress aggregation and event-detection helpers."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


TASK_STATUSES = ["backlog", "ready", "in-progress", "review", "done", "blocked"]
PRIORITIES = ["must", "should", "could"]
PRIORITY_WEIGHTS = {"must": 3, "should": 2, "could": 1}
NEXT_STATUS_ORDER = {"review": 0, "in-progress": 1, "ready": 2, "backlog": 3}
CHAPTER_STAGE_NAMES = [
    "question",
    "framework",
    "example",
    "experiment",
    "figure",
    "review",
]
CHAPTER_STAGE_LABELS = {
    "question": "问题",
    "framework": "框架",
    "example": "案例",
    "experiment": "实验",
    "figure": "图示",
    "review": "审校",
}
STATUS_LABELS = {
    "backlog": "待排期",
    "ready": "可开始",
    "in-progress": "进行中",
    "review": "待审校",
    "done": "已完成",
    "blocked": "受阻",
    "pending": "待开始",
    "planned": "已计划",
    "verified": "已验证",
}


class ProgressError(RuntimeError):
    """Raised when a generated progress artifact would be unsafe or invalid."""


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def load_json(path: Path) -> Dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ProgressError(f"无法读取 {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProgressError(f"{path} 顶层必须是 JSON object")
    return value


def load_facts(root: Path) -> Dict[str, Dict[str, Any]]:
    root = root.resolve()
    facts = {
        "tasks": load_json(root / "progress" / "tasks.json"),
        "chapters": load_json(root / "progress" / "chapters.json"),
        "experiments": load_json(root / "progress" / "experiments.json"),
    }
    feedback_path = root / "feedback" / "decisions.json"
    cycles_path = root / "progress" / "cycles.json"
    facts["feedback"] = (
        load_json(feedback_path)
        if feedback_path.is_file()
        else {"schema_version": "1.0.0", "updated": "", "readers": [], "decisions": []}
    )
    facts["cycles"] = (
        load_json(cycles_path)
        if cycles_path.is_file()
        else {"schema_version": "1.0.0", "updated": "", "active_cycle": None, "cycles": []}
    )
    return facts


def facts_fingerprint(facts: Dict[str, Dict[str, Any]]) -> str:
    digest = hashlib.sha256(canonical_json(facts).encode("utf-8")).hexdigest()
    return digest


def source_identity(root: Path, facts: Dict[str, Dict[str, Any]]) -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        commit = result.stdout.strip()
        if commit:
            fact_paths = (
                "progress/tasks.json",
                "progress/chapters.json",
                "progress/experiments.json",
                "feedback/decisions.json",
                "progress/cycles.json",
            )
            status = subprocess.run(
                ["git", "status", "--porcelain", "--", *fact_paths],
                cwd=str(root),
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
            )
            if status.stdout.strip():
                return f"{commit[:12]}-working-tree-{facts_fingerprint(facts)[:12]}"
            return commit
    except (OSError, subprocess.CalledProcessError):
        pass
    return f"working-tree-{facts_fingerprint(facts)[:12]}"


def actor_identity(root: Path, explicit_actor: Optional[str] = None) -> str:
    if explicit_actor and explicit_actor.strip():
        return explicit_actor.strip()
    for variable in ("GITHUB_ACTOR", "USER"):
        value = os.environ.get(variable, "").strip()
        if value:
            return value
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            cwd=str(root),
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        pass
    return "unknown"


def percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator * 100.0) / denominator, 1)


def _count_by(records: Iterable[Dict[str, Any]], key: str, values: Sequence[str]) -> Dict[str, int]:
    counts = {value: 0 for value in values}
    for record in records:
        value = record.get(key)
        if value not in counts:
            counts[str(value)] = 0
        counts[str(value)] += 1
    return counts


def _task_summary(task: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": task["id"],
        "title": task["title"],
        "day": task["day"],
        "status": task["status"],
        "status_label": STATUS_LABELS.get(task["status"], task["status"]),
        "priority": task["priority"],
        "owner": task["owner"],
        "planned_date": task["planned_date"],
        "dependencies": task.get("dependencies", []),
        "artifacts": task.get("artifacts", []),
        "acceptance": task.get("acceptance", []),
        "href": f"details.html#task-{task['id']}",
    }


def _cycle_task_summary(task: Dict[str, Any], cycle: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": task["id"],
        "title": task["title"],
        "day": "CYCLE",
        "scope_label": cycle["id"],
        "status": task["status"],
        "status_label": STATUS_LABELS.get(task["status"], task["status"]),
        "priority": task["priority"],
        "owner": "author",
        "planned_date": cycle.get("monthly_target", "v0.2"),
        "dependencies": task.get("dependencies", []),
        "artifacts": [],
        "acceptance": [{"text": item, "passed": False} for item in task.get("acceptance", [])],
        "href": f"details.html#cycle-task-{task['id']}",
    }


def aggregate_progress(
    facts: Dict[str, Dict[str, Any]], source_id: str, generated_at: str
) -> Dict[str, Any]:
    tasks = list(facts["tasks"].get("tasks", []))
    chapters = list(facts["chapters"].get("chapters", []))
    experiments = list(facts["experiments"].get("experiments", []))
    feedback_decisions = list(facts.get("feedback", {}).get("decisions", []))
    readers = list(facts.get("feedback", {}).get("readers", []))
    cycles = list(facts.get("cycles", {}).get("cycles", []))
    active_cycle_id = facts.get("cycles", {}).get("active_cycle")
    active_cycle = next(
        (cycle for cycle in cycles if cycle.get("id") == active_cycle_id and cycle.get("status") == "active"),
        None,
    )
    task_by_id = {task["id"]: task for task in tasks}

    done_count = sum(task.get("status") == "done" for task in tasks)
    total_weight = sum(PRIORITY_WEIGHTS.get(task.get("priority"), 0) for task in tasks)
    done_weight = sum(
        PRIORITY_WEIGHTS.get(task.get("priority"), 0)
        for task in tasks
        if task.get("status") == "done"
    )
    priority_metrics: Dict[str, Dict[str, Any]] = {}
    for priority in PRIORITIES:
        matching = [task for task in tasks if task.get("priority") == priority]
        completed = sum(task.get("status") == "done" for task in matching)
        priority_metrics[priority] = {
            "total": len(matching),
            "done": completed,
            "percent": percent(completed, len(matching)),
            "has_sample": bool(matching),
        }

    unfinished = [task for task in tasks if task.get("status") != "done"]
    current_day = min((int(task["day"]) for task in unfinished), default=14)
    all_done = bool(tasks) and not unfinished

    next_candidates = []
    for task in tasks:
        if task.get("status") in {"done", "blocked"}:
            continue
        dependencies = task.get("dependencies", [])
        if all(task_by_id.get(dep, {}).get("status") == "done" for dep in dependencies):
            next_candidates.append(task)
    next_candidates.sort(
        key=lambda task: (
            PRIORITIES.index(task.get("priority")) if task.get("priority") in PRIORITIES else 99,
            NEXT_STATUS_ORDER.get(task.get("status"), 99),
            task.get("planned_date", "9999-12-31"),
            task.get("id", ""),
        )
    )
    next_actions = [_task_summary(task) for task in next_candidates[:5]]
    if active_cycle:
        cycle_by_id = {task["id"]: task for task in active_cycle.get("tasks", [])}
        cycle_candidates = []
        for task in active_cycle.get("tasks", []):
            if task.get("status") in {"done", "blocked"}:
                continue
            if all(cycle_by_id.get(dep, {}).get("status") == "done" for dep in task.get("dependencies", [])):
                cycle_candidates.append(task)
        cycle_candidates.sort(
            key=lambda task: (
                PRIORITIES.index(task.get("priority")) if task.get("priority") in PRIORITIES else 99,
                NEXT_STATUS_ORDER.get(task.get("status"), 99),
                task.get("id", ""),
            )
        )
        next_actions = [_cycle_task_summary(task, active_cycle) for task in cycle_candidates[:5]]

    blockers = []
    for task in sorted(
        (item for item in tasks if item.get("status") == "blocked"),
        key=lambda item: (item.get("day", 99), item.get("id", "")),
    ):
        item = _task_summary(task)
        item.update(
            {
                "reason": task.get("blocker_reason", ""),
                "unblock_action": task.get("unblock_action", ""),
            }
        )
        blockers.append(item)

    timeline = []
    for day in range(1, 15):
        day_tasks = [task for task in tasks if task.get("day") == day]
        day_done = sum(task.get("status") == "done" for task in day_tasks)
        day_blocked = sum(task.get("status") == "blocked" for task in day_tasks)
        timeline.append(
            {
                "day": day,
                "total": len(day_tasks),
                "done": day_done,
                "blocked": day_blocked,
                "percent": percent(day_done, len(day_tasks)),
                "is_current": day == current_day,
                "href": f"details.html#day-{day:02d}",
            }
        )

    chapter_rows = []
    chapter_stage_totals = {name: {"done": 0, "total": 0} for name in CHAPTER_STAGE_NAMES}
    for chapter in sorted(chapters, key=lambda item: item.get("number", 999)):
        stages = []
        first_gap: Optional[str] = None
        for stage in chapter.get("stages", []):
            name = stage.get("name", "")
            status = stage.get("status", "pending")
            if first_gap is None and status != "done":
                first_gap = name
            if name in chapter_stage_totals:
                chapter_stage_totals[name]["total"] += 1
                if status == "done":
                    chapter_stage_totals[name]["done"] += 1
            stages.append(
                {
                    "name": name,
                    "label": CHAPTER_STAGE_LABELS.get(name, name),
                    "status": status,
                    "status_label": STATUS_LABELS.get(status, status),
                }
            )
        chapter_done = sum(stage["status"] == "done" for stage in stages)
        chapter_rows.append(
            {
                "id": chapter["id"],
                "number": chapter["number"],
                "title": chapter["title"],
                "question": chapter["question"],
                "stages": stages,
                "done": chapter_done,
                "total": len(stages),
                "percent": percent(chapter_done, len(stages)),
                "next_gap": first_gap,
                "next_gap_label": CHAPTER_STAGE_LABELS.get(first_gap or "", "已完成"),
                "href": f"details.html#chapter-{chapter['id']}",
            }
        )
    for name, totals in chapter_stage_totals.items():
        totals["percent"] = percent(totals["done"], totals["total"])
        totals["label"] = CHAPTER_STAGE_LABELS[name]

    experiment_triage = _count_by(experiments, "triage", ["SHIP", "KEEP-EXT", "ALREADY"])
    experiment_status_values = sorted({str(item.get("status")) for item in experiments})
    experiment_status = _count_by(experiments, "status", experiment_status_values)
    feedback_counts = _count_by(
        feedback_decisions, "decision", ["pending", "accepted", "rejected", "deferred"]
    )
    reader_counts = _count_by(readers, "status", ["not-invited", "invited", "responded"])
    unresolved_accepted = sum(
        item.get("decision") == "accepted" and not item.get("linked_task")
        for item in feedback_decisions
    )
    cycle_rows = []
    for cycle in cycles:
        cycle_rows.append(
            {
                "id": cycle.get("id"),
                "status": cycle.get("status"),
                "monthly_target": cycle.get("monthly_target"),
                "task_total": len(cycle.get("tasks", [])),
                "task_done": sum(task.get("status") == "done" for task in cycle.get("tasks", [])),
                "carried_task_total": len(cycle.get("carried_tasks", [])),
                "carried_gap_total": len(cycle.get("carried_gaps", [])),
                "href": f"details.html#cycle-{cycle.get('id')}",
            }
        )

    timestamps = []
    for document in facts.values():
        if document.get("updated"):
            timestamps.append(document["updated"])
        collection_name = next(
            (name for name in ("tasks", "chapters", "experiments") if name in document),
            None,
        )
        if collection_name:
            timestamps.extend(
                str(item.get("updated"))
                for item in document[collection_name]
                if item.get("updated")
            )
    latest_fact_update = max(timestamps, default="")

    if active_cycle:
        release_message = "v0.1 已发布；执行下一周期首个 Must"
    elif not tasks:
        release_message = "尚未创建任务，请先初始化 14 天任务事实源"
    elif all_done:
        release_message = (
            "v0.1 已完成；执行下一周期首个 Must"
            if active_cycle
            else "准备 v0.1 发布；等待真实发布回执激活下一周期"
        )
    else:
        release_message = ""
    return {
        "schema_version": "1.0.0",
        "generated_at": generated_at,
        "source_id": source_id,
        "latest_fact_update": latest_fact_update,
        "goal": {
            "name": "两周形成可发布 v0.1",
            "total_days": 14,
            "current_day": current_day,
            "days_remaining": max(14 - current_day, 0),
            "all_tasks_done": all_done,
        },
        "tasks": {
            "total": len(tasks),
            "done": done_count,
            "percent": percent(done_count, len(tasks)),
            "weighted_percent": percent(done_weight, total_weight),
            "status_counts": _count_by(tasks, "status", TASK_STATUSES),
            "priority": priority_metrics,
            "timeline": timeline,
        },
        "chapters": {
            "total": len(chapters),
            "rows": chapter_rows,
            "stage_totals": chapter_stage_totals,
        },
        "experiments": {
            "total": len(experiments),
            "triage_counts": experiment_triage,
            "status_counts": experiment_status,
            "href": "details.html#experiments",
        },
        "feedback": {
            "total": len(feedback_decisions),
            "decision_counts": feedback_counts,
            "reader_counts": reader_counts,
            "unresolved_accepted": unresolved_accepted,
            "href": "details.html#feedback",
        },
        "cycles": {
            "active_cycle": active_cycle_id,
            "rows": cycle_rows,
            "preview_count": sum(cycle.get("status") == "preview" for cycle in cycles),
            "href": "details.html#cycles",
        },
        "blockers": blockers,
        "next_actions": next_actions,
        "release_message": release_message,
    }


def _index_by_id(records: Iterable[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {str(record["id"]): record for record in records}


def _event_id(
    event_type: str, object_type: str, object_id: str, before: Any, after: Any, source_id: str
) -> str:
    material = [event_type, object_type, object_id, before, after, source_id]
    return "EVT-" + hashlib.sha256(canonical_json(material).encode("utf-8")).hexdigest()[:16]


def _event(
    event_type: str,
    object_type: str,
    object_id: str,
    before: Any,
    after: Any,
    source_id: str,
    actor: str,
    occurred_at: str,
    summary: str,
) -> Dict[str, Any]:
    return {
        "id": _event_id(event_type, object_type, object_id, before, after, source_id),
        "occurred_at": occurred_at,
        "type": event_type,
        "object_type": object_type,
        "object_id": object_id,
        "before": before,
        "after": after,
        "source_id": source_id,
        "actor": actor,
        "summary": summary,
    }


def detect_events(
    previous_facts: Optional[Dict[str, Dict[str, Any]]],
    current_facts: Dict[str, Dict[str, Any]],
    source_id: str,
    actor: str,
    occurred_at: str,
    explicit_event: Optional[Tuple[str, str, str]] = None,
) -> List[Dict[str, Any]]:
    if previous_facts is None:
        events = [
            _event(
                "system_initialized",
                "system",
                "github-writing-system",
                None,
                "initialized",
                source_id,
                actor,
                occurred_at,
                "进度系统已建立第一份可审计基线",
            )
        ]
    else:
        events = []
        previous_tasks = _index_by_id(previous_facts.get("tasks", {}).get("tasks", []))
        for task in current_facts["tasks"].get("tasks", []):
            old = previous_tasks.get(task["id"])
            if old and old.get("status") != task.get("status"):
                events.append(
                    _event(
                        "task_status_changed",
                        "task",
                        task["id"],
                        old.get("status"),
                        task.get("status"),
                        source_id,
                        actor,
                        occurred_at,
                        f"{task['id']} · {task['title']}：{old.get('status')} → {task.get('status')}",
                    )
                )

        previous_chapters = _index_by_id(previous_facts.get("chapters", {}).get("chapters", []))
        for chapter in current_facts["chapters"].get("chapters", []):
            old = previous_chapters.get(chapter["id"])
            if not old:
                continue
            old_stages = {stage["name"]: stage.get("status") for stage in old.get("stages", [])}
            for stage in chapter.get("stages", []):
                before = old_stages.get(stage["name"])
                after = stage.get("status")
                if before is not None and before != after:
                    stage_id = f"{chapter['id']}:{stage['name']}"
                    events.append(
                        _event(
                            "chapter_stage_changed",
                            "chapter_stage",
                            stage_id,
                            before,
                            after,
                            source_id,
                            actor,
                            occurred_at,
                            f"{chapter['id']} · {chapter['title']} · {CHAPTER_STAGE_LABELS.get(stage['name'], stage['name'])}：{before} → {after}",
                        )
                    )

        previous_experiments = _index_by_id(previous_facts.get("experiments", {}).get("experiments", []))
        for experiment in current_facts["experiments"].get("experiments", []):
            old = previous_experiments.get(experiment["id"])
            if not old:
                continue
            for field in ("triage", "status"):
                before = old.get(field)
                after = experiment.get(field)
                if before != after:
                    object_id = f"{experiment['id']}:{field}"
                    events.append(
                        _event(
                            "experiment_changed",
                            "experiment",
                            object_id,
                            before,
                            after,
                            source_id,
                            actor,
                            occurred_at,
                            f"{experiment['id']} · {experiment['name']} · {field}：{before} → {after}",
                        )
                    )

        previous_feedback = _index_by_id(previous_facts.get("feedback", {}).get("decisions", []))
        for feedback in current_facts.get("feedback", {}).get("decisions", []):
            old = previous_feedback.get(feedback["id"])
            before = old.get("decision") if old else None
            after = feedback.get("decision")
            if after != "pending" and before != after:
                events.append(
                    _event(
                        "feedback_decided",
                        "feedback",
                        feedback["id"],
                        before,
                        after,
                        source_id,
                        actor,
                        occurred_at,
                        f"{feedback['id']} · {feedback.get('object', '')}：{after}",
                    )
                )

        previous_cycles = _index_by_id(previous_facts.get("cycles", {}).get("cycles", []))
        for cycle in current_facts.get("cycles", {}).get("cycles", []):
            old = previous_cycles.get(cycle["id"])
            before = old.get("status") if old else None
            after = cycle.get("status")
            if after == "active" and before != after:
                events.append(
                    _event(
                        "cycle_opened",
                        "cycle",
                        cycle["id"],
                        before,
                        after,
                        source_id,
                        actor,
                        occurred_at,
                        f"{cycle['id']} 已由真实发布回执激活",
                    )
                )

    if explicit_event:
        event_type, object_id, summary = explicit_event
        events.append(
            _event(
                event_type,
                "project",
                object_id,
                None,
                summary,
                source_id,
                actor,
                occurred_at,
                summary,
            )
        )
    return sorted(events, key=lambda item: (item["object_type"], item["object_id"], item["type"]))


def read_events(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []
    events = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ProgressError(f"{path}:{line_number} 不是有效 JSON: {exc}") from exc
        if not isinstance(value, dict) or not value.get("id"):
            raise ProgressError(f"{path}:{line_number} 缺少事件 ID")
        events.append(value)
    return events


def merge_events(
    existing: Sequence[Dict[str, Any]], candidates: Sequence[Dict[str, Any]]
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    known = {event["id"] for event in existing}
    additions = [event for event in candidates if event["id"] not in known]
    return list(existing) + additions, additions


def serialize_events(events: Sequence[Dict[str, Any]]) -> str:
    if not events:
        return ""
    return "".join(canonical_json(event) + "\n" for event in events)
