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
| `v0.8.003` | （下一 Loop）真实 Reader 反馈或新内容周期 |
