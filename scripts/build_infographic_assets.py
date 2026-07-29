#!/usr/bin/env python3
"""Build English infographic PNGs and optional Release zip from manifest + chapter SVGs."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Sequence

from prepare_pages import file_sha256

MANIFEST = Path("assets/infographics/en/manifest.json")
SVG_BY_CHAPTER = {
    "CH-01": Path("book/images/fig0-1.svg"),
    "CH-02": Path("book/images/ch02-human-judgment-gate.svg"),
    "CH-03": Path("book/images/ch03-intent-to-bolt.svg"),
    "CH-04": Path("book/images/ch04-memory-bank-stack.svg"),
    "CH-05": Path("book/images/ch05-bolt-selection-matrix.svg"),
    "CH-06": Path("book/images/ch06-exsecutio-loop.svg"),
    "CH-07": Path("book/images/ch07-verification-evidence-chain.svg"),
    "CH-08": Path("book/images/ch08-operations-loop.svg"),
    "CH-09": Path("book/images/ch09-risk-ceremony-matrix.svg"),
    "CH-10": Path("book/images/ch10-org-operating-system.svg"),
}


def load_manifest(root: Path) -> dict:
    path = root / MANIFEST
    return json.loads(path.read_text(encoding="utf-8"))


def export_svg(svg: Path, png: Path, width: int) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["rsvg-convert", "-w", str(width), "-o", str(png), str(svg)],
        check=True,
        capture_output=True,
    )


def build_pngs(root: Path, width: int, force: bool) -> List[Dict[str, object]]:
    manifest = load_manifest(root)
    out_dir = root / "assets/infographics/en"
    entries: List[Dict[str, object]] = []
    for item in manifest["items"]:
        target = out_dir / item["file"]
        if item["id"] == "cover":
            if not target.is_file():
                raise RuntimeError(f"缺少封面：{target}")
        else:
            chapter = item.get("chapter")
            svg = SVG_BY_CHAPTER.get(str(chapter))
            if svg is None or not (root / svg).is_file():
                raise RuntimeError(f"无法解析章节 SVG：{chapter}")
            if force or not target.is_file():
                export_svg(root / svg, target, width)
        if not target.is_file() or target.stat().st_size < 5000:
            raise RuntimeError(f"信息图无效或过短：{target}")
        entries.append(
            {
                "id": item["id"],
                "file": item["file"],
                "title": item["title"],
                "chapter": item.get("chapter"),
                "sha256": file_sha256(target),
                "bytes": target.stat().st_size,
            }
        )
    return entries


def zip_infographics(root: Path, version: str, output: Path) -> Dict[str, object]:
    manifest = load_manifest(root)
    out_dir = root / "assets/infographics/en"
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
        bundle.write(out_dir / "manifest.json", "manifest.json")
        for item in manifest["items"]:
            path = out_dir / item["file"]
            bundle.write(path, item["file"])
    return {
        "file": output.name,
        "sha256": file_sha256(output),
        "bytes": output.stat().st_size,
    }


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--width", type=int, default=1920)
    parser.add_argument("--force", action="store_true", help="重新从 SVG 导出章节 PNG")
    parser.add_argument("--zip-version", help="例如 v0.9.007，写入 releases/<ver>-rc/")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    entries = build_pngs(root, args.width, args.force)
    if args.zip_version:
        version = args.zip_version
        rc = root / f"releases/{version}-rc"
        rc.mkdir(parents=True, exist_ok=True)
        zip_path = rc / f"aidlc-book-{version}-en-infographics.zip"
        info = zip_infographics(root, version, zip_path)
        print(f"[INFO] Infographic zip: {zip_path} ({info['bytes']} bytes)")
    print(f"[INFO] Infographic PNGs: count={len(entries)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
