#!/usr/bin/env python3
"""Deterministically verify versioned Standards against generated snapshots."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-04-02"
SCHEMA_VERSION = "1.0.0"
DISCLAIMER = "本实验只验证输入中声明的规则与标注基准，不证明这些规则对其他项目、版本或工件普适。"
SUPPORTED_RULES = {"required", "equals", "contains_all"}


class InputError(Exception):
    """A stable, machine-identifiable input failure."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="验证 Standards 演进与生成工件漂移。")
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


def parse_rules(value: Any, path: str) -> Dict[str, Dict[str, Any]]:
    rules: Dict[str, Dict[str, Any]] = {}
    for index, item in enumerate(require_list(value, path)):
        rule_path = f"{path}[{index}]"
        rule = require_object(item, rule_path)
        rule_id = require_string(rule.get("id"), f"{rule_path}.id")
        if rule_id in rules:
            raise InputError("E_DUPLICATE_ID", f"重复规则 ID：{rule_id}")
        kind = require_string(rule.get("kind"), f"{rule_path}.kind")
        if kind not in SUPPORTED_RULES:
            raise InputError("E_UNSUPPORTED_RULE", f"规则 {rule_id} 使用不支持的 kind：{kind}")
        require_string(rule.get("artifact_id"), f"{rule_path}.artifact_id")
        require_string(rule.get("path"), f"{rule_path}.path")
        if kind in {"equals", "contains_all"} and "expected" not in rule:
            raise InputError("E_REQUIRED_FIELD", f"{rule_path}.expected 缺失")
        if kind == "contains_all":
            require_list(rule["expected"], f"{rule_path}.expected")
        rules[rule_id] = dict(rule)
    if not rules:
        raise InputError("E_REQUIRED_FIELD", f"{path} 至少需要一条规则")
    return rules


def parse_snapshots(value: Any, path: str) -> Dict[str, Any]:
    snapshots: Dict[str, Any] = {}
    for index, item in enumerate(require_list(value, path)):
        snapshot_path = f"{path}[{index}]"
        snapshot = require_object(item, snapshot_path)
        artifact_id = require_string(snapshot.get("id"), f"{snapshot_path}.id")
        if artifact_id in snapshots:
            raise InputError("E_DUPLICATE_ID", f"重复工件 ID：{artifact_id}")
        snapshots[artifact_id] = require_object(snapshot.get("content"), f"{snapshot_path}.content")
    return snapshots


def parse_state(value: Any, path: str) -> Tuple[str, Dict[str, Dict[str, Any]], str, Dict[str, Any]]:
    state = require_object(value, path)
    standards = require_object(state.get("standards"), f"{path}.standards")
    artifacts = require_object(state.get("generated_artifacts"), f"{path}.generated_artifacts")
    standards_version = require_string(standards.get("version"), f"{path}.standards.version")
    rules = parse_rules(standards.get("rules"), f"{path}.standards.rules")
    artifacts_version = require_string(artifacts.get("version"), f"{path}.generated_artifacts.version")
    snapshots = parse_snapshots(artifacts.get("snapshots"), f"{path}.generated_artifacts.snapshots")
    return standards_version, rules, artifacts_version, snapshots


def resolve_path(content: Any, dotted_path: str) -> Tuple[bool, Any]:
    current = content
    for part in dotted_path.split("."):
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return False, None
    return True, current


def evaluate_rules(rules: Dict[str, Dict[str, Any]], snapshots: Dict[str, Any]) -> List[Dict[str, Any]]:
    violations: List[Dict[str, Any]] = []
    for rule_id in sorted(rules):
        rule = rules[rule_id]
        artifact_id = rule["artifact_id"]
        path = rule["path"]
        exists, actual = resolve_path(snapshots.get(artifact_id), path) if artifact_id in snapshots else (False, None)
        kind = rule["kind"]
        violated = not exists
        if exists and kind == "required":
            violated = actual is None or actual == "" or actual == []
        elif exists and kind == "equals":
            violated = actual != rule["expected"]
        elif exists and kind == "contains_all":
            violated = not isinstance(actual, list) or any(item not in actual for item in rule["expected"])
        if violated:
            violations.append(
                {
                    "artifact_id": artifact_id,
                    "actual": actual if exists else None,
                    "code": "RULE_VIOLATION",
                    "expected": rule.get("expected", "present and non-empty"),
                    "key": f"{rule_id}:{artifact_id}:{path}",
                    "path": path,
                    "rule_id": rule_id,
                    "rule_kind": kind,
                }
            )
    return violations


def map_diff(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, List[str]]:
    before_ids, after_ids = set(before), set(after)
    return {
        "added": sorted(after_ids - before_ids),
        "removed": sorted(before_ids - after_ids),
        "changed": sorted(
            item_id for item_id in before_ids & after_ids
            if canonical_json(before[item_id]) != canonical_json(after[item_id])
        ),
    }


