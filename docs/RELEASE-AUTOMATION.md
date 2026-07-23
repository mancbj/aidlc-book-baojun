# Release Automation

## Readiness Gate

```text
python3 scripts/check_release_readiness.py
```

门禁无论通过或阻断都会更新 `releases/v0.1-rc/readiness.json` 和 `readiness.md`。只有 `status=ready` 且 source 与当前事实完全一致，才允许生成可发布的 Release Notes 和候选包。`--allow-blocked` 只用于本地查看排序缺口，不代表批准发布。

## Local Candidate

```text
python3 scripts/render_release_notes.py --require-ready
python3 scripts/prepare_release.py v0.1 \
  --readiness releases/v0.1-rc/readiness.json \
  --release-notes releases/v0.1-rc/release-notes.md
```

输出位于 `.artifacts/release/v0.1/`：HTML 站点 zip、release manifest 和 Release Notes 候选。

HTML 是必交产物。PDF 只有在独立构建、打开检查和内容验证完成后才能通过 `--pdf path/to/book.pdf` 加入；脚本还会检查 `%PDF-` header 和 `%%EOF`，拒绝仅改后缀的占位文件。未提供 PDF 时 manifest 明确记录 `skipped`，不会创建伪 PDF。

## Tag Workflow

`release.yml` 只接受 `vMAJOR.MINOR[.PATCH][-suffix]`。它先运行核心 CI 和 v0.1 readiness，始终上传 readiness 或排序阻断报告；只有门禁通过才构造候选。工作流随后检查同名 Release 不存在，最后以 draft 形式创建并上传资产。

D11-T03 的本地候选包 smoke test 与安全边界记录见 [`planning/reviews/tag-release-gate.md`](../planning/reviews/tag-release-gate.md)。

正式发布前人工确认：

- 标签指向预期 commit。
- manifest 的 SHA、生成时间和文件哈希完整。
- v0.1 Must 任务和人工审阅门禁通过。
- PDF 状态与实际资产一致。
- Release Notes 已说明已知缺口和反馈入口。

重复标签或已有正式 Release 不允许覆盖。

## Published Release and Next Cycle

创建 draft 不等于公开发布。维护者完成最终审阅并把 `v0.1` draft 公开后，`post-release.yml` 才响应真实的 `release.published` 事件：

- 保存不可伪造的发布回执；
- 把 v0.2 从 preview 切换为 active；
- 将已接受反馈和未关闭缺口带入下一周期；
- 自动生成事件、快照、变更日志和驾驶舱；
- 通过 Pull Request 提交变更，权限不足时保留 30 天可恢复 artifact。

普通本地命令、tag push 和 draft Release 都不能激活下一周期。

Pages 构建树包含只读的 `.github` 配置证据并写入 `.nojekyll`，因此驾驶舱可以直接下钻到 Issue、PR 和 workflow 定义；这些公开文件不得包含 secret 或个人信息。

Pages 根入口 `index.html` 是发布成功页，会显示 `Source commit`、`Source facts`、生成时间和 workflow run，再链接到 `site/index.html` 驾驶舱。D11-T02 的本地验收记录见 [`planning/reviews/pages-publish-gate.md`](../planning/reviews/pages-publish-gate.md)。

## Release Manifest Contract

`release-manifest.json` 是候选产物清单，字段固定为：

| Field | Meaning |
|---|---|
| `schema_version` | 清单格式版本 |
| `version` | 已校验的 `vMAJOR.MINOR[.PATCH][-suffix]` |
| `source_id` / `commit_sha` | 事实来源身份与发布提交 |
| `generated_at` | 带时区的 UTC 生成时间 |
| `html` | `included`、文件名、SHA-256、字节数和页面文件数 |
| `pdf` | `included` 及哈希，或 `skipped`、原因与重试方法 |
| `release_notes` | 同一候选中的说明文件名 |
| `readiness` | 门禁状态、事实来源和 blocker 数量；开发候选可为空 |

候选目录只能由带 `.aidlc-generated` 标记的构建替换；脚本拒绝覆盖人工目录。正式 Release 已存在时，workflow 在上传前停止。

HTML zip 的 entry 时间统一取 manifest 的 UTC `generated_at`，文件权限固定。相同事实、版本、commit 和生成时间应得到逐字节相同的 archive 与 SHA-256。
