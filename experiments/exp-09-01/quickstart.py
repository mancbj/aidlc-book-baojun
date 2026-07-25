#!/usr/bin/env python3
"""Deterministic Simple / FIRE / AI-DLC flow recommendation from a fixed rubric."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-09-01"
SCHEMA_VERSION = "1.0.0"
FLOWS = ("Simple", "FIRE", "AI-DLC")
FLOW_PRIORITY = {"AI-DLC": 3, "FIRE": 2, "Simple": 1}

TASK_COMPLEXITY = ("low", "medium", "high")
CODEBASE_STATE = ("greenfield", "brownfield")
TEAM_SCALE = ("small", "medium", "large")
COMPLIANCE = ("none", "moderate", "high")

LIMITATION = (
    "Flow 建议仅依据本工具内置确定性量表生成，不构成强制选型法令；"
    "它不证明建议已达到专家级一致，最终责任仍在人工判断。"
)

REQUIRED_REASON_IDS = (
    "R-AI-DLC-HIGH-COMPLEXITY",
    "R-AI-DLC-HIGH-COMPLIANCE",
    "R-AI-DLC-LARGE-BROWNFIELD",
    "R-FIRE-MEDIUM-COMPLEXITY",
    "R-FIRE-BROWNFIELD",
    "R-FIRE-MODERATE-COMPLIANCE",
    "R-FIRE-LARGE-TEAM",
    "R-SIMPLE-LOW-RISK",
    "R-DEFAULT-SIMPLE",
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Simple/FIRE/AI-DLC Flow 建议报告。")
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


def require_enum(value: Any, path: str, allowed: Tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        allowed_text = ", ".join(allowed)
        raise InputError("E_INVALID_ENUM", f"{path} 必须是以下之一：{allowed_text}")
    return value


def parse_input(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    task_name = require_nonempty_string(data.get("task_name"), "$.task_name")
    task_complexity = require_enum(
        data.get("task_complexity"), "$.task_complexity", TASK_COMPLEXITY
    )
    codebase_state = require_enum(
        data.get("codebase_state"), "$.codebase_state", CODEBASE_STATE
    )
    team_scale = require_enum(data.get("team_scale"), "$.team_scale", TEAM_SCALE)
    compliance_requirements = require_enum(
        data.get("compliance_requirements"),
        "$.compliance_requirements",
        COMPLIANCE,
    )

    expert_label: Optional[str] = None
    if "expert_label" in data:
        raw = data.get("expert_label")
        if raw is not None:
            expert_label = require_enum(raw, "$.expert_label", FLOWS)

    return {
        "task_name": task_name,
        "task_complexity": task_complexity,
        "codebase_state": codebase_state,
        "team_scale": team_scale,
        "compliance_requirements": compliance_requirements,
        "expert_label": expert_label,
    }


def evaluate_rules(context: Dict[str, Any]) -> List[Dict[str, str]]:
    tc = context["task_complexity"]
    cs = context["codebase_state"]
    ts = context["team_scale"]
    cr = context["compliance_requirements"]

    candidates: List[Dict[str, str]] = []

    def add(rule_id: str, flow: str, text: str, when: bool) -> None:
        if when:
            candidates.append({"rule_id": rule_id, "flow": flow, "text": text})

    add(
        "R-AI-DLC-HIGH-COMPLEXITY",
        "AI-DLC",
        "任务复杂度为 high，需要完整 AI-DLC 治理与分阶段交付。",
        tc == "high",
    )
    add(
        "R-AI-DLC-HIGH-COMPLIANCE",
        "AI-DLC",
        "合规要求为 high，需要可追溯、可审计的 AI-DLC 级门禁。",
        cr == "high",
    )
    add(
        "R-AI-DLC-LARGE-BROWNFIELD",
        "AI-DLC",
        "大型团队在棕地代码库上集成，存在高不可逆变更风险。",
        ts == "large" and cs == "brownfield" and tc != "low",
    )
    add(
        "R-FIRE-MEDIUM-COMPLEXITY",
        "FIRE",
        "任务复杂度为 medium，适合 FIRE 的快进快出与检查点平衡。",
        tc == "medium",
    )
    add(
        "R-FIRE-BROWNFIELD",
        "FIRE",
        "棕地代码库需要回归、集成与发布检查点。",
        cs == "brownfield",
    )
    add(
        "R-FIRE-MODERATE-COMPLIANCE",
        "FIRE",
        "中等合规要求需要额外审阅与证据检查点。",
        cr == "moderate",
    )
    add(
        "R-FIRE-LARGE-TEAM",
        "FIRE",
        "大型团队需要协调责任边界与同步检查点。",
        ts == "large",
    )
    add(
        "R-SIMPLE-LOW-RISK",
        "Simple",
        "低复杂度、绿地、小团队且无额外合规，可优先 Simple Flow。",
        tc == "low" and cs == "greenfield" and ts == "small" and cr == "none",
    )
    return candidates


def choose_flow(matched: List[Dict[str, str]]) -> str:
    if not matched:
        return "Simple"
    flows = {item["flow"] for item in matched}
    return max(flows, key=lambda name: FLOW_PRIORITY[name])


def build_reasons(matched: List[Dict[str, str]], chosen: str) -> List[Dict[str, str]]:
    reasons = [
        {"rule_id": item["rule_id"], "text": item["text"]}
        for item in matched
        if item["flow"] == chosen
    ]
    if reasons:
        return reasons
    return [
        {
            "rule_id": "R-DEFAULT-SIMPLE",
            "text": "未命中更高仪式规则，默认采用轻量 Simple Flow。",
        }
    ]


def build_inapplicable(context: Dict[str, Any], chosen: str) -> List[Dict[str, str]]:
    tc = context["task_complexity"]
    cs = context["codebase_state"]
    ts = context["team_scale"]
    cr = context["compliance_requirements"]
    items: List[Dict[str, str]] = []

    def append(flow: str, condition: str) -> None:
        items.append({"flow": flow, "condition": condition})

    if chosen != "Simple":
        if tc != "low":
            append("Simple", f"任务复杂度为 {tc}，超出 Simple 低仪式边界。")
        if cs != "greenfield":
            append("Simple", f"代码库状态为 {cs}，Simple 缺少棕地回归检查点。")
        if ts != "small":
            append("Simple", f"团队规模为 {ts}，Simple 难以覆盖协调需求。")
        if cr != "none":
            append("Simple", f"合规要求为 {cr}，Simple 证据链不足。")

    if chosen != "FIRE":
        if tc == "high":
            append("FIRE", "任务复杂度为 high，FIRE 检查点预算不足以覆盖风险。")
        if cr == "high":
            append("FIRE", "合规要求为 high，FIRE 追溯深度不足。")
        if ts == "large" and cs == "brownfield" and tc != "low":
            append("FIRE", "大型团队棕地高不可逆集成，FIRE 仪式强度不足。")
        if tc == "low" and cs == "greenfield" and ts == "small" and cr == "none":
            append("FIRE", "低复杂度绿地小团队无合规，FIRE 会造成过度仪式。")

    if chosen != "AI-DLC":
        if tc == "high" or cr == "high" or (ts == "large" and cs == "brownfield" and tc != "low"):
            append("AI-DLC", "存在更高仪式信号，但当前量表优先匹配 FIRE。")
        elif tc == "low" and cr in ("none", "moderate") and not (
            ts == "large" and cs == "brownfield"
        ):
            append("AI-DLC", "风险信号未达 AI-DLC 级，完整治理链成本过高。")
        elif cs == "greenfield" and tc == "low" and cr == "none":
            append("AI-DLC", "绿地低合规任务不需要 AI-DLC 全链路治理。")
        else:
            append("AI-DLC", f"当前输入更匹配 {chosen}，AI-DLC 全链路治理成本过高。")

    if chosen != "FIRE":
        if tc == "medium" or cs == "brownfield" or cr == "moderate" or ts == "large":
            if chosen == "Simple":
                append("FIRE", f"存在中等风险信号，但当前量表优先匹配 {chosen}。")
        elif tc == "low" and cs == "greenfield" and ts == "small" and cr == "none":
            append("FIRE", "低复杂度绿地小团队无合规，FIRE 会造成过度仪式。")
        elif chosen == "AI-DLC":
            append("FIRE", "存在 FIRE 级信号，但更高优先级规则已选择 AI-DLC。")

    if chosen != "Simple":
        if tc == "low" and cs == "greenfield" and ts == "small" and cr == "none":
            append("Simple", f"低仪式条件已满足，但当前量表优先匹配 {chosen}。")

    for flow in FLOWS:
        if flow == chosen:
            continue
        if not any(item["flow"] == flow for item in items):
            append(flow, f"当前输入更匹配 {chosen}，{flow} 不是首选。")

    items.sort(key=lambda item: (item["flow"], item["condition"]))
    return items


def reason_completeness_rate(reasons: List[Dict[str, str]]) -> float:
    if not reasons:
        return 0.0
    complete = sum(
        1
        for reason in reasons
        if isinstance(reason.get("rule_id"), str)
        and reason["rule_id"]
        and isinstance(reason.get("text"), str)
        and reason["text"].strip()
    )
    return round(complete / len(reasons) * 100, 2)


def expert_agreement_rate(chosen: str, expert_label: Optional[str]) -> Optional[float]:
    if expert_label is None:
        return None
    return 100.0 if chosen == expert_label else 0.0


def build_report(raw: Any) -> Dict[str, Any]:
    context = parse_input(raw)
    matched = evaluate_rules(context)
    chosen = choose_flow(matched)
    reasons = build_reasons(matched, chosen)
    inapplicable = build_inapplicable(context, chosen)
    fired_rule_ids = sorted({item["rule_id"] for item in matched})
    if not fired_rule_ids and chosen == "Simple":
        fired_rule_ids = ["R-DEFAULT-SIMPLE"]

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "task_name": context["task_name"],
        "inputs": {
            "task_complexity": context["task_complexity"],
            "codebase_state": context["codebase_state"],
            "team_scale": context["team_scale"],
            "compliance_requirements": context["compliance_requirements"],
        },
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(raw).encode("utf-8")).hexdigest(),
        "flow_recommendation": chosen,
        "reasons": reasons,
        "inapplicable_conditions": inapplicable,
        "metrics": {
            "expert_agreement_rate": expert_agreement_rate(
                chosen, context["expert_label"]
            ),
            "reason_completeness_rate": reason_completeness_rate(reasons),
        },
        "rubric_basis": sorted(set(REQUIRED_REASON_IDS)),
        "fired_rule_ids": fired_rule_ids,
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
