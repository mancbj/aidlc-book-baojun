# Round 07 · HTML Accessibility

**Decision:** KEEP

## 目标

补齐键盘可达与焦点可见性，不破坏设计系统。

## 变更

- `book/templates/skip-link.html`：跳到目录
- release HTML 构建注入 `--include-before-body`
- `:focus-visible` 与 `prefers-reduced-motion` 支持
- 链接审计跳过 pandoc include 模板

## 评分

- Content: 47 / 50
- HTML: **22 / 25**
- PDF: 14 / 25
- **Total: 83 / 100**
