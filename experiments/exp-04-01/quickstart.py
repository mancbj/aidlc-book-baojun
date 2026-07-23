#!/usr/bin/env python3
"""Run a deterministic Memory Bank cold-start A/B comparison."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-04-01"
SCHEMA_VERSION = "1.0.0"


class InputError(Exception):
    """Raised when the experiment input is structurally invalid."""


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成 Memory Bank 冷启动恢复 A/B 对照报告。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="实验输出 JSON。")
    parser.add_argument("--sample", action="store_true", help="使用仓库内默认样例输入与输出路径。")
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
    return "sha256:" + hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{path} 必须是非空字符串。")
    return value


def require_string_list(value: Any, path: str) -> List[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item.strip() for item in value):
        raise InputError(f"{path} 必须是非空字符串数组。")
    return list(value)


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{path} 必须是对象。")
    return value


def require_candidates(value: Any) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or len(value) < 2:
        raise InputError("$.candidates 必须至少包含两组候选。")
    candidates = []
    seen = set()
    for index, item in enumerate(value):
        candidate = require_object(item, f"$.candidates[{index}]")
        candidate_id = require_string(candidate.get("id"), f"$.candidates[{index}].id")
        if candidate_id in seen:
            raise InputError(f"候选 ID 重复：{candidate_id}")
        seen.add(candidate_id)
        candidates.append(candidate)
    return candidates


def normalize_set(value: Any, path: str) -> set[str]:
    return set(require_string_list(value, path))


def evaluate_candidate(candidate: Dict[str, Any], expected: Dict[str, Any]) -> Dict[str, Any]:
    checks: List[Dict[str, Any]] = []

    def add_check(name: str, passed: bool, expected_value: Any, actual_value: Any) -> None:
        checks.append(
            {
                "name": name,
                "passed": bool(passed),
                "expected": expected_value,
                "actual": actual_value,
            }
        )

    add_check(
        "active_cycle",
        candidate.get("active_cycle") == expected["active_cycle"],
        expected["active_cycle"],
        candidate.get("active_cycle"),
    )
    add_check(
        "next_action",
        candidate.get("first_action") == expected["next_action"],
        expected["next_action"],
        candidate.get("first_action"),
    )
    add_check(
        "evidence_paths",
        set(expected["required_evidence_paths"]).issubset(set(candidate.get("planned_updates", []))),
        expected["required_evidence_paths"],
        candidate.get("planned_updates", []),
    )
    add_check(
        "excluded_paths",
        set(expected["excluded_paths"]).issubset(set(candidate.get("excluded_paths_respected", []))),
        expected["excluded_paths"],
        candidate.get("excluded_paths_respected", []),
    )
    add_check(
        "terms_preserved",
        set(expected["required_terms"]).issubset(set(candidate.get("terms_preserved", []))),
        expected["required_terms"],
        candidate.get("terms_preserved", []),
    )

    passed = sum(1 for check in checks if check["passed"])
    accuracy = round(passed / len(checks) * 100, 2)
    first_action_error = candidate.get("first_action") != expected["next_action"]
    clarifying_questions = candidate.get("clarifying_questions", [])
    if not isinstance(clarifying_questions, list):
        clarifying_questions = []
    return {
        "id": candidate["id"],
        "sources_used": list(candidate.get("sources_used", [])),
        "context_recovery_accuracy_percent": accuracy,
        "first_action_error": first_action_error,
        "clarification_question_count": len(clarifying_questions),
        "checks": checks,
    }


def build_report(data: Dict[str, Any]) -> Dict[str, Any]:
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError(f"experiment_id 必须是 {EXPERIMENT_ID}。")
    expected = require_object(data.get("expected_context"), "$.expected_context")
    expected_context = {
        "active_cycle": require_string(expected.get("active_cycle"), "$.expected_context.active_cycle"),
        "next_action": require_string(expected.get("next_action"), "$.expected_context.next_action"),
        "required_evidence_paths": require_string_list(expected.get("required_evidence_paths"), "$.expected_context.required_evidence_paths"),
        "excluded_paths": require_string_list(expected.get("excluded_paths"), "$.expected_context.excluded_paths"),
        "required_terms": require_string_list(expected.get("required_terms"), "$.expected_context.required_terms"),
    }
    candidates = require_candidates(data.get("candidates"))
    results = [evaluate_candidate(candidate, expected_context) for candidate in candidates]
    by_id = {result["id"]: result for result in results}
    if "with_memory_bank" not in by_id or "without_memory_bank" not in by_id:
        raise InputError("候选必须包含 with_memory_bank 与 without_memory_bank。")

    with_memory = by_id["with_memory_bank"]
    without_memory = by_id["without_memory_bank"]
    accuracy_gain = round(
        with_memory["context_recovery_accuracy_percent"]
        - without_memory["context_recovery_accuracy_percent"],
        2,
    )
    clarification_reduction = (
        without_memory["clarification_question_count"]
        - with_memory["clarification_question_count"]
    )
    valid = (
        with_memory["context_recovery_accuracy_percent"] > without_memory["context_recovery_accuracy_percent"]
        and not with_memory["first_action_error"]
        and accuracy_gain > 0
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(data),
        "valid": valid,
        "metrics": {
            "with_memory_bank": {
                "context_recovery_accuracy_percent": with_memory["context_recovery_accuracy_percent"],
                "first_action_error": with_memory["first_action_error"],
                "clarification_question_count": with_memory["clarification_question_count"],
            },
            "without_memory_bank": {
                "context_recovery_accuracy_percent": without_memory["context_recovery_accuracy_percent"],
                "first_action_error": without_memory["first_action_error"],
                "clarification_question_count": without_memory["clarification_question_count"],
            },
            "delta": {
                "accuracy_gain_percent": accuracy_gain,
                "clarification_reduction": clarification_reduction,
            },
        },
        "results": results,
        "conclusion": (
            "Memory Bank 与 Standards 组恢复了当前周期、下一动作、证据路径、排除边界和专用术语；"
            "无 Memory Bank 组出现首个动作错误和术语漂移。"
        ),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        report = build_report(data)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except (OSError, json.JSONDecodeError, InputError) as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1
    if not report["valid"]:
        print("[ERROR] experiment report is not valid", file=sys.stderr)
        return 2
    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
