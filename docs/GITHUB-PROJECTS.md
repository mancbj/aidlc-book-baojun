# GitHub Projects Projection

## 原则

Projects 是 `progress/tasks.json` 的单向投影，不是事实源。默认命令只生成计划或降级报告，不访问网络：

字段、视图、过滤和排序的完整设计稿见 [`planning/github-project.md`](../planning/github-project.md)。

```text
python3 scripts/sync_github_project.py \
  --report progress/generated/project-sync-report.json
```

只有同时提供目标仓库、Project、Token 和显式 `--apply` 才会产生远程写入。Token 只从环境变量读取，不写日志或 artifact。

## Fields

先按 `planning/github-project.json` 创建：Status、Priority、Type、Day、Chapter、Experiment、Milestone、Artifact、Task ID。单选项名称必须完全一致。

## Views

1. Board：Board layout，按 Status 分组，Priority/Day 排序。
2. Roadmap：Roadmap layout，覆盖 Day 1–14。
3. Chapters：Table，按 Chapter 分组，过滤空值。
4. Experiments：Table，Type = Experiment，按 Experiment 分组。

GitHub Projects V2 当前不为所有 view 配置提供稳定自动化接口，因此视图采用可执行人工清单，字段和 item 由同步器检查/投影。

## Stable Identity

每个投影 Issue 包含：

```text
<!-- aidlc-task:D01-T01 -->
```

同步器在创建前索引全部 marker；重复 marker 会进入 divergence 并停止，不会创建第三项。

## Apply

```text
export PROJECT_TOKEN=***
python3 scripts/sync_github_project.py \
  --repository OWNER/REPO \
  --project-owner OWNER \
  --project-number 1 \
  --project-owner-type user \
  --apply \
  --report .artifacts/project-sync-report.json
```

组织 Project 使用 `--project-owner-type organization`。Token 需要读取/写入目标 repository Issues 与 Project V2 的最小权限。

## Degradation and Divergence

- 缺少 remote/owner/number/Token：`degraded`，零网络、零事实修改。
- dry-run：输出 42 个稳定 ID，零网络、零事实修改。
- 403 或网络错误：输出 `degraded` 报告；若错误发生在部分写入后，标记 `partial_remote_changes_possible`，要求先按 Task ID 审计远端。
- 字段缺失、重复 marker 或远程 Status 分叉：`diverged` 并停止。
- 仓库事实确认权威后，维护者可显式使用 `--force-reproject`；它只覆盖 Project 投影，不反写 JSON。
- Project item 被归档或字段重命名时，重新检查配置，不从远程推测仓库状态。
