# Round 08 · PDF Page Geometry

**Decision:** KEEP

## 目标

改善 release PDF 页边距与段落节奏。

## 变更

- `book/templates/release-pdf-header.tex`：段落间距、孤行控制、`raggedbottom`
- release profile：`geometry:margin=28mm`

## 验证

- PDF 构建成功；无缺字
- 页数随章节划分进一步变化（见 Round 09）

## 评分

- Content: 47 / 50
- HTML: 22 / 25
- PDF: **18 / 25**
- **Total: 87 / 100**
