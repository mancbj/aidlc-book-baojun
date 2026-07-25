# Round 10 · Diagram / ASCII Compatibility

**Decision:** KEEP（确认既有能力，无新增破坏）

## 目标

确认 PDF 图表与 ASCII 框图在 release profile 下仍可读。

## 结果

- `pdf-compat.lua` 继续替换框图/箭头缺字字符
- Mermaid 图仍渲染进 PDF
- 抽查前 6 页截图：封面、目录、章节层级正常；无 Writing Sprint / Metadata

## 评分

- Content: 47 / 50
- HTML: 22 / 25
- PDF: **21 / 25**
- **Total: 90 / 100**
