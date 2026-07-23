---
id: 016-establish-writing-review-feedback-loop
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: should
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 004-github-writing-system-ui
implemented: true
---

# Story: 016-establish-writing-review-feedback-loop

## User Story

**As a** 作者
**I want** 把写作对话、审校意见和试读反馈变成决策或任务
**So that** 每次发布都能推动下一轮改进

## Acceptance Criteria

- [ ] **Given** 完成每日写作时，**When** 执行对应动作，**Then** 关键提示词、取舍和修订摘要可保存到 writer-chats 或决策记录
- [ ] **Given** 样章进入审阅时，**When** 执行对应动作，**Then** 技术、重复、结构、术语和实验对应检查均有结论
- [ ] **Given** 试读反馈进入仓库时，**When** 每条有效意见被标为接受、拒绝或延期，**Then** 并记录理由
- [ ] **Given** 反馈被接受时，**When** 执行对应动作，**Then** 生成或关联一个带验收标准的任务
- [ ] **Given** v0.1 前存在供 3 位试读者使用的 README 试读/复现说明和反馈模板，**When** 执行对应动作，**Then** v0.1 前存在供 3 位试读者使用的 README 试读/复现说明和反馈模板

## Technical Notes

- **Related Requirements**: FR-10
- 避免保存包含秘密或个人敏感信息的完整原始对话
- 反馈统计服务质量改进，不以数量替代判断

## Dependencies

### Requires

- 005-create-chapter-factory-template
- 006-create-experiment-governance
- 012-create-github-collaboration-templates

### Enables

- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 匿名反馈无法追问 | 仍记录证据与决策，但作者可为 anonymous |
| 相互冲突的反馈 | 拆成独立决策并记录权衡 |

## Out of Scope

- 自动接受所有反馈
- 保存外部平台的敏感原始数据
