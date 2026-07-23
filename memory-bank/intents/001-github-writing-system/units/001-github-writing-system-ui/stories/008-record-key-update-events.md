---
id: 008-record-key-update-events
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 002-github-writing-system-ui
implemented: true
---

# Story: 008-record-key-update-events

## User Story

**As a** 作者
**I want** 关键更新自动形成可审计事件
**So that** 能回看何时、因何、在哪个提交发生了变化

## Acceptance Criteria

- [x] **Given** 任务从 ready 变为 in-progress、review、done 或 blocked 时，**When** 执行对应动作，**Then** 生成包含时间、对象、前后状态、提交和摘要的事件
- [x] **Given** 章节、实验、里程碑、构建和版本发生已定义变化时，**When** 执行对应动作，**Then** 生成对应事件类型
- [x] **Given** 输入前后事实无关键变化时，**When** 执行对应动作，**Then** 不生成虚假关键事件
- [x] **Given** 新事件追加到历史记录时，**When** 执行对应动作，**Then** 既有事件内容和顺序保持不变

## Technical Notes

- **Related Requirements**: FR-5
- 事件 ID 应稳定并可检测重复
- CI 无前序快照时生成初始化事件而不是伪造逐项历史

## Dependencies

### Requires

- 003-define-task-schema-and-status

### Enables

- 009-generate-progress-snapshots

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 同一提交重复运行 | 通过稳定事件 ID 去重 |
| Git 身份不可用 | 保留 commit 与 workflow actor，可将作者标为 unknown |

## Out of Scope

- 记录每次文字字符级变更
- 替代 Git 提交历史
