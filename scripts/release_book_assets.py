#!/usr/bin/env python3
"""Canonical bilingual Release book asset names and RC paths."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Tuple


def asset_filenames(version: str) -> Dict[str, str]:
    return {
        "zh_html": f"aidlc-book-{version}-book.html",
        "en_html": f"aidlc-book-{version}-en-book.html",
        "zh_pdf": f"aidlc-book-{version}.pdf",
        "en_pdf": f"aidlc-book-{version}-en.pdf",
        "zh_md": f"aidlc-book-{version}-book.md",
        "en_md": f"aidlc-book-{version}-en-book.md",
    }


def markdown_filenames(version: str) -> Dict[str, str]:
    names = asset_filenames(version)
    return {"zh_md": names["zh_md"], "en_md": names["en_md"]}


def bilingual_required_filenames(version: str) -> list[str]:
    return list(asset_filenames(version).values())


def rc_paths(root: Path, version: str) -> Dict[str, Path]:
    rc = root / f"releases/{version}-rc"
    return {key: rc / name for key, name in asset_filenames(version).items()}


def locale_for_key(key: str) -> str:
    return "zh" if key.startswith("zh_") else "en"


def build_output_names(locale: str) -> Tuple[str, str]:
    if locale == "zh":
        return "deep-understanding-ai-dlc.html", "deep-understanding-ai-dlc.pdf"
    return "deep-understanding-ai-dlc-en.html", "deep-understanding-ai-dlc-en.pdf"
