#!/usr/bin/env python3
"""Concatenate canonical book sources into a single release Markdown file."""

from __future__ import annotations

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_book import get_book_locale  # noqa: E402
from release_book_assets import markdown_filenames, rc_paths  # noqa: E402


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_markdown_body(root: Path, locale: str, version: str, generated_at: str) -> str:
    book = get_book_locale(locale)
    header = (
        "---\n"
        f'title: "{book.title}"\n'
        f"locale: {locale}\n"
        f"version: {version}\n"
        f"generated_at: {generated_at}\n"
        "profile: release-markdown\n"
        "---\n"
    )
    chunks = [header]
    for relative in book.source_files:
        path = root / relative
        if not path.is_file():
            raise RuntimeError(f"缺少书稿源文件：{relative}")
        chunks.append(f"\n\n<!-- source: {relative.as_posix()} -->\n\n")
        chunks.append(path.read_text(encoding="utf-8").strip())
    body = "\n".join(chunks).strip() + "\n"
    if "AI-DLC" not in body and "AI-DLC" not in body.upper():
        raise RuntimeError("合并 Markdown 缺少 AI-DLC 标识")
    if len(body) < 5000:
        raise RuntimeError("合并 Markdown 过短，可能缺章")
    return body


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="例如 v0.9.006")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="默认 releases/<version>-rc/",
    )
    parser.add_argument("--generated-at")
    parser.add_argument("--locale", choices=("zh", "en", "both"), default="both")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    version = args.version
    generated_at = args.generated_at or now_utc()
    out_dir = args.output_dir or (root / f"releases/{version}-rc")
    out_dir.mkdir(parents=True, exist_ok=True)
    names = markdown_filenames(version)
    locales = ("zh", "en") if args.locale == "both" else (args.locale,)

    for locale in locales:
        key = "zh_md" if locale == "zh" else "en_md"
        target = out_dir / names[key]
        body = build_markdown_body(root, locale, version, generated_at)
        target.write_text(body, encoding="utf-8")
        print(f"[OK] {target.relative_to(root)} ({target.stat().st_size} bytes, sha256={sha256_text(body)[:12]}…)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
