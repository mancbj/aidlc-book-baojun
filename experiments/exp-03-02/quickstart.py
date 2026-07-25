#!/usr/bin/env python3
"""Validate a Unit/Story/Bolt dependency plan deterministically."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-03-02"
SCHEMA_VERSION = "1.0.0"
BOLT_STATUSES = {"pending", "completed"}


class InputError(Exception):
    """Raised when an input or output file cannot be processed."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成 Unit、Story 与 Bolt 的确定性依赖图和异常报告。"
    )
    parser.add_argument("--input", type=Path, help="依赖清单 JSON。")
    parser.add_argument("--output", type=Path, help="报告 JSON。")
    parser.add_argument(
        "--sample",
        action="store_true",
        help="使用 experiments/exp-03-02 内置样例路径。",
    )
    args = parser.parse_args(argv)
    if args.sample:
        root = Path(__file__).resolve().parent
        args.input = root / "samples" / "input.json"
        args.output = root / "output" / "sample.json"
    if args.input is None or args.output is None:
        parser.error("必须提供 --input/--output，或使用 --sample。")
    return args


def canonical_json(value: Any) -> str:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    )


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def source_digest(value: Any) -> str:
    payload = canonical_json(value).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def add_anomaly(
    anomalies: List[Dict[str, Any]],
    code: str,
    severity: str,
    path: str,
    message: str,
    value: Any = None,
) -> None:
    anomalies.append(
        {
            "code": code,
            "message": message,
            "path": path,
            "severity": severity,
            "value": value,
        }
    )


def require_fields(
    item: Dict[str, Any],
    fields: Sequence[str],
    path: str,
    anomalies: List[Dict[str, Any]],
) -> None:
    for field in fields:
        if field not in item:
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.{field}",
                "缺少必需字段。",
            )


def read_collection(
    data: Dict[str, Any],
    name: str,
    anomalies: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    value = data.get(name)
    path = f"$.{name}"
    if not isinstance(value, list) or not value:
        add_anomaly(
            anomalies, "E_SCHEMA", "error", path, "必须是非空数组。", value
        )
        return []
    items: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        if isinstance(item, dict):
            items.append(item)
        else:
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}[{index}]",
                "数组元素必须是对象。",
                item,
            )
    return items


def index_items(
    items: List[Dict[str, Any]],
    name: str,
    anomalies: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(items):
        item_id = item.get("id")
        path = f"$.{name}[{index}].id"
        if not non_empty_string(item_id):
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                path,
                "ID 必须是非空字符串。",
                item_id,
            )
        elif item_id in result:
            add_anomaly(
                anomalies,
                "E_DUPLICATE_ID",
                "error",
                path,
                "同类对象 ID 重复。",
                item_id,
            )
        else:
            result[item_id] = item
    return result


def string_list(
    value: Any,
    path: str,
    anomalies: List[Dict[str, Any]],
    allow_empty: bool,
) -> List[str]:
    valid = (
        isinstance(value, list)
        and (allow_empty or bool(value))
        and all(non_empty_string(item) for item in value)
    )
    if not valid:
        qualifier = "字符串数组" if allow_empty else "非空字符串数组"
        add_anomaly(
            anomalies, "E_SCHEMA", "error", path, f"必须是{qualifier}。", value
        )
        return []
    return list(value)


def validate_base_fields(
    units: List[Dict[str, Any]],
    stories: List[Dict[str, Any]],
    bolts: List[Dict[str, Any]],
    anomalies: List[Dict[str, Any]],
) -> None:
    for index, unit in enumerate(units):
        path = f"$.units[{index}]"
        require_fields(unit, ("id", "title"), path, anomalies)
        if "title" in unit and not non_empty_string(unit["title"]):
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.title",
                "Unit 标题必须是非空字符串。",
                unit["title"],
            )

    for index, story in enumerate(stories):
        path = f"$.stories[{index}]"
        require_fields(story, ("id", "unit_id", "title"), path, anomalies)
        if "unit_id" in story and not non_empty_string(story["unit_id"]):
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.unit_id",
                "Story 的 unit_id 必须是非空字符串。",
                story["unit_id"],
            )
        if "title" in story and not non_empty_string(story["title"]):
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.title",
                "Story 标题必须是非空字符串。",
                story["title"],
            )

    for index, bolt in enumerate(bolts):
        path = f"$.bolts[{index}]"
        require_fields(
            bolt,
            ("id", "unit_id", "story_ids", "depends_on", "status"),
            path,
            anomalies,
        )
        if "unit_id" in bolt and not non_empty_string(bolt["unit_id"]):
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.unit_id",
                "Bolt 的 unit_id 必须是非空字符串。",
                bolt["unit_id"],
            )
        if "story_ids" in bolt:
            string_list(bolt["story_ids"], f"{path}.story_ids", anomalies, False)
        if "depends_on" in bolt:
            string_list(bolt["depends_on"], f"{path}.depends_on", anomalies, True)
        if "status" in bolt and bolt["status"] not in BOLT_STATUSES:
            add_anomaly(
                anomalies,
                "E_SCHEMA",
                "error",
                f"{path}.status",
                "Bolt status 必须是 pending 或 completed。",
                bolt["status"],
            )


