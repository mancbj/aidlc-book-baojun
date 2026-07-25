#!/usr/bin/env python3
"""Generate a deterministic human-judgment responsibility checklist."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence


EXPERIMENT_ID = "EXP-02-01"
SCHEMA_VERSION = "1.0.0"
LIMITATION = (
    "判断点覆盖率仅表示输入条目命中本工具的内置规则；"
    "它不证明已覆盖项目中的全部不可委托判断。"
)

RULES = {
    "goals": {
        "id": "GOAL_APPROVAL",
        "label": "目标验收判断",
        "prompt": "由人确认目标“{statement}”的成功标准与最终取舍。",
        "boundary": "AI 可整理候选成功标准和证据，但不得最终批准目标或取舍。",
    },
    "risks": {
        "id": "RISK_ACCEPTANCE",
        "label": "风险接受判断",
        "prompt": "由人决定风险“{statement}”的缓解措施与剩余风险是否可接受。",
        "boundary": "AI 可识别风险和比较缓解方案，但不得代表责任人接受剩余风险。",
    },
    "constraints": {
        "id": "CONSTRAINT_EXCEPTION",
        "label": "约束与例外判断",
        "prompt": "由人确认约束“{statement}”的满足证据，并批准任何例外。",
        "boundary": "AI 可检查规则符合性，但不得自行放宽约束或批准例外。",
    },
}


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="生成人类判断点与责任边界清单。")
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


def parse_roles(value: Any) -> List[Dict[str, str]]:
    roles: List[Dict[str, str]] = []
    seen = set()
    for index, raw in enumerate(require_list(value, "$.responsibility_roles")):
        path = f"$.responsibility_roles[{index}]"
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
                "boundary": require_nonempty_string(raw.get("boundary"), f"{path}.boundary"),
            }
        )
    return roles


def parse_items(data: Dict[str, Any], role_ids: set[str]) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    seen = set()
    for collection in ("goals", "risks", "constraints"):
        for index, raw in enumerate(require_list(data.get(collection), f"$.{collection}")):
            path = f"$.{collection}[{index}]"
            if not isinstance(raw, dict):
                raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
            item_id = require_nonempty_string(raw.get("id"), f"{path}.id")
            if item_id in seen:
                raise InputError("E_DUPLICATE_ID", f"重复 ID：{item_id}")
            seen.add(item_id)
            owner = raw.get("owner_role")
            if owner is not None:
                owner = require_nonempty_string(owner, f"{path}.owner_role")
                if owner not in role_ids:
                    raise InputError("E_UNKNOWN_ROLE", f"{path}.owner_role 引用了未知角色：{owner}")
            items.append(
                {
                    "collection": collection,
                    "id": item_id,
                    "statement": require_nonempty_string(raw.get("statement"), f"{path}.statement"),
                    "owner_role": owner,
                }
            )
    return items


def build_report(data: Any) -> Dict[str, Any]:
    if not isinstance(data, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if data.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    project_name = require_nonempty_string(data.get("project_name"), "$.project_name")
    roles = parse_roles(data.get("responsibility_roles"))
    role_by_id = {role["id"]: role for role in roles}
    items = parse_items(data, set(role_by_id))

    checkpoints = []
    assignments: Dict[str, List[str]] = {role["id"]: [] for role in roles}
    for item in items:
        rule = RULES[item["collection"]]
        checkpoint_id = f"J-{len(checkpoints) + 1:03d}"
        owner_id = item["owner_role"]
        if owner_id:
            assignments[owner_id].append(checkpoint_id)
        checkpoints.append(
            {
                "id": checkpoint_id,
                "source": {"type": item["collection"][:-1], "id": item["id"]},
                "rule_id": rule["id"],
                "label": rule["label"],
                "human_judgment": rule["prompt"].format(statement=item["statement"]),
                "responsibility_status": "assigned" if owner_id else "unassigned",
                "accountable_role": (
                    {"id": owner_id, "name": role_by_id[owner_id]["name"]} if owner_id else None
                ),
                "delegation_boundary": rule["boundary"],
            }
        )

    covered = len(checkpoints)
    total = len(items)
    unassigned = sum(
        checkpoint["responsibility_status"] == "unassigned" for checkpoint in checkpoints
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "project_name": project_name,
        "source_digest": "sha256:"
        + hashlib.sha256(canonical_json(data).encode("utf-8")).hexdigest(),
        "human_judgment_checkpoints": checkpoints,
        "responsibility_boundaries": [
            {
                "role": {"id": role["id"], "name": role["name"]},
                "declared_boundary": role["boundary"],
                "accountable_checkpoint_ids": assignments[role["id"]],
            }
            for role in roles
        ],
        "metrics": {
            "judgment_point_coverage_percent": round(covered / total * 100, 2),
            "covered_input_count": covered,
            "candidate_input_count": total,
            "unassigned_responsibility_count": unassigned,
        },
        "coverage_basis": sorted(rule["id"] for rule in RULES.values()),
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
