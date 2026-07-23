#!/usr/bin/env python3
"""Orchestrate Pandoc HTML/PDF builds and write a hashed build manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Sequence


TITLE = "深入理解 AI-DLC"
HTML_NAME = "deep-understanding-ai-dlc.html"
PDF_NAME = "deep-understanding-ai-dlc.pdf"
MARKER_NAME = ".book-build-root"
SOURCE_FILES = (
    Path("book/build-frontmatter.md"),
    Path("book/manifesto.md"),
    Path("book/part-00-overview.md"),
    Path("book/toc.md"),
)
SUPPORT_FILES = (
    Path("book/book.css"),
    Path("book/filters/pdf-compat.lua"),
    Path("book/images/cover.png"),
    Path("book/images/fig0-1.svg"),
)
MERMAID_BLOCK = re.compile(r"^```mermaid[^\n]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tool_version(command: str) -> str:
    result = subprocess.run([command, "--version"], capture_output=True, text=True, check=False)
    if result.returncode:
        return "unknown"
    return (result.stdout or result.stderr).splitlines()[0].strip()


def require_tool(name: str, install_hint: str) -> str:
    executable = shutil.which(name)
    if not executable:
        raise RuntimeError(f"缺少 {name}。{install_hint}")
    return executable


def find_chromium_browser() -> str:
    candidates = [
        os.environ.get("PUPPETEER_EXECUTABLE_PATH"),
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Chromium.app/Contents/MacOS/Chromium",
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        shutil.which("chromium"),
        shutil.which("google-chrome"),
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file() and os.access(candidate, os.X_OK):
            return candidate
    raise RuntimeError(
        "Mermaid CLI 需要 Chromium 浏览器。请安装 Google Chrome，或设置 "
        "PUPPETEER_EXECUTABLE_PATH。"
    )


def prepare_output(root: Path, output: Path) -> None:
    root = root.resolve()
    output = output.resolve()
    if output in {Path("/").resolve(), root}:
        raise RuntimeError("拒绝把仓库根目录或文件系统根目录作为构建输出。")
    marker = output / MARKER_NAME
    if output.exists():
        if not marker.is_file():
            raise RuntimeError(f"输出目录已存在但没有 {MARKER_NAME}；拒绝覆盖：{output}")
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / MARKER_NAME).write_text("aidlc-book-build\n", encoding="utf-8")


def run_pandoc(command: List[str], label: str) -> None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    diagnostics = "\n".join(part.strip() for part in (result.stdout, result.stderr) if part.strip())
    if result.returncode:
        raise RuntimeError(f"{label}失败：\n{diagnostics}")
    if "Missing character:" in diagnostics or "could not represent character" in diagnostics:
        raise RuntimeError(f"{label}出现字体缺字：\n{diagnostics}")


def render_mermaid_sources(
    root: Path, work: Path, mmdc: str, browser: str, output_format: str
) -> List[str]:
    rendered_sources: List[str] = []
    diagram_number = 0
    puppeteer_config = work / "puppeteer.json"
    puppeteer_config.write_text(
        json.dumps({"executablePath": browser}, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    mermaid_config = work / "mermaid.json"
    mermaid_config.write_text(
        json.dumps(
            {
                "flowchart": {"htmlLabels": False, "curve": "linear"},
                "themeVariables": {
                    "fontFamily": 'Inter, "Noto Sans SC", "PingFang SC", sans-serif',
                    "primaryColor": "#F7F8FA",
                    "primaryTextColor": "#252A31",
                    "primaryBorderColor": "#DDE1E7",
                    "lineColor": "#5F6671",
                },
            },
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )
    for source_number, relative_path in enumerate(SOURCE_FILES, start=1):
        source_path = root / relative_path
        source_text = source_path.read_text(encoding="utf-8")

        def replace(match: re.Match[str]) -> str:
            nonlocal diagram_number
            diagram_number += 1
            diagram_source = work / f"diagram-{diagram_number:02d}.mmd"
            diagram_output = work / f"diagram-{diagram_number:02d}.{output_format}"
            diagram_source.write_text(match.group(1).strip() + "\n", encoding="utf-8")
            command = [
                mmdc,
                "--input", str(diagram_source),
                "--output", str(diagram_output),
                "--theme", "neutral",
                "--configFile", str(mermaid_config),
                "--puppeteerConfigFile", str(puppeteer_config),
                "--quiet",
            ]
            if output_format == "pdf":
                command.append("--pdfFit")
            else:
                command.extend(["--backgroundColor", "transparent"])
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode or not diagram_output.is_file():
                diagnostics = "\n".join(
                    part.strip() for part in (result.stdout, result.stderr) if part.strip()
                )
                raise RuntimeError(f"Mermaid 图 {diagram_number} 渲染失败：\n{diagnostics}")
            return (
                f"![Part 0 鸟瞰图 {diagram_number}](<{diagram_output.as_posix()}>)"
                "{.mermaid-diagram width=100%}"
            )

        rendered_text = MERMAID_BLOCK.sub(replace, source_text)
        if rendered_text == source_text:
            rendered_sources.append(str(source_path))
            continue
        rendered_source = work / f"source-{output_format}-{source_number:02d}-{source_path.name}"
        rendered_source.write_text(rendered_text, encoding="utf-8")
        rendered_sources.append(str(rendered_source))
    return rendered_sources


class HtmlCandidate(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids = set()
        self.images: List[str] = []
        self.text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])
        if tag == "img" and values.get("src"):
            self.images.append(values["src"])

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        self.text_parts.append(data)


def validate_html(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    parser = HtmlCandidate()
    parser.feed(text)
    visible_text = re.sub(r"\s+", " ", " ".join(parser.text_parts))
    for required in (TITLE, "𝓔 = Engineering with Exsecutio", "Part 00 · 鸟瞰 AI-DLC", "第 10 章"):
        if required not in visible_text:
            raise RuntimeError(f"HTML 候选缺少必需内容：{required}")
    if "TOC" not in parser.ids:
        raise RuntimeError("HTML 候选缺少目录导航。")
    if len(parser.images) < 5 or not all(source.startswith("data:image/") for source in parser.images):
        raise RuntimeError("HTML 候选没有完整内嵌封面、核心图与三张鸟瞰图。")


def validate_pdf(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 10_000 or not data.startswith(b"%PDF-") or b"%%EOF" not in data[-4096:]:
        raise RuntimeError("PDF 候选结构或大小异常。")


def build(root: Path, output: Path, generated_at: str, build_format: str) -> Dict[str, object]:
    root = root.resolve()
    output = output.resolve()
    missing = [str(path) for path in SOURCE_FILES + SUPPORT_FILES if not (root / path).is_file()]
    if missing:
        raise RuntimeError("缺少构建输入：" + ", ".join(missing))

    pandoc = require_tool("pandoc", "macOS 可运行：brew install pandoc")
    mmdc = require_tool("mmdc", "书稿包含 Mermaid 图，macOS 可运行：brew install mermaid-cli")
    browser = find_chromium_browser()
    tectonic = None
    if build_format in {"pdf", "all"}:
        tectonic = require_tool("tectonic", "macOS 可运行：brew install tectonic")

    prepare_output(root, output)
    resource_path = os.pathsep.join((str(root / "book"), str(root)))
    outputs: List[Dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="aidlc-book-") as directory:
        work = Path(directory)

        def common_for(sources: List[str]) -> List[str]:
            return [
                pandoc,
                *sources,
                "--from=markdown+smart+raw_tex+fenced_divs",
                "--standalone",
                f"--resource-path={resource_path}",
                "--metadata=lang:zh-CN",
            ]

        if build_format in {"html", "all"}:
            html_sources = render_mermaid_sources(root, work, mmdc, browser, "svg")
            html_path = output / HTML_NAME
            run_pandoc(
                common_for(html_sources)
                + [
                    "--to=html5",
                    "--toc",
                    "--toc-depth=3",
                    f"--css={root / 'book/book.css'}",
                    "--embed-resources",
                    f"--output={html_path}",
                ],
                "Pandoc HTML 构建",
            )
            validate_html(html_path)
            outputs.append({"path": HTML_NAME, "sha256": sha256(html_path)})

        if build_format in {"pdf", "all"}:
            pdf_sources = render_mermaid_sources(root, work, mmdc, browser, "pdf")
            pdf_path = output / PDF_NAME
            run_pandoc(
                common_for(pdf_sources)
                + [
                    "--to=pdf",
                    "--pdf-engine=tectonic",
                    f"--lua-filter={root / 'book/filters/pdf-compat.lua'}",
                    "--variable=documentclass:ctexbook",
                    "--variable=classoption:openany",
                    "--variable=papersize:a4",
                    "--variable=geometry:margin=24mm",
                    "--variable=colorlinks:true",
                    f"--output={pdf_path}",
                ],
                "Pandoc PDF 构建",
            )
            validate_pdf(pdf_path)
            outputs.append({"path": PDF_NAME, "sha256": sha256(pdf_path)})

    manifest = {
        "schema_version": "1.0.0",
        "title": TITLE,
        "generated_at": generated_at,
        "format": build_format,
        "pandoc": tool_version(pandoc),
        "diagram_engine": tool_version(mmdc),
        "diagram_browser": Path(browser).name,
        "pdf_engine": tool_version(tectonic) if tectonic else None,
        "entrypoint": HTML_NAME if build_format in {"html", "all"} else PDF_NAME,
        "sources": [
            {"path": path.as_posix(), "sha256": sha256(root / path)}
            for path in SOURCE_FILES + SUPPORT_FILES
        ],
        "outputs": outputs,
    }
    (output / "build-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path(".artifacts/book"))
    parser.add_argument("--format", choices=("html", "pdf", "all"), default="html")
    parser.add_argument("--generated-at", help="fixed ISO-8601 build time for reproducible tests")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    try:
        manifest = build(args.root, args.output, generated_at, args.format)
    except (OSError, RuntimeError, UnicodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1
    output = args.output.resolve()
    for item in manifest["outputs"]:
        print(f"[OK] Candidate: {output / item['path']}")
    print(f"[OK] Build manifest: {output / 'build-manifest.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
