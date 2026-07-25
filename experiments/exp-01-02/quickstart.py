#!/usr/bin/env python3
"""Build a deterministic AI-Assisted vs AI-Driven workflow comparison report."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set

EXPERIMENT_ID = "EXP-01-02"
SCHEMA_VERSION = "1.0.0"
REQUIRED_MODES = ("ai_assisted", "ai_driven")
LIMITATION = (
    "对照报告仅汇总输入中冻结的两套交付记录与证据链；"
    "它不证明 AI-Assisted 或 AI-Driven 在全部团队、任务或约束下更优。"
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 AI-Assisted 与 AI-Driven 对照报告。")
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


def require_nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串")
    return value.strip()


def require_non_negative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是非负整数")
    if value < 0:
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是非负整数")
    return value


def require_positive_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是正数")
    number = float(value)
    if number <= 0:
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是正数")
    return number


def require_string_list(value: Any, path: str) -> List[str]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空字符串数组")
    links: List[str] = []
    for index, item in enumerate(value):
        links.append(require_nonempty_string(item, f"{path}[{index}]"))
    return links


def parse_feature(value: Any) -> Dict[str, str]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.feature 必须是对象")
    return {
        "id": require_nonempty_string(value.get("id"), "$.feature.id"),
        "name": require_nonempty_string(value.get("name"), "$.feature.name"),
        "intent_summary": require_nonempty_string(
            value.get("intent_summary"), "$.feature.intent_summary"
        ),
    }


def parse_workflow_records(value: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(value, list) or len(value) != 2:
        raise InputError("E_REQUIRED_COLLECTION", "$.workflow_records 必须恰好包含两条记录")
    by_mode: Dict[str, Dict[str, Any]] = {}
    for index, raw in enumerate(value):
        path = f"$.workflow_records[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        mode = require_nonempty_string(raw.get("workflow_mode"), f"{path}.workflow_mode")
        if mode not in REQUIRED_MODES:
            raise InputError(
                "E_UNKNOWN_WORKFLOW_MODE",
                f"{path}.workflow_mode 必须是 ai_assisted 或 ai_driven",
            )
        if mode in by_mode:
            raise InputError("E_DUPLICATE_WORKFLOW_MODE", f"重复的 workflow_mode：{mode}")
        record_id = require_nonempty_string(raw.get("record_id"), f"{path}.record_id")
        by_mode[mode] = {
            "record_id": record_id,
            "workflow_mode": mode,
            "human_roundtrips": require_non_negative_int(
                raw.get("human_roundtrips"), f"{path}.human_roundtrips"
            ),
            "escaped_defects": require_non_negative_int(
                raw.get("escaped_defects"), f"{path}.escaped_defects"
            ),
            "elapsed_minutes": require_positive_number(
                raw.get("elapsed_minutes"), f"{path}.elapsed_minutes"
            ),
            "evidence_links": require_string_list(raw.get("evidence_links"), f"{path}.evidence_links"),
        }
    missing = [mode for mode in REQUIRED_MODES if mode not in by_mode]
    if missing:
        raise InputError("E_MISSING_WORKFLOW_MODE", f"缺少 workflow_mode：{', '.join(missing)}")
    return by_mode


def side_for_mode(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "record_id": record["record_id"],
        "workflow_mode": record["workflow_mode"],
        "human_roundtrips": record["human_roundtrips"],
        "escaped_defects": record["escaped_defects"],
        "end_to_end_minutes": record["elapsed_minutes"],
        "evidence_links": list(record["evidence_links"]),
        "evidence_link_count": len(record["evidence_links"]),
    }


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    feature = parse_feature(data.get("feature"))
    records = parse_workflow_records(data.get("workflow_records"))
    assisted = records["ai_assisted"]
    driven = records["ai_driven"]
    assisted_side = side_for_mode(assisted)
    driven_side = side_for_mode(driven)
    roundtrip_delta = driven["human_roundtrips"] - assisted["human_roundtrips"]
    defect_delta = driven["escaped_defects"] - assisted["escaped_defects"]
    minutes_delta = round(driven["elapsed_minutes"] - assisted["elapsed_minutes"], 2)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "feature": feature,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "valid": True,
        "comparison": {
            "ai_assisted": assisted_side,
            "ai_driven": driven_side,
        },
        "metrics": {
            "ai_assisted": {
                "human_roundtrips": assisted["human_roundtrips"],
                "escaped_defects": assisted["escaped_defects"],
                "end_to_end_minutes": assisted["elapsed_minutes"],
            },
            "ai_driven": {
                "human_roundtrips": driven["human_roundtrips"],
                "escaped_defects": driven["escaped_defects"],
                "end_to_end_minutes": driven["elapsed_minutes"],
            },
            "delta": {
                "human_roundtrip_delta": roundtrip_delta,
                "escaped_defect_delta": defect_delta,
                "end_to_end_minutes_delta": minutes_delta,
            },
        },
        "observation": (
            f"同一功能「{feature['name']}」：AI-Assisted 人工往返 {assisted['human_roundtrips']} 次、"
            f"缺陷逃逸 {assisted['escaped_defects']} 项、端到端 {assisted['elapsed_minutes']} 分钟；"
            f"AI-Driven 分别为 {driven['human_roundtrips']} 次、"
            f"{driven['escaped_defects']} 项、{driven['elapsed_minutes']} 分钟。"
        ),
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
        raise InputError("E_INVALID_JSON", f"输入不是有效 JSON（第 {exc.lineno} 行）") from exc


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
        print("[ERROR E_OUTPUT_WRITE] 无法写入输出文件", file=sys.stderr)
        return 1
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
