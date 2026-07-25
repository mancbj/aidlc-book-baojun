#!/usr/bin/env python3
"""Validate an AI-DLC three-phase trajectory against a frozen lifecycle guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-01-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/aidlc_three_phase_guide.json"
EXPECTED_PIN = (
    "sha256:9cd45974f4bd264ca4a357f79e1171e8ea23ea44ddd9d1060c8ab3c24b60ec39"
)
LIMITATION = (
    "本报告仅对照仓库内冻结的 AI-DLC 三阶段指南夹具与输入轨迹做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Inception/Construction/Operations 工件与检查点。")
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


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串")
    return value.strip()


def parse_checkpoint_list(value: Any, path: str) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是数组")
    parsed: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{item_path} 必须是对象")
        cp_id = require_string(item.get("checkpoint_id"), f"{item_path}.checkpoint_id")
        observed = item.get("observed")
        if not isinstance(observed, bool):
            raise InputError("E_INVALID_FIELD", f"{item_path}.observed 必须是布尔值")
        parsed.append({"checkpoint_id": cp_id, "observed": observed})
    return parsed


def parse_artifacts(value: Any, path: str) -> Dict[str, bool]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
    result: Dict[str, bool] = {}
    for key, val in value.items():
        if not isinstance(key, str) or not key.strip():
            raise InputError("E_INVALID_FIELD", f"{path} 的键必须是非空字符串")
        if not isinstance(val, bool):
            raise InputError("E_INVALID_FIELD", f"{path}.{key} 必须是布尔值")
        result[key.strip()] = val
    return result


def parse_trajectory(value: Any, guide: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.trajectory 必须是对象")
    phases = guide.get("phases")
    if not isinstance(phases, list):
        raise InputError("E_GUIDE_SHAPE", "指南 phases 必须是数组")
    expected_ids = [
        p.get("phase_id")
        for p in phases
        if isinstance(p, dict) and isinstance(p.get("phase_id"), str)
    ]
    parsed: Dict[str, Dict[str, Any]] = {}
    for phase_id in expected_ids:
        if phase_id not in value:
            raise InputError("E_MISSING_PHASE", f"$.trajectory 缺少阶段：{phase_id}")
    extra = set(value) - set(expected_ids)
    if extra:
        raise InputError("E_UNKNOWN_PHASE", f"$.trajectory 含未知阶段：{sorted(extra)[0]}")
    for phase_id in expected_ids:
        record = value[phase_id]
        base = f"$.trajectory.{phase_id}"
        if not isinstance(record, dict):
            raise InputError("E_INVALID_FIELD", f"{base} 必须是对象")
        artifacts = parse_artifacts(record.get("artifacts"), f"{base}.artifacts")
        checkpoints = parse_checkpoint_list(record.get("checkpoints"), f"{base}.checkpoints")
        parsed[phase_id] = {"artifacts": artifacts, "checkpoints": checkpoints}
    return parsed


def parse_input(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    return {"pinned_version": pinned, "trajectory_raw": raw.get("trajectory")}


def evaluate_phase(
    phase_meta: Dict[str, Any],
    record: Dict[str, Any],
) -> Dict[str, Any]:
    phase_id = phase_meta["phase_id"]
    required_artifacts = [
        a for a in phase_meta.get("required_artifacts", []) if isinstance(a, str) and a
    ]
    expected_cps = [c for c in phase_meta.get("checkpoints", []) if isinstance(c, str) and c]

    present = sum(1 for a in required_artifacts if record["artifacts"].get(a) is True)
    artifact_pct = (
        100.0 if not required_artifacts else round(100.0 * present / len(required_artifacts), 2)
    )

    cp_map = {item["checkpoint_id"]: item["observed"] for item in record["checkpoints"]}
    missing_cp = [cp for cp in expected_cps if cp not in cp_map]
    if missing_cp:
        raise InputError(
            "E_MISSING_CHECKPOINT",
            f"$.trajectory.{phase_id} 缺少检查点：{missing_cp[0]}",
        )
    satisfied_cps = sum(1 for cp in expected_cps if cp_map.get(cp) is True)
    checkpoint_adherence = (
        100.0 if not expected_cps else round(100.0 * satisfied_cps / len(expected_cps), 2)
    )

    return {
        "phase_id": phase_id,
        "artifact_completeness_percent": artifact_pct,
        "checkpoint_adherence_percent": checkpoint_adherence,
        "required_artifact_count": len(required_artifacts),
        "present_artifact_count": present,
        "checkpoint_count": len(expected_cps),
        "satisfied_checkpoint_count": satisfied_cps,
    }


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw)
    trajectory = parse_trajectory(context["trajectory_raw"], guide)
    phases_guide = guide.get("phases")
    if not isinstance(phases_guide, list):
        raise InputError("E_GUIDE_SHAPE", "指南 phases 必须是数组")

    phase_reports: List[Dict[str, Any]] = []
    artifact_pcts: List[float] = []
    total_checkpoints = 0
    total_satisfied = 0

    for meta in phases_guide:
        if not isinstance(meta, dict):
            raise InputError("E_GUIDE_SHAPE", "指南 phase 项必须是对象")
        phase_id = meta.get("phase_id")
        if not isinstance(phase_id, str):
            raise InputError("E_GUIDE_SHAPE", "指南 phase_id 必须是字符串")
        report = evaluate_phase(meta, trajectory[phase_id])
        phase_reports.append(report)
        artifact_pcts.append(report["artifact_completeness_percent"])
        total_checkpoints += report["checkpoint_count"]
        total_satisfied += report["satisfied_checkpoint_count"]

    overall_artifact = round(sum(artifact_pcts) / len(artifact_pcts), 2) if artifact_pcts else 0.0
    valid = all(r["artifact_completeness_percent"] == 100.0 for r in phase_reports) and all(
        r["satisfied_checkpoint_count"] == r["checkpoint_count"] for r in phase_reports
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": valid,
        "phases": phase_reports,
        "metrics": {
            "artifact_completeness_percent": overall_artifact,
            "checkpoint_count": total_checkpoints,
            "satisfied_checkpoint_count": total_satisfied,
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
