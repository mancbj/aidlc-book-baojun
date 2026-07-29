#!/usr/bin/env python3
"""Patch README.md / README.en.md release download tables between HTML markers."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from release_book_assets import asset_filenames  # noqa: E402

BEGIN = "<!-- RELEASE-DOWNLOADS-BEGIN -->"
END = "<!-- RELEASE-DOWNLOADS-END -->"

DEFAULT_REPO = "mancbj/aidlc-book-baojun"
MARKER_PATTERN = re.compile(
    re.escape(BEGIN) + r".*?" + re.escape(END),
    re.DOTALL,
)


def download_url(repo: str, version: str, filename: str) -> str:
    return f"https://github.com/{repo}/releases/download/{version}/{filename}"


def resolve_version(repo: str, version: Optional[str]) -> str:
    if version:
        return version if version.startswith("v") else f"v{version}"
    proc = subprocess.run(
        ["gh", "release", "view", "--repo", repo, "--json", "tagName", "-q", ".tagName"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    raise RuntimeError("无法解析最新 Release 版本；请传入 --version 或配置 gh。")


def block_zh(repo: str, version: str, names: dict[str, str], *, infographics: bool) -> str:
    base = f"https://github.com/{repo}/releases"
    lines = [
        BEGIN,
        f"当前版本：**[{version}]({base}/tag/{version})** · [查看全部 Release 资产]({base}/latest)",
        "",
        "| 语言 | PDF | 单页 HTML | Markdown 全书 |",
        "| --- | --- | --- | --- |",
        "| 中文 | "
        f"[下载]({download_url(repo, version, names['zh_pdf'])}) | "
        f"[下载]({download_url(repo, version, names['zh_html'])}) | "
        f"[下载]({download_url(repo, version, names['zh_md'])}) |",
        "| English | "
        f"[Download]({download_url(repo, version, names['en_pdf'])}) | "
        f"[Download]({download_url(repo, version, names['en_html'])}) | "
        f"[Download]({download_url(repo, version, names['en_md'])}) |",
    ]
    if infographics:
        lines.extend(
            [
                "",
                f"英文章节信息图（PNG 合集）：[下载 ZIP]({download_url(repo, version, names['en_infographics_zip'])}) · "
                f"[在仓库中浏览](assets/infographics/en/)",
            ]
        )
    lines.append(END)
    return "\n".join(lines)


def block_en(repo: str, version: str, names: dict[str, str], *, infographics: bool) -> str:
    base = f"https://github.com/{repo}/releases"
    lines = [
        BEGIN,
        f"Latest: **[{version}]({base}/tag/{version})** · [All release assets]({base}/latest)",
        "",
        "| Locale | PDF | Single-page HTML | Full-book Markdown |",
        "| --- | --- | --- | --- |",
        "| Chinese | "
        f"[Download]({download_url(repo, version, names['zh_pdf'])}) | "
        f"[Download]({download_url(repo, version, names['zh_html'])}) | "
        f"[Download]({download_url(repo, version, names['zh_md'])}) |",
        "| English | "
        f"[Download]({download_url(repo, version, names['en_pdf'])}) | "
        f"[Download]({download_url(repo, version, names['en_html'])}) | "
        f"[Download]({download_url(repo, version, names['en_md'])}) |",
    ]
    if infographics:
        lines.extend(
            [
                "",
                f"English chapter infographics (PNG bundle): "
                f"[Download ZIP]({download_url(repo, version, names['en_infographics_zip'])}) · "
                f"[Browse in repo](assets/infographics/en/)",
            ]
        )
    lines.append(END)
    return "\n".join(lines)


def patch_file(path: Path, new_block: str) -> bool:
    text = path.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError(f"{path} 缺少 {BEGIN} … {END} 标记")
    updated = pattern.sub(new_block, text, count=1)
    if updated == text:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--repo", default=DEFAULT_REPO)
    parser.add_argument("--version", help="Release tag，例如 v0.9.006")
    parser.add_argument("--json-out", type=Path, help="可选：写入解析结果 JSON")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    version = resolve_version(args.repo, args.version)
    names = asset_filenames(version)
    policy_path = root / f"planning/releases/{version}-policy.json"
    infographics = False
    if policy_path.is_file():
        infographics = bool(
            json.loads(policy_path.read_text(encoding="utf-8")).get("english_infographic_assets")
        )
    zh_block = block_zh(args.repo, version, names, infographics=infographics)
    en_block = block_en(args.repo, version, names, infographics=infographics)
    changed = patch_file(root / "README.md", zh_block)
    changed |= patch_file(root / "README.en.md", en_block)
    if args.json_out:
        payload = {"version": version, "repo": args.repo, "files": names, "changed": changed}
        args.json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[INFO] README release downloads: version={version}, changed={changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
