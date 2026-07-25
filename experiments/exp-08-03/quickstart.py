#!/usr/bin/env python3
"""Validate Operations four-stage credentials against a frozen guide pin (CH-08)."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-08-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/operations_four_stage_guide.json"
EXPECTED_PIN = (
    "sha256:dfef24406c8875dc920c3223eb5d415cec007afb3ba99e66191446d8b8f95338"
)
STAGE_STATUS = ("completed", "in_progress", "pending", "skipped")
LIMITATION = (
    "本报告仅对照仓库内冻结的 Operations 四阶段指南与输入阶段凭证做确定性核对；"
    "其中 runtime_verify 指 CH-08 Runtime Verify，不等于 CH-07 交付候选验证；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Build/Deploy/Runtime Verify/Monitor 凭证与回滚就绪度。")
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


def parse_credentials(
    value: Any, path: str, required_fields: Sequence[str]
) -> Dict[str, str]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
    extra = set(value) - set(required_fields)
    if extra:
        raise InputError("E_UNKNOWN_CREDENTIAL", f"{path} 含未知字段：{sorted(extra)[0]}")
    parsed: Dict[str, str] = {}
    for field in required_fields:
        if field not in value:
            raise InputError("E_MISSING_CREDENTIAL", f"{path} 缺少字段：{field}")
        raw = value[field]
        if not isinstance(raw, str) or not raw.strip():
            raise InputError("E_INVALID_FIELD", f"{path}.{field} 必须是非空字符串")
        parsed[field] = raw.strip()
    return parsed


def parse_stages(value: Any, guide: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", "$.stages 必须是数组")
    guide_stages = guide.get("stages")
    if not isinstance(guide_stages, list):
        raise InputError("E_GUIDE_SHAPE", "指南 stages 必须是数组")
    meta_by_id: Dict[str, Dict[str, Any]] = {}
    for item in guide_stages:
        if isinstance(item, dict) and isinstance(item.get("stage_id"), str):
            meta_by_id[item["stage_id"]] = item

    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.stages[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        stage_id = item.get("stage_id")
        if not isinstance(stage_id, str) or stage_id not in meta_by_id:
            raise InputError("E_UNKNOWN_STAGE", f"{path}.stage_id 未在指南登记：{stage_id}")
        if stage_id in seen:
            raise InputError("E_DUPLICATE_STAGE", f"{path}.stage_id 重复：{stage_id}")
        seen.add(stage_id)
        status = require_enum(item.get("status"), f"{path}.status", STAGE_STATUS)
        fields = meta_by_id[stage_id].get("credential_fields")
        if not isinstance(fields, list):
            raise InputError("E_GUIDE_SHAPE", f"指南 {stage_id} credential_fields 无效")
        field_names = [f for f in fields if isinstance(f, str)]
        credentials = parse_credentials(item.get("credentials"), f"{path}.credentials", field_names)
        parsed.append(
            {
                "stage_id": stage_id,
                "status": status,
                "credentials": credentials,
                "required": meta_by_id[stage_id].get("required") is True,
            }
        )
    return parsed


def parse_rollback_checklist(value: Any, guide: Dict[str, Any]) -> Dict[str, bool]:
    fields = guide.get("rollback_readiness_fields")
    if not isinstance(fields, list):
        raise InputError("E_GUIDE_SHAPE", "指南 rollback_readiness_fields 必须是数组")
    field_names = [f for f in fields if isinstance(f, str)]
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.rollback_readiness 必须是对象")
    extra = set(value) - set(field_names)
    if extra:
        raise InputError("E_UNKNOWN_ROLLBACK_FIELD", f"$.rollback_readiness 含未知字段：{sorted(extra)[0]}")
    parsed: Dict[str, bool] = {}
    for name in field_names:
        if name not in value:
            raise InputError("E_MISSING_ROLLBACK_FIELD", f"$.rollback_readiness 缺少字段：{name}")
        flag = value[name]
        if not isinstance(flag, bool):
            raise InputError("E_INVALID_FIELD", f"$.rollback_readiness.{name} 必须是布尔值")
        parsed[name] = flag
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    release_id = raw.get("release_id")
    if not isinstance(release_id, str) or not release_id.strip():
        raise InputError("E_INVALID_FIELD", "$.release_id 必须是非空字符串")
    stages = parse_stages(raw.get("stages"), guide)
    rollback = parse_rollback_checklist(raw.get("rollback_readiness"), guide)
    return {
        "pinned_version": pinned,
        "release_id": release_id.strip(),
        "stages": stages,
        "rollback_readiness": rollback,
    }


def evaluate(context: Dict[str, Any], guide: Dict[str, Any]) -> Dict[str, Any]:
    guide_stages = guide.get("stages")
    if not isinstance(guide_stages, list):
        raise InputError("E_GUIDE_SHAPE", "指南 stages 必须是数组")
    by_id = {s["stage_id"]: s for s in context["stages"]}
    required_total = 0
    completed_required = 0
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
        detail: Dict[str, Any] = {"stage_id": stage_id, "required": required}
        if observed is None:
            detail["status"] = "missing"
            stage_details.append(detail)
            continue
        detail["status"] = observed["status"]
        detail["credentials_complete"] = all(
            bool(observed["credentials"].get(field))
            for field in observed["credentials"]
        )
        stage_details.append(detail)
        if required:
            required_total += 1
            if observed["status"] == "completed" and detail["credentials_complete"]:
                completed_required += 1

    stage_pct = (
        100.0 if required_total == 0 else round(100.0 * completed_required / required_total, 2)
    )

    rollback_fields = context["rollback_readiness"]
    rollback_total = len(rollback_fields)
    rollback_satisfied = sum(1 for flag in rollback_fields.values() if flag)
    rollback_pct = (
        100.0 if rollback_total == 0 else round(100.0 * rollback_satisfied / rollback_total, 2)
    )

    valid = stage_pct == 100.0 and rollback_pct == 100.0
    return {
        "stage_details": stage_details,
        "rollback_readiness": rollback_fields,
        "stage_completion_percent": stage_pct,
        "rollback_readiness_percent": rollback_pct,
        "valid": valid,
    }


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw, guide)
    evaluation = evaluate(context, guide)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "runtime_verify_framing": guide.get("runtime_verify_note"),
        "valid": evaluation["valid"],
        "release_id": context["release_id"],
        "stages": evaluation["stage_details"],
        "rollback_readiness": evaluation["rollback_readiness"],
        "metrics": {
            "stage_completion_percent": evaluation["stage_completion_percent"],
            "rollback_readiness_percent": evaluation["rollback_readiness_percent"],
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
