#!/usr/bin/env python3
"""Run the same Must checks locally and in GitHub Pull Requests."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="运行 AI-DLC Book 核心 CI 门禁。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--budget-seconds", type=float, default=60.0)
    parser.add_argument("--pr-body-file", type=Path)
    parser.add_argument("--report", type=Path, help="可选 JSON 报告路径。")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    python = sys.executable
    checks: List[tuple[str, List[str]]] = [
        ("facts", [python, "scripts/validate_project.py"]),
        ("continuity", [python, "scripts/validate_feedback.py"]),
        ("github-config", [python, "scripts/validate_github_config.py"]),
        ("tests", [python, "-m", "unittest", "discover", "-s", "tests"]),
        ("verified-experiments", [python, "scripts/run_verified_experiments.py"]),
        (
            "generation-dry-run",
            [python, "scripts/generate_progress.py", "--dry-run", "--actor", "ci-check"],
        ),
        ("internal-links", [python, "scripts/check_internal_links.py"]),
    ]
    if args.pr_body_file:
        checks.append(
            (
                "pr-metadata",
                [python, "scripts/validate_pr_metadata.py", "--body-file", str(args.pr_body_file), "--required"],
            )
        )
    elif os.environ.get("GITHUB_EVENT_PATH"):
        checks.append(("pr-metadata", [python, "scripts/validate_pr_metadata.py"]))

    started = time.monotonic()
    results: List[Dict[str, object]] = []
    failed = False
    for name, command in checks:
        check_started = time.monotonic()
        completed = subprocess.run(command, cwd=str(root), text=True)
        duration = round(time.monotonic() - check_started, 3)
        results.append(
            {"name": name, "command": command, "returncode": completed.returncode, "seconds": duration}
        )
        if completed.returncode:
            failed = True
            print(
                f"[ERROR] CI check failed: {name} (exit {completed.returncode}). "
                "修复上方首个具体错误后在本地重跑。",
                file=sys.stderr,
            )

    elapsed = round(time.monotonic() - started, 3)
    budget_exceeded = elapsed > args.budget_seconds
    if budget_exceeded:
        failed = True
        print(
            f"[ERROR] core checks used {elapsed}s, budget is {args.budget_seconds}s. "
            "修复：定位最慢阶段，避免网络和重型 PDF 构建进入核心门禁。",
            file=sys.stderr,
        )
    report = {
        "schema_version": "1.0.0",
        "elapsed_seconds": elapsed,
        "budget_seconds": args.budget_seconds,
        "budget_exceeded": budget_exceeded,
        "ok": not failed,
        "checks": results,
    }
    if args.report:
        target = args.report if args.report.is_absolute() else root / args.report
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[INFO] CI summary: checks={len(checks)}, seconds={elapsed}, budget={args.budget_seconds}, ok={not failed}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
