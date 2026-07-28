#!/usr/bin/env python3
"""Prepare reproducible HTML release assets and an honest PDF status."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Sequence

from prepare_pages import GENERATED_MARKER, build_pages, file_sha256, now_utc, source_id
from release_book_assets import asset_filenames, rc_paths


VERSION_RE = re.compile(r"^v\d+\.\d+(?:\.\d+)?(?:-[0-9A-Za-z.-]+)?$")


def validate_pdf(path: Path) -> None:
    """Reject renamed placeholders before a PDF can enter a release candidate."""
    if not path.is_file() or path.suffix.lower() != ".pdf":
        raise RuntimeError("--pdf 必须指向现有 .pdf 文件；不允许伪造 PDF。")
    if path.stat().st_size < 12:
        raise RuntimeError("--pdf 文件过小，不是可验证的 PDF。")
    with path.open("rb") as handle:
        header = handle.read(8)
        handle.seek(max(0, path.stat().st_size - 4096))
        trailer = handle.read()
    if not header.startswith(b"%PDF-") or b"%%EOF" not in trailer:
        raise RuntimeError("--pdf 缺少 PDF header/EOF 结构；拒绝把占位文件作为 PDF 发布。")


def stage_book_assets(
    staged: Path,
    root: Path,
    version: str,
    pdf_arg: Optional[Path],
    book_html_arg: Optional[Path],
) -> tuple[Dict[str, object], Dict[str, object], Dict[str, object]]:
    """Copy zh/en HTML and PDF into the candidate when present in RC or via explicit args."""
    names = asset_filenames(version)
    discovered = rc_paths(root, version)
    overrides: Dict[str, Optional[Path]] = {
        "zh_html": book_html_arg,
        "zh_pdf": pdf_arg,
        "en_html": None,
        "en_pdf": None,
    }
    book_assets: Dict[str, Dict[str, object]] = {}
    for key, filename in names.items():
        explicit = overrides.get(key)
        if explicit is not None:
            src = explicit if explicit.is_absolute() else root / explicit
        else:
            src = discovered[key]
        if not src.is_file():
            continue
        if key.endswith("_pdf"):
            validate_pdf(src)
        elif key.endswith("_md"):
            validate_book_markdown(src)
        else:
            validate_book_html(src)
        target = staged / filename
        shutil.copy2(src, target)
        entry: Dict[str, object] = {
            "status": "included",
            "file": target.name,
            "sha256": file_sha256(target),
            "bytes": target.stat().st_size,
            "locale": "zh" if key.startswith("zh_") else "en",
            "kind": "markdown" if key.endswith("_md") else ("pdf" if key.endswith("_pdf") else "html"),
        }
        book_assets[key] = entry

    zh_html = book_assets.get("zh_html")
    en_html = book_assets.get("en_html")
    zh_pdf = book_assets.get("zh_pdf")
    en_pdf = book_assets.get("en_pdf")

    book_html_status: Dict[str, object]
    if zh_html:
        book_html_status = dict(zh_html)
    elif en_html:
        book_html_status = dict(en_html)
    else:
        book_html_status = {
            "status": "skipped",
            "reason": "未在 RC 目录或 --book-html 中找到书稿 HTML。",
            "retry": "运行 scripts/stage_release_rc_assets.py 或提供 --book-html。",
        }

    pdf_status: Dict[str, object]
    if zh_pdf:
        pdf_status = dict(zh_pdf)
    elif en_pdf:
        pdf_status = dict(en_pdf)
    else:
        pdf_status = {
            "status": "skipped",
            "reason": "未通过 --pdf 或 RC 目录提供可验证 PDF。",
            "retry": "运行 scripts/stage_release_rc_assets.py 或提供 --pdf。",
        }

    return book_assets, book_html_status, pdf_status


def validate_book_markdown(path: Path) -> None:
    if not path.is_file() or path.suffix.lower() != ".md":
        raise RuntimeError("书稿 Markdown 必须是 .md 文件。")
    if path.stat().st_size < 5000:
        raise RuntimeError("书稿 Markdown 过短。")
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "AI-DLC" not in text:
        raise RuntimeError("书稿 Markdown 缺少 AI-DLC 标识。")


def validate_book_html(path: Path) -> None:
    """Require a non-empty HTML book candidate before packaging it."""
    if not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
        raise RuntimeError("--book-html 必须指向现有 .html 文件。")
    if path.stat().st_size < 1024:
        raise RuntimeError("--book-html 文件过小，不是可发布书稿 HTML。")
    text = path.read_text(encoding="utf-8", errors="ignore")
    if "<html" not in text.lower() or "AI-DLC" not in text:
        raise RuntimeError("--book-html 缺少可识别的书稿 HTML 结构。")


def zip_timestamp(value: str) -> tuple[int, int, int, int, int, int]:
    """Use the declared build time instead of filesystem mtimes in release zips."""
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise RuntimeError("--generated-at 必须是带时区的 ISO-8601 时间") from exc
    if parsed.tzinfo is None:
        raise RuntimeError("--generated-at 必须包含时区")
    parsed = parsed.astimezone(timezone.utc)
    if parsed.year < 1980:
        raise RuntimeError("ZIP 生成时间不能早于 1980 年")
    return (parsed.year, parsed.month, parsed.day, parsed.hour, parsed.minute, parsed.second)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="准备 GitHub Release 候选资产。")
    parser.add_argument("version", help="例如 v0.1、v0.1.0 或 v0.1-rc.1")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path)
    parser.add_argument("--pdf", type=Path, help="已由独立可信构建生成的 PDF；不存在则明确跳过。")
    parser.add_argument(
        "--book-html",
        type=Path,
        help="已由 scripts/build_book.sh 生成的书稿 HTML；不存在则明确跳过。",
    )
    parser.add_argument("--readiness", type=Path, help="status=ready 且来源一致的 readiness JSON。")
    parser.add_argument("--release-notes", type=Path, help="由事实与 readiness 生成的 Release Notes。")
    parser.add_argument("--generated-at")
    parser.add_argument("--commit-sha")
    return parser.parse_args(argv)


def build_release(args: argparse.Namespace) -> Dict[str, object]:
    if not VERSION_RE.fullmatch(args.version):
        raise RuntimeError("版本必须符合 vMAJOR.MINOR[.PATCH][-suffix]")
    root = args.root.resolve()
    readiness: Optional[Dict[str, object]] = None
    readiness_arg = getattr(args, "readiness", None)
    if readiness_arg:
        readiness_path = readiness_arg if readiness_arg.is_absolute() else root / readiness_arg
        readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
        if readiness.get("status") != "ready":
            raise RuntimeError("readiness 不是 ready，拒绝构造可发布候选。")
        if readiness.get("source_id") != source_id(root):
            raise RuntimeError("readiness source 与当前事实来源不一致，拒绝混合候选。")
    output = (
        args.output.resolve()
        if args.output
        else (root / ".artifacts" / "release" / args.version).resolve()
    )
    if output.exists() and not (output / GENERATED_MARKER).is_file():
        raise RuntimeError(f"拒绝替换没有 {GENERATED_MARKER} 标记的目录：{output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    staged = Path(tempfile.mkdtemp(prefix=f".{args.version}-", dir=str(output.parent)))
    try:
        (staged / GENERATED_MARKER).write_text("generated by scripts/prepare_release.py\n", encoding="utf-8")
        timestamp = args.generated_at or now_utc()
        archive_time = zip_timestamp(timestamp)
        pages_root = staged / "pages-root"
        pages_manifest = build_pages(
            root,
            pages_root,
            generated_at=timestamp,
            commit_sha=args.commit_sha,
            workflow_run=os.environ.get("GITHUB_RUN_ID", "local"),
        )
        archive = staged / f"aidlc-book-{args.version}-html.zip"
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as bundle:
            for path in sorted(pages_root.rglob("*")):
                if path.is_file() and path.name != GENERATED_MARKER:
                    relative = (Path("aidlc-book") / path.relative_to(pages_root)).as_posix()
                    info = zipfile.ZipInfo(relative, date_time=archive_time)
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o100644 << 16
                    bundle.writestr(info, path.read_bytes())

        book_html_arg = getattr(args, "book_html", None)
        book_assets, book_html_status, pdf_status = stage_book_assets(
            staged,
            root,
            args.version,
            args.pdf,
            book_html_arg,
        )

        commit = args.commit_sha or os.environ.get("GITHUB_SHA") or source_id(root)
        notes_arg = getattr(args, "release_notes", None)
        if notes_arg:
            notes_path = notes_arg if notes_arg.is_absolute() else root / notes_arg
            notes = notes_path.read_text(encoding="utf-8")
            if not notes.strip():
                raise RuntimeError("--release-notes 不能为空。")
        else:
            notes = f"""# {args.version} Release Candidate

