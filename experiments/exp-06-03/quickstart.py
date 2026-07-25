#!/usr/bin/env python3
"""Validate end-to-end Bolt execution artifacts against a frozen guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-06-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/bolt_execution_guide.json"
EXPECTED_PIN = (
    "sha256:fe6252a58966ef23ac663a313c1a62094a1d70f08ce1bb536fdc950721f21bb2"
)
STAGE_STATUS = ("completed", "in_progress", "pending", "skipped")
LIMITATION = (
    "本报告仅对照仓库内冻结的 Bolt 执行指南与输入阶段工件做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 plan→implement→test Bolt 工件与耗时。")
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


def parse_timing(value: Any) -> int:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.timing 必须是对象")
    start = value.get("started_at_epoch")
    end = value.get("completed_at_epoch")
    if not isinstance(start, int) or not isinstance(end, int):
        raise InputError("E_INVALID_TIMING", "$.timing 必须含整型 started_at_epoch 与 completed_at_epoch")
    if end < start:
        raise InputError("E_INVALID_TIMING", "completed_at_epoch 不得早于 started_at_epoch")
    return end - start


def parse_stages(value: Any, guide: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", "$.stages 必须是数组")
    guide_stages = guide.get("stages")
    if not isinstance(guide_stages, list):
        raise InputError("E_GUIDE_SHAPE", "指南 stages 必须是数组")
    allowed_ids = tuple(
        s.get("stage_id")
        for s in guide_stages
        if isinstance(s, dict) and isinstance(s.get("stage_id"), str)
    )
    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.stages[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        stage_id = require_enum(item.get("stage_id"), f"{path}.stage_id", allowed_ids)
        if stage_id in seen:
            raise InputError("E_DUPLICATE_STAGE", f"{path}.stage_id 重复：{stage_id}")
        seen.add(stage_id)
        status = require_enum(item.get("status"), f"{path}.status", STAGE_STATUS)
        artifact_present = item.get("artifact_present")
        if not isinstance(artifact_present, bool):
            raise InputError("E_INVALID_FIELD", f"{path}.artifact_present 必须是布尔值")
        parsed.append(
            {
                "stage_id": stage_id,
                "status": status,
                "artifact_present": artifact_present,
            }
        )
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    bolt_id = raw.get("bolt_id")
    if not isinstance(bolt_id, str) or not bolt_id.strip():
        raise InputError("E_INVALID_FIELD", "$.bolt_id 必须是非空字符串")
    completion_seconds = parse_timing(raw.get("timing"))
    stages = parse_stages(raw.get("stages"), guide)
    return {
        "pinned_version": pinned,
        "bolt_id": bolt_id.strip(),
        "completion_seconds": completion_seconds,
        "stages": stages,
    }


def evaluate(guide: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    guide_stages = guide.get("stages")
    if not isinstance(guide_stages, list):
        raise InputError("E_GUIDE_SHAPE", "指南 stages 必须是数组")
    by_id = {s["stage_id"]: s for s in context["stages"]}

    required_total = 0
    required_satisfied = 0
    stage_details: List[Dict[str, Any]] = []

    for meta in guide_stages:
        if not isinstance(meta, dict):
            continue
        stage_id = meta.get("stage_id")
        if not isinstance(stage_id, str):
            continue
        required = meta.get("required") is True
        observed = by_id.get(stage_id)
        if required and observed is None:
            raise InputError("E_MISSING_STAGE", f"缺少必需阶段：{stage_id}")

        detail: Dict[str, Any] = {
            "stage_id": stage_id,
            "required": required,
        }
        if observed is None:
            detail["status"] = "missing"
            detail["artifact_present"] = False
            stage_details.append(detail)
            continue

        detail["status"] = observed["status"]
        detail["artifact_present"] = observed["artifact_present"]
        stage_details.append(detail)

        if required:
            required_total += 1
            if observed["status"] == "completed" and observed["artifact_present"] is True:
                required_satisfied += 1

    artifact_pct = (
        100.0 if required_total == 0 else round(100.0 * required_satisfied / required_total, 2)
    )
    valid = artifact_pct == 100.0

    return {
        "artifact_completeness_percent": artifact_pct,
        "stage_details": stage_details,
        "valid": valid,
    }


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw, guide)
    evaluation = evaluate(guide, context)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": evaluation["valid"],
        "bolt_id": context["bolt_id"],
        "stages": evaluation["stage_details"],
        "metrics": {
            "completion_seconds": context["completion_seconds"],
            "artifact_completeness_percent": evaluation["artifact_completeness_percent"],
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
