---
id: 005-create-chapter-factory-template
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 005-create-chapter-factory-template

## User Story

**As a** 作者
**I want** 让每章沿同一条六阶段生产线推进
**So that** 章节结构、实验和图表缺口能被快速识别

## Acceptance Criteria

- [ ] **Given** 创建新章节时，**When** 执行对应动作，**Then** 模板包含 Question、Framework、Example、Experiment、Figure、Review 六阶段
- [ ] **Given** 章节声明影响实践的观点时，**When** 执行对应动作，**Then** 至少关联实验、复现指南、图表或读者练习之一
- [ ] **Given** 章节进入 Review 时，**When** 执行对应动作，**Then** 审校清单覆盖技术正确性、重复度、结构连贯性、术语一致性和实验对应
- [ ] **Given** 聚合章节状态时，**When** 执行对应动作，**Then** 能够返回首个未完成阶段作为下一缺口

## Technical Notes

- **Related Requirements**: FR-7
- 模板应能服务十章目录，但 v0.1 只要求一个样章达到可读标准
- 状态字段与 Task 状态模型分离但可关联

## Dependencies

### Requires

- 001-scaffold-repository-fact-source

### Enables

- 016-establish-writing-review-feedback-loop
- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 章节暂时没有实验 | 必须标注复现指南、图表或练习，且说明后续实验落点 |
| 章节顺序调整 | ID 稳定，显示顺序单独配置 |

## Out of Scope

- 自动写出章节正文
- 强制所有章节使用相同篇幅