- Source: `{source_id(root)}`
- Commit: `{commit}`
- Generated: `{timestamp}`
- HTML zip: `{archive.name}`
- Book HTML: `{book_html_status['status']}`
- PDF: `{pdf_status['status']}`

本候选由仓库事实、测试、书稿构建和静态页面生成。正式发布前仍需检查已知缺口、反馈入口和人工门禁。
"""
        (staged / "release-notes.md").write_text(notes, encoding="utf-8")
        if notes_arg:
            notes_path = notes_arg if notes_arg.is_absolute() else root / notes_arg
            title_sidecar = notes_path.with_name("release-title.txt")
            if title_sidecar.is_file():
                shutil.copy2(title_sidecar, staged / "release-title.txt")
        manifest = {
            "schema_version": "1.0.0",
            "version": args.version,
            "source_id": source_id(root),
            "commit_sha": commit,
            "generated_at": timestamp,
            "html": {
                "status": "included",
                "file": archive.name,
                "sha256": file_sha256(archive),
                "bytes": archive.stat().st_size,
                "pages_file_count": pages_manifest["file_count"],
            },
            "book_html": book_html_status,
            "book_assets": book_assets,
            "pdf": pdf_status,
            "release_notes": "release-notes.md",
            "readiness": {
                "status": readiness.get("status"),
                "source_id": readiness.get("source_id"),
                "blockers": readiness.get("summary", {}).get("blockers"),
            }
            if readiness
            else {"status": "not-supplied", "mode": "development-candidate"},
        }
        (staged / "release-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        shutil.rmtree(pages_root)
        if output.exists():
            shutil.rmtree(output)
        shutil.move(str(staged), str(output))
        return manifest
    except Exception:
        if staged.exists():
            shutil.rmtree(staged)
        raise


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    try:
        manifest = build_release(args)
    except (OSError, RuntimeError, json.JSONDecodeError, zipfile.BadZipFile) as exc:
        print(f"[ERROR] Release preparation failed: {exc}")
        return 1
    output = args.output or args.root / ".artifacts" / "release" / args.version
    print(
        f"[INFO] Release candidate passed: version={args.version}, output={output}, "
        f"html={manifest['html']['status']}, pdf={manifest['pdf']['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
