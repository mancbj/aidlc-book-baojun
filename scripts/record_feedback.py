#!/usr/bin/env python3
"""Safely append one minimal feedback decision; default is dry-run."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

from validate_feedback import validate_feedback_document


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def atomic_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    temporary = Path(name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="记录一条匿名、最小化反馈决策。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--source", required=True, help="reader-slot / issue / review")
    parser.add_argument("--object", required=True, help="章节、实验、页面或构建对象")
    parser.add_argument("--summary", required=True, help="不含个人信息的最小证据摘要")
    parser.add_argument("--decision", choices=("pending", "accepted", "rejected", "deferred"), required=True)
    parser.add_argument("--reason", default="")
    parser.add_argument("--linked-task", default="")
    parser.add_argument("--target-cycle", default="")
    parser.add_argument("--revisit-when", default="")
    parser.add_argument("--acceptance", action="append", default=[])
    parser.add_argument("--created-at")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def build_candidate(args: argparse.Namespace) -> tuple[dict, dict]:
    root = args.root.resolve()
    path = root / "feedback/decisions.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    ids = [int(item["id"].split("-")[1]) for item in document.get("decisions", [])]
    timestamp = args.created_at or now_utc()
    feedback = {
        "id": f"FB-{(max(ids, default=0) + 1):03d}",
        "source": args.source.strip(),
        "object": args.object.strip(),
        "summary": args.summary.strip(),
        "decision": args.decision,
        "reason": args.reason.strip(),
        "linked_task": args.linked_task.strip(),
        "target_cycle": args.target_cycle.strip(),
        "revisit_when": args.revisit_when.strip(),
        "acceptance": [item.strip() for item in args.acceptance if item.strip()],
        "created_at": timestamp,
        "decided_at": None if args.decision == "pending" else timestamp,
    }
    document.setdefault("decisions", []).append(feedback)
    document["updated"] = timestamp
    issues = validate_feedback_document(document, "feedback/decisions.json")
    if issues:
        raise ValueError("\n".join(issue.render() for issue in issues))
    return document, feedback


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        document, feedback = build_candidate(args)
        if args.apply:
            atomic_json(args.root.resolve() / "feedback/decisions.json", document)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] feedback record failed: {exc}")
        return 1
    mode = "APPLIED" if args.apply else "DRY-RUN"
    print(f"[{mode}] {feedback['id']} decision={feedback['decision']} object={feedback['object']}")
    if args.apply:
        print("[NEXT] 运行 python3 scripts/generate_progress.py 记录事件并刷新驾驶舱。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
