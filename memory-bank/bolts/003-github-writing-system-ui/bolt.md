---
id: 003-github-writing-system-ui
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
type: simple-construction-bolt
status: complete
stories:
  - 012-create-github-collaboration-templates
  - 013-configure-pr-validation-workflow
  - 014-configure-pages-and-release-workflows
  - 015-define-project-views-and-sync
created: 2026-07-21T06:52:22Z
started: 2026-07-22T01:53:51Z
completed: "2026-07-22T02:35:33Z"
current_stage: null
stages_completed:
  - plan
  - implement
  - test

requires_bolts:
  - 001-github-writing-system-ui
  - 002-github-writing-system-ui
enables_bolts:
  - 004-github-writing-system-ui
requires_units: []
blocks: false

complexity:
  avg_complexity: 2
  avg_uncertainty: 2
  max_dependencies: 3
  testing_scope: 3
---

# Bolt: 003-github-writing-system-ui

## Overview

把本地可运行的写作系统接入 GitHub 协作、校验、Pages、Release 和 Projects 投影视图。

## Objective

在 Day 9–11 完成远程协作和发布自动化，同时保证权限不足时仓库事实源仍可独立运行。

## Stories Included

- [x] **012-create-github-collaboration-templates**: 创建 GitHub 协作模板与分类体系 (Must)
- [x] **013-configure-pr-validation-workflow**: 配置 Pull Request 校验工作流 (Must)
- [x] **014-configure-pages-and-release-workflows**: 配置 Pages 与版本发布工作流 (Must)
- [x] **015-define-project-views-and-sync**: 定义 GitHub Projects 鸟瞰视图与同步 (Must)

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [x] **1. Plan**: Complete → `implementation-plan.md`
- [x] **2. Implement**: Complete → source files + `implementation-walkthrough.md`
- [x] **3. Test**: Complete → tests + `test-walkthrough.md`

## Expected Outputs

- Issue/PR 模板与标签/里程碑说明
- PR 校验工作流
- Pages 与 Release 工作流
- GitHub Projects 字段和视图配置
- 可降级同步方案

## Dependencies

### Requires

- **001-github-writing-system-ui**：必须完成
- **002-github-writing-system-ui**：必须完成

### Enables

- **004-github-writing-system-ui**

### Unit Dependencies

- None（所有 Stories 位于同一静态前端 Unit）

## Success Criteria

- [x] 所有包含的 Stories 已实现
- [x] 所有 Story 验收标准已满足
- [x] 测试和校验通过
- [x] 产物路径存在并可追溯
- [x] 人工审阅完成

## Notes

GitHub Projects API 权限是不确定项。同步只做投影，不改变仓库事实源的权威性。
