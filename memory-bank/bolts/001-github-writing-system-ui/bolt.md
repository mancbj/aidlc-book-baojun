---
id: 001-github-writing-system-ui
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
type: simple-construction-bolt
status: complete
stories:
  - 001-scaffold-repository-fact-source
  - 002-define-fourteen-day-roadmap
  - 003-define-task-schema-and-status
  - 004-validate-task-and-artifact-integrity
  - 005-create-chapter-factory-template
  - 006-create-experiment-governance
created: 2026-07-21T06:52:22.000Z
started: 2026-07-21T07:08:32.000Z
completed: "2026-07-21T07:56:12Z"
current_stage: null
stages_completed:
  - name: plan
    completed: 2026-07-21T07:14:12.000Z
    artifact: implementation-plan.md
  - name: implement
    completed: 2026-07-21T07:50:13.000Z
    artifact: implementation-walkthrough.md
  - name: test
    completed: 2026-07-21T07:53:50.000Z
    artifact: test-walkthrough.md
requires_bolts: []
enables_bolts:
  - 002-github-writing-system-ui
requires_units: []
blocks: false
complexity:
  avg_complexity: 2
  avg_uncertainty: 1
  max_dependencies: 1
  testing_scope: 2
---

# Bolt: 001-github-writing-system-ui

## Overview

建立写作系统的仓库事实源、14 天计划、统一任务模型、完整性校验，以及章节和实验模板。

## Objective

在 Day 1–4 形成所有后续聚合、展示和自动化可依赖的稳定文件结构与可验收规则。

## Stories Included

- [ ] **001-scaffold-repository-fact-source**: 搭建仓库事实源 (Must)
- [ ] **002-define-fourteen-day-roadmap**: 定义 14 天 v0.1 路线图 (Must)
- [ ] **003-define-task-schema-and-status**: 定义任务模型与状态流 (Must)
- [ ] **004-validate-task-and-artifact-integrity**: 校验任务与产物完整性 (Must)
- [ ] **005-create-chapter-factory-template**: 创建章节生产线模板 (Must)
- [ ] **006-create-experiment-governance**: 创建实验治理队列 (Must)

## Bolt Type

**Type**: Simple Construction Bolt
**Definition**: `.specsmd/aidlc/templates/construction/bolt-types/simple-construction-bolt.md`

## Stages

- [ ] **1. Plan**: Pending → `implementation-plan.md`
- [ ] **2. Implement**: Pending → source files + `implementation-walkthrough.md`
- [ ] **3. Test**: Pending → tests + `test-walkthrough.md`

## Expected Outputs

- 仓库目录和职责说明
- 14 天 v0.1 执行路线图
- 任务模型与校验器计划
- 章节生产线模板
- 实验治理队列与模板

## Dependencies

### Requires

- None（首个 Bolt）

### Enables

- **002-github-writing-system-ui**

### Unit Dependencies

- None（所有 Stories 位于同一静态前端 Unit）

## Success Criteria

- [ ] 所有包含的 Stories 已实现
- [ ] 所有 Story 验收标准已满足
- [ ] 测试和校验通过
- [ ] 产物路径存在并可追溯
- [ ] 人工审阅完成

## Notes

这是基础 Bolt。路线图必须控制 v0.1 边界，避免把 8 周全部内容机械塞入 14 天。
