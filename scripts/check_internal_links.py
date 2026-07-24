#!/usr/bin/env python3
"""Check repository-local Markdown and HTML links without network access."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.parse import unquote, urlsplit


MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\((?P<target><[^>]+>|[^)\s]+)(?:\s+[\"'][^\"']*[\"'])?\)")
FENCE_RE = re.compile(r"^\s*(```|~~~)")
DEFAULT_SCOPES = (
    "README.md",
    "book",
    "docs",
    "feedback",
    "planning",
    "progress",
    "releases",
    "site",
    "writer-chats",
)
SKIP_DIRS = {".git", "__pycache__", ".artifacts", ".tmp"}


@dataclass(frozen=True)
class LinkIssue:
    source: str
    line: int
    target: str
    message: str
    fix: str

    def render(self) -> str:
        return f"[ERROR] {self.source}:{self.line} → {self.target} — {self.message} 修复：{self.fix}"


class HTMLLinks(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[Tuple[int, str]] = []
        self.ids: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(str(values["id"]))
        target = None
        if tag in {"a", "link"}:
            target = values.get("href")
        elif tag in {"script", "img", "source"}:
            target = values.get("src")
        if target:
            self.links.append((self.getpos()[0], str(target)))


def markdown_links(path: Path) -> List[Tuple[int, str]]:
    links: List[Tuple[int, str]] = []
    fenced = False
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        for match in MARKDOWN_LINK_RE.finditer(line):
            target = match.group("target")
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            links.append((line_number, target))
    return links


def html_links(path: Path) -> Tuple[List[Tuple[int, str]], Set[str]]:
    parser = HTMLLinks()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser.links, parser.ids


def discover_files(root: Path, scopes: Sequence[str]) -> List[Path]:
    files: Set[Path] = set()
    for scope in scopes:
        target = (root / scope).resolve()
        if not target.exists():
            continue
        if target.is_file() and target.suffix.lower() in {".md", ".html", ".htm"}:
            files.add(target)
            continue
        if target.is_dir():
            for path in target.rglob("*"):
                relative_parts = path.relative_to(target).parts
                if any(part in SKIP_DIRS for part in relative_parts):
                    continue
                if path.is_file() and path.suffix.lower() in {".md", ".html", ".htm"}:
                    # Packaged book HTML under releases/*-rc/ is a release asset,
                    # not a navigable repo page; skip relative-link audits.
                    if (
                        "releases" in path.relative_to(root).parts
                        and path.name.startswith("aidlc-book-")
                        and path.name.endswith(("-book.html", "-book.htm"))
                    ):
                        continue
                    files.add(path.resolve())
    return sorted(files)


def check_links(root: Path, scopes: Sequence[str]) -> Dict[str, object]:
    root = root.resolve()
    files = discover_files(root, scopes)
    html_id_cache: Dict[Path, Set[str]] = {}
    issues: List[LinkIssue] = []
    external_count = 0
    checked_count = 0

    for source in files:
        if source.suffix.lower() in {".html", ".htm"}:
            links, ids = html_links(source)
            html_id_cache[source] = ids
        else:
            links = markdown_links(source)
        for line_number, raw_target in links:
            target = raw_target.strip()
            if not target:
                continue
            parts = urlsplit(target)
            if parts.scheme or target.startswith("//"):
                external_count += 1
                continue
            checked_count += 1
            if parts.path:
                destination = (source.parent / unquote(parts.path)).resolve()
                try:
                    destination.relative_to(root)
                except ValueError:
                    issues.append(
                        LinkIssue(
                            str(source.relative_to(root)),
                            line_number,
                            target,
                            "链接越出仓库根目录。",
                            "改用仓库内相对路径。",
                        )
                    )
                    continue
            else:
                destination = source
            if not destination.exists():
                issues.append(
                    LinkIssue(
                        str(source.relative_to(root)),
                        line_number,
                        target,
                        "目标不存在。",
                        "创建目标或修正相对路径；未来产物不要渲染成链接。",
                    )
                )
                continue
            if parts.fragment and destination.suffix.lower() in {".html", ".htm"}:
                ids = html_id_cache.get(destination)
                if ids is None:
                    _, ids = html_links(destination)
                    html_id_cache[destination] = ids
                if unquote(parts.fragment) not in ids:
                    issues.append(
                        LinkIssue(
                            str(source.relative_to(root)),
                            line_number,
                            target,
                            "HTML fragment 不存在。",
                            "修正 fragment 或为目标元素添加稳定 id。",
                        )
                    )

    return {
        "root": str(root),
        "files": len(files),
        "checked_internal_links": checked_count,
        "external_links_not_fetched": external_count,
        "issues": [asdict(issue) for issue in issues],
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="检查 Markdown/HTML 仓库内链接。")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scope", action="append", dest="scopes", help="相对根目录的文件或目录；可重复。")
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告。")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    report = check_links(args.root, args.scopes or DEFAULT_SCOPES)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for issue in report["issues"]:
            print(
                LinkIssue(
                    issue["source"], issue["line"], issue["target"], issue["message"], issue["fix"]
                ).render()
            )
        print(
            "[INFO] link summary: "
            f"files={report['files']}, internal={report['checked_internal_links']}, "
            f"external-not-fetched={report['external_links_not_fetched']}, "
            f"errors={len(report['issues'])}"
        )
    return 1 if report["issues"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
