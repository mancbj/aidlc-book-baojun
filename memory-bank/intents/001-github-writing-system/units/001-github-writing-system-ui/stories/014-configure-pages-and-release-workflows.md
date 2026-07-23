---
id: 014-configure-pages-and-release-workflows
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22Z
assigned_bolt: 003-github-writing-system-ui
implemented: true
---

# Story: 014-configure-pages-and-release-workflows

## User Story

**As a** 维护者
**I want** 主分支和版本标签自动生成并发布正确产物
**So that** 进度页和 v0.1 可以持续、可复现地交付

## Acceptance Criteria

- [x] **Given** 主分支校验成功后，**When** 执行对应动作，**Then** 工作流重建 current 进度和驾驶舱并发布 Pages artifact
- [x] **Given** 创建符合版本规则的标签时，**When** 执行对应动作，**Then** 工作流生成 Release Notes 候选和 HTML/PDF 产物入口
- [x] **Given** 构建失败时，**When** 执行对应动作，**Then** 不把最后成功产物标记成当前提交的新结果
- [x] **Given** 发布页面或 Release 元数据包含来源提交 SHA 和生成时间，**When** 执行对应动作，**Then** 发布页面或 Release 元数据包含来源提交 SHA 和生成时间
- [x] **Given** 工作流权限仅在发布 Job 中提升，**When** 执行对应动作，**Then** 其他 Job 保持只读

## Technical Notes

- **Related Requirements**: FR-9
- Pages 和 Release 可拆分工作流但共享校验入口
- 未安装 Pandoc/XeLaTeX 时应明确跳过或失败策略

## Dependencies

### Requires

- 010-render-birdseye-dashboard
- 011-add-dashboard-drilldowns-accessibility
- 013-configure-pr-validation-workflow

### Enables

- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| Pages 未在仓库启用 | 工作流给出设置说明，生成 artifact 仍可下载 |
| 重复推送同一标签 | 拒绝覆盖已有正式 Release |

## Out of Scope

- 购买自定义域名
- 多环境服务器部署
