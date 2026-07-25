#!/usr/bin/env python3
"""Verify deterministic CI gate composition by parsing scripts/ci_check.py (EXP-07-01)."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


EXPERIMENT_ID = "EXP-07-01"
SCHEMA_VERSION = "1.0.0"
REUSED_IMPLEMENTATION = "scripts/ci_check.py"
LIMITATION = (
    "本实验只证明仓库 Must 门禁可被 ci_check.py 稳定聚合与合同化复现；"
    "它不证明书稿内容质量、读者理解或生产运行态已被充分验证。"
)


class InputError(Exception):
    """A validation error with a stable machine-readable code."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="验证 ci_check.py 确定性门禁组合。")
    parser.add_argument("--input", type=Path, help="实验输入 JSON。")
    parser.add_argument("--output", type=Path, help="组合报告 JSON。")
    parser.add_argument("--sample", action="store_true", help="使用仓库内默认样例路径。")
    parser.add_argument(
        "--live",
        action="store_true",
        help="可选：实际运行 scripts/ci_check.py 并合并子检查退出码（合同测试不得使用）。",
    )
    parser.add_argument("--root", type=Path, help="仓库根目录，默认自动推断。")
    args = parser.parse_args(argv)
    if args.sample:
        exp_root = Path(__file__).resolve().parent
        args.input = exp_root / "samples" / "input.json"
        args.output = exp_root / "output" / "sample.json"
    if not args.input or not args.output:
        parser.error("必须提供 --input/--output，或使用 --sample。")
    if args.root is None:
        args.root = Path(__file__).resolve().parents[2]
    return args


def pretty_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def require_object(value: Any, path: str) -> Dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError("E_EXPECTED_OBJECT", f"{path} 必须是对象。")
    return value


def require_field(parent: Dict[str, Any], field: str, path: str) -> Any:
    if field not in parent:
        raise InputError("E_REQUIRED_FIELD", f"{path}.{field} 是必填字段。")
    return parent[field]


def require_string(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError("E_EXPECTED_STRING", f"{path} 必须是非空字符串。")
    return value.strip()


def parse_expected_checks(value: Any) -> List[str]:
    if not isinstance(value, list) or not value:
        raise InputError("E_REQUIRED_COLLECTION", "$.expected_checks 必须是非空字符串数组。")
    checks: List[str] = []
    seen: Set[str] = set()
    for index, raw in enumerate(value):
        name = require_string(raw, f"$.expected_checks[{index}]")
        if name in seen:
            raise InputError("E_DUPLICATE_ID", f"expected_checks 重复：{name}")
        seen.add(name)
        checks.append(name)
    return checks


def validate_input(data: Any) -> Dict[str, Any]:
    root = require_object(data, "$")
    experiment_id = require_string(require_field(root, "experiment_id", "$"), "$.experiment_id")
    if experiment_id != EXPERIMENT_ID:
        raise InputError("E_EXPERIMENT_ID", f"experiment_id 必须是 {EXPERIMENT_ID}。")
    expected_checks = parse_expected_checks(require_field(root, "expected_checks", "$"))
    return {"experiment_id": experiment_id, "expected_checks": expected_checks}


def extract_configured_checks(ci_check_path: Path) -> List[str]:
    if not ci_check_path.is_file():
        raise InputError("E_MISSING_IMPLEMENTATION", f"找不到 {REUSED_IMPLEMENTATION}。")
    tree = ast.parse(ci_check_path.read_text(encoding="utf-8"))
    list_nodes: List[ast.List] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.AnnAssign):
            if isinstance(node.target, ast.Name) and node.target.id == "checks":
                if isinstance(node.value, ast.List):
                    list_nodes.append(node.value)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "checks":
                    if isinstance(node.value, ast.List):
                        list_nodes.append(node.value)
    for check_list in list_nodes:
        names: List[str] = []
        for elt in check_list.elts:
            if not isinstance(elt, ast.Tuple) or not elt.elts:
                continue
            first = elt.elts[0]
            if isinstance(first, ast.Constant) and isinstance(first.value, str):
                names.append(first.value)
        if names:
            return names
    raise InputError("E_PARSE_CI_CHECK", "无法从 ci_check.py 解析 checks 列表。")


def compare_composition(
    expected_checks: Sequence[str], configured_checks: Sequence[str]
) -> Tuple[Dict[str, Any], bool]:
    expected_set = set(expected_checks)
    configured_set = set(configured_checks)
    missing = sorted(expected_set - configured_set)
    extra = sorted(configured_set - expected_set)
    passed = len(expected_set & configured_set)
    failed = len(missing) + len(extra)
    composition = {
        "missing_checks": missing,
        "extra_checks": extra,
        "configured_check_count": len(configured_checks),
        "passed_check_count": passed,
        "failed_check_count": failed,
    }
    return composition, not missing and not extra


def run_live_ci_check(root: Path) -> Dict[str, Any]:
    ci_script = root / REUSED_IMPLEMENTATION
    completed = subprocess.run(
        [sys.executable, str(ci_script), "--root", str(root)],
        cwd=str(root),
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "ok": completed.returncode == 0,
        "exit_code": completed.returncode,
        "stdout_tail": completed.stdout.strip()[-2000:],
        "stderr_tail": completed.stderr.strip()[-2000:],
    }


def build_report(
    parsed_input: Dict[str, Any],
    *,
    root: Path,
    live: bool,
) -> Dict[str, Any]:
    ci_check_path = root / REUSED_IMPLEMENTATION
    configured_checks = extract_configured_checks(ci_check_path)
    composition, composition_ok = compare_composition(
        parsed_input["expected_checks"], configured_checks
    )

    report: Dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "experiment_id": EXPERIMENT_ID,
        "reused_implementation": REUSED_IMPLEMENTATION,
        "mode": "live" if live else "composition",
        "configured_checks": configured_checks,
        "expected_checks": parsed_input["expected_checks"],
        "composition": composition,
        "metrics": {
            "passed_check_count": composition["passed_check_count"],
            "failed_check_count": composition["failed_check_count"],
            "configured_check_count": composition["configured_check_count"],
        },
        "valid": composition_ok,
        "limitation": LIMITATION,
    }

    if live:
        live_result = run_live_ci_check(root)
        report["live_run"] = live_result
        report["valid"] = composition_ok and live_result["ok"]
        if not live_result["ok"]:
            report["metrics"]["failed_check_count"] = max(
                report["metrics"]["failed_check_count"], 1
            )

    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    try:
        raw_data = json.loads(args.input.read_text(encoding="utf-8"))
        parsed = validate_input(raw_data)
        report = build_report(parsed, root=root, live=args.live)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(pretty_json(report), encoding="utf-8")
    except json.JSONDecodeError as exc:
        print(f"[ERROR E_INVALID_JSON] 输入不是有效 JSON：{exc.msg}", file=sys.stderr)
        return 1
    except InputError as exc:
        print(f"[ERROR {exc.code}] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"[ERROR E_IO] 文件操作失败：{exc}", file=sys.stderr)
        return 1

    if not report["valid"]:
        print(
            f"[ERROR E_COMPOSITION_MISMATCH] 期望门禁与 {REUSED_IMPLEMENTATION} 配置不一致。",
            file=sys.stderr,
        )
        return 1

    print(f"[OK] {EXPERIMENT_ID} report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
