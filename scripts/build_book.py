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
from dataclasses import dataclass
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


MARKER_NAME = ".book-build-root"
RELEASE_PROFILE_FILTER = Path("book/filters/release-profile.lua")
MERMAID_BLOCK = re.compile(r"^```mermaid[^\n]*\n(.*?)^```[ \t]*$", re.MULTILINE | re.DOTALL)
PDF_FULL_PAGE_COVER = r"""\newgeometry{margin=0pt}
\thispagestyle{empty}
\AddToShipoutPictureBG*{\AtPageLowerLeft{\makebox[\paperwidth][c]{\includegraphics[width=0.75\paperheight,height=\paperheight,keepaspectratio=false]{\detokenize{__PDF_COVER_PATH__}}}}}
\null
\clearpage
\restoregeometry"""

SOURCE_FILES_ZH: Tuple[Path, ...] = (
    Path("book/build-frontmatter.md"),
    Path("book/manifesto.md"),
    Path("book/part-00-overview.md"),
    Path("book/toc.md"),
    Path("book/chapters/ch01-ai-native-sdlc.md"),
    Path("book/chapters/ch02-human-judgment.md"),
    Path("book/chapters/ch03-inception.md"),
    Path("book/chapters/ch04-memory-bank-standards.md"),
    Path("book/chapters/ch05-bolts.md"),
    Path("book/chapters/ch06-exsecutio.md"),
    Path("book/chapters/ch07-verification.md"),
    Path("book/chapters/ch08-operations.md"),
    Path("book/chapters/ch09-adaptive-engineering.md"),
    Path("book/chapters/ch10-organization-metrics.md"),
)

SOURCE_FILES_EN: Tuple[Path, ...] = (
    Path("book/en/build-frontmatter.md"),
    Path("book/en/manifesto.md"),
    Path("book/en/part-00-overview.md"),
    Path("book/en/toc.md"),
    Path("book/en/chapters/ch01-ai-native-sdlc.md"),
    Path("book/en/chapters/ch02-human-judgment.md"),
    Path("book/en/chapters/ch03-inception.md"),
    Path("book/en/chapters/ch04-memory-bank-standards.md"),
    Path("book/en/chapters/ch05-bolts.md"),
    Path("book/en/chapters/ch06-exsecutio.md"),
    Path("book/en/chapters/ch07-verification.md"),
    Path("book/en/chapters/ch08-operations.md"),
    Path("book/en/chapters/ch09-adaptive-engineering.md"),
    Path("book/en/chapters/ch10-organization-metrics.md"),
    Path("book/en/glossary.md"),
)

SUPPORT_FILES: Tuple[Path, ...] = (
    Path("book/book.css"),
    Path("book/filters/pdf-compat.lua"),
    Path("book/filters/release-profile.lua"),
    Path("book/fonts/fraunces.woff2"),
    Path("book/fonts/source-serif-4.woff2"),
    Path("book/fonts/ibm-plex-mono-400.woff2"),
    Path("book/fonts/ibm-plex-mono-500.woff2"),
    Path("book/templates/skip-link.html"),
    Path("book/templates/release-pdf-header.tex"),
    Path("book/images/cover.png"),
    Path("book/images/fig0-1.svg"),
    Path("book/images/chapter-figures.json"),
    Path("book/images/ch02-human-judgment-gate.svg"),
    Path("book/images/ch03-intent-to-bolt.svg"),
    Path("book/images/ch04-memory-bank-stack.svg"),
    Path("book/images/ch05-bolt-selection-matrix.svg"),
    Path("book/images/ch06-exsecutio-loop.svg"),
    Path("book/images/ch07-verification-evidence-chain.svg"),
    Path("book/images/ch08-operations-loop.svg"),
    Path("book/images/ch09-risk-ceremony-matrix.svg"),
    Path("book/images/ch10-org-operating-system.svg"),
)

# Backward-compatible defaults (Chinese locale).
TITLE = "深入理解 AI-DLC"
HTML_NAME = "deep-understanding-ai-dlc.html"
PDF_NAME = "deep-understanding-ai-dlc.pdf"
SOURCE_FILES = SOURCE_FILES_ZH
COVER_MARKDOWN = "![《深入理解 AI-DLC》书籍封面](images/cover.png){.book-cover width=42%}"
COVER_MARKDOWN_EN = (
    "![Deep Understanding AI-DLC book cover](../images/cover.png){.book-cover width=42%}"
)

SUPPORTED_LOCALES = ("zh", "en")


@dataclass(frozen=True)
class BookLocaleConfig:
    code: str
    title: str
    html_name: str
    pdf_name: str
    pandoc_lang: str
    source_files: Tuple[Path, ...]
    resource_path_parts: Tuple[str, ...]
    frontmatter_path: Path
    cover_markdown: str
    cover_image_path: Path
    pdf_documentclass: str
    html_required_phrases: Tuple[str, ...]
    min_embedded_images: int
    mermaid_caption_prefix: str


