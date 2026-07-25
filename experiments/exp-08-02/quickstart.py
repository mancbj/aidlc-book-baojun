#!/usr/bin/env python3
"""Deterministic tabletop rollback drill timeline simulator."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-08-02"
SCHEMA_VERSION = "1.0.0"
PHASES = ("detect", "decide", "rollback", "recover")
LIMITATION = (
    "桌面演练时间线与 Runbook 缺口只表示演练脚本可复现性；"
    "它不证明生产环境真实恢复能力或数据零损失。"
)

TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


class DrillInputError(Exception):
    """An input error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成回滚桌面演练 detect→decide→rollback→recover 时间线。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="演练报告输出 JSON。")
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
        raise DrillInputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise DrillInputError("E_EXPECTED_ARRAY", f"{path} 必须是数组。")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DrillInputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise DrillInputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def parse_timestamp(value: Any, path: str) -> datetime:
    text = require_string(value, path)
    if not TIMESTAMP_PATTERN.match(text):
        raise DrillInputError("E_INVALID_TIMESTAMP", f"{path} 必须是 UTC ISO-8601 时间戳。")
    normalized = text.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def format_timestamp(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def require_positive_number(value: Any, path: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise DrillInputError("E_EXPECTED_NUMBER", f"{path} 必须是正数。")
    if value <= 0:
        raise DrillInputError("E_EXPECTED_NUMBER", f"{path} 必须是正数。")
    return float(value)


def parse_topology(value: Any) -> Dict[str, Any]:
    root = require_object(value, "$.deployment_topology")
    environment = require_string(
        require_field(root, "environment", "$.deployment_topology"),
        "$.deployment_topology.environment",
    )
    components_raw = require_list(
        require_field(root, "components", "$.deployment_topology"), "$.deployment_topology.components"
    )
    components: Dict[str, Dict[str, Any]] = {}
    for index, raw in enumerate(components_raw):
        path = f"$.deployment_topology.components[{index}]"
        entry = require_object(raw, path)
        comp_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if comp_id in components:
            raise DrillInputError("E_DUPLICATE_ID", f"组件 ID 重复：{comp_id}")
        parsed: Dict[str, Any] = {
            "id": comp_id,
            "current_version": require_string(
                require_field(entry, "current_version", path), f"{path}.current_version"
            ),
        }
        if "rollback_target" in entry:
            parsed["rollback_target"] = require_string(
                entry["rollback_target"], f"{path}.rollback_target"
            )
        components[comp_id] = parsed
    return {"environment": environment, "components": components}


def parse_fault(value: Any) -> Dict[str, Any]:
    root = require_object(value, "$.fault_scenario")
    path = "$.fault_scenario"
    fault_id = require_string(require_field(root, "id", path), f"{path}.id")
    data_impact = root.get("data_impact")
    if not isinstance(data_impact, bool):
        raise DrillInputError("E_EXPECTED_BOOLEAN", f"{path}.data_impact 必须是布尔值。")
    affected_raw = require_list(
        require_field(root, "affected_component_ids", path), f"{path}.affected_component_ids"
    )
    affected: List[str] = []
    for index, item in enumerate(affected_raw):
        affected.append(require_string(item, f"{path}.affected_component_ids[{index}]"))
    return {
        "id": fault_id,
        "summary": require_string(require_field(root, "summary", path), f"{path}.summary"),
        "occurred_at": require_string(
            require_field(root, "occurred_at", path), f"{path}.occurred_at"
        ),
        "affected_component_ids": affected,
        "data_impact": data_impact,
        "_occurred_at": parse_timestamp(root["occurred_at"], f"{path}.occurred_at"),
    }


def parse_signals(value: Any, fault_id: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(require_list(value, "$.monitoring_signals")):
        path = f"$.monitoring_signals[{index}]"
        entry = require_object(raw, path)
        signal_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if signal_id in seen:
            raise DrillInputError("E_DUPLICATE_ID", f"监控信号 ID 重复：{signal_id}")
        seen.add(signal_id)
        linked = require_string(
            require_field(entry, "fault_scenario_id", path), f"{path}.fault_scenario_id"
        )
        if linked != fault_id:
            raise DrillInputError(
                "E_UNKNOWN_FAULT_ID",
                f"{path}.fault_scenario_id 与 fault_scenario.id 不一致：{linked}",
            )
        observed = require_string(
            require_field(entry, "observed_at", path), f"{path}.observed_at"
        )
        items.append(
            {
                "id": signal_id,
                "signal": require_string(
                    require_field(entry, "signal", path), f"{path}.signal"
                ),
                "source": require_string(
                    require_field(entry, "source", path), f"{path}.source"
                ),
                "observed_at": observed,
                "fault_scenario_id": linked,
                "_observed_at": parse_timestamp(observed, f"{path}.observed_at"),
            }
        )
    return items


def parse_runbook(value: Any, component_ids: Set[str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(require_list(value, "$.runbook_steps")):
        path = f"$.runbook_steps[{index}]"
        entry = require_object(raw, path)
        step_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if step_id in seen:
            raise DrillInputError("E_DUPLICATE_ID", f"Runbook 步骤 ID 重复：{step_id}")
        seen.add(step_id)
        phase = require_string(require_field(entry, "phase", path), f"{path}.phase")
        if phase not in PHASES:
            raise DrillInputError(
                "E_INVALID_PHASE",
                f"{path}.phase 必须是 detect、decide、rollback、recover 之一。",
            )
        started = require_string(
            require_field(entry, "started_at", path), f"{path}.started_at"
        )
        duration = require_positive_number(
            require_field(entry, "duration_minutes", path), f"{path}.duration_minutes"
        )
        parsed: Dict[str, Any] = {
            "id": step_id,
            "phase": phase,
            "title": require_string(require_field(entry, "title", path), f"{path}.title"),
            "started_at": started,
            "duration_minutes": duration,
            "_started_at": parse_timestamp(started, f"{path}.started_at"),
            "_ended_at": parse_timestamp(started, f"{path}.started_at")
            + timedelta(minutes=duration),
        }
        if "target_component_ids" in entry:
            targets_raw = require_list(entry["target_component_ids"], f"{path}.target_component_ids")
            targets: List[str] = []
            for t_index, target in enumerate(targets_raw):
                target_id = require_string(
                    target, f"{path}.target_component_ids[{t_index}]"
                )
                if target_id not in component_ids:
                    raise DrillInputError(
                        "E_UNKNOWN_COMPONENT_ID",
                        f"{path}.target_component_ids 引用了未知组件：{target_id}",
                    )
                targets.append(target_id)
            parsed["target_component_ids"] = targets
        items.append(parsed)
    return items


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(
        require_field(root, "experiment_id", "$"), "$.experiment_id"
    )
    if experiment_id != EXPERIMENT_ID:
        raise DrillInputError(
            "E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。"
        )
    topology = parse_topology(require_field(root, "deployment_topology", "$"))
    component_ids = set(topology["components"])
    fault = parse_fault(require_field(root, "fault_scenario", "$"))
    for affected in fault["affected_component_ids"]:
        if affected not in component_ids:
            raise DrillInputError(
                "E_UNKNOWN_COMPONENT_ID",
                f"fault_scenario.affected_component_ids 引用了未知组件：{affected}",
            )
    signals = parse_signals(require_field(root, "monitoring_signals", "$"), fault["id"])
    runbook = parse_runbook(require_field(root, "runbook_steps", "$"), component_ids)
    return {
        "experiment_id": experiment_id,
        "topology": topology,
        "fault": fault,
        "signals": signals,
        "runbook": runbook,
    }


def step_sort_key(step: Dict[str, Any]) -> Tuple[datetime, str]:
    return step["_started_at"], step["id"]


def signal_sort_key(signal: Dict[str, Any]) -> Tuple[datetime, str]:
    return signal["_observed_at"], signal["id"]


def steps_by_phase(runbook: Sequence[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {phase: [] for phase in PHASES}
    for step in runbook:
        grouped[step["phase"]].append(step)
    for phase in PHASES:
        grouped[phase].sort(key=step_sort_key)
    return grouped


def strip_internal(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if record is None:
        return None
    return {key: value for key, value in record.items() if not key.startswith("_")}


def strip_step(step: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if step is None:
        return None
    result = strip_internal(step)
    if result is None:
        return None
    if isinstance(result.get("duration_minutes"), float) and result["duration_minutes"].is_integer():
        result["duration_minutes"] = int(result["duration_minutes"])
    return result


def minutes_between(start: datetime, end: datetime) -> float:
    delta = end - start
    return round(delta.total_seconds() / 60.0, 2)


def collect_runbook_gaps(
    grouped: Dict[str, List[Dict[str, Any]]],
    fault: Dict[str, Any],
    topology: Dict[str, Any],
) -> List[Dict[str, str]]:
    gaps: List[Dict[str, str]] = []
    for phase in PHASES:
        if not grouped[phase]:
            gaps.append(
                {
                    "code": f"MISSING_PHASE_{phase.upper()}",
                    "detail": f"Runbook 缺少 {phase} 阶段步骤。",
                }
            )
    rollback_steps = grouped["rollback"]
    if rollback_steps:
        step = rollback_steps[0]
        targets = step.get("target_component_ids")
        if not targets:
            gaps.append(
                {
                    "code": "ROLLBACK_TARGETS_UNSPECIFIED",
                    "detail": "rollback 步骤未声明 target_component_ids。",
                }
            )
        else:
            affected = set(fault["affected_component_ids"])
            target_set = set(targets)
            uncovered = sorted(affected - target_set)
            if uncovered:
                gaps.append(
                    {
                        "code": "UNCOVERED_AFFECTED_COMPONENT",
                        "detail": f"受影响组件未纳入 rollback 目标：{', '.join(uncovered)}。",
                    }
                )
            components = topology["components"]
            for target in sorted(target_set):
                component = components[target]
                if "rollback_target" not in component:
                    gaps.append(
                        {
                            "code": "MISSING_ROLLBACK_TARGET",
                            "detail": f"组件 {target} 缺少 rollback_target。",
                        }
                    )
    gaps.sort(key=lambda item: (item["code"], item["detail"]))
    return gaps


def build_phase_entry(
    phase: str,
    started: datetime,
    ended: datetime,
    runbook_step: Optional[Dict[str, Any]],
    monitoring_signal_ids: Optional[List[str]] = None,
    codes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    entry: Dict[str, Any] = {
        "phase": phase,
        "started_at": format_timestamp(started),
        "ended_at": format_timestamp(ended),
        "runbook_step": strip_step(runbook_step),
        "codes": codes or [],
    }
    if monitoring_signal_ids is not None:
        entry["monitoring_signal_ids"] = monitoring_signal_ids
    return entry


def build_report(raw_data: Any) -> Dict[str, Any]:
    data = validate_input(raw_data)
    fault = data["fault"]
    signals = sorted(data["signals"], key=signal_sort_key)
    grouped = steps_by_phase(data["runbook"])
    gaps = collect_runbook_gaps(grouped, fault, data["topology"])

    detect_signals = signals
    detect_step = grouped["detect"][0] if grouped["detect"] else None
    decide_step = grouped["decide"][0] if grouped["decide"] else None
    rollback_step = grouped["rollback"][0] if grouped["rollback"] else None
    recover_step = grouped["recover"][0] if grouped["recover"] else None

    if detect_signals:
        detect_started = detect_signals[0]["_observed_at"]
        signal_ids = [item["id"] for item in detect_signals]
        detect_codes = ["DETECT_FROM_MONITORING"]
    elif detect_step:
        detect_started = detect_step["_started_at"]
        signal_ids = []
        detect_codes = ["DETECT_FROM_RUNBOOK_ONLY"]
    else:
        detect_started = fault["_occurred_at"]
        signal_ids = []
        detect_codes = ["DETECT_INFERRED_FROM_FAULT"]

    if detect_step and detect_step["_ended_at"] > detect_started:
        detect_ended = detect_step["_ended_at"]
    else:
        detect_ended = detect_started

    timeline: List[Dict[str, Any]] = []
    timeline.append(
        build_phase_entry(
            "detect",
            detect_started,
            detect_ended,
            detect_step,
            monitoring_signal_ids=signal_ids,
            codes=detect_codes,
        )
    )

    if decide_step:
        timeline.append(
            build_phase_entry(
                "decide",
                decide_step["_started_at"],
                decide_step["_ended_at"],
                decide_step,
                codes=["PHASE_ANCHORED"],
            )
        )

    if rollback_step:
        timeline.append(
            build_phase_entry(
                "rollback",
                rollback_step["_started_at"],
                rollback_step["_ended_at"],
                rollback_step,
                codes=["PHASE_ANCHORED"],
            )
        )

    if recover_step:
        timeline.append(
            build_phase_entry(
                "recover",
                recover_step["_started_at"],
                recover_step["_ended_at"],
                recover_step,
                codes=["PHASE_ANCHORED"],
            )
        )

    detect_to_rollback: Optional[float] = None
    if rollback_step:
        detect_to_rollback = minutes_between(detect_started, rollback_step["_started_at"])

    data_loss_window: Optional[float] = None
    if fault["data_impact"]:
        if rollback_step:
            data_loss_window = minutes_between(fault["_occurred_at"], rollback_step["_ended_at"])
        else:
            data_loss_window = minutes_between(fault["_occurred_at"], detect_ended)

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(raw_data),
        "valid": True,
        "metrics": {
            "detect_to_rollback_minutes": detect_to_rollback,
            "data_loss_window_minutes": data_loss_window,
            "runbook_gap_count": len(gaps),
        },
        "summary": {
            "environment": data["topology"]["environment"],
            "fault_scenario_id": fault["id"],
            "monitoring_signal_count": len(signals),
            "runbook_step_count": len(data["runbook"]),
        },
        "drill_timeline": timeline,
        "runbook_gaps": gaps,
        "limitation": LIMITATION,
        "interpretation": (
            "detect 锚定最早监控信号；若无信号则使用 detect Runbook 或故障发生时刻。"
            "decide、rollback、recover 各取最早 Runbook 步骤。"
            "data_loss_window_minutes 在 data_impact=true 时度量故障至 rollback 结束窗口；"
            "否则为 null。桌面演练不等于 CH-07 Verify，Recover 中的 Runtime Verify 指运行态核验。"
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
    except DrillInputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
