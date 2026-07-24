# Release Evidence

此目录保存候选门禁与真实发布回执，两者不能混用。

- `v0.1-rc/`：v0.1 readiness、排序缺口和 Release Notes candidate。
- `v0.1/release.json`：由真实 GitHub `release.published` 事件生成的 v0.1 回执。
- `v0.2-rc/`：v0.2 readiness、书稿 HTML/PDF 与 Release Notes candidate。
- `v0.2/release.json`：只允许由真实 GitHub `release.published` 事件生成；公开 v0.2 后写入。

查看 [`docs/RELEASE-AUTOMATION.md`](../docs/RELEASE-AUTOMATION.md) 与 [`planning/releases/v0.2.md`](../planning/releases/v0.2.md)。