def get_book_locale(locale: str) -> BookLocaleConfig:
    if locale == "zh":
        return BookLocaleConfig(
            code="zh",
            title=TITLE,
            html_name=HTML_NAME,
            pdf_name=PDF_NAME,
            pandoc_lang="zh-CN",
            source_files=SOURCE_FILES_ZH,
            resource_path_parts=("book", ""),
            frontmatter_path=Path("book/build-frontmatter.md"),
            cover_markdown=COVER_MARKDOWN,
            cover_image_path=Path("book/images/cover.png"),
            pdf_documentclass="ctexbook",
            html_required_phrases=(
                TITLE,
                "𝓔 = Engineering with Exsecutio",
                "Part 00 · 鸟瞰 AI-DLC",
                "第 10 章",
            ),
            min_embedded_images=5,
            mermaid_caption_prefix="Part 0 鸟瞰图",
        )
    if locale == "en":
        return BookLocaleConfig(
            code="en",
            title="Deep Understanding AI-DLC",
            html_name="deep-understanding-ai-dlc-en.html",
            pdf_name="deep-understanding-ai-dlc-en.pdf",
            pandoc_lang="en-US",
            source_files=SOURCE_FILES_EN,
            resource_path_parts=("book/en", "book", ""),
            frontmatter_path=Path("book/en/build-frontmatter.md"),
            cover_markdown=COVER_MARKDOWN_EN,
            cover_image_path=Path("book/images/cover.png"),
            pdf_documentclass="book",
            html_required_phrases=(
                "Deep Understanding AI-DLC",
                "Engineering with Exsecutio",
                "Chapter 10",
                "Organization and metrics",
                "Verification",
            ),
            min_embedded_images=14,
            mermaid_caption_prefix="Part 0 diagram",
        )
    raise RuntimeError(f"未知 locale：{locale}；支持：{', '.join(SUPPORTED_LOCALES)}")


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
        shutil.which("chromium-browser"),
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
    root: Path,
    work: Path,
    mmdc: str,
    browser: str,
    output_format: str,
    book_locale: BookLocaleConfig,
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
        )
        + "\n",
        encoding="utf-8",
    )
    for source_number, relative_path in enumerate(book_locale.source_files, start=1):
        source_path = root / relative_path
        source_text = source_path.read_text(encoding="utf-8")
        source_changed = False
        if output_format == "pdf" and relative_path == book_locale.frontmatter_path:
            cover_path = (root / book_locale.cover_image_path).as_posix()
            next_text = source_text.replace(book_locale.cover_markdown, PDF_FULL_PAGE_COVER)
            next_text = next_text.replace("__PDF_COVER_PATH__", cover_path)
            source_changed = next_text != source_text
            source_text = next_text

        def replace(match: re.Match[str]) -> str:
            nonlocal diagram_number
            diagram_number += 1
            diagram_source = work / f"diagram-{diagram_number:02d}.mmd"
            diagram_output = work / f"diagram-{diagram_number:02d}.{output_format}"
            diagram_source.write_text(match.group(1).strip() + "\n", encoding="utf-8")
            command = [
                mmdc,
                "--input",
                str(diagram_source),
                "--output",
                str(diagram_output),
                "--theme",
                "neutral",
                "--configFile",
                str(mermaid_config),
                "--puppeteerConfigFile",
                str(puppeteer_config),
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
                f"![{book_locale.mermaid_caption_prefix} {diagram_number}](<{diagram_output.as_posix()}>)"
                "{.mermaid-diagram width=100%}"
            )

        rendered_text = MERMAID_BLOCK.sub(replace, source_text)
        if rendered_text == source_text and not source_changed:
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


def validate_html(path: Path, book_locale: BookLocaleConfig) -> None:
    text = path.read_text(encoding="utf-8")
    parser = HtmlCandidate()
    parser.feed(text)
    visible_text = re.sub(r"\s+", " ", " ".join(parser.text_parts))
    for required in book_locale.html_required_phrases:
        if required not in visible_text:
            raise RuntimeError(f"HTML 候选缺少必需内容：{required}")
    if "TOC" not in parser.ids:
        raise RuntimeError("HTML 候选缺少目录导航。")
    if len(parser.images) < book_locale.min_embedded_images or not all(
        source.startswith("data:image/") for source in parser.images
    ):
        raise RuntimeError("HTML 候选没有完整内嵌封面、核心图与 Mermaid 图。")


def validate_pdf(path: Path) -> None:
    data = path.read_bytes()
    if len(data) < 10_000 or not data.startswith(b"%PDF-") or b"%%EOF" not in data[-4096:]:
        raise RuntimeError("PDF 候选结构或大小异常。")


