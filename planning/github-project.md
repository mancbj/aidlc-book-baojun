# GitHub Projects View Plan

> D10-T03 产物：定义 GitHub Projects V2 的字段、视图和单向同步复现步骤。

## 1. 设计目标

GitHub Projects 用来给协作者提供鸟瞰视图：当前做什么、14 天路线走到哪里、哪些章节和实验正在推进。它不是事实源，不反向决定任务状态。

权威关系：

- 任务事实源：[`progress/tasks.json`](../progress/tasks.json)
- 章节事实源：[`progress/chapters.json`](../progress/chapters.json)
- 实验事实源：[`progress/experiments.json`](../progress/experiments.json)
- Project 机器配置：[`planning/github-project.json`](github-project.json)
- Projects 运行说明：[`docs/GITHUB-PROJECTS.md`](../docs/GITHUB-PROJECTS.md)
- 标签与里程碑总规则：[`planning/github-taxonomy.md`](github-taxonomy.md)

## 2. 字段配置

在 GitHub Project V2 中创建以下 9 个字段。字段名和单选项必须与 [`planning/github-project.json`](github-project.json) 完全一致，大小写也要一致。

| 字段 | 类型 | 选项 / 格式 | 来源 |
|---|---|---|---|
| `Status` | Single select | `Backlog`, `Ready`, `In Progress`, `Review`, `Done`, `Blocked` | `tasks[].status` 经 `status_mapping` 投影 |
| `Priority` | Single select | `Must`, `Should`, `Could` | `tasks[].priority` |
| `Type` | Single select | `Writing`, `Experiment`, `Engineering`, `Review`, `Release` | `tasks[].type` |
| `Day` | Number | `1`–`14` | `tasks[].day` |
| `Chapter` | Text | 章节 ID 或空值 | `tasks[].chapter` |
| `Experiment` | Text | 实验 ID 或空值 | `tasks[].experiment` |
| `Milestone` | Text | `v0.0.1` 或 `v0.1` | Day 1–7 → `v0.0.1`，Day 8–14 → `v0.1` |
| `Artifact` | Text | 逗号分隔的仓库相对路径 | `tasks[].artifacts[].path` |
| `Task ID` | Text | `D01-T01` 形式的稳定 ID | `tasks[].id` |

## 3. 视图配置

### Board

用途：日常推进看板，回答“现在卡在哪里、下一步谁做什么”。

- Layout：Board
- Group by：`Status`
- Sort：`Priority` → `Day`
- 可选过滤：`Status` is not `Done`
- 使用建议：维护者每日先看 `Blocked` 与 `In Progress`，再看 `Backlog` 中 priority 为 `Must` 的项。

### Roadmap

用途：14 天 v0.1 路线鸟瞰，回答“哪一天的计划正在超前或滞后”。

- Layout：Roadmap 或 Table
- Primary ordering：`Day`
- Sort：`Day` → `Priority`
- Group by：`Milestone`
- 可选切片：Day 1–7 对应 `v0.0.1`，Day 8–14 对应 `v0.1`
- 使用建议：如果 GitHub Roadmap 需要日期字段，可先以 `Day` 数字字段保留节奏；正式公开仓库后再增加 `Planned Date` 字段，不替代 `Day`。

### Chapter / Chapters

用途：章节生产线鸟瞰，回答“哪些章节已有任务、哪些章节缺证据”。

- Layout：Table
- Group by：`Chapter`
- Filter：`Chapter` is not empty
- Sort：`Chapter` → `Status` → `Priority`
- 使用建议：章节状态仍以 [`progress/chapters.json`](../progress/chapters.json) 为准；Project 只显示与章节相关的任务投影。

### Experiment / Experiments

用途：实验治理鸟瞰，回答“哪些实验已经进入任务、证据链在哪里”。

- Layout：Table
- Group by：`Experiment`
- Filter：`Type` = `Experiment`
- Sort：`Experiment` → `Status` → `Priority`
- 使用建议：实验池完整性仍以 [`progress/experiments.json`](../progress/experiments.json) 为准；Project 只显示被任务引用的实验。

## 4. 手工复现步骤

GitHub Projects V2 对 view layout 的自动化接口并不稳定，因此本仓库把“字段和 item 投影”自动化，把“视图创建”保留为可执行人工清单。

1. 在目标仓库或组织中创建 Project V2。
2. 按“字段配置”创建 9 个字段，确保名称与选项完全一致。
3. 创建 `Board` 视图，并设置 Board layout、`Status` 分组、`Priority`/`Day` 排序。
4. 创建 `Roadmap` 视图，并按 `Day` 和 `Milestone` 展开 14 天计划。
5. 创建 `Chapters` 视图，设置 `Chapter is not empty`，按 `Chapter` 分组。
6. 创建 `Experiments` 视图，设置 `Type = Experiment`，按 `Experiment` 分组。
7. 先执行 dry-run，确认任务 ID 和字段投影：

   ```text
   python3 scripts/sync_github_project.py \
     --repository OWNER/REPO \
     --project-owner OWNER \
     --project-number 1 \
     --project-owner-type user \
     --report progress/generated/project-sync-report.json
   ```

8. 只有在维护者确认目标仓库、Project 和权限后，才显式执行 apply：

   ```text
   export PROJECT_TOKEN=***
   python3 scripts/sync_github_project.py \
     --repository OWNER/REPO \
     --project-owner OWNER \
     --project-number 1 \
     --project-owner-type user \
     --apply \
     --report progress/generated/project-sync-report.json
   ```

## 5. 同步边界

- 默认模式是 dry-run：不访问 GitHub、不写远端、不修改事实源。
- `--apply` 是唯一允许远端写入 Issue / Project item / Project 字段投影的入口。
- `Task ID` 和 Issue body 中的 `<!-- aidlc-task:Dxx-Txx -->` 是稳定身份标记。
- 发现重复 marker、字段缺失或远端 `Status` 与仓库事实源冲突时，同步器必须停止并报告 `diverged`。
- 维护者确认仓库事实源权威后，才可使用 `--force-reproject` 覆盖远端 Project 投影。
- Token 只从环境变量读取，不写入日志、报告或仓库文件。

## 6. D10-T03 验收清单

- `Board` 视图可复现：按 `Status` 看当前推进状态。
- `Roadmap` 视图可复现：按 `Day` 和 `Milestone` 看 14 天路线。
- `Chapter / Chapters` 视图可复现：按 `Chapter` 看章节任务。
- `Experiment / Experiments` 视图可复现：按 `Experiment` 看实验任务。
- 字段契约可校验：`python3 scripts/validate_github_config.py`。
- 同步器可 dry-run：`python3 scripts/sync_github_project.py --repository OWNER/REPO --project-owner OWNER --project-number 1 --report progress/generated/project-sync-report.json`。
