# GitHub Collaboration

## 权威关系

`progress/tasks.json`、`progress/chapters.json`、`progress/experiments.json` 是状态事实源。Issues、Pull Requests、Milestones 和 Projects 用于协作与投影，不得静默覆盖仓库事实。

## Issue

从 Writing、Experiment、Bug、Feedback 四个 Issue Form 进入。每个表单都要求 Task ID、目标、产物和验收；没有现有任务时使用 `N/A` 并解释，再由维护者决定是否进入 14 天事实源。

标题保留类型前缀，正文保留稳定 ID。一个 Issue 优先只对应一个 Task ID；涉及多个任务时逐项说明产物和验收。

## Pull Request

PR 必须包含：

- 一个或多个 Task ID
- 变更类型与目标
- 仓库相对产物路径
- 本地 CI 与生成 dry-run 结果
- 二元验收、风险和回滚

Fork PR 只运行只读校验，不获取发布或 Project secret。维护者合并前确认事实源与生成物的边界。

## Labels and Milestones

标签、里程碑和使用边界的总说明见 [`planning/github-taxonomy.md`](../planning/github-taxonomy.md)。

标签定义在 [`.github/labels.yml`](../.github/labels.yml)，当前不会自动修改远程标签。目标仓库确定后可人工创建或由后续显式命令同步。

v0.0.1 和 v0.1 的范围与关闭门禁见 [`planning/github-milestones.md`](../planning/github-milestones.md)。

## Local Review

```text
python3 scripts/ci_check.py
python3 scripts/generate_progress.py --dry-run
```

仓库尚未公开、没有 remote 或没有权限时，模板、标签和里程碑仍可在本地审阅，不阻断写作事实系统。