def build(
    root: Path,
    output: Path,
    generated_at: str,
    build_format: str,
    profile: str = "dev",
    locale: str = "zh",
) -> Dict[str, object]:
    root = root.resolve()
    output = output.resolve()
    if profile not in {"dev", "release"}:
        raise RuntimeError(f"未知构建 profile：{profile}")
    book_locale = get_book_locale(locale)
    missing = [
        str(path)
        for path in book_locale.source_files + SUPPORT_FILES
        if not (root / path).is_file()
    ]
    if missing:
        raise RuntimeError("缺少构建输入：" + ", ".join(missing))

    pandoc = require_tool("pandoc", "macOS 可运行：brew install pandoc")
    mmdc = require_tool("mmdc", "书稿包含 Mermaid 图，macOS 可运行：brew install mermaid-cli")
    browser = find_chromium_browser()
    tectonic = None
    if build_format in {"pdf", "all"}:
        tectonic = require_tool("tectonic", "macOS 可运行：brew install tectonic")

    prepare_output(root, output)
    resource_path = os.pathsep.join(str(root / part) for part in book_locale.resource_path_parts if part != "")
    release_filter = root / RELEASE_PROFILE_FILTER
    outputs: List[Dict[str, str]] = []
    with tempfile.TemporaryDirectory(prefix="aidlc-book-") as directory:
        work = Path(directory)

        def common_for(sources: List[str]) -> List[str]:
            command = [
                pandoc,
                *sources,
                "--from=markdown+smart+raw_tex+fenced_divs",
                "--standalone",
                f"--resource-path={resource_path}",
                f"--metadata=lang:{book_locale.pandoc_lang}",
            ]
            if profile == "release":
                command.append(f"--lua-filter={release_filter}")
            return command

        if build_format in {"html", "all"}:
            html_sources = render_mermaid_sources(
                root, work, mmdc, browser, "svg", book_locale
            )
            html_path = output / book_locale.html_name
            html_args = [
                "--to=html5",
                "--toc",
                "--toc-depth=3",
                f"--css={root / 'book/book.css'}",
                "--embed-resources",
                f"--output={html_path}",
            ]
            if profile == "release":
                html_args.append(
                    f"--include-before-body={root / 'book/templates/skip-link.html'}"
                )
            run_pandoc(
                common_for(html_sources) + html_args,
                "Pandoc HTML 构建",
            )
            validate_html(html_path, book_locale)
            outputs.append({"path": book_locale.html_name, "sha256": sha256(html_path)})

        if build_format in {"pdf", "all"}:
            pdf_sources = render_mermaid_sources(
                root, work, mmdc, browser, "pdf", book_locale
            )
            pdf_path = output / book_locale.pdf_name
            pdf_command = common_for(pdf_sources) + [
                "--to=pdf",
                "--pdf-engine=tectonic",
                f"--lua-filter={root / 'book/filters/pdf-compat.lua'}",
                f"--variable=documentclass:{book_locale.pdf_documentclass}",
                "--variable=classoption:openany",
                "--variable=papersize:a4",
                "--variable=colorlinks:true",
                f"--output={pdf_path}",
            ]
            if profile == "release":
                pdf_command.extend(
                    [
                        "--top-level-division=chapter",
                        "--variable=geometry:margin=28mm",
                        f"--include-in-header={root / 'book/templates/release-pdf-header.tex'}",
                    ]
                )
            else:
                pdf_command.append("--variable=geometry:margin=24mm")
            run_pandoc(pdf_command, "Pandoc PDF 构建")
            validate_pdf(pdf_path)
            outputs.append({"path": book_locale.pdf_name, "sha256": sha256(pdf_path)})

    manifest = {
        "schema_version": "1.0.0",
        "locale": book_locale.code,
        "title": book_locale.title,
        "generated_at": generated_at,
        "format": build_format,
        "profile": profile,
        "pandoc": tool_version(pandoc),
        "diagram_engine": tool_version(mmdc),
        "diagram_browser": Path(browser).name,
        "pdf_engine": tool_version(tectonic) if tectonic else None,
        "entrypoint": book_locale.html_name
        if build_format in {"html", "all"}
        else book_locale.pdf_name,
        "sources": [
            {"path": path.as_posix(), "sha256": sha256(root / path)}
            for path in book_locale.source_files + SUPPORT_FILES
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
    parser.add_argument(
        "--profile",
        choices=("dev", "release"),
        default="dev",
        help="dev 保留写作脚手架；release 剥离 Metadata/Gate/Review Notes 等内部信息",
    )
    parser.add_argument(
        "--locale",
        choices=SUPPORTED_LOCALES,
        default="zh",
        help="zh 中文全书；en 英文书稿（Part 0 + 章节，v0.9.002 起含 CH01–03）",
    )
    parser.add_argument("--generated-at", help="fixed ISO-8601 build time for reproducible tests")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    try:
        manifest = build(
            args.root,
            args.output,
            generated_at,
            args.format,
            profile=args.profile,
            locale=args.locale,
        )
    except (OSError, RuntimeError, UnicodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1
    output = args.output.resolve()
    for item in manifest["outputs"]:
        print(f"[OK] Candidate: {output / item['path']}")
    print(f"[OK] Build manifest: {output / 'build-manifest.json'}")
    print(f"[OK] Locale: {manifest['locale']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
