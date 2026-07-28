#!/usr/bin/env python3
"""Build zh/en release-profile HTML+PDF into releases/<version>-rc/."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_book import build  # noqa: E402
from release_book_assets import asset_filenames, build_output_names, rc_paths  # noqa: E402


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("version", help="例如 v0.9.005")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--format",
        choices=("html", "pdf", "all"),
        default="all",
        help="构建格式；默认 html+pdf 四类资产",
    )
    parser.add_argument("--generated-at", help="固定 ISO-8601 时间（测试用）")
    parser.add_argument("--skip-audit", action="store_true", help="跳过 content-audit（仅诊断）")
    return parser.parse_args(argv)


def run_audit(python: str, root: Path, html: Path, pdf: Optional[Path]) -> None:
    cmd = [python, str(root / "scripts/audit_release_content.py"), "--html", str(html)]
    if pdf and pdf.is_file():
        cmd.extend(["--pdf", str(pdf)])
    completed = subprocess.run(cmd, cwd=str(root), text=True)
    if completed.returncode:
        raise RuntimeError(f"content audit 失败：{html.name}")


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    version = args.version
    if not version.startswith("v"):
        print("[ERROR] version 必须以 v 开头", file=sys.stderr)
        return 2

    generated_at = args.generated_at or now_utc()
    targets = rc_paths(root, version)
    rc_dir = targets["zh_html"].parent
    rc_dir.mkdir(parents=True, exist_ok=True)

    manifest_assets: dict[str, dict[str, object]] = {}
    python = sys.executable

    for locale in ("zh", "en"):
        html_name, pdf_name = build_output_names(locale)
        with tempfile.TemporaryDirectory(prefix=f"release-{locale}-") as temp:
            work = Path(temp) / "out"
            book_manifest = build(
                root,
                work,
                generated_at,
                args.format,
                profile="release",
                locale=locale,
            )
            built_html = work / html_name
            if not built_html.is_file():
                raise RuntimeError(f"缺少 {locale} HTML：{built_html}")
            zh_key = "zh_html" if locale == "zh" else "en_html"
            html_target = targets[zh_key]
            shutil.copy2(built_html, html_target)
            outputs_by_path = {item["path"]: item["sha256"] for item in book_manifest["outputs"]}
            manifest_assets[locale] = {
                "html": html_target.name,
                "html_sha256": outputs_by_path[html_name],
            }

            pdf_target_key = "zh_pdf" if locale == "zh" else "en_pdf"
            pdf_target = targets[pdf_target_key]
            if args.format in {"pdf", "all"}:
                built_pdf = work / pdf_name
                if not built_pdf.is_file():
                    raise RuntimeError(f"缺少 {locale} PDF：{built_pdf}")
                shutil.copy2(built_pdf, pdf_target)
                manifest_assets[locale]["pdf"] = pdf_target.name
                manifest_assets[locale]["pdf_sha256"] = outputs_by_path[pdf_name]
                if not args.skip_audit:
                    run_audit(python, root, html_target, pdf_target)
            elif not args.skip_audit:
                run_audit(python, root, html_target, None)

    audit_report = {
        "schema_version": "1.0.0",
        "version": version,
        "ok": True,
        "assets": asset_filenames(version),
        "generated_at": generated_at,
        "locales": manifest_assets,
    }
    (rc_dir / "content-audit.json").write_text(
        json.dumps(audit_report, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    for path in targets.values():
        if path.suffix == ".html" or (args.format in {"pdf", "all"} and path.suffix == ".pdf"):
            if path.is_file():
                print(f"[OK] {path.relative_to(root)} ({path.stat().st_size} bytes)")

    md_cmd = [python, str(root / "scripts/build_release_markdown.py"), version]
    completed = subprocess.run(md_cmd, cwd=str(root), text=True)
    if completed.returncode:
        raise RuntimeError("build_release_markdown.py 失败")
    for key in ("zh_md", "en_md"):
        path = targets[key]
        if path.is_file():
            print(f"[OK] {path.relative_to(root)} ({path.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
