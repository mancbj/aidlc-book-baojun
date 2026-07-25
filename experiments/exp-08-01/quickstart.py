#!/usr/bin/env python3
"""Deterministic release-candidate source manifest validator."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set


EXPERIMENT_ID = "EXP-08-01"
SCHEMA_VERSION = "1.0.0"
HASH_PATTERN = re.compile(r"^sha256:[a-f0-9]{64}$")

LIMITATION = (
    "来源与 manifest 资产清单校验只证明输入模型内的可追溯一致性；"
    "它不证明真实生产环境可观测能力或 Operations 监控成熟度。"
)


class ManifestInputError(Exception):
    """An input error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验发布候选来源与 manifest 资产清单。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="校验报告输出 JSON。")
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
        raise ManifestInputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise ManifestInputError("E_EXPECTED_ARRAY", f"{path} 必须是数组。")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ManifestInputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value.strip()


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise ManifestInputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def require_non_negative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise ManifestInputError("E_INVALID_BYTES", f"{path} 必须是非负整数。")
    if value < 0:
        raise ManifestInputError("E_INVALID_BYTES", f"{path} 必须是非负整数。")
    return value


def parse_readiness(value: Any) -> Dict[str, str]:
    root = require_object(value, "$.readiness")
    return {
        "status": require_string(require_field(root, "status", "$.readiness"), "$.readiness.status"),
        "source_id": require_string(
            require_field(root, "source_id", "$.readiness"), "$.readiness.source_id"
        ),
    }


def parse_required_assets(value: Any) -> List[str]:
    items = require_list(value, "$.required_assets")
    if not items:
        raise ManifestInputError("E_REQUIRED_FIELD", "$.required_assets 至少包含一项。")
    names: List[str] = []
    seen: Set[str] = set()
    for index, raw in enumerate(items):
        name = require_string(raw, f"$.required_assets[{index}]")
        if name in seen:
            raise ManifestInputError("E_DUPLICATE_NAME", f"required_assets 名称重复：{name}")
        seen.add(name)
        names.append(name)
    return names


def parse_candidate_assets(value: Any) -> List[Dict[str, Any]]:
    items = require_list(value, "$.candidate_assets")
    assets: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(items):
        path = f"$.candidate_assets[{index}]"
        entry = require_object(raw, path)
        name = require_string(require_field(entry, "name", path), f"{path}.name")
        if name in seen:
            raise ManifestInputError("E_DUPLICATE_NAME", f"candidate_assets 名称重复：{name}")
        seen.add(name)
        sha256 = require_string(require_field(entry, "sha256", path), f"{path}.sha256")
        bytes_value = require_non_negative_int(
            require_field(entry, "bytes", path), f"{path}.bytes"
        )
        assets.append({"name": name, "sha256": sha256, "bytes": bytes_value})
    return assets


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(require_field(root, "experiment_id", "$"), "$.experiment_id")
    if experiment_id != EXPERIMENT_ID:
        raise ManifestInputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。")
    expected_source_id = require_string(
        require_field(root, "expected_source_id", "$"), "$.expected_source_id"
    )
    readiness = parse_readiness(require_field(root, "readiness", "$"))
    required_assets = parse_required_assets(require_field(root, "required_assets", "$"))
    candidate_assets = parse_candidate_assets(require_field(root, "candidate_assets", "$"))
    return {
        "expected_source_id": expected_source_id,
        "readiness": readiness,
        "required_assets": required_assets,
        "candidate_assets": candidate_assets,
    }


def count_hash_format_issues(assets: Sequence[Dict[str, Any]]) -> int:
    return sum(1 for asset in assets if not HASH_PATTERN.match(asset["sha256"]))


def assert_consistency(parsed: Dict[str, Any]) -> None:
    readiness = parsed["readiness"]
    if readiness["source_id"] != parsed["expected_source_id"]:
        raise ManifestInputError(
            "E_SOURCE_MISMATCH",
            "readiness.source_id 与 expected_source_id 不一致。",
        )

    hash_issues = count_hash_format_issues(parsed["candidate_assets"])
    if hash_issues:
        raise ManifestInputError(
            "E_INVALID_HASH",
            f"发现 {hash_issues} 个 candidate_assets.sha256 格式无效。",
        )

    by_name = {asset["name"]: asset for asset in parsed["candidate_assets"]}
    missing = [name for name in parsed["required_assets"] if name not in by_name]
    if missing:
        raise ManifestInputError(
            "E_MISSING_ASSET",
            f"required_assets 缺少候选资产：{', '.join(missing)}。",
        )


def source_completeness_percent(parsed: Dict[str, Any]) -> float:
    required = parsed["required_assets"]
    by_name = {asset["name"]: asset for asset in parsed["candidate_assets"]}
    present = sum(1 for name in required if name in by_name)
    source_ok = 1 if parsed["readiness"]["source_id"] == parsed["expected_source_id"] else 0
    denominator = 1 + len(required)
    numerator = source_ok + present
    return round(100.0 * numerator / denominator, 2)


def build_report(raw_data: Any) -> Dict[str, Any]:
    parsed = validate_input(raw_data)
    assert_consistency(parsed)
    required = parsed["required_assets"]
    candidates = parsed["candidate_assets"]
    by_name = {asset["name"]: asset for asset in candidates}
    present_names = [name for name in required if name in by_name]

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(raw_data),
        "valid": True,
        "metrics": {
            "source_completeness_percent": source_completeness_percent(parsed),
            "hash_mismatch_count": count_hash_format_issues(candidates),
        },
        "summary": {
            "expected_source_id": parsed["expected_source_id"],
            "readiness_status": parsed["readiness"]["status"],
            "readiness_source_id": parsed["readiness"]["source_id"],
            "required_asset_count": len(required),
            "present_required_asset_count": len(present_names),
            "candidate_asset_count": len(candidates),
        },
        "manifest_assets": [
            {
                "bytes": by_name[name]["bytes"],
                "name": name,
                "sha256": by_name[name]["sha256"],
            }
            for name in sorted(present_names)
        ],
        "limitation": LIMITATION,
        "interpretation": (
            "readiness.source_id 必须与 expected_source_id 一致；"
            "required_assets 中的名称必须出现在 candidate_assets；"
            "每个 candidate_assets.sha256 必须为 sha256:<64 位小写十六进制>。"
            "source_completeness_percent 按来源一致性与必需资产覆盖率计算。"
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
    except ManifestInputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
