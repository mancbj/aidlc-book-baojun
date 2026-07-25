#!/usr/bin/env python3
"""Deterministic Bolt type stage / checkpoint adherence against a frozen guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-05-03"
SCHEMA_VERSION = "1.0.0"
EXPECTED_PIN = (
    "sha256:32d73fc5231f81eabaf9c881e1c64f3353882c605c729bfbbca9f5bb4aa0b481"
)
GUIDE_PATH = Path(__file__).resolve().parent / "fixtures" / "bolt_type_checkpoint_guide.json"
TRACK_KEYS = ("simple", "ddd")
STAGE_STATUS = ("completed", "in_progress", "pending", "skipped")

LIMITATION = (
    "本报告仅对照仓库内冻结的 Bolt 类型检查点指南夹具与输入阶段记录做确定性核对；"
    "它不将外部 specs.md 页面或该 pin 写成唯一标准，也不能替代人工 Bolt 类型选择与阶段裁量。"
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Simple/DDD 阶段完整率与检查点遵循率。")
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


def load_frozen_guide() -> Dict[str, Any]:
    try:
        data = json.loads(GUIDE_PATH.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError("E_GUIDE_READ", f"无法读取冻结指南：{GUIDE_PATH}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_GUIDE_JSON", f"冻结指南不是有效 JSON（第 {exc.lineno} 行）") from exc
    if not isinstance(data, dict):
        raise InputError("E_GUIDE_SHAPE", "冻结指南根节点必须是对象")
    if data.get("pinned_version") != EXPECTED_PIN:
        raise InputError("E_GUIDE_PIN", "冻结指南 pinned_version 与实验登记 pin 不一致")
    return data


def require_enum(value: Any, path: str, allowed: Tuple[str, ...]) -> str:
    if not isinstance(value, str) or value not in allowed:
        allowed_text = ", ".join(allowed)
        raise InputError("E_INVALID_ENUM", f"{path} 必须是以下之一：{allowed_text}")
    return value


def parse_checkpoint_list(value: Any, path: str) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是数组")
    parsed: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{item_path} 必须是对象")
        checkpoint_id = require_enum(
            item.get("checkpoint_id"), f"{item_path}.checkpoint_id", ("human_validation",)
        )
        observed = item.get("observed")
        if not isinstance(observed, bool):
            raise InputError("E_INVALID_FIELD", f"{item_path}.observed 必须是布尔值")
        parsed.append({"checkpoint_id": checkpoint_id, "observed": observed})
    return parsed


def parse_stage_list(value: Any, path: str) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是数组")
    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{item_path} 必须是对象")
        stage_id = require_enum(
            item.get("stage_id"),
            f"{item_path}.stage_id",
            (
                "plan",
                "implement",
                "test",
                "domain-model",
                "technical-design",
                "adr-analysis",
            ),
        )
        if stage_id in seen:
            raise InputError("E_DUPLICATE_STAGE", f"{item_path}.stage_id 重复：{stage_id}")
        seen.add(stage_id)
        status = require_enum(item.get("status"), f"{item_path}.status", STAGE_STATUS)
        checkpoints = parse_checkpoint_list(item.get("checkpoints"), f"{item_path}.checkpoints")
        parsed.append(
            {"stage_id": stage_id, "status": status, "checkpoints": checkpoints}
        )
    return parsed


def parse_stage_records(value: Any) -> Dict[str, Dict[str, Any]]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.stage_records 必须是对象")
    parsed: Dict[str, Dict[str, Any]] = {}
    for track in TRACK_KEYS:
        if track not in value:
            raise InputError("E_MISSING_TRACK", f"$.stage_records 缺少轨道：{track}")
        record = value[track]
        path = f"$.stage_records.{track}"
        if not isinstance(record, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        bolt_id = record.get("bolt_id")
        if not isinstance(bolt_id, str) or not bolt_id.strip():
            raise InputError("E_INVALID_FIELD", f"{path}.bolt_id 必须是非空字符串")
        stages = parse_stage_list(record.get("stages"), f"{path}.stages")
        parsed[track] = {"bolt_id": bolt_id.strip(), "stages": stages}
    extra = set(value) - set(TRACK_KEYS)
    if extra:
        raise InputError("E_UNKNOWN_TRACK", f"$.stage_records 含未知轨道：{sorted(extra)[0]}")
    return parsed


def parse_input(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = data.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    stage_records = parse_stage_records(data.get("stage_records"))
    return {"pinned_version": pinned, "stage_records": stage_records}


def guide_stage_map(track_guide: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    stages = track_guide.get("stages")
    if not isinstance(stages, list):
        raise InputError("E_GUIDE_SHAPE", "指南 stages 必须是数组")
    mapping: Dict[str, Dict[str, Any]] = {}
    for item in stages:
        if not isinstance(item, dict):
            raise InputError("E_GUIDE_SHAPE", "指南 stage 项必须是对象")
        stage_id = item.get("stage_id")
        if not isinstance(stage_id, str):
            raise InputError("E_GUIDE_SHAPE", "指南 stage_id 必须是字符串")
        mapping[stage_id] = item
    return mapping


def evaluate_track(
    track_key: str,
    guide_track: Dict[str, Any],
    record: Dict[str, Any],
) -> Dict[str, Any]:
    stage_by_id = {item["stage_id"]: item for item in record["stages"]}
    guide_stages = guide_stage_map(guide_track)

    unknown = sorted(set(stage_by_id) - set(guide_stages))
    if unknown:
        raise InputError(
            "E_UNKNOWN_STAGE",
            f"$.stage_records.{track_key} 含指南未定义阶段：{unknown[0]}",
        )

    required_ids = [
        stage_id
        for stage_id, meta in guide_stages.items()
        if meta.get("required") is True
    ]
    completed_required = sum(
        1
        for stage_id in required_ids
        if stage_by_id.get(stage_id, {}).get("status") == "completed"
    )
    stage_completeness = (
        0.0 if not required_ids else round(100.0 * completed_required / len(required_ids), 2)
    )

    required_checkpoint_total = 0
    satisfied_checkpoint_total = 0
    stage_details: List[Dict[str, Any]] = []

    for stage_id, meta in sorted(guide_stages.items()):
        required = meta.get("required") is True
        expected_checkpoints = meta.get("checkpoints")
        if not isinstance(expected_checkpoints, list):
            raise InputError("E_GUIDE_SHAPE", f"指南 {track_key}.{stage_id} checkpoints 无效")
        expected_ids = [
            cp for cp in expected_checkpoints if isinstance(cp, str) and cp
        ]
        counts_toward_adherence = required

        observed = stage_by_id.get(stage_id)
        if observed is None:
            stage_details.append(
                {
                    "stage_id": stage_id,
                    "required": required,
                    "status": "missing",
                    "checkpoint_adherence_percent": 0.0 if required else None,
                }
            )
            if counts_toward_adherence:
                required_checkpoint_total += len(expected_ids)
            continue

        status = observed["status"]
        observed_map = {
            item["checkpoint_id"]: item["observed"] for item in observed["checkpoints"]
        }
        missing_cp = [cp for cp in expected_ids if cp not in observed_map]
        if missing_cp:
            raise InputError(
                "E_MISSING_CHECKPOINT",
                f"$.stage_records.{track_key} 阶段 {stage_id} 缺少检查点：{missing_cp[0]}",
            )

        if counts_toward_adherence:
            required_checkpoint_total += len(expected_ids)

        satisfied = 0
        if status == "completed":
            for cp_id in expected_ids:
                if observed_map.get(cp_id) is True:
                    satisfied += 1
                    if counts_toward_adherence:
                        satisfied_checkpoint_total += 1

        cp_percent: Optional[float]
        if counts_toward_adherence:
            cp_percent = (
                0.0
                if not expected_ids
                else round(100.0 * satisfied / len(expected_ids), 2)
            )
        else:
            cp_percent = None

        stage_details.append(
            {
                "stage_id": stage_id,
                "required": required,
                "status": status,
                "checkpoint_adherence_percent": cp_percent,
            }
        )

    checkpoint_adherence = (
        0.0
        if required_checkpoint_total == 0
        else round(100.0 * satisfied_checkpoint_total / required_checkpoint_total, 2)
    )

    return {
        "bolt_id": record["bolt_id"],
        "bolt_type": guide_track.get("bolt_type"),
        "stage_completeness_percent": stage_completeness,
        "checkpoint_adherence_percent": checkpoint_adherence,
        "stages": stage_details,
    }


def average_percent(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return round(sum(values) / len(values), 2)


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw)
    guide_tracks = guide.get("tracks")
    if not isinstance(guide_tracks, dict):
        raise InputError("E_GUIDE_SHAPE", "指南 tracks 必须是对象")

    track_reports: Dict[str, Any] = {}
    completeness_values: List[float] = []
    adherence_values: List[float] = []

    for track_key in TRACK_KEYS:
        guide_track = guide_tracks.get(track_key)
        if not isinstance(guide_track, dict):
            raise InputError("E_GUIDE_SHAPE", f"指南缺少轨道 {track_key}")
        report = evaluate_track(track_key, guide_track, context["stage_records"][track_key])
        track_reports[track_key] = report
        completeness_values.append(report["stage_completeness_percent"])
        adherence_values.append(report["checkpoint_adherence_percent"])

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "tracks": track_reports,
        "metrics": {
            "stage_completeness_percent": average_percent(completeness_values),
            "checkpoint_adherence_percent": average_percent(adherence_values),
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
        raise InputError("E_INPUT_READ", f"无法读取输入文件：{path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_INVALID_JSON", f"输入不是有效 JSON（第 {exc.lineno} 行）") from exc


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        guide = load_frozen_guide()
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
