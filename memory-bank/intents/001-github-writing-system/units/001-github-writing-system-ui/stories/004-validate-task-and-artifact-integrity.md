---
id: 004-validate-task-and-artifact-integrity
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 004-validate-task-and-artifact-integrity

## User Story

**As a** 作者
**I want** 在合并前发现重复、断链和虚假完成
**So that** 驾驶舱数字不会因坏数据失真

## Acceptance Criteria

- [ ] **Given** 任务集合包含重复 ID 时，**When** 执行对应动作，**Then** 校验返回非零状态并列出冲突文件
- [ ] **Given** 任务引用未知依赖或形成循环时，**When** 执行对应动作，**Then** 校验失败并显示依赖链
- [ ] **Given** 任务标记 done 但产物缺失或验收未完成时，**When** 执行对应动作，**Then** 校验失败并指出缺口
- [ ] **Given** 时间戳无时区或事件时间倒序时，**When** 执行对应动作，**Then** 校验失败并给出期望格式

## Technical Notes

- **Related Requirements**: FR-3 / NFR-8
- 使用 unittest 覆盖正常、边界和失败数据
- 错误信息包含文件、字段、错误值和修复建议

## Dependencies

### Requires

- 003-define-task-schema-and-status

### Enables

- 013-configure-pr-validation-workflow

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 外部 URL 暂时不可达 | 记录 warning，不把网络波动当作事实源错误 |
| 可选产物缺失 | 仅在任务明确声明 Must 时阻止 |

## Out of Scope

- 验证正文事实正确性
- 持续监控外部网站可用性
