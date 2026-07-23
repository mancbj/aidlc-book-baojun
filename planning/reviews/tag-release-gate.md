# Tag Release Gate Review

> D11-T03 验收记录：确认版本标签链路能生成候选产物和 Release Notes，并在发布前保留 readiness 门禁。

## 1. 发布入口

- Workflow： [`.github/workflows/release.yml`](../../.github/workflows/release.yml)
- 候选包脚本： [`scripts/prepare_release.py`](../../scripts/prepare_release.py)
- Release Notes 脚本： [`scripts/render_release_notes.py`](../../scripts/render_release_notes.py)
- Readiness 门禁： [`scripts/check_release_readiness.py`](../../scripts/check_release_readiness.py)
- 发布运行手册： [`docs/V0.1-RELEASE-RUNBOOK.md`](../../docs/V0.1-RELEASE-RUNBOOK.md)

## 2. Tag Release 链路

`release.yml` 在 `push.tags: ["v*"]` 时启动：

1. 解析并校验版本号，只接受 `vMAJOR.MINOR[.PATCH][-suffix]`。
2. 运行 `python3 scripts/ci_check.py --budget-seconds 60`。
3. 运行 v0.1 readiness，并始终上传 readiness 或 blocker 报告。
4. 只有 readiness 为 `ready` 时生成 Release Notes。
5. 使用 `scripts/prepare_release.py` 构造不可变候选包。
6. 上传 `release-candidate` artifact。
7. 发布前检查同名 Release 是否已存在；存在则 `refusing overwrite`。
8. 创建 draft GitHub Release，不自动公开 published release。

## 3. 本地候选包 smoke test

本地使用人工 fake-ready readiness 只验证打包机械链路；它不是 v0.1 发布授权，也不会改变真实 readiness。

命令形态：

```text
python3 scripts/prepare_release.py v0.1-d11t03 \
  --output TEMP/candidate \
  --readiness TEMP/readiness.json \
  --release-notes TEMP/release-notes.md \
  --generated-at 2026-07-23T03:32:00Z \
  --commit-sha SOURCE_ID
```

验收结果：

- `release-manifest.json.version` 等于 `v0.1-d11t03`。
- `release-manifest.json.commit_sha` 等于当前 source identity。
- HTML 候选 zip 生成，且结构校验通过。
- HTML zip 包含 Pages 根入口和 `site/index.html` 驾驶舱。
- `release-notes.md` 存在并进入候选目录。
- PDF 未提供时 manifest 明确记录 `skipped`，不创建伪 PDF。

## 4. 安全与不可变性

- `release.yml` 默认 `contents: read`。
- 只有 `publish` job 申请 `contents: write`，用于创建 draft Release。
- Tag 或手动 workflow 都不会跳过 readiness 构建正式候选。
- 同名 Release 存在时拒绝覆盖。
- 真正激活下一周期只接受后续 `release.published` 事件，不接受 draft、tag push 或本地 smoke test。

## 5. D11-T03 结论

版本标签发布链路已配置：ready 时可以生成候选 HTML zip、`release-manifest.json` 和 Release Notes；blocked 时只保留 readiness/blocker 报告，不会冒充发布。
