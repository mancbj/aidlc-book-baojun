---
id: 001-scaffold-repository-fact-source
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 001-scaffold-repository-fact-source

## User Story

**As a** 作者
**I want** 获得职责清晰的写作仓库骨架和权威事实源
**So that** 书稿、计划、进度、脚本与生成产物不会混在一起

## Acceptance Criteria

- [ ] **Given** 仓库处于初始化状态，**When** 执行骨架创建后，**Then** 存在 book、docs、planning、progress、scripts、tests、writer-chats 和 .github/workflows 的职责说明
- [ ] **Given** 新协作者打开 README 时，**When** 执行对应动作，**Then** 能找到定位、目标读者、核心公式、章节、实验、构建和贡献入口
- [ ] **Given** 生成器运行时，**When** 只从版本化事实源读取数据，**Then** 生成文件被明确标注且不反向成为人工输入

## Technical Notes

- **Related Requirements**: FR-1
- 复用现有行动指南建议的 book、chapter、scripts 和 writer-chats 分层
- 所有事实源必须可由 Git diff 审阅

## Dependencies

### Requires

- None

### Enables

- 002-define-fourteen-day-roadmap
- 003-define-task-schema-and-status
- 005-create-chapter-factory-template
- 006-create-experiment-governance
- 012-create-github-collaboration-templates

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 目标目录已存在 | 保留现有内容，只补缺失目录和说明 |
| 生成目录被人工修改 | 校验给出警告并指出权威源文件 |

## Out of Scope

- 填充十章完整正文
- 迁移参考仓库全部代码
