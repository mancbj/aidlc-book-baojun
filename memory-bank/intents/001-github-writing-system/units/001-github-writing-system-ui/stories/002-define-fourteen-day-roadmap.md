---
id: 002-define-fourteen-day-roadmap
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 002-define-fourteen-day-roadmap

## User Story

**As a** 作者
**I want** 看到 Day 1–14 的目标、任务、依赖、产物和验收
**So that** 两周压缩计划仍保留从写作到发布的完整闭环

## Acceptance Criteria

- [ ] **Given** 需求基线已确认，**When** 生成路线图后，**Then** Day 1 至 Day 14 每天都有至少一个任务、明确产物和二元验收
- [ ] **Given** 查看 Day 7 里程碑时，**When** 执行对应动作，**Then** 核心公式、目录、仓库、样章提纲、最小实验、构建链和 v0.0.1 均有落点
- [ ] **Given** 查看 Day 14 里程碑时，**When** 执行对应动作，**Then** 样章、核心图、学习路线、审校、反馈入口、v0.1 产物和下一周期均有落点
- [ ] **Given** 容量不足时，**When** 路线图明确保留样章、单实验、核心图、构建链和自动留痕，**Then** 并标出可延期项

## Technical Notes

- **Related Requirements**: FR-2
- 路线图是 8 周指南的 MVP 压缩版，不承诺 14 天写完十章
- 每项行动引用 Story 或后续可执行 Task ID

## Dependencies

### Requires

- 001-scaffold-repository-fact-source

### Enables

- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 执行开始日期改变 | 按相对 Day 重新计算日期，任务依赖保持不变 |
| 某日任务未完成 | 记录影响、替代方案和新落点，不静默顺延 |

## Out of Scope

- 十章全部完成
- 替代日常任务状态跟踪
