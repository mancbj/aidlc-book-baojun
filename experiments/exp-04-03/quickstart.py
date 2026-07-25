#!/usr/bin/env python3
"""Validate a minimal Memory Bank tree against a frozen specs.md pin fixture."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-04-03"
SCHEMA_VERSION = "1.0.0"
PIN_FIXTURE = "fixtures/pin/frozen-structure.json"
LIMITATION = (
    "本报告只对仓库内冻结 pin 夹具与给定 Memory Bank 根目录做结构与引用校验；"
    "它不验证实时 specs.md portal，也不把 specs.md 视为唯一标准。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验最小 Memory Bank 目录结构与引用。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="报告输出 JSON。")
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


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_TYPE", f"{path} 必须是对象")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_TYPE", f"{path} 必须是数组")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_REQUIRED_FIELD", f"{path} 必须是非空字符串")
    return value


def load_pin_fixture(experiment_root: Path) -> Dict[str, Any]:
    pin_path = experiment_root / PIN_FIXTURE
    try:
        data = json.loads(pin_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise InputError("E_PIN_NOT_FOUND", str(exc)) from exc
    except json.JSONDecodeError as exc:
        raise InputError("E_PIN_JSON_INVALID", f"第 {exc.lineno} 行：{exc.msg}") from exc
    return require_object(data, PIN_FIXTURE)


def verify_pinned_version(input_pin: str, fixture: Dict[str, Any]) -> None:
    fixture_pin = require_string(fixture.get("pinned_version"), f"{PIN_FIXTURE}.pinned_version")
    if input_pin != fixture_pin:
        raise InputError(
            "E_PIN_MISMATCH",
            f"输入 pinned_version 与冻结 pin 夹具不一致：期望 {fixture_pin}，得到 {input_pin}",
        )


def check_required_paths(bank_root: Path, paths: Sequence[str]) -> Tuple[List[str], List[str]]:
    missing: List[str] = []
    present: List[str] = []
    for rel in paths:
        target = bank_root / rel
        if target.is_file():
            present.append(rel)
        else:
            missing.append(rel)
    return present, missing


def check_declared_references(bank_root: Path, references: Sequence[str]) -> Tuple[List[str], List[str]]:
    valid: List[str] = []
    invalid: List[str] = []
    for rel in references:
        target = bank_root / rel
        if target.is_file():
            valid.append(rel)
        else:
            invalid.append(rel)
    return valid, invalid


def percent(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 100.0
    return round(numerator / denominator * 100, 2)


def build_report(data: Dict[str, Any], experiment_root: Path) -> Dict[str, Any]:
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise InputError("E_SCHEMA_VERSION", f"schema_version 必须是 {SCHEMA_VERSION}")

    input_pin = require_string(data.get("pinned_version"), "$.pinned_version")
    fixture = load_pin_fixture(experiment_root)
    verify_pinned_version(input_pin, fixture)

    bank_rel = require_string(data.get("memory_bank_root"), "$.memory_bank_root")
    bank_root = (experiment_root / bank_rel).resolve()
    if not bank_root.is_dir():
        raise InputError("E_BANK_ROOT", f"Memory Bank 根目录不存在：{bank_rel}")

    required_paths = [
        require_string(item, f"$.required_paths[{index}]")
        for index, item in enumerate(require_list(data.get("required_paths"), "$.required_paths"))
    ]
    if not required_paths:
        raise InputError("E_REQUIRED_FIELD", "$.required_paths 至少需要一条路径")

    declared_raw = data.get("declared_references", [])
    declared_references = [
        require_string(item, f"$.declared_references[{index}]")
        for index, item in enumerate(require_list(declared_raw, "$.declared_references"))
    ] if declared_raw is not None else []

    present, missing = check_required_paths(bank_root, required_paths)
    ref_valid, ref_invalid = check_declared_references(bank_root, declared_references)

    completeness = percent(len(present), len(required_paths))
    ref_validity = percent(len(ref_valid), len(declared_references)) if declared_references else 100.0
    structure_ok = not missing
    references_ok = not ref_invalid

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": digest(data),
        "valid": structure_ok and references_ok,
        "loadable_minimal_memory_bank": structure_ok,
        "limitation": LIMITATION,
        "pinned_version": input_pin,
        "memory_bank_root": bank_rel,
        "frozen_pin_fixture": PIN_FIXTURE,
        "required_path_check": {
            "present": present,
            "missing": missing,
        },
        "reference_check": {
            "valid": ref_valid,
            "invalid": ref_invalid,
        },
        "metrics": {
            "required_file_completeness_percent": completeness,
            "reference_validity_percent": ref_validity,
            "required_path_count": len(required_paths),
            "present_required_path_count": len(present),
            "declared_reference_count": len(declared_references),
            "valid_reference_count": len(ref_valid),
        },
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    experiment_root = Path(__file__).resolve().parent
    try:
        try:
            data = json.loads(args.input.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise InputError("E_INPUT_NOT_FOUND", str(exc)) from exc
        except json.JSONDecodeError as exc:
            raise InputError("E_JSON_INVALID", f"第 {exc.lineno} 行第 {exc.colno} 列：{exc.msg}") from exc
        except OSError as exc:
            raise InputError("E_INPUT_READ", str(exc)) from exc

        report = build_report(require_object(data, "$"), experiment_root)
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(pretty_json(report), encoding="utf-8")
        except OSError as exc:
            raise InputError("E_OUTPUT_WRITE", str(exc)) from exc
    except InputError as exc:
        print(f"[{exc.code}] {exc}", file=sys.stderr)
        return 1
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
