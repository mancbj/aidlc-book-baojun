#!/usr/bin/env python3
"""Compare frozen clarify vs no-clarify sessions on one ambiguous requirement."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-02-02"
SCHEMA_VERSION = "1.0.0"
ARM_NO_CLARIFY = "no_clarify"
ARM_WITH_CLARIFY = "with_clarify"
REQUIRED_ARMS = (ARM_NO_CLARIFY, ARM_WITH_CLARIFY)
LIMITATION = (
    "本报告只对输入中两组冻结会话做确定性对照与差分；"
    "它不证明澄清提问总能减少实现后需求变更。"
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成需求决策日志与实现差异对照报告。")
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


def require_nonempty_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非空字符串")
    return value.strip()


def require_non_negative_int(value: Any, path: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非负整数")
    if value < 0:
        raise InputError("E_INVALID_FIELD", f"{path} 必须是非负整数")
    return value


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是数组")
    return value


def parse_decision_log(value: Any, path: str) -> List[Dict[str, str]]:
    entries: List[Dict[str, str]] = []
    seen: Set[str] = set()
    raw_items = require_list(value, path)
    if not raw_items:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组")
    for index, raw in enumerate(raw_items):
        entry_path = f"{path}[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{entry_path} 必须是对象")
        entry_id = require_nonempty_string(raw.get("id"), f"{entry_path}.id")
        if entry_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{entry_id}")
        seen.add(entry_id)
        entries.append(
            {
                "id": entry_id,
                "phase": require_nonempty_string(raw.get("phase"), f"{entry_path}.phase"),
                "summary": require_nonempty_string(raw.get("summary"), f"{entry_path}.summary"),
            }
        )
    entries.sort(key=lambda item: item["id"])
    return entries


def parse_labeled_items(
    value: Any, path: str, field: str, require_non_empty: bool = False
) -> List[Dict[str, str]]:
    items: List[Dict[str, str]] = []
    seen: Set[str] = set()
    items_raw = require_list(value, path)
    if require_non_empty and not items_raw:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组")
    for index, raw in enumerate(items_raw):
        item_path = f"{path}[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{item_path} 必须是对象")
        item_id = require_nonempty_string(raw.get("id"), f"{item_path}.id")
        if item_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{item_id}")
        seen.add(item_id)
        items.append(
            {
                "id": item_id,
                field: require_nonempty_string(raw.get(field), f"{item_path}.{field}"),
            }
        )
    items.sort(key=lambda item: item["id"])
    return items


def parse_implemented_items(value: Any, path: str) -> List[Dict[str, str]]:
    return parse_labeled_items(value, path, "capability", require_non_empty=True)


def parse_session(value: Any, path: str, arm: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
    clarification_rounds = require_non_negative_int(
        value.get("clarification_rounds"), f"{path}.clarification_rounds"
    )
    if arm == ARM_NO_CLARIFY and clarification_rounds != 0:
        raise InputError(
            "E_INVALID_CLARIFICATION_ROUNDS",
            f"{path}.clarification_rounds 在无澄清臂必须为 0",
        )
    if arm == ARM_WITH_CLARIFY and clarification_rounds < 1:
        raise InputError(
            "E_INVALID_CLARIFICATION_ROUNDS",
            f"{path}.clarification_rounds 在澄清臂必须 >= 1",
        )
    transcript = value.get("session_transcript")
    if transcript is not None:
        if not isinstance(transcript, list) or not transcript:
            raise InputError("E_REQUIRED_COLLECTION", f"{path}.session_transcript 必须是非空数组")
        for index, turn in enumerate(transcript):
            turn_path = f"{path}.session_transcript[{index}]"
            if not isinstance(turn, dict):
                raise InputError("E_INVALID_FIELD", f"{turn_path} 必须是对象")
            require_nonempty_string(turn.get("role"), f"{turn_path}.role")
            require_nonempty_string(turn.get("content"), f"{turn_path}.content")
    return {
        "arm": arm,
        "clarification_rounds": clarification_rounds,
        "session_transcript": transcript,
        "decision_log": parse_decision_log(value.get("decision_log"), f"{path}.decision_log"),
        "post_impl_requirement_changes": parse_labeled_items(
            value.get("post_impl_requirement_changes"),
            f"{path}.post_impl_requirement_changes",
            "change",
        ),
        "critical_omissions": parse_labeled_items(
            value.get("critical_omissions"),
            f"{path}.critical_omissions",
            "omission",
        ),
        "implemented_items": parse_implemented_items(
            value.get("implemented_items"), f"{path}.implemented_items"
        ),
    }


def build_implementation_difference(
    arms: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    by_arm_capability: Dict[str, Dict[str, str]] = {}
    for arm_name, session in arms.items():
        by_arm_capability[arm_name] = {
            item["id"]: item["capability"] for item in session["implemented_items"]
        }
    no_ids = set(by_arm_capability[ARM_NO_CLARIFY])
    with_ids = set(by_arm_capability[ARM_WITH_CLARIFY])
    shared_ids = sorted(no_ids & with_ids)
    no_only = sorted(no_ids - with_ids)
    with_only = sorted(with_ids - no_ids)

    def materialize(ids: List[str], arm: str) -> List[Dict[str, str]]:
        lookup = by_arm_capability[arm]
        return [{"id": item_id, "capability": lookup[item_id]} for item_id in ids]

    return {
        "shared_implementations": [
            {
                "id": item_id,
                "capability": by_arm_capability[ARM_NO_CLARIFY][item_id],
            }
            for item_id in shared_ids
        ],
        "no_clarify_only": materialize(no_only, ARM_NO_CLARIFY),
        "with_clarify_only": materialize(with_only, ARM_WITH_CLARIFY),
        "unique_implementation_count": len(no_only) + len(with_only),
    }


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    ambiguous_requirement = require_nonempty_string(
        data.get("ambiguous_requirement"), "$.ambiguous_requirement"
    )
    sessions_raw = data.get("sessions")
    if not isinstance(sessions_raw, dict):
        raise InputError("E_INVALID_FIELD", "$.sessions 必须是对象")
    missing_arms = [arm for arm in REQUIRED_ARMS if arm not in sessions_raw]
    if missing_arms:
        raise InputError(
            "E_MISSING_SESSION_ARM",
            f"缺少会话臂：{', '.join(missing_arms)}",
        )
    arms = {
        arm: parse_session(sessions_raw[arm], f"$.sessions.{arm}", arm)
        for arm in REQUIRED_ARMS
    }

    metrics_by_arm = {
        arm: {
            "clarification_rounds": session["clarification_rounds"],
            "post_impl_requirement_change_count": len(
                session["post_impl_requirement_changes"]
            ),
            "critical_omission_count": len(session["critical_omissions"]),
        }
        for arm, session in arms.items()
    }
    no_metrics = metrics_by_arm[ARM_NO_CLARIFY]
    with_metrics = metrics_by_arm[ARM_WITH_CLARIFY]

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "ambiguous_requirement": ambiguous_requirement,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "decision_log_by_arm": {
            arm: arms[arm]["decision_log"] for arm in REQUIRED_ARMS
        },
        "implementation_difference_report": build_implementation_difference(arms),
        "metrics": {
            "by_arm": metrics_by_arm,
            "delta_no_clarify_minus_with_clarify": {
                "post_impl_requirement_change_count": (
                    no_metrics["post_impl_requirement_change_count"]
                    - with_metrics["post_impl_requirement_change_count"]
                ),
                "critical_omission_count": (
                    no_metrics["critical_omission_count"]
                    - with_metrics["critical_omission_count"]
                ),
            },
        },
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
        report = build_report(load_input(args.input))
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