def value_drift(before: Any, after: Any, artifact_id: str, path: str = "$") -> List[Dict[str, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        items: List[Dict[str, Any]] = []
        for key in sorted(set(before) | set(after)):
            child_path = f"{path}.{key}"
            if key not in before:
                items.append({"artifact_id": artifact_id, "kind": "field_added", "path": child_path})
            elif key not in after:
                items.append({"artifact_id": artifact_id, "kind": "field_removed", "path": child_path})
            else:
                items.extend(value_drift(before[key], after[key], artifact_id, child_path))
        return items
    if canonical_json(before) != canonical_json(after):
        return [{"artifact_id": artifact_id, "kind": "value_changed", "path": path}]
    return []


def artifact_drift(before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for artifact_id in sorted(set(before) | set(after)):
        if artifact_id not in before:
            items.append({"artifact_id": artifact_id, "kind": "artifact_added", "path": "$"})
        elif artifact_id not in after:
            items.append({"artifact_id": artifact_id, "kind": "artifact_removed", "path": "$"})
        else:
            items.extend(value_drift(before[artifact_id], after[artifact_id], artifact_id))
    return items


def parse_expected_keys(data: Dict[str, Any]) -> Set[str]:
    benchmark = require_object(data.get("benchmark"), "$.benchmark")
    labels = require_list(benchmark.get("expected_violation_keys"), "$.benchmark.expected_violation_keys")
    keys: Set[str] = set()
    for index, value in enumerate(labels):
        key = require_string(value, f"$.benchmark.expected_violation_keys[{index}]")
        if key in keys:
            raise InputError("E_DUPLICATE_ID", f"重复标注 key：{key}")
        keys.add(key)
    return keys


def build_report(data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    if data.get("schema_version") != SCHEMA_VERSION:
        raise InputError("E_SCHEMA_VERSION", f"schema_version 必须是 {SCHEMA_VERSION}")
    baseline_version, baseline_rules, baseline_artifact_version, baseline_snapshots = parse_state(
        data.get("baseline"), "$.baseline"
    )
    candidate_version, candidate_rules, candidate_artifact_version, candidate_snapshots = parse_state(
        data.get("candidate"), "$.candidate"
    )
    expected_keys = parse_expected_keys(data)
    violations = evaluate_rules(candidate_rules, candidate_snapshots)
    predicted_keys = {item["key"] for item in violations}
    false_positives = sorted(predicted_keys - expected_keys)
    false_negatives = sorted(expected_keys - predicted_keys)
    drift_items = artifact_drift(baseline_snapshots, candidate_snapshots)
    rule_diff = map_diff(baseline_rules, candidate_rules)
    artifact_diff = map_diff(baseline_snapshots, candidate_snapshots)
    total_rules = len(candidate_rules)
    coverage = round((total_rules / total_rules) * 100, 2)
    false_positive_rate = round(
        len(false_positives) / len(predicted_keys) * 100, 2
    ) if predicted_keys else 0.0
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": digest(data),
        "valid": not false_positives and not false_negatives,
        "compliant": not violations,
        "disclaimer": DISCLAIMER,
        "violations": violations,
        "version_diff": {
            "standards": {
                "from_version": baseline_version,
                "to_version": candidate_version,
                "rules": rule_diff,
            },
            "generated_artifacts": {
                "from_version": baseline_artifact_version,
                "to_version": candidate_artifact_version,
                "snapshots": artifact_diff,
                "drift_items": drift_items,
            },
        },
        "metrics": {
            "rule_count": total_rules,
            "evaluated_rule_count": total_rules,
            "rule_coverage_percent": coverage,
            "false_positive_count": len(false_positives),
            "false_positive_rate_percent": false_positive_rate,
            "false_negative_count": len(false_negatives),
            "drift_item_count": len(drift_items),
        },
        "benchmark_evaluation": {
            "basis": "仅基于输入 benchmark.expected_violation_keys 标注",
            "expected_violation_keys": sorted(expected_keys),
            "predicted_violation_keys": sorted(predicted_keys),
            "false_positive_keys": false_positives,
            "false_negative_keys": false_negatives,
        },
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        try:
            data = json.loads(args.input.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise InputError("E_INPUT_NOT_FOUND", str(exc)) from exc
        except json.JSONDecodeError as exc:
            raise InputError("E_JSON_INVALID", f"第 {exc.lineno} 行第 {exc.colno} 列：{exc.msg}") from exc
        except OSError as exc:
            raise InputError("E_INPUT_READ", str(exc)) from exc
        report = build_report(require_object(data, "$"))
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
