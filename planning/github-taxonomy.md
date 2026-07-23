# GitHub Taxonomy

> D10-T02 产物：定义本书 GitHub 协作层的标签、里程碑和使用边界。

## 1. 权威关系

本仓库采用“仓库事实源 → GitHub 协作投影”的关系：

- [`progress/tasks.json`](../progress/tasks.json)、[`progress/chapters.json`](../progress/chapters.json)、[`progress/experiments.json`](../progress/experiments.json) 是任务、章节和实验状态的事实源。
- [`.github/labels.yml`](../.github/labels.yml) 是标签配置事实源。
- [`planning/github-milestones.md`](github-milestones.md) 是 v0.0.1 与 v0.1 的里程碑范围和关闭门禁事实源。
- GitHub Issues、Pull Requests、Milestones 和 Projects 用于协作、讨论、鸟瞰和追踪，不得静默反向覆盖仓库事实源。

## 2. 标签分组

每个计划内 Issue 应尽量具备：一个 `type:*`、一个 `priority:*`、一个 `phase:*`。如对象明确，可补充一个 `object:*`。只有存在阻塞原因和解除动作时，才使用 `status:blocked`。

| 分组 | 含义 | 来源映射 | 示例 |
|---|---|---|---|
| `type:*` | 工作类型 | `progress/tasks.json[].type` 或 Issue Form 类型 | `type:writing`, `type:experiment`, `type:engineering` |
| `priority:*` | v0.1 优先级 | `progress/tasks.json[].priority` | `priority:must`, `priority:should`, `priority:could` |
| `phase:*` | 14 天计划阶段 | `progress/tasks.json[].phase` | `phase:foundation`, `phase:github`, `phase:release` |
| `object:*` | 主要产物对象 | 章节、实验或专题对象 | `object:chapter`, `object:experiment` |
| `status:*` | 临时协作状态 | 只在事实源存在对应状态时投影 | `status:blocked` |

## 3. 标签清单

| Label | 使用场景 |
|---|---|
| `type:writing` | 书稿正文、章节、图示说明和编辑改写。 |
| `type:experiment` | 可复现实验、实验数据、失败样例和证据链。 |
| `type:engineering` | 脚本、构建、校验、仪表盘和自动化。 |
| `type:review` | 事实审校、技术审校、语言审校和发布前检查。 |
| `type:release` | 版本构建、Release Notes、发布包和发布回滚。 |
| `type:bug` | 可复现缺陷、构建失败、链接错误和数据异常。 |
| `type:feedback` | 读者、协作者或发布后反馈。 |
| `priority:must` | v0.1 必须完成；未完成会阻断发布。 |
| `priority:should` | 重要但可降级；未完成必须在 Release Notes 解释。 |
| `priority:could` | 有余力时完成；不阻断 v0.1。 |
| `phase:foundation` | 核心公式、目录、样章、实验池和基础结构。 |
| `phase:progress` | 进度记录、关键事件、核心图和驾驶舱。 |
| `phase:github` | Issue、PR、标签、里程碑、项目视图和协作自动化。 |
| `phase:release` | 审校、构建、发布、反馈入口和下一周期。 |
| `object:chapter` | 以章节为主要对象的任务或反馈。 |
| `object:experiment` | 以实验为主要对象的任务或反馈。 |
| `status:blocked` | 事实源中已有 blocker reason 与 unblock action 的阻塞项。 |

## 4. 里程碑

### v0.0.1 · Day 7 可读闭环

用途：验证“一个样章 + 一个实验 + 一张图 + 一次构建”能够端到端运行。

关闭条件：

- Day 1–7 的 Must 任务已完成或已明确记录缺口。
- 至少一个可读样章草稿、一个可复现实验、一张核心图和一次 HTML 构建存在。
- 进度快照、关键事件和校验记录可追踪。
- 本地 CI 通过，或失败项有明确 blocker 与解除动作。

### v0.1 · Day 14 可发布版本

用途：交付可公开试读、可复现实验、可追踪进度并能接收反馈的首个版本。

关闭条件：

- v0.1 Must 任务全部完成。
- 没有未解释 blocker。
- 全套 CI 通过。
- 发布产物包含来源 SHA、生成时间、哈希与 Release Notes。
- 人工发布审阅通过。

## 5. 任务到里程碑的映射

- Day 1–7 的任务默认投影到 `v0.0.1 · Day 7 可读闭环`。
- Day 8–14 的任务默认投影到 `v0.1 · Day 14 可发布版本`。
- 如果 Day 1–7 的任务仍是 v0.1 发布阻断项，应同时在 v0.1 发布检查中列为 blocker，而不是只依赖 GitHub milestone 状态。
- `scripts/sync_github_project.py` 的 milestone 投影规则应与上述约定保持一致。

## 6. Issue 与 PR 使用规则

- Issue 从四个表单进入：Writing、Experiment、Bug、Feedback。
- Issue 必须保留 Task ID、产物路径和验收条件；没有现成任务时使用 `N/A` 并解释。
- PR 必须填写 Task ID、产物、测试与构建、验收、风险与回滚。
- 标签和里程碑用于帮助协作者鸟瞰，不替代 [`progress/tasks.json`](../progress/tasks.json) 的二元验收。

## 7. 远端同步边界

当前任务只定义仓库内契约，不自动写入远端 GitHub。目标仓库确定后，可按以下顺序执行：

1. 按 [`.github/labels.yml`](../.github/labels.yml) 创建或同步 labels。
2. 按 [`planning/github-milestones.md`](github-milestones.md) 创建两个 milestones。
3. 依据 [`planning/github-project.md`](github-project.md) 和 [`planning/github-project.json`](github-project.json) 创建项目字段与视图。
4. 运行 `python3 scripts/ci_check.py`，确认本地契约未破坏。

## 8. D10-T02 验收

- 标签体系已定义：见 [`.github/labels.yml`](../.github/labels.yml)。
- v0.0.1/v0.1 完成条件已定义：见 [`planning/github-milestones.md`](github-milestones.md)。
- 协作说明入口已定义：见 [`docs/GITHUB-COLLABORATION.md`](../docs/GITHUB-COLLABORATION.md)。
- PR 契约已定义：见 [`.github/pull_request_template.md`](../.github/pull_request_template.md)。
