#!/usr/bin/env python3
"""Fail if a release HTML/PDF still contains authoring or production meta."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence


FORBIDDEN_PATTERNS = (
    ("Writing Sprint Card", re.compile(r"Writing\s+Sprint\s+Card")),
    ("Draft Completeness", re.compile(r"Draft\s+Completeness")),
    ("Status Source", re.compile(r"Status\s+Source")),
    ("Chapter ID", re.compile(r"Chapter\s+ID")),
    ("Review Notes", re.compile(r"Review\s+Notes\s+for\s+D\d+-T\d+")),
    ("D01 acceptance", re.compile(r"D01-T0[13]\s")),
    ("question audit", re.compile(r"核心问题去重审计")),
    ("source ledger", re.compile(r"来源记录")),
    ("v0.1 boundary meta", re.compile(r"v0\.1\s*边界")),
    ("gate checklist item", re.compile(r"核心问题只有一个")),
    ("waiting for review meta", re.compile(r"等待\s*D\d+-T\d+\s*审校")),
)


def extract_pdf_text(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(f"pdftotext 失败：{result.stderr or result.stdout}")
    return result.stdout


def scan_text(label: str, text: str) -> List[Dict[str, object]]:
    findings: List[Dict[str, object]] = []
    for name, pattern in FORBIDDEN_PATTERNS:
        matches = list(pattern.finditer(text))
        if matches:
            sample = matches[0].group(0)
            findings.append(
                {
                    "source": label,
                    "marker": name,
                    "count": len(matches),
                    "sample": sample,
                }
            )
    # Standalone Metadata headings are authoring scaffold.
    metadata_hits = len(re.findall(r"(?m)^(?:#+\s*)?Metadata\s*$", text)) + text.count("> Metadata")
    # Pandoc TOC often renders as bare "Metadata" lines; count table-ish neighbors.
    if "Writing Sprint Card" not in text and re.search(r"(?m)^\s*Metadata\s*$", text):
        findings.append(
            {
                "source": label,
                "marker": "Metadata heading",
                "count": len(re.findall(r"(?m)^\s*Metadata\s*$", text)),
                "sample": "Metadata",
            }
        )
    elif "Chapter ID" in text or "Draft Completeness" in text:
        # Already covered by specific markers.
        pass
    elif metadata_hits and ("Status Source" in text or "Draft Completeness" in text):
        findings.append(
            {
                "source": label,
                "marker": "Metadata block",
                "count": metadata_hits,
                "sample": "Metadata",
            }
        )
    return findings


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, help="release HTML candidate")
    parser.add_argument("--pdf", type=Path, help="release PDF candidate")
    parser.add_argument("--pdf-text", type=Path, help="pre-extracted PDF text")
    parser.add_argument("--json-out", type=Path, help="optional findings JSON path")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if not args.html and not args.pdf and not args.pdf_text:
        print("[ERROR] 至少提供 --html、--pdf 或 --pdf-text 之一", file=sys.stderr)
        return 2

    findings: List[Dict[str, object]] = []
    if args.html:
        if not args.html.is_file():
            print(f"[ERROR] HTML 不存在：{args.html}", file=sys.stderr)
            return 2
        findings.extend(scan_text("html", args.html.read_text(encoding="utf-8", errors="replace")))
    if args.pdf_text:
        findings.extend(scan_text("pdf-text", args.pdf_text.read_text(encoding="utf-8", errors="replace")))
    elif args.pdf:
        if not args.pdf.is_file():
            print(f"[ERROR] PDF 不存在：{args.pdf}", file=sys.stderr)
            return 2
        findings.extend(scan_text("pdf", extract_pdf_text(args.pdf)))

    report = {
        "schema_version": "1.0.0",
        "ok": not findings,
        "findings": findings,
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if findings:
        print("[FAIL] release content still contains authoring/production meta:")
        for item in findings:
            print(f"  - {item['source']}: {item['marker']} x{item['count']} (sample={item['sample']!r})")
        return 1

    print("[OK] release content hygiene pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
