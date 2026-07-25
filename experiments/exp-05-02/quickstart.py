#!/usr/bin/env python3
"""Deterministic Simple / DDD Bolt type recommendation from a fixed rubric."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-05-02"
SCHEMA_VERSION = "1.0.0"
BOLT_TYPES = ("Simple", "DDD")
LEVEL = ("low", "medium", "high")
REVERSIBILITY = ("easy", "moderate", "hard")

LIMITATION = (
    "Bolt 类型建议仅依据本工具内置确定性量表生成；"
    "它不证明建议已达到专家级一致，也不能替代人工判断与领域评审。"
)

REQUIRED_REASON_IDS = (
    "R-DDD-CROSS-BOUNDARY",
    "R-DDD-HARD-REVERSE",
    "R-DDD-HIGH-COMPLEXITY",
    "R-DDD-HIGH-RISK",
    "R-GRAY-GATES",
    "R-GRAY-SPLIT",
    "R-SIMPLE-LOW-RISK",
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Simple/DDD Bolt 类型建议报告。")
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


def require_bool(value: Any, path: str) -> bool:
    if not isinstance(value, bool):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是布尔值")
    return value


def parse_input(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    task_description = require_nonempty_string(
        data.get("task_description"), "$.task_description"
    )
    domain_complexity = require_enum(
        data.get("domain_complexity"), "$.domain_complexity", LEVEL
    )
    risk = require_enum(data.get("risk"), "$.risk", LEVEL)
    reversibility = require_enum(
        data.get("reversibility"), "$.reversibility", REVERSIBILITY
    )
    cross_boundary_risk = (
        require_bool(data.get("cross_boundary_risk"), "$.cross_boundary_risk")
        if "cross_boundary_risk" in data
        else False
    )

    expert_label: Optional[str] = None
    if "expert_label" in data:
        raw = data.get("expert_label")
        if raw is not None:
            expert_label = require_enum(raw, "$.expert_label", BOLT_TYPES)

    return {
        "task_description": task_description,
        "domain_complexity": domain_complexity,
        "risk": risk,
        "reversibility": reversibility,
        "cross_boundary_risk": cross_boundary_risk,
        "expert_label": expert_label,
    }


def evaluate_rules(context: Dict[str, Any]) -> List[Dict[str, str]]:
    dc = context["domain_complexity"]
    risk = context["risk"]
    rev = context["reversibility"]
    cross = context["cross_boundary_risk"]

    candidates: List[Dict[str, str]] = []

    def add(rule_id: str, bolt: str, text: str, when: bool) -> None:
        if when:
            candidates.append({"rule_id": rule_id, "bolt_type": bolt, "text": text})

    add(
        "R-DDD-HIGH-COMPLEXITY",
        "DDD",
        "领域复杂度为 high，需要 DDD 阶段化建模与边界澄清。",
        dc == "high",
    )
    add(
        "R-DDD-HIGH-RISK",
        "DDD",
        "风险为 high，需要 DDD 级测试、审查与回滚设计。",
        risk == "high",
    )
    add(
        "R-DDD-HARD-REVERSE",
        "DDD",
        "可逆性为 hard，变更难以回退，需要 DDD 级设计与门禁。",
        rev == "hard",
    )
    add(
        "R-DDD-CROSS-BOUNDARY",
        "DDD",
        "存在跨边界风险，需要 DDD 显式上下文与集成契约。",
        cross,
    )
    add(
        "R-SIMPLE-LOW-RISK",
        "Simple",
        "低领域复杂度、低风险、易回退且无跨边界风险，可优先 Simple Bolt。",
        dc == "low" and risk == "low" and rev == "easy" and not cross,
    )
    return candidates


def clear_ddd(context: Dict[str, Any], matched: List[Dict[str, str]]) -> bool:
    return any(item["bolt_type"] == "DDD" for item in matched)


def clear_simple(context: Dict[str, Any], matched: List[Dict[str, str]]) -> bool:
    return any(item["rule_id"] == "R-SIMPLE-LOW-RISK" for item in matched)


def ddd_score(context: Dict[str, Any]) -> int:
    dc = context["domain_complexity"]
    risk = context["risk"]
    rev = context["reversibility"]
    score = 0
    if dc == "medium":
        score += 1
    elif dc == "high":
        score += 2
    if risk == "medium":
        score += 1
    elif risk == "high":
        score += 2
    if rev == "moderate":
        score += 1
    elif rev == "hard":
        score += 2
    if context["cross_boundary_risk"]:
        score += 2
    return score


def is_gray_zone(context: Dict[str, Any], matched: List[Dict[str, str]]) -> bool:
    if clear_ddd(context, matched) and not clear_simple(context, matched):
        return False
    if clear_simple(context, matched):
        return False
    return True


def build_gray_zone_advice(context: Dict[str, Any]) -> Dict[str, str]:
    dc = context["domain_complexity"]
    risk = context["risk"]
    if dc == "medium" and risk in ("medium", "high"):
        return {
            "advice_type": "split",
            "text": "领域与风险信号处于灰区，建议拆分为更小 Bolt 并单独验证边界假设。",
        }
    return {
        "advice_type": "gates",
        "text": "信号未达明确 DDD 或 Simple 边界，建议增加人工评审与发布门禁后再定型。",
    }


def choose_bolt_type(
    context: Dict[str, Any], matched: List[Dict[str, str]]
) -> Tuple[str, bool]:
    gray = is_gray_zone(context, matched)
    if clear_simple(context, matched) and not clear_ddd(context, matched):
        return "Simple", gray
    if clear_ddd(context, matched):
        return "DDD", gray
    if ddd_score(context) >= 2:
        return "DDD", True
    return "Simple", True


def build_reasons(matched: List[Dict[str, str]], chosen: str) -> List[Dict[str, str]]:
    reasons = [
        {"rule_id": item["rule_id"], "text": item["text"]}
        for item in matched
        if item["bolt_type"] == chosen
    ]
    if reasons:
        return reasons
    if chosen == "Simple":
        return [
            {
                "rule_id": "R-SIMPLE-LOW-RISK",
                "text": "未命中 DDD 强信号，灰区量表倾向轻量 Simple Bolt。",
            }
        ]
    return [
        {
            "rule_id": "R-DDD-HIGH-COMPLEXITY",
            "text": "灰区量表综合评分偏高，倾向 DDD 以控制集成与回滚风险。",
        }
    ]


def append_gray_reasons(
    reasons: List[Dict[str, str]], advice: Optional[Dict[str, str]]
) -> List[Dict[str, str]]:
    if not advice:
        return reasons
    rule_id = "R-GRAY-SPLIT" if advice["advice_type"] == "split" else "R-GRAY-GATES"
    extra = {"rule_id": rule_id, "text": advice["text"]}
    if any(item["rule_id"] == rule_id for item in reasons):
        return reasons
    return reasons + [extra]


def expert_agreement_rate(chosen: str, expert_label: Optional[str]) -> Optional[float]:
    if expert_label is None:
        return None
    return 100.0 if chosen == expert_label else 0.0


def engineering_counts(
    chosen: str, expert_label: Optional[str]
) -> Tuple[int, int]:
    if expert_label is None:
        return 0, 0
    over = 1 if chosen == "DDD" and expert_label == "Simple" else 0
    under = 1 if chosen == "Simple" and expert_label == "DDD" else 0
    return over, under


def build_report(raw: Any) -> Dict[str, Any]:
    context = parse_input(raw)
    matched = evaluate_rules(context)
    chosen, gray = choose_bolt_type(context, matched)
    gray_advice = build_gray_zone_advice(context) if gray else None
    reasons = append_gray_reasons(build_reasons(matched, chosen), gray_advice)
    fired_rule_ids = sorted({item["rule_id"] for item in matched})
    if gray_advice:
        fired_rule_ids = sorted(
            set(fired_rule_ids) | {reasons[-1]["rule_id"]}
        )
    over, under = engineering_counts(chosen, context["expert_label"])

    report: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "task_description": context["task_description"],
        "inputs": {
            "cross_boundary_risk": context["cross_boundary_risk"],
            "domain_complexity": context["domain_complexity"],
            "reversibility": context["reversibility"],
            "risk": context["risk"],
        },
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(raw).encode("utf-8")).hexdigest(),
        "bolt_type_recommendation": chosen,
        "selection_rationale": reasons,
        "gray_zone": gray,
        "metrics": {
            "expert_agreement_rate": expert_agreement_rate(
                chosen, context["expert_label"]
            ),
            "over_engineering_count": over,
            "under_engineering_count": under,
        },
        "rubric_basis": sorted(set(REQUIRED_REASON_IDS)),
        "fired_rule_ids": fired_rule_ids,
        "limitation": LIMITATION,
    }
    if gray_advice is not None:
        report["gray_zone_advice"] = gray_advice
    return report


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
