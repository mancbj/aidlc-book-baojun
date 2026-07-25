#!/usr/bin/env python3
"""Validate Inception Agent decomposition artifacts against a frozen guide pin."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-03-03"
SCHEMA_VERSION = "1.0.0"
GUIDE_REL = "fixtures/inception_agent_guide.json"
EXPECTED_PIN = (
    "sha256:d65ec6e39e641b3009ef88f78cf22aaa19e127a35f75f0e6bcff671dc66f416a"
)
LIMITATION = (
    "本报告仅对照仓库内冻结的 Inception Agent 分解指南与输入工件包做确定性核对；"
    "冻结 pin 不等于唯一标准，且不访问或验证实时 specs.md portal。"
)


class InputError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="核对 Requirements 至 Bolt Plan 工件与追踪链接。")
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


def parse_artifacts(value: Any, required: Sequence[str]) -> Dict[str, bool]:
    if not isinstance(value, dict):
        raise InputError("E_INVALID_FIELD", "$.artifacts 必须是对象")
    present: Dict[str, bool] = {}
    for art in required:
        if art not in value:
            raise InputError("E_MISSING_ARTIFACT", f"$.artifacts 缺少登记工件：{art}")
        flag = value[art]
        if not isinstance(flag, bool):
            raise InputError("E_INVALID_FIELD", f"$.artifacts.{art} 必须是布尔值")
        present[art] = flag
    extra = set(value) - set(required)
    if extra:
        raise InputError("E_UNKNOWN_ARTIFACT", f"$.artifacts 含未知工件：{sorted(extra)[0]}")
    return present


def link_key(link: Dict[str, Any]) -> Tuple[str, str, str]:
    return (str(link["from"]), str(link["to"]), str(link["relation"]))


def parse_trace_links(value: Any) -> List[Dict[str, str]]:
    if not isinstance(value, list):
        raise InputError("E_INVALID_FIELD", "$.trace_links 必须是数组")
    parsed: List[Dict[str, str]] = []
    seen: Set[Tuple[str, str, str]] = set()
    for index, item in enumerate(value):
        path = f"$.trace_links[{index}]"
        if not isinstance(item, dict):
            raise InputError("E_INVALID_FIELD", f"{path} 必须是对象")
        for field in ("from", "to", "relation"):
            val = item.get(field)
            if not isinstance(val, str) or not val.strip():
                raise InputError("E_INVALID_FIELD", f"{path}.{field} 必须是非空字符串")
        normalized = {
            "from": item["from"].strip(),
            "to": item["to"].strip(),
            "relation": item["relation"].strip(),
        }
        key = link_key(normalized)
        if key in seen:
            raise InputError("E_DUPLICATE_LINK", f"{path} 追踪链接重复")
        seen.add(key)
        parsed.append(normalized)
    return parsed


def parse_input(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(raw, dict):
        raise InputError("E_INVALID_ROOT", "JSON 根节点必须是对象")
    if raw.get("experiment_id") != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}")
    pinned = raw.get("pinned_version")
    if not isinstance(pinned, str) or pinned != EXPECTED_PIN:
        raise InputError("E_PIN_MISMATCH", f"pinned_version 必须是 {EXPECTED_PIN}")
    required = [
        a for a in guide.get("required_artifacts", []) if isinstance(a, str) and a
    ]
    artifacts = parse_artifacts(raw.get("artifacts"), required)
    trace_links = parse_trace_links(raw.get("trace_links"))
    return {"pinned_version": pinned, "artifacts": artifacts, "trace_links": trace_links}


def required_links(guide: Dict[str, Any]) -> List[Dict[str, str]]:
    links = guide.get("required_trace_links")
    if not isinstance(links, list):
        raise InputError("E_GUIDE_SHAPE", "指南 required_trace_links 必须是数组")
    result: List[Dict[str, str]] = []
    for index, item in enumerate(links):
        if not isinstance(item, dict):
            raise InputError("E_GUIDE_SHAPE", f"指南链接[{index}] 必须是对象")
        for field in ("from", "to", "relation"):
            if not isinstance(item.get(field), str):
                raise InputError("E_GUIDE_SHAPE", f"指南链接[{index}].{field} 无效")
        result.append(
            {
                "from": item["from"],
                "to": item["to"],
                "relation": item["relation"],
            }
        )
    return result


def build_report(raw: Any, guide: Dict[str, Any]) -> Dict[str, Any]:
    context = parse_input(raw, guide)
    required = [
        a for a in guide.get("required_artifacts", []) if isinstance(a, str) and a
    ]
    present_count = sum(1 for a in required if context["artifacts"].get(a) is True)
    artifact_pct = (
        100.0 if not required else round(100.0 * present_count / len(required), 2)
    )

    expected_links = required_links(guide)
    observed = {link_key(link) for link in context["trace_links"]}
    covered = sum(1 for link in expected_links if link_key(link) in observed)
    trace_pct = (
        100.0 if not expected_links else round(100.0 * covered / len(expected_links), 2)
    )

    missing_links = [link for link in expected_links if link_key(link) not in observed]
    if missing_links and artifact_pct == 100.0:
        # Domain error only when claiming full artifacts but missing required trace
        pass

    valid = artifact_pct == 100.0 and trace_pct == 100.0

    return {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "pinned_version": context["pinned_version"],
        "guide_digest": "sha256:"
        + hashlib.sha256(canonical_json(guide).encode("utf-8")).hexdigest(),
        "external_source": guide.get("external_source"),
        "valid": valid,
        "artifacts": context["artifacts"],
        "missing_trace_links": missing_links,
        "metrics": {
            "artifact_completeness_percent": artifact_pct,
            "trace_link_coverage_percent": trace_pct,
            "required_artifact_count": len(required),
            "required_trace_link_count": len(expected_links),
            "covered_trace_link_count": covered,
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
