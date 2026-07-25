#!/usr/bin/env python3
"""Deterministic checkpoint budget simulation from risks and governance preferences."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-09-02"
SCHEMA_VERSION = "1.0.0"

REVERSIBILITY = ("high", "medium", "low")
IMPACT_SCOPE = ("local", "team", "organization", "external")
AUTONOMY = ("minimal", "balanced", "maximal")
SEVERITY = ("critical", "major", "minor")
PHASES = ("design", "implement", "verify", "release")
PHASE_ORDER = {name: index for index, name in enumerate(PHASES)}

SEVERITY_WEIGHT = {"critical": 3, "major": 2, "minor": 1}
REVIEW_COST = {"critical_touch": 2.0, "major_touch": 1.5, "other": 0.75}

LIMITATION = (
    "检查点预算仅依据本工具内置确定性加权规则生成，不构成强制治理法令；"
    "它不证明所有风险都能被预算公式穷尽，未建模风险仍需人工补充。"
)

RUBRIC_RULE_IDS = (
    "R-CP-MANDATORY-CRITICAL",
    "R-CP-MAJOR-GUARDRAIL",
    "R-CP-MINOR-GUARDRAIL",
    "R-CP-BASELINE-KICKOFF",
    "R-CP-BASELINE-MID-SYNC",
    "R-CP-BASELINE-ROLLBACK-VERIFY",
    "R-CP-BASELINE-PRE-RELEASE",
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成风险到检查点预算模拟报告。")
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


def parse_risks(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", "$.risks 必须是非空数组")
    risks: List[Dict[str, str]] = []
    seen: set[str] = set()
    for index, raw in enumerate(value):
        path = f"$.risks[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        risk_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if risk_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复风险 ID：{risk_id}")
        seen.add(risk_id)
        risks.append(
            {
                "id": risk_id,
                "statement": require_nonempty_string(raw.get("statement"), f"{path}.statement"),
                "severity": require_enum(raw.get("severity"), f"{path}.severity", SEVERITY),
                "phase": require_enum(raw.get("phase"), f"{path}.phase", PHASES),
            }
        )
    risks.sort(key=lambda item: item["id"])
    return risks


def parse_input(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    return {
        "task_name": require_nonempty_string(data.get("task_name"), "$.task_name"),
        "risks": parse_risks(data.get("risks")),
        "reversibility": require_enum(data.get("reversibility"), "$.reversibility", REVERSIBILITY),
        "impact_scope": require_enum(data.get("impact_scope"), "$.impact_scope", IMPACT_SCOPE),
        "autonomy_preference": require_enum(
            data.get("autonomy_preference"), "$.autonomy_preference", AUTONOMY
        ),
    }


def major_needs_checkpoint(context: Dict[str, Any]) -> bool:
    rev = context["reversibility"]
    scope = context["impact_scope"]
    autonomy = context["autonomy_preference"]
    return (
        rev == "low"
        or scope in ("team", "organization", "external")
        or autonomy == "minimal"
    )


def minor_needs_checkpoint(context: Dict[str, Any]) -> bool:
    return context["autonomy_preference"] == "minimal" and context["reversibility"] == "low"


def append_checkpoint(
    checkpoints: List[Dict[str, Any]],
    *,
    phase: str,
    rule_id: str,
    trigger: str,
    confirms: str,
    covers_risk_ids: List[str],
) -> None:
    checkpoints.append(
        {
            "phase": phase,
            "rule_id": rule_id,
            "trigger": trigger,
            "confirms": confirms,
            "covers_risk_ids": sorted(covers_risk_ids),
        }
    )


def build_checkpoints(context: Dict[str, Any]) -> List[Dict[str, Any]]:
    checkpoints: List[Dict[str, Any]] = []
    rev = context["reversibility"]
    scope = context["impact_scope"]
    autonomy = context["autonomy_preference"]

    for risk in sorted(context["risks"], key=lambda item: (-SEVERITY_WEIGHT[item["severity"]], item["id"])):
        rid = risk["id"]
        statement = risk["statement"]
        severity = risk["severity"]
        phase = risk["phase"]

        if severity == "critical":
            append_checkpoint(
                checkpoints,
                phase=phase,
                rule_id="R-CP-MANDATORY-CRITICAL",
                trigger=f"关键风险 {rid} 进入 {phase} 阶段",
                confirms=f"人工确认风险“{statement}”的缓解与剩余暴露可接受。",
                covers_risk_ids=[rid],
            )
        elif severity == "major" and major_needs_checkpoint(context):
            append_checkpoint(
                checkpoints,
                phase=phase,
                rule_id="R-CP-MAJOR-GUARDRAIL",
                trigger=f"重大风险 {rid} 在 {rev} 可逆性与 {scope} 影响面下需要闸门",
                confirms=f"人工审阅风险“{statement}”的缓解计划与证据。",
                covers_risk_ids=[rid],
            )
        elif severity == "minor" and minor_needs_checkpoint(context):
            append_checkpoint(
                checkpoints,
                phase=phase,
                rule_id="R-CP-MINOR-GUARDRAIL",
                trigger=f"低自治偏好下，次要风险 {rid} 仍需显式确认",
                confirms=f"人工确认风险“{statement}”已有可接受处置。",
                covers_risk_ids=[rid],
            )

    if autonomy == "minimal":
        append_checkpoint(
            checkpoints,
            phase="design",
            rule_id="R-CP-BASELINE-KICKOFF",
            trigger="自治偏好为 minimal，需要在设计阶段对齐人工意图",
            confirms="人工确认目标、边界与不可自动化决策清单。",
            covers_risk_ids=[],
        )

    if autonomy == "balanced":
        append_checkpoint(
            checkpoints,
            phase="implement",
            rule_id="R-CP-BASELINE-MID-SYNC",
            trigger="自治偏好为 balanced，实施中期需要同步检查点",
            confirms="人工确认当前增量与风险清单仍一致。",
            covers_risk_ids=[],
        )

    if rev == "low":
        append_checkpoint(
            checkpoints,
            phase="verify",
            rule_id="R-CP-BASELINE-ROLLBACK-VERIFY",
            trigger="可逆性为 low，必须验证回滚与恢复路径",
            confirms="人工确认回滚演练、数据恢复与观测信号齐备。",
            covers_risk_ids=[],
        )

    if scope in ("organization", "external"):
        append_checkpoint(
            checkpoints,
            phase="release",
            rule_id="R-CP-BASELINE-PRE-RELEASE",
            trigger=f"影响范围为 {scope}，发布前需要跨团队/外部影响闸门",
            confirms="人工确认发布窗口、沟通计划与升级路径。",
            covers_risk_ids=[],
        )

    checkpoints.sort(
        key=lambda item: (
            PHASE_ORDER[item["phase"]],
            item["rule_id"],
            ",".join(item["covers_risk_ids"]),
            item["trigger"],
        )
    )

    for index, checkpoint in enumerate(checkpoints, start=1):
        checkpoint["id"] = f"CP-{index:03d}"
        checkpoint["essential"] = bool(checkpoint["covers_risk_ids"]) or checkpoint["rule_id"] in (
            "R-CP-BASELINE-ROLLBACK-VERIFY",
            "R-CP-BASELINE-PRE-RELEASE",
        )

    return checkpoints


def critical_risk_coverage_percent(
    risks: List[Dict[str, str]], checkpoints: List[Dict[str, Any]]
) -> float:
    critical_ids = {risk["id"] for risk in risks if risk["severity"] == "critical"}
    if not critical_ids:
        return 100.0
    covered: set[str] = set()
    for checkpoint in checkpoints:
        for risk_id in checkpoint["covers_risk_ids"]:
            if risk_id in critical_ids:
                covered.add(risk_id)
    return round(len(covered) / len(critical_ids) * 100, 2)


def nonessential_checkpoint_count(checkpoints: List[Dict[str, Any]]) -> int:
    critical_ids = set()
    return sum(1 for checkpoint in checkpoints if not checkpoint["essential"])


def checkpoint_review_cost(checkpoint: Dict[str, Any], risks_by_id: Dict[str, Dict[str, str]]) -> float:
    covered = checkpoint["covers_risk_ids"]
    if not covered:
        return REVIEW_COST["other"]
    severities = {risks_by_id[rid]["severity"] for rid in covered if rid in risks_by_id}
    if "critical" in severities:
        return REVIEW_COST["critical_touch"]
    if "major" in severities:
        return REVIEW_COST["major_touch"]
    return REVIEW_COST["other"]


def estimated_review_cost_hours(
    checkpoints: List[Dict[str, Any]], risks_by_id: Dict[str, Dict[str, str]]
) -> float:
    total = sum(checkpoint_review_cost(item, risks_by_id) for item in checkpoints)
    return round(total, 2)


def cost_benefit_estimate(
    checkpoints: List[Dict[str, Any]],
    risks: List[Dict[str, str]],
    review_cost: float,
) -> Dict[str, float]:
    risks_by_id = {risk["id"]: risk for risk in risks}
    covered_ids: set[str] = set()
    for checkpoint in checkpoints:
        covered_ids.update(checkpoint["covers_risk_ids"])

    reduction = sum(
        SEVERITY_WEIGHT[risks_by_id[rid]["severity"]] for rid in sorted(covered_ids) if rid in risks_by_id
    )
    reduction = round(float(reduction), 2)
    ratio = round(reduction / review_cost, 2) if review_cost > 0 else 0.0
    return {
        "estimated_review_cost_hours": review_cost,
        "estimated_risk_reduction_score": reduction,
        "benefit_cost_ratio": ratio,
    }


def fired_rule_ids(checkpoints: List[Dict[str, Any]]) -> List[str]:
    return sorted({checkpoint["rule_id"] for checkpoint in checkpoints})


def build_report(raw: Any) -> Dict[str, Any]:
    context = parse_input(raw)
    checkpoints = build_checkpoints(context)
    risks_by_id = {risk["id"]: risk for risk in context["risks"]}
    review_cost = estimated_review_cost_hours(checkpoints, risks_by_id)

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "task_name": context["task_name"],
        "inputs": {
            "autonomy_preference": context["autonomy_preference"],
            "impact_scope": context["impact_scope"],
            "reversibility": context["reversibility"],
            "risk_count": len(context["risks"]),
        },
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(raw).encode("utf-8")).hexdigest(),
        "checkpoint_count": len(checkpoints),
        "checkpoint_placements": checkpoints,
        "cost_benefit_estimate": cost_benefit_estimate(checkpoints, context["risks"], review_cost),
        "metrics": {
            "critical_risk_coverage_percent": critical_risk_coverage_percent(
                context["risks"], checkpoints
            ),
            "nonessential_checkpoint_count": nonessential_checkpoint_count(checkpoints),
            "estimated_review_cost": review_cost,
        },
        "rubric_basis": list(RUBRIC_RULE_IDS),
        "fired_rule_ids": fired_rule_ids(checkpoints),
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
