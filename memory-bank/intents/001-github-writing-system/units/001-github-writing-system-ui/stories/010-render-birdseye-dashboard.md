---
id: 010-render-birdseye-dashboard
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 002-github-writing-system-ui
implemented: true
---

# Story: 010-render-birdseye-dashboard

## User Story

**As a** 作者
**I want** 在一个静态页面看到两周全局进度和关键更新
**So that** 能从宏观态势快速切换到下一项行动

## Acceptance Criteria

- [x] **Given** 聚合数据有效时，**When** 执行对应动作，**Then** 页面展示总体、当前 Day、倒计时、阶段、Must/Should、更新时间和下一动作
- [x] **Given** 页面展示 14 天时间线、状态分布、章节生产线、实验队列、阻塞项和最近事件，**When** 执行对应动作，**Then** 页面展示 14 天时间线、状态分布、章节生产线、实验队列、阻塞项和最近事件
- [x] **Given** 生成流程运行后，**When** 执行对应动作，**Then** 页面数字全部来自生成数据而非人工复制
- [x] **Given** JavaScript 禁用时，**When** 执行对应动作，**Then** 页面仍显示核心摘要和关键链接
- [x] **Given** 页面延续作者本地行动指南的 IBM Carbon 视觉语言，**When** 执行对应动作，**Then** 页面无需依赖或发布本地行动指南即可独立运行

## Technical Notes

- **Related Requirements**: FR-4
- 可采用独立 progress JSON 加静态回退片段
- 现有指南内容应保留，并增加当前状态层而非整体重写

## Dependencies

### Requires

- 007-aggregate-progress-metrics
- 009-generate-progress-snapshots

### Enables

- 011-add-dashboard-drilldowns-accessibility
- 014-configure-pages-and-release-workflows

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 数据文件缺失 | 显示明确的未生成状态和本地生成命令 |
| 指标为 0 或 100 | 图表和文本均正确显示边界值 |

## Out of Scope

- 复杂实时 WebSocket 更新
- 数据库查询和登录态
