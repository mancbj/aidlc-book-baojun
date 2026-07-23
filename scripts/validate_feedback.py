#!/usr/bin/env python3
"""Validate feedback decisions and continuous-update cycle facts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence


FEEDBACK_ID_RE = re.compile(r"^FB-\d{3}$")
LINKED_TASK_RE = re.compile(r"^(?:D\d{2}|C\d{2})-T\d{2}$")
CYCLE_ID_RE = re.compile(r"^v\d+\.\d+(?:-draft)?$")
CYCLE_TASK_RE = re.compile(r"^C\d{2}-T\d{2}$")
DECISIONS = {"pending", "accepted", "rejected", "deferred"}
READER_STATUSES = {"not-invited", "invited", "responded"}
CYCLE_STATUSES = {"preview", "active", "complete"}
TASK_STATUSES = {"backlog", "ready", "in-progress", "review", "done", "blocked"}
FORBIDDEN_KEYS = {
    "name",
    "email",
    "phone",
    "contact",
    "cookie",
    "token",
    "api_key",
    "raw_text",
    "full_transcript",
}


@dataclass(frozen=True)
class ContinuityIssue:
    source: str
    object_id: str
    field: str
    message: str
    fix: str

    def render(self) -> str:
        return f"[ERROR] {self.source} :: {self.object_id} :: {self.field} — {self.message} 修复：{self.fix}"


@dataclass
class ContinuityReport:
    issues: List[ContinuityIssue]
    feedback_count: int = 0
    cycle_count: int = 0

    @property
    def ok(self) -> bool:
        return not self.issues


def load_object(path: Path) -> Dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("顶层必须是 JSON object")
    return value


def valid_timestamp(value: Any, *, allow_null: bool = False) -> bool:
    if value is None and allow_null:
        return True
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def nonempty_strings(value: Any) -> bool:
    return isinstance(value, list) and bool(value) and all(
        isinstance(item, str) and item.strip() for item in value
    )


def _forbidden_key_paths(value: Any, prefix: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key).lower() in FORBIDDEN_KEYS:
                yield path
            yield from _forbidden_key_paths(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _forbidden_key_paths(child, f"{prefix}[{index}]")


def validate_feedback_document(document: Dict[str, Any], source: str) -> List[ContinuityIssue]:
    issues: List[ContinuityIssue] = []

    def add(object_id: str, field: str, message: str, fix: str) -> None:
        issues.append(ContinuityIssue(source, object_id, field, message, fix))

    if not valid_timestamp(document.get("updated")):
        add("document", "updated", "updated 必须是带时区时间。", "使用 ISO 8601 UTC 时间。")
    forbidden = list(_forbidden_key_paths(document))
    for path in forbidden:
        add("document", path, "反馈事实包含禁止的敏感/原始字段。", "只保留匿名槽位和最小决策摘要。")

    readers = document.get("readers")
    if not isinstance(readers, list):
        add("document", "readers", "readers 必须是数组。", "创建 Reader-A/B/C 匿名槽位。")
        readers = []
    reader_ids = set()
    for index, reader in enumerate(readers):
        object_id = str(reader.get("id", f"reader[{index}]")) if isinstance(reader, dict) else f"reader[{index}]"
        if not isinstance(reader, dict):
            add(object_id, "record", "reader 必须是 object。", "使用 id/status/time 字段。")
            continue
        reader_id = reader.get("id")
        if reader_id in reader_ids:
            add(object_id, "id", "Reader ID 重复。", "使用唯一匿名槽位。")
        reader_ids.add(reader_id)
        if not isinstance(reader_id, str) or not re.fullmatch(r"Reader-[A-Z]", reader_id):
            add(object_id, "id", "Reader ID 必须是匿名 Reader-A 形式。", "删除姓名或联系方式。")
        if reader.get("status") not in READER_STATUSES:
            add(object_id, "status", "reader status 非法。", "使用 not-invited/invited/responded。")
        if not valid_timestamp(reader.get("invited_at"), allow_null=True):
            add(object_id, "invited_at", "邀请时间必须为空或带时区。", "使用 ISO 8601。")
        if not valid_timestamp(reader.get("responded_at"), allow_null=True):
            add(object_id, "responded_at", "响应时间必须为空或带时区。", "使用 ISO 8601。")
        if reader.get("status") in {"invited", "responded"} and not reader.get("invited_at"):
            add(object_id, "invited_at", "invited/responded 必须有邀请时间。", "记录真实时间，不要伪造。")
        if reader.get("status") == "responded" and not reader.get("responded_at"):
            add(object_id, "responded_at", "responded 必须有响应时间。", "记录真实响应时间。")

    decisions = document.get("decisions")
    if not isinstance(decisions, list):
        add("document", "decisions", "decisions 必须是数组。", "使用空数组或反馈对象。")
        return issues
    ids = set()
    for index, item in enumerate(decisions):
        object_id = str(item.get("id", f"feedback[{index}]")) if isinstance(item, dict) else f"feedback[{index}]"
        if not isinstance(item, dict):
            add(object_id, "record", "反馈必须是 object。", "使用 feedback schema。")
            continue
        feedback_id = item.get("id")
        if not isinstance(feedback_id, str) or not FEEDBACK_ID_RE.fullmatch(feedback_id):
            add(object_id, "id", "反馈 ID 必须是 FB-NNN。", "例如 FB-001。")
        elif feedback_id in ids:
            add(object_id, "id", "反馈 ID 重复。", "分配新的稳定 ID。")
        ids.add(feedback_id)
        for field in ("source", "object", "summary"):
            if not isinstance(item.get(field), str) or not item[field].strip():
                add(object_id, field, f"{field} 必须是非空摘要。", "补充最小必要信息。")
        decision = item.get("decision")
        if decision not in DECISIONS:
            add(object_id, "decision", "decision 非法。", "使用 pending/accepted/rejected/deferred。")
        if not valid_timestamp(item.get("created_at")):
            add(object_id, "created_at", "created_at 必须带时区。", "使用 ISO 8601。")
        if not valid_timestamp(item.get("decided_at"), allow_null=True):
            add(object_id, "decided_at", "decided_at 必须为空或带时区。", "使用 ISO 8601。")
        if decision != "pending" and not item.get("decided_at"):
            add(object_id, "decided_at", "已决策反馈必须有决定时间。", "记录真实时间。")
        reason = item.get("reason")
        linked_task = item.get("linked_task")
        if decision == "accepted":
            if not isinstance(linked_task, str) or not LINKED_TASK_RE.fullmatch(linked_task):
                add(object_id, "linked_task", "accepted 必须关联任务。", "使用 DNN-TNN 或 CNN-TNN。")
            if not nonempty_strings(item.get("acceptance")):
                add(object_id, "acceptance", "accepted 必须有二元验收。", "提供至少一条可判断标准。")
        if decision in {"rejected", "deferred"} and (not isinstance(reason, str) or not reason.strip()):
            add(object_id, "reason", f"{decision} 必须记录理由。", "说明权衡和证据。")
        if decision == "deferred":
            if not isinstance(item.get("target_cycle"), str) or not item["target_cycle"].strip():
                add(object_id, "target_cycle", "deferred 必须有目标周期。", "例如 v0.2-draft。")
            if not isinstance(item.get("revisit_when"), str) or not item["revisit_when"].strip():
                add(object_id, "revisit_when", "deferred 必须有重评条件。", "写明何时重新判断。")
    return issues


def validate_cycle_document(document: Dict[str, Any], source: str) -> List[ContinuityIssue]:
    issues: List[ContinuityIssue] = []

    def add(object_id: str, field: str, message: str, fix: str) -> None:
        issues.append(ContinuityIssue(source, object_id, field, message, fix))

    if not valid_timestamp(document.get("updated")):
        add("document", "updated", "updated 必须是带时区时间。", "使用 ISO 8601 UTC 时间。")
    cycles = document.get("cycles")
    if not isinstance(cycles, list):
        add("document", "cycles", "cycles 必须是数组。", "创建 preview 或空数组。")
        return issues
    cycle_ids = set()
    active_count = 0
    for index, cycle in enumerate(cycles):
        object_id = str(cycle.get("id", f"cycle[{index}]")) if isinstance(cycle, dict) else f"cycle[{index}]"
        if not isinstance(cycle, dict):
            add(object_id, "record", "cycle 必须是 object。", "使用 cycle schema。")
            continue
        cycle_id = cycle.get("id")
        if not isinstance(cycle_id, str) or not CYCLE_ID_RE.fullmatch(cycle_id):
            add(object_id, "id", "cycle ID 格式非法。", "例如 v0.2-draft。")
        elif cycle_id in cycle_ids:
            add(object_id, "id", "cycle ID 重复。", "保留唯一版本周期。")
        cycle_ids.add(cycle_id)
        status = cycle.get("status")
        if status not in CYCLE_STATUSES:
            add(object_id, "status", "cycle status 非法。", "使用 preview/active/complete。")
        if status == "active":
            active_count += 1
            receipt = cycle.get("origin_release")
            if not isinstance(receipt, dict) or receipt.get("status") != "published":
                add(object_id, "origin_release", "active cycle 必须关联 published receipt。", "先处理真实 release.published。")
        for field in ("accepted_feedback", "carried_tasks", "carried_gaps"):
            if field in cycle and not isinstance(cycle[field], list):
                add(object_id, field, f"{field} 必须是数组。", "无记录时使用 []。")
        cadence = cycle.get("cadence")
        required_cadence = {
            "content_per_week",
            "experiment_per_week",
            "build_or_review_per_week",
            "release_per_month",
        }
        if not isinstance(cadence, dict) or any(
            not isinstance(cadence.get(key), int) or cadence.get(key) < 1 for key in required_cadence
        ):
            add(object_id, "cadence", "周期节奏必须覆盖每周内容/实验/审校和每月发布。", "四项均设为至少 1。")
        tasks = cycle.get("tasks")
        if not isinstance(tasks, list) or not tasks:
            add(object_id, "tasks", "cycle 必须至少有一个任务。", "创建依赖已满足的 Must。")
            continue
        by_id = {}
        kinds = set()
        for task in tasks:
            task_id = task.get("id") if isinstance(task, dict) else None
            if not isinstance(task, dict) or not isinstance(task_id, str) or not CYCLE_TASK_RE.fullmatch(task_id):
                add(object_id, "tasks.id", "cycle task ID 必须是 CNN-TNN。", "例如 C02-T01。")
                continue
            if task_id in by_id:
                add(task_id, "id", "cycle task ID 重复。", "分配唯一 ID。")
            by_id[task_id] = task
            kinds.add(task.get("kind"))
            if task.get("priority") not in {"must", "should", "could"}:
                add(task_id, "priority", "priority 非法。", "使用 must/should/could。")
            if task.get("status") not in TASK_STATUSES:
                add(task_id, "status", "status 非法。", "使用任务有限状态。")
            if not nonempty_strings(task.get("acceptance")):
                add(task_id, "acceptance", "cycle task 必须有验收。", "提供二元标准。")
            if not isinstance(task.get("dependencies"), list):
                add(task_id, "dependencies", "dependencies 必须是数组。", "无依赖时使用 []。")
        for task_id, task in by_id.items():
            for dependency in task.get("dependencies", []):
                if dependency not in by_id:
                    add(task_id, "dependencies", "cycle task 引用未知依赖。", "修正为同周期 Task ID。")
        ready_must = sum(
            1
            for task in by_id.values()
            if task.get("priority") == "must"
            and task.get("status") == "ready"
            and isinstance(task.get("dependencies"), list)
            and all(by_id.get(dependency, {}).get("status") == "done" for dependency in task.get("dependencies", []))
        )
        if not {"content", "experiment", "build-review"}.issubset(kinds):
            add(object_id, "tasks.kind", "周期缺少内容、实验或构建审校节奏任务。", "至少各创建一项。")
        if status == "active" and ready_must < 1:
            add(object_id, "tasks", "active cycle 必须有依赖已满足的 ready Must。", "将下一个可执行 Must 设为 ready，并确保其依赖已 done。")
    if active_count > 1:
        add("document", "active_cycle", "只能有一个 active cycle。", "完成或降级其他周期。")
    active_id = document.get("active_cycle")
    if active_id is not None:
        matching = [cycle for cycle in cycles if isinstance(cycle, dict) and cycle.get("id") == active_id]
        if len(matching) != 1 or matching[0].get("status") != "active":
            add("document", "active_cycle", "active_cycle 必须指向唯一 active 记录。", "修正 ID 或设为 null。")
    return issues


def run_validation(root: Path) -> ContinuityReport:
    root = root.resolve()
    issues: List[ContinuityIssue] = []
    feedback_count = cycle_count = 0
    try:
        feedback = load_object(root / "feedback/decisions.json")
        feedback_count = len(feedback.get("decisions", [])) if isinstance(feedback.get("decisions"), list) else 0
        issues.extend(validate_feedback_document(feedback, "feedback/decisions.json"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        issues.append(ContinuityIssue("feedback/decisions.json", "document", "json", str(exc), "创建有效 JSON。"))
    try:
        cycles = load_object(root / "progress/cycles.json")
        cycle_count = len(cycles.get("cycles", [])) if isinstance(cycles.get("cycles"), list) else 0
        issues.extend(validate_cycle_document(cycles, "progress/cycles.json"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        issues.append(ContinuityIssue("progress/cycles.json", "document", "json", str(exc), "创建有效 JSON。"))
    return ContinuityReport(issues, feedback_count, cycle_count)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验反馈决策与持续更新周期。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    report = run_validation(parse_args(argv).root)
    for issue in report.issues:
        print(issue.render(), file=sys.stderr)
    print(f"[INFO] continuity summary: feedback={report.feedback_count}, cycles={report.cycle_count}, errors={len(report.issues)}")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
