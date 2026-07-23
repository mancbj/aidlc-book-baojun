# Pages Publish Gate Review

> D11-T02 验收记录：确认 GitHub Pages 发布树能标注来源提交，并能在本地复现。

## 1. 发布入口

- Workflow： [`.github/workflows/pages.yml`](../../.github/workflows/pages.yml)
- 构建脚本： [`scripts/prepare_pages.py`](../../scripts/prepare_pages.py)
- Workflow 总说明： [`.github/workflows/README.md`](../../.github/workflows/README.md)
- 发布/Pages 说明： [`docs/RELEASE-AUTOMATION.md`](../../docs/RELEASE-AUTOMATION.md)

## 2. 来源标注链路

`pages.yml` 在构建 Pages 树时显式传入：

```text
--commit-sha "$GITHUB_SHA"
--workflow-run "$GITHUB_RUN_ID"
```

`scripts/prepare_pages.py` 会把同一组来源信息写入两个位置：

- `index.html`：可见的发布成功页，显示 `Source commit`、`Source facts`、`Generated at` 和 `Workflow run`。
- `publish-manifest.json`：机器可读发布清单，包含 `commit_sha`、`source_id`、`generated_at`、`workflow_run`、入口文件和文件哈希。

## 3. 本地验收命令

```text
python3 scripts/prepare_pages.py \
  --output TEMP/pages \
  --generated-at 2026-07-23T03:20:00Z \
  --commit-sha D11T02-test-sha \
  --workflow-run D11T02-test-run
```

验收结果：

- `index.html` 包含 `Source commit`。
- `index.html` 包含测试提交 `D11T02-test-sha`。
- `publish-manifest.json.commit_sha` 等于 `D11T02-test-sha`。
- `publish-manifest.json.entrypoint` 等于 `site/index.html`。
- Pages 构建树内部链接检查通过：57 个文件、495 条内部链接、0 错误。

## 4. 安全与降级

- `validate` job 和 `build` job 默认只读。
- `deploy` job 只在构建成功后申请 `pages: write` 与 `id-token: write`。
- `record` job 的 `contents: write` 只用于 allow-listed 进度记录；分支保护阻止推送时保留 `progress-record` artifact。
- Pages 构建树写入 `.nojekyll`，并拒绝覆盖没有 `.aidlc-generated` 标记的人工目录。

## 5. D11-T02 结论

成功页面已经标注来源提交；即使 GitHub Pages 未启用或部署环境不可用，维护者也可以通过本地构建树和 `publish-manifest.json` 审计本次发布来源。
