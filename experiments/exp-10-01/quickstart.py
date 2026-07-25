#!/usr/bin/env python3
"""Generate a deterministic human–Agent RACI matrix."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-10-01"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "本工具只检查输入活动是否具备可见的 Accountable 与冲突信号；"
    "它不证明生成的 RACI 已适合所有组织或团队结构。"
)
ACCOUNTABLE_RULE = "Accountable 必须为人类角色，不得为 Agent。"
RACI_LETTERS = ("R", "A", "C", "I")
AGENT_KINDS = ("master", "inception", "construction", "operations")

ACTIVITY_PATTERNS: Dict[str, Dict[str, Any]] = {
    "STAGE_ROUTING": {
        "label": "路由到下一阶段",
        "responsible_agent_kind": "master",
        "default_consulted_roles": [],
        "default_informed_agent_kinds": ["operations"],
    },
    "INTENT_DECOMPOSITION": {
        "label": "分解 Intent／Unit／Story",
        "responsible_agent_kind": "inception",
        "default_consulted_roles": ["tech_lead"],
        "default_informed_agent_kinds": ["master"],
    },
    "BOLT_EXECUTION": {
        "label": "执行 Bolt／修复失败",
        "responsible_agent_kind": "construction",
        "default_consulted_roles": ["tech_lead"],
        "default_informed_agent_kinds": ["master", "operations"],
    },
    "RELEASE_ROLLBACK": {
        "label": "发布与回滚",
        "responsible_agent_kind": "operations",
        "default_consulted_roles": ["tech_lead"],
        "default_informed_agent_kinds": ["master"],
    },
    "INDEPENDENT_REVIEW": {
        "label": "独立评审与放行",
        "responsible_agent_kind": "construction",
        "default_consulted_roles": ["quality_owner"],
        "default_informed_agent_kinds": ["master", "inception"],
    },
}


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成人–Agent RACI 责任矩阵。")
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


def require_list(value: Any, path: str) -> List[Any]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", f"{path} 必须是非空数组")
    return value


def parse_agents(value: Any) -> List[Dict[str, str]]:
    raw_items = require_list(value, "$.agents")
    if len(raw_items) != 4:
        raise InputError("E_AGENT_SET", "$.agents 必须恰好包含四类 Agent")
    agents: List[Dict[str, str]] = []
    seen_ids: Set[str] = set()
    seen_kinds: Set[str] = set()
    for index, raw in enumerate(raw_items):
        path = f"$.agents[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        agent_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if agent_id in seen_ids:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{agent_id}")
        seen_ids.add(agent_id)
        kind = require_nonempty_string(raw.get("kind"), f"{path}.kind")
        if kind not in AGENT_KINDS:
            raise InputError("E_UNKNOWN_AGENT_KIND", f"{path}.kind 必须是 {AGENT_KINDS} 之一")
        if kind in seen_kinds:
            raise InputError("E_DUPLICATE_AGENT_KIND", f"重复的 Agent kind：{kind}")
        seen_kinds.add(kind)
        agents.append(
            {
                "id": agent_id,
                "name": require_nonempty_string(raw.get("name"), f"{path}.name"),
                "kind": kind,
            }
        )
    if seen_kinds != set(AGENT_KINDS):
        raise InputError("E_AGENT_SET", "$.agents 必须包含 master、inception、construction、operations")
    agents.sort(key=lambda item: AGENT_KINDS.index(item["kind"]))
    return agents


def parse_team_roles(value: Any) -> List[Dict[str, str]]:
    roles: List[Dict[str, str]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(require_list(value, "$.team_roles")):
        path = f"$.team_roles[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        role_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if role_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{role_id}")
        seen.add(role_id)
        roles.append(
            {
                "id": role_id,
                "name": require_nonempty_string(raw.get("name"), f"{path}.name"),
            }
        )
    return roles


def parse_string_list(value: Any, path: str, optional: bool = False) -> List[str]:
    if value is None:
        if optional:
            return []
        raise InputError("E_INVALID_FIELD", f"{path} 必须是字符串数组")
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", f"{path} 必须是字符串数组")
    result: List[str] = []
    for index, item in enumerate(value):
        result.append(require_nonempty_string(item, f"{path}[{index}]"))
    return result


def parse_activities(
    value: Any,
    human_ids: Set[str],
    agent_ids: Set[str],
) -> List[Dict[str, Any]]:
    activities: List[Dict[str, Any]] = []
    seen: Set[str] = set()
    for index, raw in enumerate(require_list(value, "$.development_activities")):
        path = f"$.development_activities[{index}]"
        if not isinstance(raw, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        activity_id = require_nonempty_string(raw.get("id"), f"{path}.id")
        if activity_id in seen:
            raise InputError("E_DUPLICATE_ID", f"重复 ID：{activity_id}")
        seen.add(activity_id)
        pattern_id = require_nonempty_string(raw.get("pattern_id"), f"{path}.pattern_id")
        if pattern_id not in ACTIVITY_PATTERNS:
            raise InputError("E_UNKNOWN_PATTERN", f"{path}.pattern_id 未知：{pattern_id}")

        accountable_role = raw.get("accountable_role")
        if accountable_role is not None:
            accountable_role = require_nonempty_string(accountable_role, f"{path}.accountable_role")
            if accountable_role in agent_ids:
                raise InputError(
                    "E_ACCOUNTABLE_AGENT",
                    f"{path}.accountable_role 不得引用 Agent：{accountable_role}",
                )
            if accountable_role not in human_ids:
                raise InputError(
                    "E_UNKNOWN_ROLE",
                    f"{path}.accountable_role 引用了未知团队角色：{accountable_role}",
                )

        extra_accountable = parse_string_list(
            raw.get("additional_accountable_roles"),
            f"{path}.additional_accountable_roles",
            optional=True,
        )
        for extra_index, role_id in enumerate(extra_accountable):
            extra_path = f"{path}.additional_accountable_roles[{extra_index}]"
            if role_id in agent_ids:
                raise InputError("E_ACCOUNTABLE_AGENT", f"{extra_path} 不得引用 Agent：{role_id}")
            if role_id not in human_ids:
                raise InputError("E_UNKNOWN_ROLE", f"{extra_path} 引用了未知团队角色：{role_id}")

        consulted = parse_string_list(
            raw.get("consulted_roles"),
            f"{path}.consulted_roles",
            optional=True,
        )
        for c_index, role_id in enumerate(consulted):
            if role_id not in human_ids:
                raise InputError(
                    "E_UNKNOWN_ROLE",
                    f"{path}.consulted_roles[{c_index}] 引用了未知团队角色：{role_id}",
                )

        informed_roles = parse_string_list(
            raw.get("informed_roles"),
            f"{path}.informed_roles",
            optional=True,
        )
        for i_index, role_id in enumerate(informed_roles):
            if role_id not in human_ids:
                raise InputError(
                    "E_UNKNOWN_ROLE",
                    f"{path}.informed_roles[{i_index}] 引用了未知团队角色：{role_id}",
                )

        responsible_agents = parse_string_list(
            raw.get("responsible_agents"),
            f"{path}.responsible_agents",
            optional=True,
        )
        for r_index, agent_id in enumerate(responsible_agents):
            if agent_id not in agent_ids:
                raise InputError(
                    "E_UNKNOWN_AGENT",
                    f"{path}.responsible_agents[{r_index}] 引用了未知 Agent：{agent_id}",
                )

        activities.append(
            {
                "id": activity_id,
                "name": require_nonempty_string(raw.get("name"), f"{path}.name"),
                "pattern_id": pattern_id,
                "accountable_role": accountable_role,
                "additional_accountable_roles": extra_accountable,
                "consulted_roles": consulted,
                "informed_roles": informed_roles,
                "responsible_agents": responsible_agents,
            }
        )
    return activities


def agent_by_kind(agents: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {agent["kind"]: agent for agent in agents}


def participant_ref(participant_id: str, humans: Dict[str, Dict[str, str]], agents: Dict[str, Dict[str, str]]) -> Dict[str, str]:
    if participant_id in humans:
        return {"id": participant_id, "name": humans[participant_id]["name"], "kind": "human"}
    if participant_id in agents:
        return {"id": participant_id, "name": agents[participant_id]["name"], "kind": "agent"}
    raise InputError("E_UNKNOWN_PARTICIPANT", f"未知参与者：{participant_id}")


def merge_assignments(assignments: List[Tuple[str, str]]) -> List[Dict[str, Any]]:
    """Merge duplicate participant rows by concatenating RACI letters deterministically."""
    by_participant: Dict[str, Set[str]] = {}
    for participant_id, letter in assignments:
        by_participant.setdefault(participant_id, set()).add(letter)
    merged: List[Dict[str, Any]] = []
    for participant_id in sorted(by_participant):
        letters = "".join(letter for letter in RACI_LETTERS if letter in by_participant[participant_id])
        merged.append({"participant_id": participant_id, "letters": letters})
    return merged


def build_activity_row(
    activity: Dict[str, Any],
    humans: Dict[str, Dict[str, str]],
    agents_by_id: Dict[str, Dict[str, str]],
    agents_by_kind: Dict[str, Dict[str, str]],
) -> Dict[str, Any]:
    pattern = ACTIVITY_PATTERNS[activity["pattern_id"]]
    assignments: List[Tuple[str, str]] = []

    responsible_agents = activity["responsible_agents"]
    if not responsible_agents:
        responsible_agents = [agents_by_kind[pattern["responsible_agent_kind"]]["id"]]
    for agent_id in sorted(set(responsible_agents)):
        assignments.append((agent_id, "R"))

    accountable_ids: List[str] = []
    if activity["accountable_role"]:
        accountable_ids.append(activity["accountable_role"])
    accountable_ids.extend(activity["additional_accountable_roles"])
    accountable_ids = list(dict.fromkeys(accountable_ids))

    for role_id in accountable_ids:
        assignments.append((role_id, "A"))

    consulted = activity["consulted_roles"] or pattern["default_consulted_roles"]
    for role_id in sorted(set(consulted)):
        assignments.append((role_id, "C"))

    informed_roles = activity["informed_roles"]
    informed_agent_kinds = pattern["default_informed_agent_kinds"]
    for role_id in sorted(set(informed_roles)):
        assignments.append((role_id, "I"))
    for kind in informed_agent_kinds:
        assignments.append((agents_by_kind[kind]["id"], "I"))

    merged = merge_assignments(assignments)
    matrix_cells = []
    for cell in merged:
        ref = participant_ref(cell["participant_id"], humans, agents_by_id)
        matrix_cells.append(
            {
                "participant": ref,
                "letters": cell["letters"],
            }
        )

    conflict_codes: List[str] = []
    if len(accountable_ids) == 0:
        conflict_codes.append("MISSING_ACCOUNTABLE")
    elif len(accountable_ids) > 1:
        conflict_codes.append("MULTIPLE_ACCOUNTABLE")

    accountable_status = "assigned" if len(accountable_ids) == 1 else "unassigned"
    if len(accountable_ids) > 1:
        accountable_status = "conflict"

    return {
        "activity": {
            "id": activity["id"],
            "name": activity["name"],
            "pattern_id": activity["pattern_id"],
            "pattern_label": pattern["label"],
        },
        "assignments": matrix_cells,
        "accountable_status": accountable_status,
        "accountable_roles": [
            {"id": role_id, "name": humans[role_id]["name"]} for role_id in accountable_ids
        ],
        "conflict_codes": conflict_codes,
    }


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")

    project_name = require_nonempty_string(data.get("project_name"), "$.project_name")
    agents = parse_agents(data.get("agents"))
    team_roles = parse_team_roles(data.get("team_roles"))
    humans = {role["id"]: role for role in team_roles}
    agents_by_id = {agent["id"]: agent for agent in agents}
    activities = parse_activities(
        data.get("development_activities"),
        set(humans),
        set(agents_by_id),
    )
    agents_by_kind = agent_by_kind(agents)

    rows = [
        build_activity_row(activity, humans, agents_by_id, agents_by_kind)
        for activity in activities
    ]

    unassigned = sum(row["accountable_status"] == "unassigned" for row in rows)
    conflicts = sum(
        1 for row in rows if "MULTIPLE_ACCOUNTABLE" in row["conflict_codes"]
    )

    for row in rows:
        for cell in row["assignments"]:
            if "A" in cell["letters"] and cell["participant"]["kind"] != "human":
                raise InputError(
                    "E_INTERNAL_ACCOUNTABLE",
                    "输出矩阵违反 Accountable 必须为人类角色的硬规则",
                )

    participants = [
        {"id": role["id"], "name": role["name"], "kind": "human"} for role in team_roles
    ] + [
        {"id": agent["id"], "name": agent["name"], "kind": "agent", "agent_kind": agent["kind"]}
        for agent in agents
    ]

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "project_name": project_name,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "accountable_rule": ACCOUNTABLE_RULE,
        "participants": participants,
        "raci_matrix": rows,
        "pattern_basis": sorted(ACTIVITY_PATTERNS),
        "metrics": {
            "activity_count": len(rows),
            "unassigned_accountable_decisions_count": unassigned,
            "responsibility_conflict_count": conflicts,
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
