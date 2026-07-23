---
id: 013-configure-pr-validation-workflow
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22Z
assigned_bolt: 003-github-writing-system-ui
implemented: true
---

# Story: 013-configure-pr-validation-workflow

## User Story

**As a** 维护者
**I want** 在合并前自动运行数据、测试、链接和生成检查
**So that** 错误状态不会进入主分支并污染驾驶舱

## Acceptance Criteria

- [x] **Given** Pull Request 修改相关文件时，**When** 执行对应动作，**Then** 工作流运行任务数据校验、unittest、内部链接检查和生成冒烟测试
- [x] **Given** 任一 Must 校验失败时，**When** 执行对应动作，**Then** 工作流返回失败并提供文件与修复建议
- [x] **Given** 工作流使用最小只读权限，**When** 执行对应动作，**Then** 来自 Fork 的运行不访问发布秘密
- [x] **Given** 本地文档提供与 CI 等价的关键命令，**When** 执行对应动作，**Then** 本地文档提供与 CI 等价的关键命令
- [x] **Given** MVP 数据规模下纯校验和进度生成在 GitHub Runner 上 60 秒内完成，**When** 执行对应动作，**Then** MVP 数据规模下纯校验和进度生成在 GitHub Runner 上 60 秒内完成

## Technical Notes

- **Related Requirements**: FR-9
- 工作流应允许 workflow_dispatch 便于诊断
- 书稿 PDF 构建可独立成较慢 Job，不计入 60 秒核心目标

## Dependencies

### Requires

- 004-validate-task-and-artifact-integrity
- 009-generate-progress-snapshots

### Enables

- 014-configure-pages-and-release-workflows
- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 只修改文案 | 仍至少运行结构和内部链接检查 |
| 第三方外部链接波动 | 作为 warning，不阻断核心事实校验 |

## Out of Scope

- 自动修复所有错误
- 在 Fork PR 中执行发布
