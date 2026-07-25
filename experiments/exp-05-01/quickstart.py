#!/usr/bin/env python3
"""Deterministic Bolt scope and duration estimator."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-05-01"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "预计时长来自固定启发式系数与输入字段；"
    "它不证明真实世界排期或交付工期的准确性。"
)
DEFAULT_CONFIG = {
    "base_hours_per_story": 2.0,
    "complexity_factor": 1.5,
    "risk_factor": 1.0,
    "dependency_factor": 0.75,
    "max_bolt_hours": 16.0,
}
SCALE_MIN = 1
SCALE_MAX = 5


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Bolt 范围、预计时长与拆分建议。")
    parser.add_argument("--input", type=Path, help="输入 JSON 路径。")
    parser.add_argument("--output", type=Path, help="输出 JSON 路径。")
    parser.add_argument("--sample", action="store_true", help="使用内置样例路径。")
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


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise InputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串。")
    return value.strip()


def require_scale(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是 {SCALE_MIN}-{SCALE_MAX} 的整数。")
    if value < SCALE_MIN or value > SCALE_MAX:
        raise InputError("E_INVALID_FIELD", f"{path} 必须是 {SCALE_MIN}-{SCALE_MAX} 的整数。")
    return value


def require_dependency_list(value: Any, path: str) -> List[str]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是字符串数组。")
    result: List[str] = []
    for index, item in enumerate(value):
        result.append(require_string(item, f"{path}[{index}]"))
    return result


def parse_config(value: Any) -> Dict[str, float]:
    if value is None:
        return dict(DEFAULT_CONFIG)
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.estimation_config 必须是对象。")
    config = dict(DEFAULT_CONFIG)
    for key in DEFAULT_CONFIG:
        if key not in value:
            continue
        raw = value[key]
        if not isinstance(raw, (int, float)) or isinstance(raw, bool):
            raise InputError("E_INVALID_FIELD", f"$.estimation_config.{key} 必须是数字。")
        if raw <= 0:
            raise InputError("E_INVALID_FIELD", f"$.estimation_config.{key} 必须大于 0。")
        config[key] = float(raw)
    return config


def story_hours(story: Dict[str, Any], config: Dict[str, float]) -> float:
    complexity = story["complexity"]
    risk = story["risk"]
    dependency_count = len(story["dependencies"])
    return (
        config["base_hours_per_story"]
        + complexity * config["complexity_factor"]
        + risk * config["risk_factor"]
        + dependency_count * config["dependency_factor"]
    )


def round_hours(value: float) -> float:
    return round(value, 2)


def split_suggestions(
    bolt_id: str,
    story_ids: List[str],
    hours_by_story: Dict[str, float],
    max_hours: float,
) -> List[Dict[str, Any]]:
    total = sum(hours_by_story[story_id] for story_id in story_ids)
    if total <= max_hours:
        return []
    ordered = sorted(story_ids)
    groups: List[List[str]] = []
    current: List[str] = []
    current_hours = 0.0
    for story_id in ordered:
        hours = hours_by_story[story_id]
        if current and current_hours + hours > max_hours:
            groups.append(current)
            current = [story_id]
            current_hours = hours
        else:
            current.append(story_id)
            current_hours += hours
    if current:
        groups.append(current)
    if len(groups) <= 1:
        return [
            {
                "reason": "single_story_exceeds_max_bolt_hours",
                "suggested_bolt_id": f"{bolt_id}-SPLIT-{index + 1:02d}",
                "story_ids": [story_id],
            }
            for index, story_id in enumerate(ordered)
        ]
    return [
        {
            "reason": "estimated_hours_exceeds_max_bolt_hours",
            "suggested_bolt_id": f"{bolt_id}-SPLIT-{index + 1:02d}",
            "story_ids": group,
        }
        for index, group in enumerate(groups)
    ]


def parse_stories(value: Any) -> Tuple[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_FIELD", "$.stories 必须是非空数组。")
    stories: List[Dict[str, Any]] = []
    by_id: Dict[str, Dict[str, Any]] = {}
    for index, raw in enumerate(value):
        path = f"$.stories[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象。")
        story_id = require_string(require_field(raw, "id", path), f"{path}.id")
        if story_id in by_id:
            raise InputError("E_DUPLICATE_ID", f"重复 Story ID：{story_id}")
        title = require_string(require_field(raw, "title", path), f"{path}.title")
        complexity = require_scale(require_field(raw, "complexity", path), f"{path}.complexity")
        risk = require_scale(require_field(raw, "risk", path), f"{path}.risk")
        dependencies = require_dependency_list(
            raw.get("dependencies", []), f"{path}.dependencies"
        )
        actual_hours: Optional[float] = None
        if "actual_hours" in raw:
            raw_actual = raw["actual_hours"]
            if not isinstance(raw_actual, (int, float)) or isinstance(raw_actual, bool):
                raise InputError("E_INVALID_FIELD", f"{path}.actual_hours 必须是数字。")
            if raw_actual < 0:
                raise InputError("E_INVALID_FIELD", f"{path}.actual_hours 不能为负数。")
            actual_hours = float(raw_actual)
        story = {
            "id": story_id,
            "title": title,
            "complexity": complexity,
            "risk": risk,
            "dependencies": dependencies,
            "actual_hours": actual_hours,
        }
        stories.append(story)
        by_id[story_id] = story
    for index, story in enumerate(stories):
        path = f"$.stories[{index}].dependencies"
        for dep_index, dependency_id in enumerate(story["dependencies"]):
            if dependency_id not in by_id:
                raise InputError(
                    "E_UNKNOWN_STORY",
                    f"{path}[{dep_index}] 引用了未知 Story：{dependency_id}",
                )
    return stories, by_id


def parse_bolts(value: Any, story_ids: set[str]) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_FIELD", "$.bolts 必须是非空数组。")
    bolts: List[Dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(value):
        path = f"$.bolts[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象。")
        bolt_id = require_string(require_field(raw, "id", path), f"{path}.id")
        if bolt_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 Bolt ID：{bolt_id}")
        seen.add(bolt_id)
        story_id_list = require_field(raw, "story_ids", path)
        if not isinstance(story_id_list, list) or not story_id_list:
            raise InputError("E_INVALID_FIELD", f"{path}.story_ids 必须是非空字符串数组。")
        normalized: List[str] = []
        for story_index, story_id in enumerate(story_id_list):
            normalized_id = require_string(story_id, f"{path}.story_ids[{story_index}]")
            if normalized_id not in story_ids:
                raise InputError(
                    "E_UNKNOWN_STORY",
                    f"{path}.story_ids[{story_index}] 引用了未知 Story：{normalized_id}",
                )
            normalized.append(normalized_id)
        bolts.append({"id": bolt_id, "story_ids": normalized})
    return bolts


def estimation_error_percent(
    stories: List[Dict[str, Any]],
    hours_by_story: Dict[str, float],
) -> Optional[float]:
    estimated_total = 0.0
    actual_total = 0.0
    baseline_count = 0
    for story in stories:
        if story["actual_hours"] is None:
            continue
        baseline_count += 1
        estimated_total += hours_by_story[story["id"]]
        actual_total += story["actual_hours"]
    if baseline_count == 0:
        return None
    if actual_total == 0:
        return 0.0 if estimated_total == 0 else None
    error = abs(estimated_total - actual_total) / actual_total * 100.0
    return round(error, 2)


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象。")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise InputError(
            "E_SCHEMA_VERSION",
            f"schema_version 必须是 {SCHEMA_VERSION}。",
        )
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。")

    config = parse_config(data.get("estimation_config"))
    stories, story_by_id = parse_stories(data.get("stories"))
    bolts = parse_bolts(data.get("bolts"), set(story_by_id))

    hours_by_story = {
        story["id"]: round_hours(story_hours(story, config)) for story in stories
    }
    max_bolt_hours = config["max_bolt_hours"]

    bolt_estimates: List[Dict[str, Any]] = []
    overflow_count = 0
    for bolt in bolts:
        story_ids = sorted(set(bolt["story_ids"]))
        estimated = round_hours(sum(hours_by_story[story_id] for story_id in story_ids))
        scope_overflow = estimated > max_bolt_hours
        if scope_overflow:
            overflow_count += 1
        splits = split_suggestions(bolt["id"], story_ids, hours_by_story, max_bolt_hours)
        bolt_estimates.append(
            {
                "id": bolt["id"],
                "story_ids": story_ids,
                "estimated_hours": estimated,
                "scope_overflow": scope_overflow,
                "story_estimates": [
                    {
                        "story_id": story_id,
                        "estimated_hours": hours_by_story[story_id],
                        "complexity": story_by_id[story_id]["complexity"],
                        "risk": story_by_id[story_id]["risk"],
                        "dependency_count": len(story_by_id[story_id]["dependencies"]),
                    }
                    for story_id in story_ids
                ],
                "split_suggestions": splits,
            }
        )

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "estimation_config": config,
        "bolt_estimates": bolt_estimates,
        "metrics": {
            "schedule_estimation_error_percent": estimation_error_percent(
                stories, hours_by_story
            ),
            "scope_overflow_count": overflow_count,
        },
        "limitation": LIMITATION,
    }


def load_input(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("E_INPUT_NOT_FOUND", f"输入文件不存在：{path}") from exc
    except OSError as exc:
        raise InputError("E_INPUT_READ", f"无法读取输入文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_INVALID_JSON", f"输入不是有效 JSON（第 {exc.lineno} 行）。") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        report = build_report(load_input(args.input))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except InputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError:
        print("[ERROR E_OUTPUT_WRITE] 无法写入输出文件。", file=sys.stderr)
        return 1
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
