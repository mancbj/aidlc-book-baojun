#!/usr/bin/env python3
"""Generate a deterministic Intent-to-Story trace report.

This demo intentionally uses only the Python standard library. It checks the
structural traceability of a candidate Inception decomposition; it does not
judge whether the content is strategically or semantically correct.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-03-01"
SCHEMA_VERSION = "1.0.0"
REQUIREMENT_TYPES = {"functional", "non-functional"}


class InputError(Exception):
    """Raised when the input file cannot produce a structural report."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成 Intent → Requirement → Unit → Story 的确定性追踪报告。"
    )
    parser.add_argument("--input", required=True, type=Path, help="候选分解 JSON。")
    parser.add_argument("--output", required=True, type=Path, help="追踪报告 JSON。")
    return parser.parse_args(argv)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def source_digest(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def non_empty_string_list(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(non_empty_string(item) for item in value)
    )


def add_error(
    errors: List[Dict[str, Any]],
    code: str,
    path: str,
    message: str,
    value: Any = None,
) -> None:
    errors.append(
        {
            "code": code,
            "path": path,
            "message": message,
            "value": value,
        }
    )


def require_fields(
    item: Dict[str, Any],
    fields: Iterable[str],
    path: str,
    errors: List[Dict[str, Any]],
) -> None:
    for field in fields:
        if field not in item:
            add_error(errors, "E_SCHEMA", f"{path}.{field}", "缺少必需字段。")


def collection(value: Any, path: str, errors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        add_error(errors, "E_SCHEMA", path, "必须是非空数组。", value)
        return []
    objects: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            objects.append(item)
        else:
            add_error(errors, "E_SCHEMA", f"{path}[{index}]", "数组元素必须是对象。", item)
    return objects


def indexed_by_id(
    items: List[Dict[str, Any]],
    path: str,
    errors: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    by_id: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(items):
        item_path = f"{path}[{index}]"
        item_id = item.get("id")
        if not non_empty_string(item_id):
            add_error(errors, "E_SCHEMA", f"{item_path}.id", "ID 必须是非空字符串。", item_id)
            continue
        if item_id in by_id:
            add_error(
                errors,
                "E_DUPLICATE_ID",
                f"{item_path}.id",
                "同类对象 ID 重复。",
                item_id,
            )
            continue
        by_id[item_id] = item
    return by_id


def valid_string_refs(value: Any) -> Set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if non_empty_string(item)}


def validate_document(data: Any) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    if not isinstance(data, dict):
        add_error(errors, "E_SCHEMA", "$", "顶层必须是 JSON 对象。", type(data).__name__)
        return build_report(data, errors, [], {}, {}, {})

    require_fields(data, ("schema_version", "intent", "requirements", "units", "stories"), "$", errors)

    intent = data.get("intent")
    if not isinstance(intent, dict):
        add_error(errors, "E_SCHEMA", "$.intent", "intent 必须是对象。", intent)
    else:
        require_fields(intent, ("id", "statement", "outcomes", "constraints"), "$.intent", errors)
        for field in ("id", "statement"):
            if field in intent and not non_empty_string(intent[field]):
                add_error(errors, "E_SCHEMA", f"$.intent.{field}", "必须是非空字符串。", intent[field])
        for field in ("outcomes", "constraints"):
            if field in intent and not non_empty_string_list(intent[field]):
                add_error(errors, "E_SCHEMA", f"$.intent.{field}", "必须是非空字符串数组。", intent[field])

    requirements = collection(data.get("requirements"), "$.requirements", errors)
    units = collection(data.get("units"), "$.units", errors)
    stories = collection(data.get("stories"), "$.stories", errors)

    requirement_by_id = indexed_by_id(requirements, "$.requirements", errors)
    unit_by_id = indexed_by_id(units, "$.units", errors)
    story_by_id = indexed_by_id(stories, "$.stories", errors)

    requirement_types = set()
    for index, requirement in enumerate(requirements):
        item_path = f"$.requirements[{index}]"
        require_fields(requirement, ("id", "type", "text", "acceptance"), item_path, errors)
        kind = requirement.get("type")
        if kind not in REQUIREMENT_TYPES:
            add_error(errors, "E_SCHEMA", f"{item_path}.type", "需求类型必须是 functional 或 non-functional。", kind)
        else:
            requirement_types.add(kind)
        if "text" in requirement and not non_empty_string(requirement["text"]):
            add_error(errors, "E_SCHEMA", f"{item_path}.text", "需求正文必须是非空字符串。", requirement["text"])
        if "acceptance" in requirement and not non_empty_string_list(requirement["acceptance"]):
            add_error(errors, "E_ACCEPTANCE", f"{item_path}.acceptance", "需求验收必须至少包含一个非空项。", requirement.get("acceptance"))

    if "functional" not in requirement_types and requirements:
        add_error(errors, "E_MISSING_FUNCTIONAL", "$.requirements", "至少需要一个 functional Requirement。")
    if "non-functional" not in requirement_types and requirements:
        add_error(errors, "E_MISSING_NFR", "$.requirements", "至少需要一个 non-functional Requirement。")

    valid_requirement_ids = set(requirement_by_id)
    valid_unit_ids = set(unit_by_id)

    for index, unit in enumerate(units):
        item_path = f"$.units[{index}]"
        require_fields(unit, ("id", "title", "responsibilities", "requirement_refs"), item_path, errors)
        if "title" in unit and not non_empty_string(unit["title"]):
            add_error(errors, "E_SCHEMA", f"{item_path}.title", "Unit 标题必须是非空字符串。", unit["title"])
        if "responsibilities" in unit and not non_empty_string_list(unit["responsibilities"]):
            add_error(errors, "E_SCHEMA", f"{item_path}.responsibilities", "Unit 职责必须是非空字符串数组。", unit.get("responsibilities"))
        refs = unit.get("requirement_refs")
        if not non_empty_string_list(refs):
            add_error(errors, "E_SCHEMA", f"{item_path}.requirement_refs", "Unit 必须引用至少一个 Requirement。", refs)
        for ref in valid_string_refs(refs):
            if ref not in valid_requirement_ids:
                add_error(errors, "E_UNKNOWN_REF", f"{item_path}.requirement_refs", "Unit 引用了未知 Requirement。", ref)

    for index, story in enumerate(stories):
        item_path = f"$.stories[{index}]"
        require_fields(story, ("id", "unit_id", "title", "requirement_refs", "acceptance"), item_path, errors)
        if "title" in story and not non_empty_string(story["title"]):
            add_error(errors, "E_SCHEMA", f"{item_path}.title", "Story 标题必须是非空字符串。", story["title"])
        unit_id = story.get("unit_id")
        if not non_empty_string(unit_id):
            add_error(errors, "E_SCHEMA", f"{item_path}.unit_id", "Story 必须引用一个 Unit。", unit_id)
        elif unit_id not in valid_unit_ids:
            add_error(errors, "E_UNKNOWN_REF", f"{item_path}.unit_id", "Story 引用了未知 Unit。", unit_id)
        refs = story.get("requirement_refs")
        if not non_empty_string_list(refs):
            add_error(errors, "E_SCHEMA", f"{item_path}.requirement_refs", "Story 必须引用至少一个 Requirement。", refs)
        for ref in valid_string_refs(refs):
            if ref not in valid_requirement_ids:
                add_error(errors, "E_UNKNOWN_REF", f"{item_path}.requirement_refs", "Story 引用了未知 Requirement。", ref)
        if "acceptance" in story and not non_empty_string_list(story["acceptance"]):
            add_error(errors, "E_ACCEPTANCE", f"{item_path}.acceptance", "Story 验收必须至少包含一个非空项。", story.get("acceptance"))

    report = build_report(data, errors, stories, requirement_by_id, unit_by_id, story_by_id)
    return report


def build_report(
    data: Any,
    errors: List[Dict[str, Any]],
    stories: List[Dict[str, Any]],
    requirement_by_id: Dict[str, Dict[str, Any]],
    unit_by_id: Dict[str, Dict[str, Any]],
    story_by_id: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    requirement_ids = set(requirement_by_id)
    unit_ids = set(unit_by_id)

    units_by_requirement: Dict[str, Set[str]] = {req_id: set() for req_id in requirement_ids}
    for unit_id, unit in unit_by_id.items():
        for ref in valid_string_refs(unit.get("requirement_refs")):
            if ref in requirement_ids:
                units_by_requirement.setdefault(ref, set()).add(unit_id)

    stories_by_requirement: Dict[str, Set[str]] = {req_id: set() for req_id in requirement_ids}
    orphan_story_count = 0
    complete_acceptance_count = 0
    invalid_reference_count = 0

    for unit in unit_by_id.values():
        invalid_reference_count += len(
            [ref for ref in valid_string_refs(unit.get("requirement_refs")) if ref not in requirement_ids]
        )

    for story_id, story in story_by_id.items():
        unit_id = story.get("unit_id")
        refs = valid_string_refs(story.get("requirement_refs"))
        valid_refs = refs & requirement_ids
        has_valid_unit = non_empty_string(unit_id) and unit_id in unit_ids
        valid_trace_refs: Set[str] = set()
        if has_valid_unit:
            upstream_refs = valid_string_refs(unit_by_id[unit_id].get("requirement_refs"))
            valid_trace_refs = valid_refs & upstream_refs
        if not has_valid_unit or not valid_trace_refs:
            orphan_story_count += 1
            add_error(
                errors,
                "E_ORPHAN_STORY",
                f"$.stories[{story_id}]",
                "Story 缺少可贯通的 Unit → Requirement 上游路径。",
                story_id,
            )
        if non_empty_string_list(story.get("acceptance")):
            complete_acceptance_count += 1
        if non_empty_string(unit_id) and unit_id not in unit_ids:
            invalid_reference_count += 1
        invalid_reference_count += len([ref for ref in refs if ref not in requirement_ids])

        if has_valid_unit:
            for ref in valid_trace_refs:
                stories_by_requirement.setdefault(ref, set()).add(story_id)

    traces = []
    covered = 0
    for requirement_id in sorted(requirement_ids):
        trace = {
            "requirement_id": requirement_id,
            "unit_ids": sorted(units_by_requirement.get(requirement_id, set())),
            "story_ids": sorted(stories_by_requirement.get(requirement_id, set())),
        }
        if trace["unit_ids"] and trace["story_ids"]:
            covered += 1
        traces.append(trace)

    requirement_count = len(requirement_ids)
    story_count = len(story_by_id)
    metrics = {
        "requirement_coverage_percent": percent(covered, requirement_count),
        "orphan_story_count": orphan_story_count,
        "acceptance_completeness_percent": percent(complete_acceptance_count, story_count),
        "invalid_reference_count": invalid_reference_count,
    }

    sorted_errors = sorted(
        errors,
        key=lambda item: (str(item.get("path")), str(item.get("code")), str(item.get("message"))),
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(data),
        "valid": not sorted_errors,
        "metrics": metrics,
        "traces": traces,
        "errors": sorted_errors,
    }


def percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round(numerator / denominator * 100, 1)


def read_input(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError(f"输入文件不存在：{path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"输入文件不是有效 JSON：{path} ({exc})") from exc
    except OSError as exc:
        raise InputError(f"无法读取输入文件：{path} ({exc})") from exc


def write_report(path: Path, report: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        data = read_input(args.input)
        report = validate_document(data)
        write_report(args.output, report)
    except InputError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR] 无法写入输出文件：{args.output} ({exc})", file=sys.stderr)
        return 1
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
