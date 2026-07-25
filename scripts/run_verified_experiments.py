#!/usr/bin/env python3
"""Validate and run every verified experiment that publishes a contract test path."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


PATH_FIELDS = (
    "repository_path",
    "readme_path",
    "sample_input",
    "sample_output",
    "test_path",
)
CONTRACT_TRIAGES = {"SHIP", "ALREADY", "KEEP-EXT"}


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--check-only", action="store_true", help="只检查工件，不执行测试。")
    return parser.parse_args(argv)


def verified_contract_experiments(root: Path) -> List[Dict[str, object]]:
    """Return verified experiments that declare the five contract artifact paths.

    SHIP remains the main verified set. ALREADY / KEEP-EXT may also enter CI once
    they publish repository_path/readme/sample/test paths without changing triage.
    """
    document = json.loads((root / "progress/experiments.json").read_text(encoding="utf-8"))
    selected: List[Dict[str, object]] = []
    for item in document["experiments"]:
        if item.get("status") != "verified":
            continue
        if item.get("triage") not in CONTRACT_TRIAGES:
            continue
        if all(isinstance(item.get(field), str) and item.get(field).strip() for field in PATH_FIELDS):
            selected.append(item)
    return selected


def verified_ship_experiments(root: Path) -> List[Dict[str, object]]:
    """Backward-compatible alias used by existing tests."""
    return [
        item
        for item in verified_contract_experiments(root)
        if item.get("triage") == "SHIP"
    ]


def artifact_errors(root: Path, experiment: Dict[str, object]) -> List[str]:
    errors: List[str] = []
    experiment_id = str(experiment.get("id", "unknown"))
    for field in PATH_FIELDS:
        value = experiment.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{experiment_id}: {field} 缺失")
            continue
        target = root / value
        expected = "directory" if field == "repository_path" else "file"
        exists = target.is_dir() if expected == "directory" else target.is_file()
        if not exists:
            errors.append(f"{experiment_id}: {field} 不存在或类型错误：{value}")
    return errors


def run_contract_test(root: Path, experiment: Dict[str, object]) -> Tuple[int, str]:
    test_path = root / str(experiment["test_path"])
    completed = subprocess.run(
        [sys.executable, str(test_path)],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
        timeout=30,
    )
    diagnostics = "\n".join(
        part.strip() for part in (completed.stdout, completed.stderr) if part.strip()
    )
    return completed.returncode, diagnostics


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    try:
        experiments = verified_contract_experiments(root)
    except (OSError, KeyError, json.JSONDecodeError) as exc:
        print(f"[ERROR] 无法读取实验事实源：{exc}", file=sys.stderr)
        return 1

    if not experiments:
        print("[ERROR] 没有带合同路径的 verified 实验；发布证据门禁拒绝空跑。", file=sys.stderr)
        return 1

    failed = False
    for experiment in experiments:
        experiment_id = str(experiment["id"])
        errors = artifact_errors(root, experiment)
        if errors:
            failed = True
            for error in errors:
                print(f"[ERROR] {error}", file=sys.stderr)
            continue
        if args.check_only:
            print(f"[OK] {experiment_id}: artifacts")
            continue
        try:
            returncode, diagnostics = run_contract_test(root, experiment)
        except subprocess.TimeoutExpired:
            failed = True
            print(f"[ERROR] {experiment_id}: contract test 超过 30 秒", file=sys.stderr)
            continue
        if returncode:
            failed = True
            print(f"[ERROR] {experiment_id}: contract test exit={returncode}", file=sys.stderr)
            if diagnostics:
                print(diagnostics, file=sys.stderr)
        else:
            print(f"[OK] {experiment_id}: contract test")

    print(
        f"[INFO] verified experiment summary: total={len(experiments)}, ok={not failed}"
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
