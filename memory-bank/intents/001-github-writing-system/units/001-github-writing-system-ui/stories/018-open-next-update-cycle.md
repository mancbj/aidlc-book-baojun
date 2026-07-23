---
id: 018-open-next-update-cycle
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: should
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 004-github-writing-system-ui
implemented: true
---

# Story: 018-open-next-update-cycle

## User Story

**As a** 作者
**I want** 在 v0.1 发布后立即看到下一周期任务
**So that** 发布不会成为项目停摆点

## Acceptance Criteria

- [ ] **Given** v0.1 发布成功时，**When** 执行对应动作，**Then** 生成包含未完成项、接受反馈和下一版本目标的周期入口
- [ ] **Given** 新周期至少安排每周一节、一次实验、一次构建/审校，**When** 执行对应动作，**Then** 并保留每月发布目标
- [ ] **Given** 已完成 v0.1 任务保持历史状态，**When** 执行对应动作，**Then** 不被重置为 backlog
- [ ] **Given** 驾驶舱在发布后把下一动作指向新周期首个依赖已满足的 Must 任务，**When** 执行对应动作，**Then** 驾驶舱在发布后把下一动作指向新周期首个依赖已满足的 Must 任务

## Technical Notes

- **Related Requirements**: FR-10
- 下一周期只建立入口和节奏，不在本 Story 中详细规划全部内容
- 周期编号和版本目标必须可追溯到 v0.1 Release

## Dependencies

### Requires

- 017-prepare-v0-1-release

### Enables

- None

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 没有接受的反馈 | 从已知缺口和未完成 Should 任务生成候选 |
| 下一版本尚未命名 | 默认使用 v0.2 draft，不创建正式标签 |

## Out of Scope

- 自动决定长期书稿方向
- 自动发布下一版本
