---
id: 015-define-project-views-and-sync
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22Z
assigned_bolt: 003-github-writing-system-ui
implemented: true
---

# Story: 015-define-project-views-and-sync

## User Story

**As a** 作者
**I want** 在 GitHub Projects 中按 Board、Roadmap、章节和实验查看同一计划
**So that** 远程协作时也能鸟瞰进度

## Acceptance Criteria

- [x] **Given** Project 字段和视图说明包含 Status、Priority、Type、Day、Chapter、Experiment、Milestone 和 Artifact，**When** 执行对应动作，**Then** Project 字段和视图说明包含 Status、Priority、Type、Day、Chapter、Experiment、Milestone 和 Artifact
- [x] **Given** Board 视图按状态分列，**When** Roadmap 视图覆盖 Day 1–14，**Then** 章节/实验视图按对应字段分组
- [x] **Given** 同步过程能用稳定任务 ID 关联仓库事实与 Project item，**When** 执行对应动作，**Then** 重复运行不创建重复项
- [x] **Given** 缺少 Project Token 或权限时，**When** 执行对应动作，**Then** 同步明确降级且不修改仓库事实源
- [x] **Given** 同步后检测到状态分叉时，**When** 报告差异并要求选择权威方向，**Then** 不静默覆盖

## Technical Notes

- **Related Requirements**: FR-6
- GitHub Projects 是投影而非事实源
- 优先提供可执行配置清单，API 自动化可在权限明确后启用

## Dependencies

### Requires

- 012-create-github-collaboration-templates
- 003-define-task-schema-and-status

### Enables

- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Project 字段被远程重命名 | 同步停止并指出预期字段 |
| 任务被远程归档 | 仓库任务保持不变并报告投影差异 |

## Out of Scope

- 把 Project 变成唯一权威源
- 支持多个组织间双向同步
