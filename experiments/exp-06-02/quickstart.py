#!/usr/bin/env python3
"""Generate a deterministic fail-fix-retest repair evidence chain."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


EXPERIMENT_ID = "EXP-06-02"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "证据完整率只表示失败是否同时关联到修复提交与复测结果；"
    "它不证明修复质量或一次通过优于多轮修复。"
)

TIMESTAMP_PATTERN = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z$"
)


class ChainInputError(Exception):
    """An input error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成失败—修复—复测确定性证据链。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="证据链输出 JSON。")
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
        raise ChainInputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise ChainInputError("E_EXPECTED_ARRAY", f"{path} 必须是数组。")
    return value


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ChainInputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise ChainInputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def parse_timestamp(value: Any, path: str) -> datetime:
    text = require_string(value, path)
    if not TIMESTAMP_PATTERN.match(text):
        raise ChainInputError("E_INVALID_TIMESTAMP", f"{path} 必须是 UTC ISO-8601 时间戳。")
    normalized = text.replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_failures(value: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(require_list(value, "$.failures")):
        path = f"$.failures[{index}]"
        entry = require_object(raw, path)
        item_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if item_id in seen:
            raise ChainInputError("E_DUPLICATE_ID", f"失败 ID 重复：{item_id}")
        seen.add(item_id)
        parsed = {
            "id": item_id,
            "timestamp": require_string(
                require_field(entry, "timestamp", path), f"{path}.timestamp"
            ),
            "summary": require_string(
                require_field(entry, "summary", path), f"{path}.summary"
            ),
            "_ts": parse_timestamp(entry["timestamp"], f"{path}.timestamp"),
        }
        if "log_ref" in entry:
            parsed["log_ref"] = require_string(entry["log_ref"], f"{path}.log_ref")
        items.append(parsed)
    return items


def parse_commits(value: Any, failure_ids: set[str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(require_list(value, "$.commits")):
        path = f"$.commits[{index}]"
        entry = require_object(raw, path)
        item_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if item_id in seen:
            raise ChainInputError("E_DUPLICATE_ID", f"提交 ID 重复：{item_id}")
        seen.add(item_id)
        parsed = {
            "id": item_id,
            "timestamp": require_string(
                require_field(entry, "timestamp", path), f"{path}.timestamp"
            ),
            "message": require_string(
                require_field(entry, "message", path), f"{path}.message"
            ),
            "_ts": parse_timestamp(entry["timestamp"], f"{path}.timestamp"),
        }
        failure_id = entry.get("failure_id")
        if failure_id is not None:
            failure_id = require_string(failure_id, f"{path}.failure_id")
            if failure_id not in failure_ids:
                raise ChainInputError(
                    "E_UNKNOWN_FAILURE_ID",
                    f"{path}.failure_id 引用了未知失败：{failure_id}",
                )
            parsed["failure_id"] = failure_id
        items.append(parsed)
    return items


def parse_tests(
    value: Any, failure_ids: set[str], commit_ids: set[str]
) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for index, raw in enumerate(require_list(value, "$.tests")):
        path = f"$.tests[{index}]"
        entry = require_object(raw, path)
        item_id = require_string(require_field(entry, "id", path), f"{path}.id")
        if item_id in seen:
            raise ChainInputError("E_DUPLICATE_ID", f"测试 ID 重复：{item_id}")
        seen.add(item_id)
        passed = entry.get("passed")
        if not isinstance(passed, bool):
            raise ChainInputError("E_EXPECTED_BOOLEAN", f"{path}.passed 必须是布尔值。")
        parsed = {
            "id": item_id,
            "timestamp": require_string(
                require_field(entry, "timestamp", path), f"{path}.timestamp"
            ),
            "passed": passed,
            "_ts": parse_timestamp(entry["timestamp"], f"{path}.timestamp"),
        }
        failure_id = entry.get("failure_id")
        if failure_id is not None:
            failure_id = require_string(failure_id, f"{path}.failure_id")
            if failure_id not in failure_ids:
                raise ChainInputError(
                    "E_UNKNOWN_FAILURE_ID",
                    f"{path}.failure_id 引用了未知失败：{failure_id}",
                )
            parsed["failure_id"] = failure_id
        commit_id = entry.get("commit_id")
        if commit_id is not None:
            commit_id = require_string(commit_id, f"{path}.commit_id")
            if commit_id not in commit_ids:
                raise ChainInputError(
                    "E_UNKNOWN_COMMIT_ID",
                    f"{path}.commit_id 引用了未知提交：{commit_id}",
                )
            parsed["commit_id"] = commit_id
        items.append(parsed)
    return items


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(
        require_field(root, "experiment_id", "$"), "$.experiment_id"
    )
    if experiment_id != EXPERIMENT_ID:
        raise ChainInputError(
            "E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。"
        )

    failures = parse_failures(require_field(root, "failures", "$"))
    failure_ids = {item["id"] for item in failures}
    commits = parse_commits(require_field(root, "commits", "$"), failure_ids)
    commit_ids = {item["id"] for item in commits}
    tests = parse_tests(require_field(root, "tests", "$"), failure_ids, commit_ids)
    return {
        "experiment_id": experiment_id,
        "failures": failures,
        "commits": commits,
        "tests": tests,
    }


def sort_key(record: Dict[str, Any]) -> Tuple[datetime, str]:
    return record["_ts"], record["id"]


def strip_internal(record: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if record is None:
        return None
    return {key: value for key, value in record.items() if not key.startswith("_")}


def link_fix_commit(
    failure: Dict[str, Any], commits: Sequence[Dict[str, Any]]
) -> Optional[Dict[str, Any]]:
    explicit = [item for item in commits if item.get("failure_id") == failure["id"]]
    if explicit:
        return min(explicit, key=sort_key)
    implicit = [
        item
        for item in commits
        if item["_ts"] > failure["_ts"] and "failure_id" not in item
    ]
    if implicit:
        return min(implicit, key=sort_key)
    return None


def link_retest(
    failure: Dict[str, Any],
    fix_commit: Optional[Dict[str, Any]],
    tests: Sequence[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    if fix_commit is None:
        return None
    candidates: List[Dict[str, Any]] = []
    for test in tests:
        if test["_ts"] < fix_commit["_ts"]:
            continue
        commit_id = test.get("commit_id")
        failure_id = test.get("failure_id")
        if commit_id is not None:
            if commit_id == fix_commit["id"]:
                candidates.append(test)
            continue
        if failure_id == failure["id"]:
            candidates.append(test)
    if not candidates:
        return None
    return min(candidates, key=sort_key)


def round_codes(
    fix_commit: Optional[Dict[str, Any]], retest: Optional[Dict[str, Any]]
) -> List[str]:
    codes: List[str] = []
    if fix_commit is None:
        codes.append("MISSING_FIX_COMMIT")
    if fix_commit is not None and retest is None:
        codes.append("MISSING_RETEST")
    if fix_commit is not None and retest is not None:
        codes.append("CHAIN_COMPLETE")
    return codes


def build_report(raw_data: Any) -> Dict[str, Any]:
    data = validate_input(raw_data)
    failures = sorted(data["failures"], key=sort_key)
    commits = data["commits"]
    tests = data["tests"]

    rounds: List[Dict[str, Any]] = []
    complete_count = 0
    fix_count = 0
    retest_count = 0
    passed_retests = 0

    for index, failure in enumerate(failures, start=1):
        fix_commit = link_fix_commit(failure, commits)
        retest = link_retest(failure, fix_commit, tests)
        evidence_complete = fix_commit is not None and retest is not None
        if fix_commit is not None:
            fix_count += 1
        if retest is not None:
            retest_count += 1
            if retest["passed"]:
                passed_retests += 1
        if evidence_complete:
            complete_count += 1
        rounds.append(
            {
                "round_index": index,
                "failure_id": failure["id"],
                "failure": strip_internal(failure),
                "fix_commit": strip_internal(fix_commit),
                "retest": strip_internal(retest),
                "evidence_complete": evidence_complete,
                "codes": round_codes(fix_commit, retest),
            }
        )

    failure_count = len(failures)
    completeness = (
        round(complete_count / failure_count * 100, 2) if failure_count else 100.0
    )
    regression_pass_rate = (
        round(passed_retests / retest_count * 100, 2) if retest_count else 100.0
    )

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "source_digest": source_digest(raw_data),
        "valid": True,
        "metrics": {
            "repair_round_count": fix_count,
            "regression_pass_rate": regression_pass_rate,
            "evidence_completeness_percent": completeness,
        },
        "summary": {
            "failure_count": failure_count,
            "linked_fix_count": fix_count,
            "linked_retest_count": retest_count,
            "complete_round_count": complete_count,
        },
        "evidence_chain": rounds,
        "limitation": LIMITATION,
        "interpretation": (
            "证据链按失败时间排序；修复提交优先匹配 failure_id，否则取失败后最早的未绑定提交；"
            "复测优先匹配 commit_id，否则匹配 failure_id。"
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
    except ChainInputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
