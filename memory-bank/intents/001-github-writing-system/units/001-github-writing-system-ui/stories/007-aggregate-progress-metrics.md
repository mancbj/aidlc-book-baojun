---
id: 007-aggregate-progress-metrics
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 002-github-writing-system-ui
implemented: true
---

# Story: 007-aggregate-progress-metrics

## User Story

**As a** 作者
**I want** 从事实源自动得到当前完成率、阻塞和下一动作
**So that** 无需手工统计即可鸟瞰项目

## Acceptance Criteria

- [x] **Given** 存在有效任务集时，**When** 执行对应动作，**Then** 聚合器输出总完成率、Must/Should 完成率、状态分布、当前 Day 和最新更新时间
- [x] **Given** 存在章节和实验数据时，**When** 执行对应动作，**Then** 输出六阶段章节状态和 SHIP/KEEP-EXT/ALREADY 分布
- [x] **Given** 存在 blocked 任务时，**When** 执行对应动作，**Then** 输出阻塞原因和解除阻塞下一动作
- [x] **Given** 候选下一动作超过一个时，**When** 执行对应动作，**Then** 按 Must、依赖已满足、计划日期和稳定 ID 排序
- [x] **Given** 同一提交重复运行时，**When** 执行对应动作，**Then** 除显式生成时间外得到等价指标

## Technical Notes

- **Related Requirements**: FR-4 / FR-5
- 输出机器可读 JSON 和人可读摘要
- 避免浮点累计误差，百分比规则需固定

## Dependencies

### Requires

- 003-define-task-schema-and-status

### Enables

- 009-generate-progress-snapshots
- 010-render-birdseye-dashboard

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 任务集合为空 | 输出 0% 和初始化提示，不发生除零错误 |
| 任务全部完成 | 下一动作指向发布或下一周期，而非空白 |

## Out of Scope

- 预测真实完成日期
- 根据情绪自动调整优先级
