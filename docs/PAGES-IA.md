# GitHub Pages · 信息架构（v0.9.005+）

> Loop 编排：[`v0.9-loop-orchestration.md`](../planning/publication/v0.9-loop-orchestration.md)

**对外基址（README / 分享链接请用完整 URL）：** `https://mancbj.github.io/aidlc-book-baojun/`  
在 GitHub 仓库页点击相对路径 `book-site/index.html` 会进入源码视图，不会渲染为网页；克隆仓库后本地可 `python3 scripts/build_book_site.py` 再用浏览器打开 `book-site/index.html`。  
若 `github.io` 提示无站点，说明 Pages 尚未成功部署，见 [`GITHUB-PAGES-SETUP.md`](GITHUB-PAGES-SETUP.md)。

## URL 结构（Pages 根 = 仓库 GitHub Pages）

| 路径 | 用途 | 语言 |
| --- | --- | --- |
| `/` | 发布索引（commit、事实源、进入阅读/驾驶舱） | UI 中/英 |
| `/book-site/index.html` | **Carbon 着陆页**（封面、公式、fig0-1） | UI 中/英 |
| `/book-site/reader.html` | **可视化阅读器**（Side nav、章节锚点、图放大） | 书稿 zh / en |
| `/book-site/assets/<locale>/book.html` | Pandoc 单页书稿（与 Release 同源构建） | zh / en |
| `/site/index.html` | 写作进度 **运维驾驶舱**（现状保留） | 中文为主 |

Release 离线包仍从 [GitHub Releases](https://github.com/mancbj/aidlc-book-baojun/releases) 下载；Pages 为默认可浏览面（v0.9.008 manifest hash 对齐）。

## 设计 token

- 静态 CSS：`book-site/carbon-tokens.css`（IBM Carbon 色型/间距/字阶子集，无 npm 运行时）
- 书稿排版：`book-site/reader.css` + 仓库 `book/book.css` 在 iframe 内加载

## 构建命令

```bash
python3 scripts/build_book_site.py --output book-site/assets
python3 scripts/prepare_pages.py --output .artifacts/pages
```

## a11y（v0.9.007）

- Skip link、`<main>` / `nav` landmark、可见 focus ring
- `prefers-reduced-motion` 关闭图放大动画
- `hreflang`：`book-site/index.html` 与 `reader.html` 链到中/英书稿
