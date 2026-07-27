# Release Versioning Policy

自 `v0.8` 起，可读发布采用 **patch-grain** 三位补丁号：

```text
v0.<minor>.<patch:000-999>
```

## 规则

1. 大主题线仍落在 `v0.<minor>`（例如 `v0.8` 表示 ALREADY/KEEP-EXT 合同化主线）。
2. 主线内的每次可发布 Loop 递增最后三位：`v0.8.001` → `v0.8.002` → …
3. Git tag、policy `version`、RC 目录 `releases/<version>-rc/`、回执 `releases/<version>/release.json` 必须使用同一完整版本字符串。
4. 反馈 deferred 的 `target_cycle` 可用 `v0.8.002-draft` 这类 draft 周期（允许可选第三段数字）。
5. 不得跳号伪装进度；不得把未发布候选写成已发布 tag。

## 当前序列

| Version | Theme |
|---|---|
| `v0.8` | ALREADY + 首批 KEEP-EXT（04-03 / 05-03） |
| `v0.8.001` | KEEP-EXT 批次：01-03 / 02-03 / 03-03 / 06-03 |
| `v0.8.002` | KEEP-EXT 收尾批次：07-03 / 08-03 / 09-03 / 10-03 |
| `v0.8.003` | 度量/发布卫生：驾驶舱同步、draft 周期、patch 文档 |
| `v0.8.004` | PDF 封面全出血与公式排版修复 |
| `v0.8.005` | README 开篇致谢 ai-agent-book 与 specs.md |
| `v0.8.006` | README 三阶段转化、结构与信任优化 |
| `v0.8.010` | 官方来源三角、workflow 映射与中文章节摘要增补 |
| `v0.9` | **新 minor 主题线**：英文出版物 + Carbon 可视化 GitHub Pages |
| `v0.9.001` | 英文书稿构建脊柱（locale、源树、CI） |
| `v0.9.002` | 英文 Part 0 + CH01–03 |
| `v0.9.003` | 英文 CH04–06 |
| `v0.9.004` | 英文 CH07–10 + 首次英文 Release PDF/HTML |
| `v0.9.005` | **双语 Release**：zh/en 各 HTML+PDF 四类 GitHub Release 资产 |
| `v0.9.005`（原规划） | Carbon 站点信息架构（已在 v0.9.005–008 Loop 提前合入 main） |
| `v0.9.006` | 可视化章节阅读器 v1 |
| `v0.9.007` | 中英切换与 a11y |
| `v0.9.008` | Pages 阅读站与 Release 构建同源 |

`v0.8.011` 及「以真实 Reader 反馈为下一稿主题」的规划 **已取消**；`READER-RESPONSES` 仍为 known-gap，不驱动 tag 主题。详见 [`v0.9-roadmap.md`](v0.9-roadmap.md)。
