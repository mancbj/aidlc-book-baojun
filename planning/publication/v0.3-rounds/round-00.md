# Round 00 · Baseline

**Decision:** KEEP（仅文档与基线度量）

## 目标

建立 v0.3 Loop 的基线构建、评分卡与冻结清单，不改内容。

## 构建

```bash
export PATH="$HOME/.local/bin:$PATH"
python3 scripts/build_book.py \
  --format all \
  --output .artifacts/v0.3-loop/round-00/book \
  --generated-at 2026-07-25T00:00:00Z
```

产物（本地，不入库）：

- HTML ~5.2MB：`.artifacts/v0.3-loop/round-00/book/deep-understanding-ai-dlc.html`
- PDF ~4.9MB / 112 页 A4：`.artifacts/v0.3-loop/round-00/book/deep-understanding-ai-dlc.pdf`
- 字体：Fandol + Latin Modern 等已嵌入

## 基线发现

### 内容卫生（严重）

HTML/PDF 同时泄漏：

| 标记 | HTML | PDF text |
|------|------|----------|
| Metadata | 20 | 20 |
| Writing Sprint Card | 8 | 8 |
| Draft Completeness | 10 | 10 |
| Status Source | 10 | 10 |
| Chapter ID | 10 | 10 |
| 五类审校 | 14 | 14 |
| Review Notes | 有 | 4 |
| Dxx-Txx 任务号 | 大量 | 52 |
| Gate 写作清单 | 有 | 目录可见 |

另有宣言/目录中的生产元段落：`D01-T01 验收`、`来源记录`、`核心问题去重审计`、`v0.1 边界`、`D01-T03 持续验收`。

### HTML

- 单栏可读，但视觉接近默认技术文档
- Inter / 系统栈；背景偏平
- 目录可用；内嵌封面与图存在

### PDF

- 112 页，结构完整，字体嵌入良好
- 版式偏默认 `ctexbook`；框图已做 ASCII 兼容
- 目录被 Metadata / Gate / Review Notes 污染

## 评分

- Content: **18 / 50**（事实大体可读，但不可直接出版）
- HTML: **12 / 25**
- PDF: **13 / 25**
- **Total: 43 / 100**

## 下一轮

Round 01：实现 `book/filters/release-profile.lua` + release 构建入口，使发布产物零 meta 泄漏。
