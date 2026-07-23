---
id: 003-define-task-schema-and-status
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 003-define-task-schema-and-status

## User Story

**As a** 作者
**I want** 用统一字段描述所有写作和工程任务
**So that** 进度可以被可靠聚合、校验和展示

## Acceptance Criteria

- [ ] **Given** 创建任务时，**When** 执行对应动作，**Then** 缺少 ID、类型、阶段、状态、优先级、负责人、日期、依赖、产物、验收或更新时间任一必需字段会校验失败
- [ ] **Given** 更新状态时，**When** 执行对应动作，**Then** 只有 backlog、ready、in-progress、review、done、blocked 被接受
- [ ] **Given** 任务进入 done 时，**When** 执行对应动作，**Then** 验收清单全部通过且声明的产物存在
- [ ] **Given** 任务进入 blocked 时，**When** 执行对应动作，**Then** 阻塞原因和解除阻塞下一动作均非空

## Technical Notes

- **Related Requirements**: FR-3
- 任务模型优先选择 Python 标准库可解析的格式
- 状态词需要在 README 或 planning 文档中解释

## Dependencies

### Requires

- 001-scaffold-repository-fact-source

### Enables

- 004-validate-task-and-artifact-integrity
- 007-aggregate-progress-metrics
- 008-record-key-update-events
- 012-create-github-collaboration-templates

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 未知任务类型 | 校验失败并列出允许值 |
| 任务没有依赖 | 使用空数组而不是省略字段 |

## Out of Scope

- 自动决定任务优先级
- 个人工时精确计费