def strongly_connected_components(
    node_ids: Set[str], edges: List[Tuple[str, str]]
) -> List[List[str]]:
    adjacency: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    for source, target in edges:
        adjacency[source].append(target)
    for targets in adjacency.values():
        targets.sort()

    index = 0
    stack: List[str] = []
    indices: Dict[str, int] = {}
    lowlinks: Dict[str, int] = {}
    on_stack: Set[str] = set()
    components: List[List[str]] = []

    def visit(node_id: str) -> None:
        nonlocal index
        indices[node_id] = index
        lowlinks[node_id] = index
        index += 1
        stack.append(node_id)
        on_stack.add(node_id)

        for target in adjacency[node_id]:
            if target not in indices:
                visit(target)
                lowlinks[node_id] = min(lowlinks[node_id], lowlinks[target])
            elif target in on_stack:
                lowlinks[node_id] = min(lowlinks[node_id], indices[target])

        if lowlinks[node_id] == indices[node_id]:
            component: List[str] = []
            while True:
                member = stack.pop()
                on_stack.remove(member)
                component.append(member)
                if member == node_id:
                    break
            components.append(sorted(component))

    for node_id in sorted(node_ids):
        if node_id not in indices:
            visit(node_id)
    return sorted(components)


def validate_document(data: Any) -> Dict[str, Any]:
    anomalies: List[Dict[str, Any]] = []
    if not isinstance(data, dict):
        add_anomaly(
            anomalies,
            "E_SCHEMA",
            "error",
            "$",
            "顶层必须是 JSON 对象。",
            type(data).__name__,
        )
        return build_report(data, {}, {}, {}, [], anomalies)

    require_fields(
        data, ("schema_version", "units", "stories", "bolts"), "$", anomalies
    )
    if data.get("schema_version") != SCHEMA_VERSION:
        add_anomaly(
            anomalies,
            "E_SCHEMA_VERSION",
            "error",
            "$.schema_version",
            f"schema_version 必须是 {SCHEMA_VERSION}。",
            data.get("schema_version"),
        )

    units = read_collection(data, "units", anomalies)
    stories = read_collection(data, "stories", anomalies)
    bolts = read_collection(data, "bolts", anomalies)
    validate_base_fields(units, stories, bolts, anomalies)

    unit_by_id = index_items(units, "units", anomalies)
    story_by_id = index_items(stories, "stories", anomalies)
    bolt_by_id = index_items(bolts, "bolts", anomalies)

    for index, story in enumerate(stories):
        unit_id = story.get("unit_id")
        if non_empty_string(unit_id) and unit_id not in unit_by_id:
            add_anomaly(
                anomalies,
                "E_UNKNOWN_UNIT",
                "error",
                f"$.stories[{index}].unit_id",
                "Story 引用了未知 Unit。",
                unit_id,
            )

    assigned_stories: Dict[str, List[str]] = {}
    valid_edges: List[Tuple[str, str]] = []
    for index, bolt in enumerate(bolts):
        path = f"$.bolts[{index}]"
        bolt_id = bolt.get("id")
        unit_id = bolt.get("unit_id")
        if non_empty_string(unit_id) and unit_id not in unit_by_id:
            add_anomaly(
                anomalies,
                "E_UNKNOWN_UNIT",
                "error",
                f"{path}.unit_id",
                "Bolt 引用了未知 Unit。",
                unit_id,
            )
        story_ids = bolt.get("story_ids")
        if isinstance(story_ids, list):
            for story_id in sorted(
                {item for item in story_ids if non_empty_string(item)}
            ):
                if story_id not in story_by_id:
                    add_anomaly(
                        anomalies,
                        "E_UNKNOWN_STORY",
                        "error",
                        f"{path}.story_ids",
                        "Bolt 引用了未知 Story。",
                        story_id,
                    )
                else:
                    assigned_stories.setdefault(story_id, []).append(str(bolt_id))
                    story_unit = story_by_id[story_id].get("unit_id")
                    if (
                        non_empty_string(unit_id)
                        and non_empty_string(story_unit)
                        and unit_id != story_unit
                    ):
                        add_anomaly(
                            anomalies,
                            "E_STORY_UNIT_MISMATCH",
                            "error",
                            f"{path}.story_ids",
                            "Bolt 与其 Story 不属于同一 Unit。",
                            story_id,
                        )
        dependencies = bolt.get("depends_on")
        if isinstance(dependencies, list) and non_empty_string(bolt_id):
            for dependency_id in sorted(
                {item for item in dependencies if non_empty_string(item)}
            ):
                if dependency_id not in bolt_by_id:
                    add_anomaly(
                        anomalies,
                        "E_UNKNOWN_BOLT",
                        "error",
                        f"{path}.depends_on",
                        "Bolt 引用了未知前置 Bolt。",
                        dependency_id,
                    )
                else:
                    valid_edges.append((dependency_id, bolt_id))

    for story_id in sorted(story_by_id):
        assignments = sorted(assigned_stories.get(story_id, []))
        if not assignments:
            add_anomaly(
                anomalies,
                "E_UNASSIGNED_STORY",
                "error",
                "$.stories",
                "Story 未分配给任何 Bolt。",
                story_id,
            )
        elif len(assignments) > 1:
            add_anomaly(
                anomalies,
                "E_MULTIPLE_BOLT_ASSIGNMENT",
                "error",
                "$.bolts",
                "Story 被分配给多个 Bolt。",
                {"bolt_ids": assignments, "story_id": story_id},
            )

    return build_report(
        data, unit_by_id, story_by_id, bolt_by_id, valid_edges, anomalies
    )


