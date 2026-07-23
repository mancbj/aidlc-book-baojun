---
id: 011-add-dashboard-drilldowns-accessibility
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 002-github-writing-system-ui
implemented: true
---

# Story: 011-add-dashboard-drilldowns-accessibility

## User Story

**As a** 作者或协作者
**I want** 从总览下钻任务并在不同设备上使用驾驶舱
**So that** 鸟瞰不是只读海报，而是可行动入口

## Acceptance Criteria

- [x] **Given** 点击时间线、章节、实验或阻塞项时，**When** 执行对应动作，**Then** 能到达对应任务、产物路径或 GitHub 链接
- [x] **Given** 在 360px 宽移动视口和桌面视口中，**When** 执行对应动作，**Then** 核心指标与下一动作无水平溢出
- [x] **Given** 仅使用键盘时，**When** 执行对应动作，**Then** 主要导航、过滤器和详情链接可获得焦点并激活
- [x] **Given** 状态同时使用文字或图形符号表达，**When** 执行对应动作，**Then** 关闭颜色后仍可区分
- [x] **Given** 首次阅读 README 的用户在 30 秒内能定位当前阶段、阻塞和下一项 Must，**When** 执行对应动作，**Then** 首次阅读 README 的用户在 30 秒内能定位当前阶段、阻塞和下一项 Must

## Technical Notes

- **Related Requirements**: FR-4 / NFR-4 / NFR-5
- 保留现有响应式断点并补充语义标签与焦点样式
- 不以动画作为理解状态的必要条件

## Dependencies

### Requires

- 010-render-birdseye-dashboard

### Enables

- 014-configure-pages-and-release-workflows

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| GitHub URL 尚未配置 | 显示仓库内相对路径而不是死链 |
| 事件列表很长 | 默认展示最近事件并提供静态完整日志链接 |

## Out of Scope

- 完整 WCAG 审计认证
- 复杂图表编辑功能
