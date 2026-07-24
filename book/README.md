# Book Source

本目录保存书稿源文件、核心公式、十章目录和统一章节模板。

- [manifesto.md](manifesto.md)：核心公式及边界
- [part-00-overview.md](part-00-overview.md)：AI-DLC 鸟瞰图、全书叙事结构与阅读路线
- [toc.md](toc.md)：Part 0 导读、十章结构与实验方向
- [chapters/ch01-ai-native-sdlc.md](chapters/ch01-ai-native-sdlc.md)：CH-01 可读稿与审校记录入口
- [chapters/ch02-human-judgment.md](chapters/ch02-human-judgment.md)：CH-02 论证骨架稿
- [chapters/ch03-inception.md](chapters/ch03-inception.md)：CH-03 正式十章生产线可读稿
- [chapters/sample.md](chapters/sample.md)：CH-03 v0.1 样章证据副本
- [chapters/ch04-memory-bank-standards.md](chapters/ch04-memory-bank-standards.md)：CH-04 正式十章生产线可读稿
- [chapters/ch05-bolts.md](chapters/ch05-bolts.md)：CH-05 正式十章生产线可读稿
- [chapters/ch06-exsecutio.md](chapters/ch06-exsecutio.md)：CH-06 正式十章生产线可读稿
- [chapters/ch07-verification.md](chapters/ch07-verification.md)：CH-07 正式十章生产线可读稿
- [chapters/ch08-operations.md](chapters/ch08-operations.md)：CH-08 正式十章生产线可读稿与审校记录入口
- [chapters/ch09-adaptive-engineering.md](chapters/ch09-adaptive-engineering.md)：CH-09 正式十章生产线可读稿与审校记录入口
- [chapter-template.md](chapter-template.md)：章节六阶段生产线
- [images/cover.png](images/cover.png)：作者定稿封面（1200 × 1600 PNG）
- [images/README.md](images/README.md)：视觉资产来源与校验信息

章节状态不在 Markdown 中手工汇总，权威状态见 [../progress/chapters.json](../progress/chapters.json)。

## 最小书稿构建

在仓库根目录运行：

```bash
scripts/build_book.sh
```

默认使用 Pandoc 生成自包含的 `.artifacts/book/deep-understanding-ai-dlc.html` 和 `build-manifest.json`。同时构建 HTML 与 PDF：

```bash
scripts/build_book.sh .artifacts/book all
```

HTML 依赖 Pandoc 与 Mermaid CLI；PDF 额外依赖 Tectonic。macOS 安装命令为 `brew install pandoc mermaid-cli tectonic`。Mermaid 图会先渲染为 SVG，再由 Pandoc 内嵌到 HTML/PDF。`.artifacts/` 为可重新生成的本地产物，不进入版本库。
