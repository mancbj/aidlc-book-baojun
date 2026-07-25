#!/usr/bin/env python3
"""Validate a four-agent session against a frozen checkpoint guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-02-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/four_agent_checkpoint_guide.json"
EXPECTED_PIN = (
    "sha256:37725f7af797f4e7589afb48686349a940384029e0f46d76cda8ddd747141953"
)
SESSION_ACTIONS = ("route", "propose", "human_approval", "handoff")
LIMITATION = (
    "本报告仅对照仓库内冻结的四 Agent 检查点指南与输入会话记录做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对四 Agent 路由/提议/审批/交接与会话检查点。")
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


def parse_session_events(value: Any, guide: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise InputError("E_INVALID_FIELD", "$.session_events 必须是非空数组")
    agents = guide.get("agents")
    if not isinstance(agents, list):
        raise InputError("E_GUIDE_SHAPE", "指南 agents 必须是数组")
    allowed_agents = tuple(a for a in agents if isinstance(a, str))
    parsed: List[Dict[str, Any]] = []
    for index, item in enumerate(value):
        path = f"$.session_events[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        agent_id = require_enum(item.get("agent_id"), f"{path}.agent_id", allowed_agents)
        action = require_enum(item.get("action"), f"{path}.action", SESSION_ACTIONS)
        checkpoint_id = item.get("checkpoint_id")
        if checkpoint_id is not None and (
            not isinstance(checkpoint_id, str) or not checkpoint_id.strip()
        ):
            raise InputError("E_INVALID_FIELD", f"{path}.checkpoint_id 必须是非空字符串或省略")
        evidence = item.get("evidence")
        rationale = item.get("rationale")
        if evidence is not None and not isinstance(evidence, str):
            raise InputError("E_INVALID_FIELD", f"{path}.evidence 必须是字符串或省略")
        if rationale is not None and not isinstance(rationale, str):
            raise InputError("E_INVALID_FIELD", f"{path}.rationale 必须是字符串或省略")
        parsed.append(
            {
                "agent_id": agent_id,
                "action": action,
                "checkpoint_id": checkpoint_id.strip() if isinstance(checkpoint_id, str) else None,
                "evidence": evidence if isinstance(evidence, str) else None,
                "rationale": rationale if isinstance(rationale, str) else None,
            }
        )
    return parsed


def parse_input(raw: Any) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    return {"pinned_version": pinned}


def is_grounded_approval(event: Dict[str, Any], guide: Dict[str, Any]) -> bool:
    requires = guide.get("approval_requires")
    if not isinstance(requires, list):
        return False
    for field in requires:
        if not isinstance(field, str):
            continue
        val = event.get(field)
        if not isinstance(val, str) or not val.strip():
            return False
    return True


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw)
    events = parse_session_events(raw.get("session_events"), guide)
    required_cps = [
        cp
        for cp in guide.get("required_session_checkpoints", [])
        if isinstance(cp, str) and cp
    ]
    observed_map: Dict[str, bool] = {}
    for event in events:
        cp = event.get("checkpoint_id")
        if cp:
            observed_map[cp] = True

    missing = [cp for cp in required_cps if cp not in observed_map]
    if missing:
        raise InputError("E_MISSING_CHECKPOINT", f"会话缺少必需检查点：{missing[0]}")

    satisfied = sum(1 for cp in required_cps if observed_map.get(cp))
    adherence = (
        100.0 if not required_cps else round(100.0 * satisfied / len(required_cps), 2)
    )

    ungrounded = 0
    approval_details: List[Dict[str, Any]] = []
    for index, event in enumerate(events):
        if event["action"] != "human_approval":
            continue
        grounded = is_grounded_approval(event, guide)
        if not grounded:
            ungrounded += 1
        approval_details.append(
            {
                "event_index": index,
                "agent_id": event["agent_id"],
                "grounded": grounded,
            }
        )

    valid = adherence == 100.0 and ungrounded == 0

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": valid,
        "session_event_count": len(events),
        "human_approvals": approval_details,
        "metrics": {
            "checkpoint_adherence_percent": adherence,
            "ungrounded_approval_count": ungrounded,
            "required_checkpoint_count": len(required_cps),
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
