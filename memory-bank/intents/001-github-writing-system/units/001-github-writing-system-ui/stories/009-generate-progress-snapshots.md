---
id: 009-generate-progress-snapshots
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 002-github-writing-system-ui
implemented: true
---

# Story: 009-generate-progress-snapshots

## User Story

**As a** 作者
**I want** 在关键更新后保存整体状态和人类可读摘要
**So that** 任一里程碑都能被快速复盘

## Acceptance Criteria

- [x] **Given** 主分支推送或手动触发时，**When** 执行对应动作，**Then** 生成包含提交、指标、阻塞和下一动作的快照
- [x] **Given** 检测到关键事件时，**When** 执行对应动作，**Then** 同一次生成更新人类可读变更日志
- [x] **Given** 快照文件名或键能唯一关联提交和时间，**When** 执行对应动作，**Then** 不覆盖不同提交的历史快照
- [x] **Given** 生成失败时，**When** 执行对应动作，**Then** 最后一次成功快照保持不变且进程返回非零状态

## Technical Notes

- **Related Requirements**: FR-5
- 快照与当前聚合结果分离：历史不可变，current 可替换
- 避免无意义快照爆炸，策略在文档中明确

## Dependencies

### Requires

- 007-aggregate-progress-metrics
- 008-record-key-update-events

### Enables

- 010-render-birdseye-dashboard
- 013-configure-pr-validation-workflow

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 同一提交被多次触发 | 复用或验证同一快照，不追加冲突副本 |
| 无关键事件但手动触发 | 允许更新 current 摘要，并明确无状态变化 |

## Out of Scope

- 二进制附件归档
- 永久保存 Actions 临时日志