def build_report(
    data: Any,
    unit_by_id: Dict[str, Dict[str, Any]],
    story_by_id: Dict[str, Dict[str, Any]],
    bolt_by_id: Dict[str, Dict[str, Any]],
    edges: List[Tuple[str, str]],
    anomalies: List[Dict[str, Any]],
) -> Dict[str, Any]:
    edge_set = sorted(set(edges))
    components = strongly_connected_components(set(bolt_by_id), edge_set)
    self_edges = {source for source, target in edge_set if source == target}
    cycles = [
        component
        for component in components
        if len(component) > 1 or component[0] in self_edges
    ]
    for component in cycles:
        add_anomaly(
            anomalies,
            "E_CYCLE",
            "error",
            "$.bolts",
            "Bolt 依赖图包含循环依赖分量。",
            component,
        )

    cross_unit_edges: List[Tuple[str, str]] = []
    unmet_edges: List[Tuple[str, str]] = []
    for source, target in edge_set:
        source_bolt = bolt_by_id[source]
        target_bolt = bolt_by_id[target]
        if source_bolt.get("unit_id") != target_bolt.get("unit_id"):
            cross_unit_edges.append((source, target))
            add_anomaly(
                anomalies,
                "W_CROSS_UNIT_COUPLING",
                "warning",
                "$.bolts",
                "依赖边跨越 Unit，需人工确认耦合是否必要。",
                {"from": source, "to": target},
            )
        if (
            target_bolt.get("status") == "completed"
            and source_bolt.get("status") != "completed"
        ):
            unmet_edges.append((source, target))
            add_anomaly(
                anomalies,
                "W_UNMET_PREREQUISITE",
                "warning",
                "$.bolts",
                "已完成 Bolt 的前置 Bolt 尚未完成。",
                {"from": source, "to": target},
            )

    sorted_anomalies = sorted(
        anomalies,
        key=lambda item: (
            item["path"],
            item["code"],
            canonical_json(item.get("value")),
        ),
    )
    structural_valid = not any(
        item["severity"] == "error" for item in sorted_anomalies
    )
    plan_optimal = (
        structural_valid
        and not cycles
        and not cross_unit_edges
        and not unmet_edges
    )

    nodes = []
    for bolt_id in sorted(bolt_by_id):
        bolt = bolt_by_id[bolt_id]
        nodes.append(
            {
                "id": bolt_id,
                "status": bolt.get("status"),
                "story_ids": sorted(
                    {
                        item
                        for item in bolt.get("story_ids", [])
                        if non_empty_string(item)
                    }
                )
                if isinstance(bolt.get("story_ids"), list)
                else [],
                "unit_id": bolt.get("unit_id"),
            }
        )

    return {
        "anomalies": sorted_anomalies,
        "dependency_graph": {
            "edges": [
                {"from": source, "to": target}
                for source, target in edge_set
            ],
            "nodes": nodes,
        },
        "experiment_id": EXPERIMENT_ID,
        "metrics": {
            "cross_unit_coupling_edge_count": len(cross_unit_edges),
            "cycle_count": len(cycles),
            "unmet_prerequisite_count": len(unmet_edges),
        },
        "plan_optimal": plan_optimal,
        "schema_version": SCHEMA_VERSION,
        "source_digest": source_digest(data),
        "structural_valid": structural_valid,
    }


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
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(pretty_json(report), encoding="utf-8")
    except OSError as exc:
        raise InputError(f"无法写入输出文件：{path} ({exc})") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = validate_document(read_input(args.input))
        write_report(args.output, report)
    except InputError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if not report["structural_valid"]:
        print("[ERROR] 依赖清单结构不合法；详见输出报告。", file=sys.stderr)
        return 2
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
