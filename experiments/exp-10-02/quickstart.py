#!/usr/bin/env python3
"""Generate a deterministic AI-DLC pilot value scorecard."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from statistics import median
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-10-02"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "记分卡仅对输入中的交付基线、运行记录、缺陷与业务结果做确定性汇总；"
    "它不证明某次试点的业务价值已被因果证实。"
)
SCALE_DECISIONS = ("expand", "shrink", "stop")

# Deterministic scale thresholds (pilot rubric, not organizational policy).
CYCLE_TIME_IMPROVE_EXPAND_PERCENT = -5.0
CYCLE_TIME_REGRESSION_STOP_PERCENT = 15.0
DEFECT_ESCAPE_EXPAND_MAX = 0.10
DEFECT_ESCAPE_STOP_MIN = 0.30
REVIEW_BURDEN_EXPAND_MAX = 1.25
REVIEW_BURDEN_STOP_MIN = 2.0
BUSINESS_DECLINE_STOP_PERCENT = -10.0


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 AI-DLC 试点价值记分卡。")
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


def round_percent(value: float) -> float:
    return round(value, 2)


def round_ratio(value: float) -> float:
    return round(value, 4)


def require_nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串")
    return value.strip()


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组")
    return value


def require_positive_number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是正数")
    number = float(value)
    if number <= 0:
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是正数")
    return number


def require_non_negative_number(value: Any, path: str) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是非负数")
    number = float(value)
    if number < 0:
        raise InputError("E_INVALID_NUMBER", f"{path} 必须是非负数")
    return number


def parse_baseline(value: Any) -> Dict[str, float]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.delivery_baseline 必须是对象")
    return {
        "median_cycle_time_hours": require_positive_number(
            value.get("median_cycle_time_hours"),
            "$.delivery_baseline.median_cycle_time_hours",
        ),
        "human_review_minutes_per_delivery": require_non_negative_number(
            value.get("human_review_minutes_per_delivery"),
            "$.delivery_baseline.human_review_minutes_per_delivery",
        ),
    }


def parse_runs(value: Any) -> List[Dict[str, Any]]:
    runs: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(require_list(value, "$.aidlc_runs")):
        path = f"$.aidlc_runs[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        run_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if run_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{run_id}")
        seen.add(run_id)
        runs.append(
            {
                "id": run_id,
                "cycle_time_hours": require_positive_number(
                    raw.get("cycle_time_hours"), f"{path}.cycle_time_hours"
                ),
                "human_review_minutes": require_non_negative_number(
                    raw.get("human_review_minutes"), f"{path}.human_review_minutes"
                ),
            }
        )
    runs.sort(key=lambda item: item["id"])
    return runs


def parse_defects(value: Any, run_ids: Set[str]) -> List[Dict[str, Any]]:
    defects: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    items = value if value is not None else []
    if not isinstance(items, list):
        raise InputError("E_INVALID_FIELD", "$.defects 必须是数组")
    for index, raw in enumerate(items):
        path = f"$.defects[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        defect_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if defect_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{defect_id}")
        seen.add(defect_id)
        run_id = require_nonempty_string(raw.get("run_id"), f"{path}.run_id")
        if run_id not in run_ids:
            raise InputError("E_UNKNOWN_RUN", f"{path}.run_id 引用了未知运行：{run_id}")
        escaped = raw.get("escaped")
        if not isinstance(escaped, bool):
            raise InputError("E_INVALID_FIELD", f"{path}.escaped 必须是布尔值")
        defects.append({"id": defect_id, "run_id": run_id, "escaped": escaped})
    defects.sort(key=lambda item: item["id"])
    return defects


def parse_business_outcomes(value: Any) -> Optional[Dict[str, Any]]:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.business_outcomes 必须是对象或 null")
    baseline = value.get("baseline_value")
    current = value.get("current_value")
    if baseline is None and current is None:
        return None
    if baseline is None or current is None:
        raise InputError(
            "E_INCOMPLETE_BUSINESS",
            "$.business_outcomes 的 baseline_value 与 current_value 必须同时提供或同时为 null",
        )
    unit = value.get("unit")
    parsed: Dict[str, Any] = {
        "baseline_value": require_non_negative_number(
            baseline, "$.business_outcomes.baseline_value"
        ),
        "current_value": require_non_negative_number(
            current, "$.business_outcomes.current_value"
        ),
    }
    if unit is not None:
        parsed["unit"] = require_nonempty_string(unit, "$.business_outcomes.unit")
    return parsed


def compute_cycle_time_change_percent(
    baseline_hours: float, runs: List[Dict[str, Any]]
) -> Tuple[float, Dict[str, Any]]:
    observed = [run["cycle_time_hours"] for run in runs]
    current_median = float(median(observed))
    change = ((current_median - baseline_hours) / baseline_hours) * 100.0
    return round_percent(change), {
        "baseline_median_cycle_time_hours": baseline_hours,
        "observed_median_cycle_time_hours": round(current_median, 4),
        "run_count": len(runs),
        "cycle_time_change_percent": round_percent(change),
    }


def compute_defect_escape_rate(
    runs: List[Dict[str, Any]], defects: List[Dict[str, Any]]
) -> Tuple[float, Dict[str, Any]]:
    deliveries = len(runs)
    escaped = sum(1 for defect in defects if defect["escaped"])
    rate = escaped / deliveries if deliveries else 0.0
    return round_ratio(rate), {
        "deliveries_count": deliveries,
        "defects_total": len(defects),
        "defects_escaped": escaped,
        "defect_escape_rate": round_ratio(rate),
    }


def compute_human_review_burden(
    baseline_minutes: float, runs: List[Dict[str, Any]]
) -> Tuple[float, Dict[str, Any]]:
    if baseline_minutes == 0:
        average = sum(run["human_review_minutes"] for run in runs) / len(runs)
        return round_ratio(average), {
            "baseline_human_review_minutes_per_delivery": baseline_minutes,
            "observed_average_human_review_minutes": round(average, 4),
            "human_review_burden_ratio": None,
            "note": "基线审阅分钟为 0，输出绝对平均审阅分钟作为负担代理",
        }
    average = sum(run["human_review_minutes"] for run in runs) / len(runs)
    ratio = average / baseline_minutes
    return round_ratio(ratio), {
        "baseline_human_review_minutes_per_delivery": baseline_minutes,
        "observed_average_human_review_minutes": round(average, 4),
        "human_review_burden_ratio": round_ratio(ratio),
    }


def compute_business_result_change(
    business: Optional[Dict[str, Any]],
) -> Tuple[Optional[float], Dict[str, Any]]:
    if business is None:
        return None, {
            "status": "not_provided",
            "baseline_value": None,
            "current_value": None,
            "business_result_change_percent": None,
        }
    baseline = business["baseline_value"]
    current = business["current_value"]
    if baseline == 0:
        change: Optional[float] = None
        panel: Dict[str, Any] = {
            "status": "baseline_zero",
            "baseline_value": baseline,
            "current_value": current,
            "business_result_change_percent": change,
        }
        if business.get("unit"):
            panel["unit"] = business["unit"]
        return change, panel
    percent = ((current - baseline) / baseline) * 100.0
    panel = {
        "status": "computed",
        "baseline_value": baseline,
        "current_value": current,
        "business_result_change_percent": round_percent(percent),
    }
    if business.get("unit"):
        panel["unit"] = business["unit"]
    return round_percent(percent), panel


def evaluate_scale_decision(
    cycle_change: float,
    defect_escape_rate: float,
    review_burden: float,
    business_change: Optional[float],
    baseline_review_minutes: float,
    observed_review_average: float,
) -> Dict[str, Any]:
    stop_codes: List[str] = []
    expand_codes: List[str] = []
    shrink_codes: List[str] = []

    if defect_escape_rate >= DEFECT_ESCAPE_STOP_MIN:
        stop_codes.append("STOP_HIGH_DEFECT_ESCAPE")
    if cycle_change >= CYCLE_TIME_REGRESSION_STOP_PERCENT:
        stop_codes.append("STOP_CYCLE_REGRESSION")
    if baseline_review_minutes > 0 and review_burden >= REVIEW_BURDEN_STOP_MIN:
        stop_codes.append("STOP_REVIEW_OVERLOAD")
    if business_change is not None and business_change <= BUSINESS_DECLINE_STOP_PERCENT:
        stop_codes.append("STOP_BUSINESS_DECLINE")

    if cycle_change <= CYCLE_TIME_IMPROVE_EXPAND_PERCENT:
        expand_codes.append("EXPAND_CYCLE_IMPROVED")
    else:
        shrink_codes.append("SHRINK_CYCLE_NOT_IMPROVED")

    if defect_escape_rate <= DEFECT_ESCAPE_EXPAND_MAX:
        expand_codes.append("EXPAND_QUALITY_STABLE")
    else:
        shrink_codes.append("SHRINK_ELEVATED_DEFECT_ESCAPE")

    if baseline_review_minutes == 0:
        shrink_codes.append("SHRINK_REVIEW_BASELINE_ZERO")
    elif review_burden <= REVIEW_BURDEN_EXPAND_MAX:
        expand_codes.append("EXPAND_REVIEW_ACCEPTABLE")
    else:
        shrink_codes.append("SHRINK_REVIEW_BURDEN_HIGH")

    if business_change is None:
        shrink_codes.append("SHRINK_BUSINESS_NOT_PROVIDED")
    elif business_change > 0:
        expand_codes.append("EXPAND_BUSINESS_UP")
    elif business_change == 0:
        shrink_codes.append("SHRINK_BUSINESS_FLAT")
    else:
        shrink_codes.append("SHRINK_BUSINESS_DOWN")

    if stop_codes:
        decision = "stop"
        reason_codes = sorted(set(stop_codes))
    elif len(expand_codes) >= 4:
        decision = "expand"
        reason_codes = sorted(set(expand_codes))
    else:
        decision = "shrink"
        reason_codes = sorted(set(shrink_codes + expand_codes))

    rationale = build_rationale(
        decision,
        cycle_change,
        defect_escape_rate,
        review_burden,
        business_change,
        observed_review_average,
    )
    return {
        "decision": decision,
        "allowed_decisions": list(SCALE_DECISIONS),
        "reason_codes": reason_codes,
        "rationale": rationale,
    }


def build_rationale(
    decision: str,
    cycle_change: float,
    defect_escape_rate: float,
    review_burden: float,
    business_change: Optional[float],
    observed_review_average: float,
) -> List[str]:
    lines = [
        f"交付周期相对基线变化 {cycle_change:+.2f}%。",
        f"缺陷逃逸率为 {defect_escape_rate:.4f}（逃逸数／交付次数）。",
        f"人工审阅负担比率为 {review_burden:.4f}（观测均值 {observed_review_average:.4f} 分钟）。",
    ]
    if business_change is None:
        lines.append("业务结果未提供，规模决策不将其视为因果收益信号。")
    else:
        lines.append(f"业务结果相对基线变化 {business_change:+.2f}%。")
    if decision == "expand":
        lines.append("周期、质量、审阅与业务信号同时满足扩大试点的内置阈值。")
    elif decision == "stop":
        lines.append("至少一项停止阈值被触发；应暂停扩大并回到责任与节奏检查。")
    else:
        lines.append("信号混合或未同时满足扩大条件；建议收缩试点范围并补齐证据。")
    return lines


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    pilot_name = require_nonempty_string(data.get("pilot_name"), "$.pilot_name")
    baseline = parse_baseline(data.get("delivery_baseline"))
    runs = parse_runs(data.get("aidlc_runs"))
    run_ids = {run["id"] for run in runs}
    defects = parse_defects(data.get("defects"), run_ids)
    business = parse_business_outcomes(data.get("business_outcomes"))

    cycle_change, cycle_panel = compute_cycle_time_change_percent(
        baseline["median_cycle_time_hours"], runs
    )
    defect_rate, quality_panel = compute_defect_escape_rate(runs, defects)
    review_burden, review_panel = compute_human_review_burden(
        baseline["human_review_minutes_per_delivery"], runs
    )
    business_change, business_panel = compute_business_result_change(business)

    observed_review_average = review_panel["observed_average_human_review_minutes"]
    scale_decision = evaluate_scale_decision(
        cycle_change,
        defect_rate,
        review_burden,
        business_change,
        baseline["human_review_minutes_per_delivery"],
        observed_review_average,
    )

    metrics: Dict[str, Any] = {
        "cycle_time_change_percent": cycle_change,
        "defect_escape_rate": defect_rate,
        "human_review_burden": review_burden,
        "business_result_change": business_change,
    }

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pilot_name": pilot_name,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "scorecard": {
            "cycle_time": cycle_panel,
            "quality": quality_panel,
            "review_burden": review_panel,
            "business_result": business_panel,
        },
        "metrics": metrics,
        "scale_decision": scale_decision,
        "threshold_basis": sorted(
            [
                "BUSINESS_DECLINE_STOP",
                "CYCLE_TIME_IMPROVE_EXPAND",
                "CYCLE_TIME_REGRESSION_STOP",
                "DEFECT_ESCAPE_EXPAND_MAX",
                "DEFECT_ESCAPE_STOP_MIN",
                "REVIEW_BURDEN_EXPAND_MAX",
                "REVIEW_BURDEN_STOP_MIN",
            ]
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
