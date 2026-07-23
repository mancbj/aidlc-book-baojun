# Dashboard Accessibility Review

> D09-T02「完成响应式与键盘检查」审查记录。  
> 生成时间：2026-07-23T02:36:52Z  
> 范围：`site/index.html`、`site/progress.html`、`site/details.html`

## 结论

通过。

- 360px 视口下，三页均无页面级横向溢出。
- 桌面 1280px 视口下，三页均无页面级横向溢出。
- 键盘 Tab 顺序能先到达 skip link，再进入主导航。
- 当前核心阅读路径可通过键盘到达：驾驶舱、生产线、对象下钻、文字摘要、更新记录，以及页面内的任务/产物/GitHub 下钻链接。

## 自动检查方法

使用 Codex bundled Node.js + bundled Playwright 包，并指定本机 Chrome 可执行文件运行真实浏览器检查。

检查项：

1. 设置视口为 `360 × 900` 与 `1280 × 900`。
2. 读取 `document.documentElement.scrollWidth`、`document.body.scrollWidth` 与 `clientWidth`，确认页面级横向溢出不超过 1px。
3. 连续按 Tab 9 次，记录焦点元素。
4. 确认首个焦点为 `.skip-link`。
5. 确认主导航链接可获得焦点。

## 证据摘要

| 页面 | 视口 | 页面级横向溢出 | Skip link 可聚焦 | 主导航可聚焦 | 结果 |
|---|---:|---:|---|---|---|
| `site/index.html` | 360px | 0px | 是 | 是 | 通过 |
| `site/index.html` | 1280px | 0px | 是 | 是 | 通过 |
| `site/progress.html` | 360px | 0px | 是 | 是 | 通过 |
| `site/progress.html` | 1280px | 0px | 是 | 是 | 通过 |
| `site/details.html` | 360px | 0px | 是 | 是 | 通过 |
| `site/details.html` | 1280px | 0px | 是 | 是 | 通过 |

## 人工审视补充

- `.topbar nav` 在小屏下允许横向滚动，避免导航项挤压导致文字遮挡。
- `.timeline` 与 `.table-wrap` 使用局部横向滚动承载宽表，不让 `body` 产生横向溢出。
- `a:focus-visible`、`button:focus-visible` 与 `[tabindex]:focus-visible` 提供 3px 蓝色焦点环。
- 三页均保留 `<a class="skip-link" href="#main">跳到主要内容</a>`。
- 生产线页新增的任务、产物、GitHub 下钻均为原生 `<a>` 链接，天然支持键盘焦点。
- `@media (prefers-reduced-motion: reduce)` 已关闭平滑滚动，降低动效干扰。

## 关闭标准映射

验收项：`360px 无横向溢出且主要导航键盘可用`

- 360px 无横向溢出：通过真实浏览器检查。
- 主要导航键盘可用：通过 Tab 焦点检查。
- 证据位置：本文件与 `progress/events/events.jsonl` 中的 D09-T02 状态事件。

## 后续建议

D09-T03 可继续做「30 秒下一动作测试」，重点验证首次访问者是否能在驾驶舱与生产线页中快速找到下一项 Must。
