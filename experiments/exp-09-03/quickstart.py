#!/usr/bin/env python3
"""Validate a brownfield three-flow decision case against a frozen choose-flow guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-09-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/brownfield_flow_decision_guide.json"
EXPECTED_PIN = (
    "sha256:0af0a8b0344a245e7d2a3a08c92da32a5a6d1076e9a00712420be0a6723db685"
)
FLOWS = ("Simple", "FIRE", "AI-DLC")
LIMITATION = (
    "本报告仅对照仓库内冻结的棕地 Flow 决策指南与输入三方案案例做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Simple/FIRE/AI-DLC 决策依据与流程开销。")
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


def load_frozen_guide(experiment_root: Path) -> Dict[str, Any]:
    path = experiment_root / GUIDE_REL
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("E_GUIDE_NOT_FOUND", str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_GUIDE_JSON", f"冻结指南 JSON 无效（第 {exc.lineno} 行）") from exc
    if not isinstance(data, dict):
        raise InputError("E_GUIDE_SHAPE", "冻结指南根节点必须是对象")
    if data.get("pinned_version") != EXPECTED_PIN:
        raise InputError("E_GUIDE_PIN", "冻结指南 pinned_version 与实验登记不一致")
    return data


def require_enum(value: Any, path: str, allowed: Sequence[str]) -> str:
    if not isinstance(value, str) or value not in allowed:
        raise InputError("E_INVALID_ENUM", f"{path} 必须是以下之一：{', '.join(allowed)}")
    return value


def parse_rationale(value: Any, required_dimensions: Sequence[str]) -> List[Dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_INVALID_FIELD", "$.decision_rationale 必须是非空数组")
    required_set = set(required_dimensions)
    parsed: List[Dict[str, str]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.decision_rationale[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        dimension_id = item.get("dimension_id")
        if not isinstance(dimension_id, str) or dimension_id not in required_set:
            raise InputError("E_UNKNOWN_DIMENSION", f"{path}.dimension_id 未在指南登记：{dimension_id}")
        if dimension_id in seen:
            raise InputError("E_DUPLICATE_DIMENSION", f"{path}.dimension_id 重复：{dimension_id}")
        seen.add(dimension_id)
        text = item.get("text")
        if not isinstance(text, str) or not text.strip():
            raise InputError("E_INVALID_FIELD", f"{path}.text 必须是非空字符串")
        parsed.append({"dimension_id": dimension_id, "text": text.strip()})
    parsed.sort(key=lambda row: row["dimension_id"])
    return parsed


def parse_flow_options(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or len(value) != 3:
        raise InputError("E_INVALID_FIELD", "$.flow_options 必须是长度为 3 的数组")
    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.flow_options[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        flow = require_enum(item.get("flow"), f"{path}.flow", FLOWS)
        if flow in seen:
            raise InputError("E_DUPLICATE_FLOW", f"{path}.flow 重复：{flow}")
        seen.add(flow)
        feasible = item.get("feasible")
        if not isinstance(feasible, bool):
            raise InputError("E_INVALID_FIELD", f"{path}.feasible 必须是布尔值")
        parsed.append({"flow": flow, "feasible": feasible})
    if seen != set(FLOWS):
        raise InputError("E_INCOMPLETE_FLOWS", "$.flow_options 必须覆盖 Simple、FIRE、AI-DLC")
    parsed.sort(key=lambda row: row["flow"])
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    case_id = raw.get("case_id")
    if not isinstance(case_id, str) or not case_id.strip():
        raise InputError("E_INVALID_FIELD", "$.case_id 必须是非空字符串")
    chosen_flow = require_enum(raw.get("chosen_flow"), "$.chosen_flow", FLOWS)
    required_dims = [
        d
        for d in guide.get("required_rationale_dimensions", [])
        if isinstance(d, str) and d
    ]
    if len(required_dims) < 1:
        raise InputError("E_GUIDE_SHAPE", "指南 required_rationale_dimensions 无效")
    rationale = parse_rationale(raw.get("decision_rationale"), required_dims)
    flow_options = parse_flow_options(raw.get("flow_options"))
    chosen_row = next((row for row in flow_options if row["flow"] == chosen_flow), None)
    if chosen_row is None:
        raise InputError("E_CHOSEN_NOT_LISTED", "$.chosen_flow 未出现在 flow_options 中")
    if not chosen_row["feasible"]:
        raise InputError("E_INFEASIBLE_CHOICE", f"所选 Flow 不可行：{chosen_flow}")
    return {
        "pinned_version": pinned,
        "case_id": case_id.strip(),
        "chosen_flow": chosen_flow,
        "decision_rationale": rationale,
        "flow_options": flow_options,
        "required_dimensions": required_dims,
    }


def overhead_score(chosen_flow: str, guide: Dict[str, Any]) -> float:
    weights = guide.get("overhead_weights")
    if not isinstance(weights, dict):
        raise InputError("E_GUIDE_SHAPE", "指南 overhead_weights 必须是对象")
    weight = weights.get(chosen_flow)
    if not isinstance(weight, (int, float)):
        raise InputError("E_GUIDE_SHAPE", f"指南缺少 {chosen_flow} 开销权重")
    return round(float(weight) * 10.0, 2)


def evaluate(context: Dict[str, Any]) -> Dict[str, Any]:
    covered = {row["dimension_id"] for row in context["decision_rationale"]}
    required = context["required_dimensions"]
    coverage = round(100.0 * len(covered) / len(required), 2)
    valid = coverage == 100.0
    return {
        "decision_rationale_coverage_percent": coverage,
        "valid": valid,
    }


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw, guide)
    evaluation = evaluate(context)
    overhead = overhead_score(context["chosen_flow"], guide)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": evaluation["valid"],
        "case_id": context["case_id"],
        "chosen_flow": context["chosen_flow"],
        "flow_options": context["flow_options"],
        "decision_rationale": context["decision_rationale"],
        "metrics": {
            "decision_rationale_coverage_percent": evaluation["decision_rationale_coverage_percent"],
            "estimated_process_overhead_score": overhead,
        },
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(raw).encode("utf-8")).hexdigest(),
        "limitation": LIMITATION,
    }


def load_input(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("E_INPUT_NOT_FOUND", f"输入文件不存在：{path}") from exc
    except OSError as exc:
        raise InputError("E_INPUT_READ", f"无法读取输入：{path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_INVALID_JSON", f"输入不是有效 JSON（第 {exc.lineno} 行）") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    experiment_root = Path(__file__).resolve().parent
    try:
        guide = load_frozen_guide(experiment_root)
        report = build_report(load_input(args.input), guide)
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
