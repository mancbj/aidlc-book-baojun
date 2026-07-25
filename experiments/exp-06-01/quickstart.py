#!/usr/bin/env python3
"""Generate a deterministic Plan–Walkthrough deviation audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-06-01"
SCHEMA_VERSION = "1.0.0"
CHANGE_TYPES = {"added", "modified", "deleted"}


class AuditInputError(Exception):
    """An input error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Plan–Walkthrough 确定性偏差报告。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="审计输出 JSON。")
    parser.add_argument("--sample", action="store_true", help="使用仓库内默认样例路径。")
    args = parser.parse_args(argv)
    if args.sample:
        root = Path(__file__).resolve().parent
        args.input = root / "samples" / "input.json"
        args.output = root / "output" / "sample.json"
    if not args.input or not args.output:
        parser.error("必须提供 --input/--output，或使用 --sample。")
    return args


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def source_digest(value: Any) -> str:
    digest = hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
    return f"sha256:{digest}"


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise AuditInputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise AuditInputError("E_EXPECTED_ARRAY", f"{path} 必须是数组。")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AuditInputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise AuditInputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def validate_path_entries(
    value: Any,
    path: str,
    required_fields: Sequence[str],
) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    seen = set()
    for index, raw_entry in enumerate(require_list(value, path)):
        item_path = f"{path}[{index}]"
        entry = require_object(raw_entry, item_path)
        normalized = {
            field: require_string(require_field(entry, field, item_path), f"{item_path}.{field}")
            for field in required_fields
        }
        change_path = normalized["path"]
        if change_path in seen:
            raise AuditInputError("E_DUPLICATE_PATH", f"{path} 中路径重复：{change_path}")
        seen.add(change_path)
        entries.append(normalized)
    return entries


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(
        require_field(root, "experiment_id", "$"), "$.experiment_id"
    )
    if experiment_id != EXPERIMENT_ID:
        raise AuditInputError(
            "E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。"
        )

    plan = require_object(
        require_field(root, "implementation_plan", "$"), "$.implementation_plan"
    )
    actual = validate_path_entries(
        require_field(root, "actual_changes", "$"),
        "$.actual_changes",
        ("path", "change_type", "summary"),
    )
    for index, change in enumerate(actual):
        if change["change_type"] not in CHANGE_TYPES:
            raise AuditInputError(
                "E_CHANGE_TYPE",
                f"$.actual_changes[{index}].change_type 必须是 "
                f"{', '.join(sorted(CHANGE_TYPES))} 之一。",
            )

    walkthrough = require_object(
        require_field(root, "walkthrough", "$"), "$.walkthrough"
    )
    deliverables = validate_path_entries(
        require_field(plan, "deliverables", "$.implementation_plan"),
        "$.implementation_plan.deliverables",
        ("id", "path", "description"),
    )
    deliverable_ids = set()
    for deliverable in deliverables:
        if deliverable["id"] in deliverable_ids:
            raise AuditInputError(
                "E_DUPLICATE_ID", f"计划项 ID 重复：{deliverable['id']}"
            )
        deliverable_ids.add(deliverable["id"])

    declared_changes = validate_path_entries(
        require_field(walkthrough, "changes", "$.walkthrough"),
        "$.walkthrough.changes",
        ("path", "summary"),
    )
    declared_deviations = validate_path_entries(
        require_field(walkthrough, "deviations", "$.walkthrough"),
        "$.walkthrough.deviations",
        ("path", "reason"),
    )
    overlap = {item["path"] for item in declared_changes} & {
        item["path"] for item in declared_deviations
    }
    if overlap:
        raise AuditInputError(
            "E_DUPLICATE_DECLARATION",
            f"Walkthrough changes 与 deviations 重复声明路径：{sorted(overlap)[0]}",
        )
    return {
        "experiment_id": experiment_id,
        "implementation_plan": {
            "goal": require_string(
                require_field(plan, "goal", "$.implementation_plan"),
                "$.implementation_plan.goal",
            ),
            "deliverables": deliverables,
        },
        "actual_changes": actual,
        "walkthrough": {
            "changes": declared_changes,
            "deviations": declared_deviations,
        },
    }


def build_report(raw_data: Any) -> Dict[str, Any]:
    data = validate_input(raw_data)
    plan_by_path = {
        item["path"]: item for item in data["implementation_plan"]["deliverables"]
    }
    actual_by_path = {item["path"]: item for item in data["actual_changes"]}
    changes_by_path = {item["path"]: item for item in data["walkthrough"]["changes"]}
    deviations_by_path = {
        item["path"]: item for item in data["walkthrough"]["deviations"]
    }
    declared_paths = set(changes_by_path) | set(deviations_by_path)
    all_paths = sorted(set(plan_by_path) | set(actual_by_path) | declared_paths)

    rows = []
    for path in all_paths:
        plan_item = plan_by_path.get(path)
        actual_change = actual_by_path.get(path)
        declared_as = (
            "change"
            if path in changes_by_path
            else "deviation"
            if path in deviations_by_path
            else None
        )
        codes: List[str] = []
        classification = "aligned"
        if plan_item and not actual_change:
            classification = "failure"
            codes.append("PLAN_ITEM_MISSING")
        if not plan_item and actual_change:
            classification = "deviation"
            codes.append("UNPLANNED_CHANGE")
        if actual_change and path not in declared_paths:
            if classification != "failure":
                classification = "deviation"
            codes.append("UNDECLARED_CHANGE")
        if not actual_change and path in declared_paths:
            classification = "failure"
            codes.append("WALKTHROUGH_CHANGE_NOT_FOUND")
        rows.append(
            {
                "path": path,
                "plan_item": plan_item,
                "actual_change": actual_change,
                "walkthrough_declared_as": declared_as,
                "classification": classification,
                "codes": codes,
            }
        )

    planned_count = len(plan_by_path)
    delivered_count = sum(path in actual_by_path for path in plan_by_path)
    coverage = round(delivered_count / planned_count * 100, 2) if planned_count else 100.0
    undeclared_count = sum(path not in declared_paths for path in actual_by_path)
    deviation_count = sum(row["classification"] == "deviation" for row in rows)
    failure_count = sum(row["classification"] == "failure" for row in rows)

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(raw_data),
        "valid": failure_count == 0,
        "metrics": {
            "deliverable_coverage_percent": coverage,
            "undeclared_change_count": undeclared_count,
            "deviation_count": deviation_count,
            "failure_count": failure_count,
        },
        "summary": {
            "planned_deliverable_count": planned_count,
            "delivered_plan_item_count": delivered_count,
            "actual_change_count": len(actual_by_path),
            "walkthrough_declaration_count": len(declared_paths),
        },
        "audit_table": rows,
        "interpretation": (
            "deviation 表示计划或声明不一致，需人工审阅，但不自动构成 failure；"
            "failure 表示计划交付缺失或 Walkthrough 声明缺少实际证据。"
        ),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        raw_data = json.loads(args.input.read_text(encoding="utf-8"))
        report = build_report(raw_data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except json.JSONDecodeError as exc:
        print(f"[ERROR E_INVALID_JSON] 输入不是有效 JSON：{exc.msg}", file=sys.stderr)
        return 1
    except AuditInputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    status = "OK" if report["valid"] else "FAIL"
    print(f"[{status}] {EXPERIMENT_ID} report: {args.output}")
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
