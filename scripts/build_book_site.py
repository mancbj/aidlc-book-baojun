#!/usr/bin/env python3
"""Stage Pandoc book HTML for the Carbon reader (zh/en)."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_book.py"


def en_locale_available(root: Path) -> bool:
    return (root / "book/en/build-frontmatter.md").is_file()


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "book-site" / "assets",
        help="Directory for assets/<locale>/book.html",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--generated-at", default="2026-07-27T10:00:00Z")
    return parser.parse_args(argv)


def build_locale(locale: str, output: Path, generated_at: str, root: Path) -> dict:
    staging = output / locale
    if staging.exists():
        shutil.rmtree(staging)
    build_py = root / "scripts" / "build_book.py"
    result = subprocess.run(
        [
            sys.executable,
            str(build_py),
            "--root",
            str(root),
            "--output",
            str(staging),
            "--format",
            "html",
            "--locale",
            locale,
            "--generated-at",
            generated_at,
        ],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    html_name = "deep-understanding-ai-dlc.html" if locale == "zh" else "deep-understanding-ai-dlc-en.html"
    source = staging / html_name
    target = staging / "book.html"
    target.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    manifest = json.loads((staging / "build-manifest.json").read_text(encoding="utf-8"))
    return {
        "locale": locale,
        "book_html": f"book-site/assets/{locale}/book.html",
        "sha256": manifest["outputs"][0]["sha256"],
        "generated_at": generated_at,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    output = args.output if args.output.is_absolute() else root / args.output
    output.mkdir(parents=True, exist_ok=True)
    locales_meta = []
    for locale in ("zh", "en"):
        if locale == "en" and not en_locale_available(root):
            continue
        locales_meta.append(build_locale(locale, output, args.generated_at, root))
    meta = {"schema_version": "1.0.0", "locales": locales_meta}
    meta_path = output / "build-site-manifest.json"
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Book site assets: {output}")
    print(f"[OK] Manifest: {meta_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
