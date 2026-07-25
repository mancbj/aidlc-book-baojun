#!/usr/bin/env python3
"""Validate Mob sessions and agent handoff against a frozen collaboration guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set


EXPERIMENT_ID = "EXP-10-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/mob_collaboration_handoff_guide.json"
EXPECTED_PIN = (
    "sha256:1fffdb9c183ca0f19f2706e466ba2105bb0c54297df705d18d545d874ff35235"
)
LIMITATION = (
    "本报告仅对照仓库内冻结的 Mob 协作与交接指南与会话记录做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Mob 会话决策一致性与交接信息损失。")
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


def parse_decisions(value: Any, path: str, allowed: Set[str]) -> Dict[str, str]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
    extra = set(value) - allowed
    if extra:
        raise InputError("E_UNKNOWN_DECISION", f"{path} 含未知决策键：{sorted(extra)[0]}")
    parsed: Dict[str, str] = {}
    for key in allowed:
        if key not in value:
            raise InputError("E_MISSING_DECISION", f"{path} 缺少决策：{key}")
        raw = value[key]
        if not isinstance(raw, str) or not raw.strip():
            raise InputError("E_INVALID_FIELD", f"{path}.{key} 必须是非空字符串")
        parsed[key] = raw.strip()
    return parsed


def parse_mob_sessions(value: Any, guide: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", "$.mob_sessions 必须是数组")
    guide_sessions = guide.get("mob_sessions")
    if not isinstance(guide_sessions, list):
        raise InputError("E_GUIDE_SHAPE", "指南 mob_sessions 必须是数组")
    meta_by_id: Dict[str, List[str]] = {}
    for item in guide_sessions:
        if isinstance(item, dict) and isinstance(item.get("session_id"), str):
            decisions = item.get("required_decisions")
            if isinstance(decisions, list):
                meta_by_id[item["session_id"]] = [d for d in decisions if isinstance(d, str)]
    parsed: List[Dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        path = f"$.mob_sessions[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        session_id = item.get("session_id")
        if not isinstance(session_id, str) or session_id not in meta_by_id:
            raise InputError("E_UNKNOWN_SESSION", f"{path}.session_id 未在指南登记：{session_id}")
        if session_id in seen:
            raise InputError("E_DUPLICATE_SESSION", f"{path}.session_id 重复：{session_id}")
        seen.add(session_id)
        required = set(meta_by_id[session_id])
        decisions = parse_decisions(item.get("decisions"), f"{path}.decisions", required)
        parsed.append({"session_id": session_id, "decisions": decisions})
    for session_id in meta_by_id:
        if session_id not in seen:
            raise InputError("E_MISSING_SESSION", f"缺少 Mob 会话：{session_id}")
    parsed.sort(key=lambda row: row["session_id"])
    return parsed


def parse_handoff_log(value: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    fields = guide.get("handoff_required_fields")
    if not isinstance(fields, list):
        raise InputError("E_GUIDE_SHAPE", "指南 handoff_required_fields 必须是数组")
    field_names = [f for f in fields if isinstance(f, str)]
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.handoff_log 必须是对象")
    extra = set(value) - set(field_names)
    if extra:
        raise InputError("E_UNKNOWN_HANDOFF_FIELD", f"$.handoff_log 含未知字段：{sorted(extra)[0]}")
    parsed: Dict[str, Any] = {}
    for name in field_names:
        if name not in value:
            raise InputError("E_MISSING_HANDOFF_FIELD", f"$.handoff_log 缺少字段：{name}")
        raw = value[name]
        if name == "approved_decisions":
            if not isinstance(raw, list) or not raw:
                raise InputError("E_INVALID_FIELD", "$.handoff_log.approved_decisions 必须是非空数组")
            decisions: List[str] = []
            for index, item in enumerate(raw):
                if not isinstance(item, str) or not item.strip():
                    raise InputError(
                        "E_INVALID_FIELD",
                        f"$.handoff_log.approved_decisions[{index}] 必须是非空字符串",
                    )
                decisions.append(item.strip())
            parsed[name] = sorted(set(decisions))
        else:
            if not isinstance(raw, str) or not raw.strip():
                raise InputError("E_INVALID_FIELD", f"$.handoff_log.{name} 必须是非空字符串")
            parsed[name] = raw.strip()
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    collaboration_id = raw.get("collaboration_id")
    if not isinstance(collaboration_id, str) or not collaboration_id.strip():
        raise InputError("E_INVALID_FIELD", "$.collaboration_id 必须是非空字符串")
    collaboration_seconds = parse_timing(raw.get("timing"))
    mob_sessions = parse_mob_sessions(raw.get("mob_sessions"), guide)
    handoff_log = parse_handoff_log(raw.get("handoff_log"), guide)
    return {
        "pinned_version": pinned,
        "collaboration_id": collaboration_id.strip(),
        "collaboration_seconds": collaboration_seconds,
        "mob_sessions": mob_sessions,
        "handoff_log": handoff_log,
    }


def reference_decisions(guide: Dict[str, Any]) -> Dict[str, str]:
    ref = guide.get("reference_decisions")
    if not isinstance(ref, dict):
        raise InputError("E_GUIDE_SHAPE", "指南 reference_decisions 必须是对象")
    parsed: Dict[str, str] = {}
    for key, value in ref.items():
        if isinstance(key, str) and isinstance(value, str):
            parsed[key] = value
    return parsed


def evaluate(context: Dict[str, Any], guide: Dict[str, Any]) -> Dict[str, Any]:
    reference = reference_decisions(guide)
    total_decisions = 0
    agreed = 0
    session_details: List[Dict[str, Any]] = []
    for session in context["mob_sessions"]:
        session_agreed = 0
        session_total = len(session["decisions"])
        mismatches: List[str] = []
        for decision_id, observed in session["decisions"].items():
            total_decisions += 1
            expected = reference.get(decision_id)
            if expected is not None and observed == expected:
                agreed += 1
                session_agreed += 1
            else:
                mismatches.append(decision_id)
        session_details.append(
            {
                "session_id": session["session_id"],
                "decision_agreement_percent": (
                    100.0
                    if session_total == 0
                    else round(100.0 * session_agreed / session_total, 2)
                ),
                "mismatched_decisions": sorted(mismatches),
            }
        )

    agreement_pct = (
        100.0 if total_decisions == 0 else round(100.0 * agreed / total_decisions, 2)
    )

    handoff = context["handoff_log"]
    required_payload_fields = [
        "intent_summary",
        "open_risks",
        "approved_decisions",
    ]
    present = 0
    for field in required_payload_fields:
        value = handoff.get(field)
        if field == "approved_decisions":
            if isinstance(value, list) and value:
                present += 1
        elif isinstance(value, str) and value.strip():
            present += 1
    payload_coverage = round(100.0 * present / len(required_payload_fields), 2)
    handoff_loss = round(100.0 - payload_coverage, 2)

    valid = agreement_pct == 100.0 and handoff_loss == 0.0
    return {
        "session_details": session_details,
        "decision_agreement_percent": agreement_pct,
        "handoff_information_loss_percent": handoff_loss,
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
        "valid": evaluation["valid"],
        "collaboration_id": context["collaboration_id"],
        "mob_sessions": evaluation["session_details"],
        "handoff_log": context["handoff_log"],
        "metrics": {
            "handoff_information_loss_percent": evaluation["handoff_information_loss_percent"],
            "decision_agreement_percent": evaluation["decision_agreement_percent"],
            "collaboration_seconds": context["collaboration_seconds"],
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
