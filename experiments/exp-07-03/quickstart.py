#!/usr/bin/env python3
"""Validate injected defects against a frozen CH-07 layered verification guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-07-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/layered_verification_guide.json"
EXPECTED_PIN = (
    "sha256:29411a610e2f4466e1c903adb62212d60c048e5918b9d2bb4907fd45bd2e3c44"
)
LIMITATION = (
    "本报告仅对照仓库内冻结的分层交付验证指南与注入缺陷记录做确定性核对；"
    "属于 CH-07 交付候选验证，不等于 CH-08 Runtime Verify；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对分层验证层上的缺陷发现与逃逸。")
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


def layer_order(guide: Dict[str, Any]) -> List[str]:
    layers = guide.get("layers")
    if not isinstance(layers, list):
        raise InputError("E_GUIDE_SHAPE", "指南 layers 必须是数组")
    ordered: List[tuple[int, str]] = []
    for index, item in enumerate(layers):
        if not isinstance(item, dict):
            raise InputError("E_GUIDE_SHAPE", f"指南 layers[{index}] 必须是对象")
        layer_id = item.get("layer_id")
        order = item.get("order")
        if not isinstance(layer_id, str) or not layer_id.strip():
            raise InputError("E_GUIDE_SHAPE", f"指南 layers[{index}].layer_id 无效")
        if not isinstance(order, int):
            raise InputError("E_GUIDE_SHAPE", f"指南 layers[{index}].order 必须是整数")
        ordered.append((order, layer_id))
    ordered.sort(key=lambda pair: pair[0])
    return [layer_id for _, layer_id in ordered]


def registered_defect_ids(guide: Dict[str, Any]) -> List[str]:
    defects = guide.get("registered_defects")
    if not isinstance(defects, list):
        raise InputError("E_GUIDE_SHAPE", "指南 registered_defects 必须是数组")
    ids: List[str] = []
    for index, item in enumerate(defects):
        if not isinstance(item, dict):
            raise InputError("E_GUIDE_SHAPE", f"指南 registered_defects[{index}] 必须是对象")
        defect_id = item.get("defect_id")
        if not isinstance(defect_id, str) or not defect_id.strip():
            raise InputError("E_GUIDE_SHAPE", f"指南 registered_defects[{index}].defect_id 无效")
        ids.append(defect_id)
    return ids


def parse_defects(
    value: Any, layer_ids: Sequence[str], allowed_defect_ids: Sequence[str]
) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_INVALID_FIELD", "$.injected_defects 必须是非空数组")
    allowed_set = set(allowed_defect_ids)
    layer_set = set(layer_ids)
    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.injected_defects[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        defect_id = item.get("defect_id")
        if not isinstance(defect_id, str) or not defect_id.strip():
            raise InputError("E_INVALID_FIELD", f"{path}.defect_id 必须是非空字符串")
        defect_id = defect_id.strip()
        if defect_id not in allowed_set:
            raise InputError("E_UNKNOWN_DEFECT", f"{path}.defect_id 未在指南登记：{defect_id}")
        if defect_id in seen:
            raise InputError("E_DUPLICATE_DEFECT", f"{path}.defect_id 重复：{defect_id}")
        seen.add(defect_id)
        detections = item.get("layer_detections")
        if not isinstance(detections, dict):
            raise InputError("E_INVALID_FIELD", f"{path}.layer_detections 必须是对象")
        extra_layers = set(detections) - layer_set
        if extra_layers:
            raise InputError(
                "E_UNKNOWN_LAYER",
                f"{path}.layer_detections 含未知层：{sorted(extra_layers)[0]}",
            )
        missing_layers = layer_set - set(detections)
        if missing_layers:
            raise InputError(
                "E_MISSING_LAYER",
                f"{path}.layer_detections 缺少层：{sorted(missing_layers)[0]}",
            )
        normalized: Dict[str, bool] = {}
        for layer_id in layer_ids:
            flag = detections[layer_id]
            if not isinstance(flag, bool):
                raise InputError(
                    "E_INVALID_FIELD",
                    f"{path}.layer_detections.{layer_id} 必须是布尔值",
                )
            normalized[layer_id] = flag
        parsed.append({"defect_id": defect_id, "layer_detections": normalized})
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    candidate_id = raw.get("delivery_candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise InputError("E_INVALID_FIELD", "$.delivery_candidate_id 必须是非空字符串")
    verification_seconds = raw.get("verification_seconds")
    if not isinstance(verification_seconds, int) or verification_seconds < 0:
        raise InputError("E_INVALID_FIELD", "$.verification_seconds 必须是非负整数")
    layer_ids = layer_order(guide)
    defects = parse_defects(
        raw.get("injected_defects"), layer_ids, registered_defect_ids(guide)
    )
    return {
        "pinned_version": pinned,
        "delivery_candidate_id": candidate_id.strip(),
        "verification_seconds": verification_seconds,
        "injected_defects": defects,
        "layer_ids": layer_ids,
    }


def first_discovery(layer_ids: Sequence[str], detections: Dict[str, bool]) -> Optional[str]:
    for layer_id in layer_ids:
        if detections[layer_id]:
            return layer_id
    return None


def evaluate(context: Dict[str, Any]) -> Dict[str, Any]:
    layer_ids = context["layer_ids"]
    records: List[Dict[str, Any]] = []
    escaped = 0
    first_stages: Dict[str, Optional[str]] = {}
    for defect in context["injected_defects"]:
        stage = first_discovery(layer_ids, defect["layer_detections"])
        first_stages[defect["defect_id"]] = stage
        escaped_flag = stage is None
        if escaped_flag:
            escaped += 1
        records.append(
            {
                "defect_id": defect["defect_id"],
                "escaped": escaped_flag,
                "first_discovery_stage": stage,
            }
        )
    records.sort(key=lambda item: item["defect_id"])
    return {
        "defect_records": records,
        "escaped_defect_count": escaped,
        "first_discovery_stage": first_stages,
        "valid": escaped == 0,
    }


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw, guide)
    evaluation = evaluate(context)
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "verification_framing": guide.get("verification_framing"),
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": evaluation["valid"],
        "delivery_candidate_id": context["delivery_candidate_id"],
        "layers": context["layer_ids"],
        "defect_records": evaluation["defect_records"],
        "metrics": {
            "escaped_defect_count": evaluation["escaped_defect_count"],
            "first_discovery_stage": evaluation["first_discovery_stage"],
            "verification_seconds": context["verification_seconds"],
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
