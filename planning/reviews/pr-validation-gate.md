# Pull Request Validation Gate Review

> D11-T01 验收记录：确认 Pull Request 门禁能阻止坏数据，并且 Fork PR 不读取秘密。

## 1. 门禁入口

- GitHub Workflow： [`.github/workflows/validate.yml`](../../.github/workflows/validate.yml)
- 本地等价入口： [`scripts/ci_check.py`](../../scripts/ci_check.py)
- PR 正文元数据检查： [`scripts/validate_pr_metadata.py`](../../scripts/validate_pr_metadata.py)
- 运行手册： [`docs/CI-RUNBOOK.md`](../../docs/CI-RUNBOOK.md)

## 2. 安全边界

`validate.yml` 使用：

- `on: pull_request`
- 顶层 `permissions: contents: read`
- 不使用 `pull_request_target`
- 不引用 `secrets.*`
- 第三方 Actions 锁定到 40 位提交 SHA

因此 Fork PR 只运行只读校验，不进入特权上下文，不读取发布、Pages 或 Project 相关 secret。

## 3. 阻止坏 PR 正文

本地负例：

```text
## 验收
- [ ] 待完成
```

命令：

```text
python3 scripts/validate_pr_metadata.py --body-file BAD_PR_BODY --required
```

结果：失败，原因包括缺少 Task ID、缺少 `## 测试与构建`、缺少 `## 产物`，且没有任何 `- [x]` 已确认项。

## 4. 接受最小合格 PR 正文

本地正例：

```text
## 关联任务
D11-T01

## 产物
.github/workflows/validate.yml

## 测试与构建
- [x] python3 scripts/ci_check.py --budget-seconds 60

## 验收
- [x] 坏数据 PR 被阻止且 Fork 不读取秘密
```

命令：

```text
python3 scripts/validate_pr_metadata.py --body-file GOOD_PR_BODY --required
```

结果：通过，检测到 1 个有效 Task ID。

## 5. D11-T01 结论

- 坏数据 PR 会被 `pr-metadata` 门禁阻止。
- Fork PR 不读取秘密，且不会获得写权限。
- 事实、反馈、GitHub 配置、unittest、生成 dry-run 和内部链接仍通过同一个 `scripts/ci_check.py` 入口执行。
