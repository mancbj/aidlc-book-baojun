#!/usr/bin/env python3
"""Validate that a Pull Request body links work to evidence and acceptance."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Optional, Sequence


TASK_ID_RE = re.compile(r"\bD(?:0[1-9]|1[0-4])-T\d{2}\b")
REQUIRED_SECTIONS = ("## 测试与构建", "## 验收", "## 产物")


def body_from_event(path: Path) -> Optional[str]:
    try:
        event = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"无法读取 GitHub event JSON: {exc}") from exc
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        return None
    body = pull_request.get("body")
    return body if isinstance(body, str) else ""


def validate_body(body: str) -> list[str]:
    issues = []
    if not TASK_ID_RE.search(body):
        issues.append("缺少有效 Task ID（D01-T01 至 D14-TNN）。")
    for section in REQUIRED_SECTIONS:
        if section not in body:
            issues.append(f"缺少段落：{section}")
    if "- [x]" not in body.lower():
        issues.append("验收/测试清单没有任何已确认项（- [x]）。")
    if "<!-- DNN-TNN" in body or "粘贴关键结果" in body:
        issues.append("PR 模板占位提示尚未替换。")
    return issues


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验 Pull Request 正文元数据。")
    parser.add_argument("--body-file", type=Path, help="本地 PR body 文件。")
    parser.add_argument("--event-file", type=Path, help="GitHub event JSON；默认 GITHUB_EVENT_PATH。")
    parser.add_argument("--required", action="store_true", help="没有 PR 上下文时也返回失败。")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    body: Optional[str] = None
    source = ""
    try:
        if args.body_file:
            body = args.body_file.read_text(encoding="utf-8")
            source = str(args.body_file)
        else:
            event_path = args.event_file or (
                Path(os.environ["GITHUB_EVENT_PATH"]) if os.environ.get("GITHUB_EVENT_PATH") else None
            )
            if event_path and event_path.exists():
                body = body_from_event(event_path)
                source = str(event_path)
    except (OSError, ValueError) as exc:
        print(f"[ERROR] {exc} 修复：提供有效 UTF-8 PR body 或 event JSON。", file=sys.stderr)
        return 1

    if body is None:
        if args.required:
            print("[ERROR] 没有 Pull Request body。修复：传入 --body-file 或 --event-file。", file=sys.stderr)
            return 1
        print("[INFO] no Pull Request context; metadata check skipped")
        return 0

    issues = validate_body(body)
    for issue in issues:
        print(f"[ERROR] {source}: {issue} 修复：补全 .github/pull_request_template.md 对应内容。")
    if issues:
        return 1
    print(f"[INFO] Pull Request metadata passed: source={source}, task_ids={len(TASK_ID_RE.findall(body))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
