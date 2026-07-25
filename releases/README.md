# Release Evidence

此目录保存候选门禁与真实发布回执，两者不能混用。

- `v0.1-rc/`：v0.1 readiness、排序缺口和 Release Notes candidate。
- `v0.1/release.json`：由真实 GitHub `release.published` 事件生成的 v0.1 回执。
- `v0.2-rc/`：v0.2 readiness、书稿 HTML/PDF 与 Release Notes candidate。
- `v0.2/release.json`：v0.2 真实 GitHub `release.published` 回执。

查看 [`docs/RELEASE-AUTOMATION.md`](../docs/RELEASE-AUTOMATION.md) 与 [`planning/releases/v0.2.md`](../planning/releases/v0.2.md)。


## Patch-Grain Evidence (v0.8+)

- `v0.8/`、`v0.8.001/`、`v0.8.002/`、`v0.8.003/` …：各版本正式回执 `release.json`
- 对应 `*-rc/`：readiness、Release Notes、书稿 HTML/PDF、scorecard、content-audit
- 版本策略：[`planning/releases/VERSIONING.md`](../planning/releases/VERSIONING.md)
- HTML zip 只存在于 GitHub Release 资产，不进入本目录
