---
id: 017-prepare-v0-1-release
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 004-github-writing-system-ui
implemented: true
---

# Story: 017-prepare-v0-1-release

## User Story

**As a** 作者
**I want** 在 Day 14 形成可公开试读、可复现、可追溯的 v0.1
**So that** 项目获得真实时间锚点和外部反馈入口

## Acceptance Criteria

- [ ] **Given** 到 Day 14 时，**When** 执行对应动作，**Then** 至少一个样章达到可读标准、十章结构存在、一个实验可复现、一张核心图存在且构建链可运行
- [ ] **Given** v0.1 候选通过任务数据、测试、链接、驾驶舱和书稿构建检查，**When** 执行对应动作，**Then** v0.1 候选通过任务数据、测试、链接、驾驶舱和书稿构建检查
- [ ] **Given** Release Notes 列出新增内容、实验状态、已知缺口、关键指标、来源提交和下一版本目标，**When** 执行对应动作，**Then** Release Notes 列出新增内容、实验状态、已知缺口、关键指标、来源提交和下一版本目标
- [ ] **Given** 发布入口包含 HTML/PDF 或明确可下载产物、README、驾驶舱和反馈方式，**When** 执行对应动作，**Then** 发布入口包含 HTML/PDF 或明确可下载产物、README、驾驶舱和反馈方式
- [ ] **Given** 未满足 Must 验收时，**When** 执行对应动作，**Then** 发布被阻止并生成按优先级排序的缺口清单

## Technical Notes

- **Related Requirements**: FR-2 / FR-9 / FR-10
- v0.1 是可试读 MVP，不是十章完稿
- v0.0.1 可在 Day 7 作为内部时间锚点

## Dependencies

### Requires

- 002-define-fourteen-day-roadmap
- 013-configure-pr-validation-workflow
- 014-configure-pages-and-release-workflows
- 015-define-project-views-and-sync
- 016-establish-writing-review-feedback-loop

### Enables

- 018-open-next-update-cycle

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| PDF 工具链暂不可用 | 若需求仍要求 PDF，则阻止正式 v0.1；否则需经明确范围变更批准 |
| 3 位试读者未全部响应 | 发布可列为已知缺口，但反馈入口必须存在 |

## Out of Scope

- 宣布全书完成
- 隐藏已知缺口
