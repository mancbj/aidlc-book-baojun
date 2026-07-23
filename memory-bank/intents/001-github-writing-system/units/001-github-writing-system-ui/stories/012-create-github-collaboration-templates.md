---
id: 012-create-github-collaboration-templates
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22Z
assigned_bolt: 003-github-writing-system-ui
implemented: true
---

# Story: 012-create-github-collaboration-templates

## User Story

**As a** 协作者
**I want** 用一致的 Issue 和 PR 格式提交工作
**So that** 任务、产物和验收可以自动关联

## Acceptance Criteria

- [x] **Given** 创建写作、实验、缺陷或反馈 Issue 时，**When** 执行对应动作，**Then** 模板要求任务 ID、目标、产物和验收标准
- [x] **Given** 创建 Pull Request 时，**When** 执行对应动作，**Then** 模板要求关联任务、变更类型、测试/构建结果和验收清单
- [x] **Given** 标签说明覆盖类型、优先级、阶段、章节/实验和 blocked，**When** 执行对应动作，**Then** 标签说明覆盖类型、优先级、阶段、章节/实验和 blocked
- [x] **Given** v0.0.1 与 v0.1 里程碑的用途、范围和完成条件被文档化，**When** 执行对应动作，**Then** v0.0.1 与 v0.1 里程碑的用途、范围和完成条件被文档化

## Technical Notes

- **Related Requirements**: FR-6
- 实际远程标签和里程碑创建可由脚本或清单完成
- 仓库尚未公开时模板仍能本地评审

## Dependencies

### Requires

- 001-scaffold-repository-fact-source
- 003-define-task-schema-and-status

### Enables

- 015-define-project-views-and-sync
- 016-establish-writing-review-feedback-loop

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 贡献者不填写任务 ID | PR 校验或人工清单标记缺失 |
| 同一 PR 涉及多个任务 | 允许列表，但每个任务都需对应产物或说明 |

## Out of Scope

- 自动授予仓库权限
- 取代维护者的合并判断
