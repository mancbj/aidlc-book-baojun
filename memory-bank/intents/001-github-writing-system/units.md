---
intent: 001-github-writing-system
phase: inception
status: units-decomposed
updated: 2026-07-21T06:52:22Z
---

# GitHub Writing System - Unit Decomposition

## Units Overview

项目类型为 `frontend-app`，后端单元已禁用。该 Intent 因此形成一个可独立发布的静态前端单元，仓库事实源、生成脚本和 GitHub 工作流作为同一发布边界内的支持能力，通过多个 Simple Construction Bolts 分阶段建设。

### Unit 1: `001-github-writing-system-ui`

**Description**：交付写作仓库事实源、14 天计划、任务/事件模型、进度生成器、鸟瞰驾驶舱、GitHub 自动化和 v0.1 发布闭环。

**Deliverables**：

- 结构化任务、事件、快照和变更日志
- 14 天 v0.1 路线图及写作/实验模板
- 基于现有 HTML 的静态进度驾驶舱
- 本地校验/生成命令与测试
- GitHub 协作模板、Actions、Projects 配置说明和 Pages/Release 流程
- v0.1 发布清单、反馈回流和下一周期入口

**Dependencies**：

- Depends on：GitHub 仓库管理权限；可选的 Pandoc/XeLaTeX 书稿工具链
- Depended by：后续章节扩展、实验实现和持续发布 Intent

**Estimated Complexity**：XL，总体拆为 4 个连续 Bolts，每个 Bolt 3–6 个 Stories。

## Requirement-to-Unit Mapping

每项功能需求仅分配给一个 Unit：

- **FR-1** 建立写作仓库事实源 → `001-github-writing-system-ui`
- **FR-2** 生成 14 天 v0.1 路线图 → `001-github-writing-system-ui`
- **FR-3** 定义统一任务模型和状态流 → `001-github-writing-system-ui`
- **FR-4** 提供进度鸟瞰驾驶舱 → `001-github-writing-system-ui`
- **FR-5** 自动记录关键更新和进度快照 → `001-github-writing-system-ui`
- **FR-6** 接入 GitHub 协作与项目视图 → `001-github-writing-system-ui`
- **FR-7** 固化章节生产线 → `001-github-writing-system-ui`
- **FR-8** 管理实验证据与治理队列 → `001-github-writing-system-ui`
- **FR-9** 自动校验、构建和发布 → `001-github-writing-system-ui`
- **FR-10** 建立审校、反馈与持续发布闭环 → `001-github-writing-system-ui`

## Unit Dependency Graph

```text
[001-github-writing-system-ui]
            │
            ├── Repository facts + 14-day plan
            ├── Progress engine + dashboard
            ├── GitHub automation + publishing
            └── v0.1 release + feedback loop
```

## Execution Order

1. Day 1–4：仓库事实源、14 天计划、任务模型、章节和实验模板
2. Day 5–8：进度聚合、关键事件、快照和鸟瞰驾驶舱
3. Day 9–11：GitHub 协作模板、CI、Pages、Release 与 Projects 投影
4. Day 12–14：审校反馈、v0.1 发布与下一周期入口

## Independence Validation

- 单元可以仅用本地文件和 Python 独立开发与测试。
- GitHub Projects 同步失败时，仓库事实源和静态驾驶舱仍可工作。
- 静态资源可独立部署到 GitHub Pages。
- 对外接口是稳定的文件格式、命令行入口和 GitHub 事件，不依赖私有数据库。
