---
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
unit_type: frontend
default_bolt_type: simple-construction-bolt
phase: construction
status: complete
created: 2026-07-21T06:52:22.000Z
updated: 2026-07-22T03:42:12Z
---

# Unit Brief: GitHub Writing System UI

## Purpose

提供一个以仓库文件为事实源、可在本地和 GitHub 上运行的写作控制面：把 14 天 v0.1 路线、章节/实验生产线、任务状态、关键事件、静态鸟瞰页面和发布反馈整合成可持续闭环。

## Scope

### In Scope

- 写作仓库骨架、事实源模型与 14 天行动规划
- 章节模板、实验治理和审校/反馈模板
- 任务校验、进度聚合、关键事件、快照和变更日志
- 原生 HTML/CSS/JavaScript 驾驶舱与下钻链接
- GitHub Issues、PR、Projects、Actions、Pages 和 Releases 的配置与自动化
- v0.1 发布清单和下一周期入口

### Out of Scope

- 数据库、服务器端应用、自建认证和多人在线编辑
- 10 章全部正文与全部实验的实现
- 依赖 Unity/Unreal 或商业 API 的重型实验实现
- v0.1 后的搜索、订阅、流量分析和多语言站点

---

## Assigned Requirements

| FR | Requirement | Priority |
|----|-------------|----------|
| FR-1 | 建立写作仓库事实源 | Must |
| FR-2 | 生成 14 天 v0.1 路线图 | Must |
| FR-3 | 定义统一任务模型和状态流 | Must |
| FR-4 | 提供进度鸟瞰驾驶舱 | Must |
| FR-5 | 自动记录关键更新和进度快照 | Must |
| FR-6 | 接入 GitHub 协作与项目视图 | Must |
| FR-7 | 固化章节生产线 | Must |
| FR-8 | 管理实验证据与治理队列 | Must |
| FR-9 | 自动校验、构建和发布 | Must |
| FR-10 | 建立审校、反馈与持续发布闭环 | Should |

## Domain Concepts

### Key Entities

| Entity | Description | Attributes |
|--------|-------------|------------|
| Task | 单个可验收行动 | id、type、phase、status、priority、day、dependencies、artifact、acceptance、updated |
| Milestone | 版本或阶段时间锚点 | id、due、scope、status、release |
| ProgressEvent | 关键状态变化 | timestamp、type、subject、before、after、commit、summary |
| Snapshot | 某提交的整体状态 | generated_at、commit、metrics、blockers、next_actions |
| Chapter | 六阶段章节生产线 | question、framework、example、experiment、figure、review |
| Experiment | 可复现实验证据 | id、chapter、triage、effort、input、output、metrics、command、acceptance |
| Release | 可读版本与反馈入口 | version、commit、artifacts、known_gaps、next_goal |

### Key Operations

| Operation | Description | Inputs | Outputs |
|-----------|-------------|--------|---------|
| Validate | 校验任务、依赖、状态和产物一致性 | Task/Chapter/Experiment files | Validation report / exit code |
| Aggregate | 聚合任务和生产线进度 | Versioned facts | Metrics and next actions |
| Record | 检测并记录关键状态变化 | Previous/current facts + commit | Progress events and changelog |
| Snapshot | 保存某提交的整体鸟瞰状态 | Aggregated metrics | Versioned snapshot |
| Render | 生成静态驾驶舱数据和页面 | Metrics/events/templates | HTML/JSON/static fragments |
| Publish | 校验并发布 Pages/Release | Tag/commit/artifacts | Public site and release |

## Story Summary

| Metric | Count |
|--------|-------|
| Total Stories | 18 |
| Must Have | 16 |
| Should Have | 2 |
| Could Have | 0 |

### Stories

| Story ID | Title | Priority | Status |
|----------|-------|----------|--------|
| 001 | 搭建仓库事实源 | Must | Complete |
| 002 | 定义 14 天 v0.1 路线图 | Must | Complete |
| 003 | 定义任务模型与状态流 | Must | Complete |
| 004 | 校验任务与产物完整性 | Must | Complete |
| 005 | 创建章节生产线模板 | Must | Complete |
| 006 | 创建实验治理队列 | Must | Complete |
| 007 | 聚合进度指标与下一动作 | Must | Complete |
| 008 | 记录关键状态变化事件 | Must | Complete |
| 009 | 生成版本化进度快照与变更日志 | Must | Complete |
| 010 | 渲染进度鸟瞰驾驶舱 | Must | Complete |
| 011 | 增加下钻、响应式与无障碍能力 | Must | Complete |
| 012 | 创建 GitHub 协作模板与分类体系 | Must | Complete |
| 013 | 配置 Pull Request 校验工作流 | Must | Complete |
| 014 | 配置 Pages 与版本发布工作流 | Must | Complete |
| 015 | 定义 GitHub Projects 鸟瞰视图与同步 | Must | Complete |
| 016 | 建立写作、审校与反馈回流 | Should | Complete |
| 017 | 准备并验收 v0.1 发布 | Must | Complete |
| 018 | 自动建立下一轮更新入口 | Should | Complete |

## Dependencies

### Depends On

无其他内部 Unit。

### Depended By

后续书稿章节、实验实现和长期运营 Intent 将复用本单元的任务、进度和发布能力。

### External Dependencies

| System | Purpose | Risk |
|--------|---------|------|
| GitHub Repository | Git 事实源和权限 | Low |
| GitHub Actions | 校验、生成和发布 | Low |
| GitHub Projects API | Project 投影同步 | Medium |
| GitHub Pages/Releases | 静态站与版本分发 | Low |
| Pandoc/XeLaTeX | PDF 构建 | Medium |

## Technical Context

### Suggested Technology

- 原生 HTML、CSS、JavaScript；复用现有行动指南视觉基线
- Python 3 标准库处理 YAML 限制之外的仓库内结构化数据；事实源可采用 JSON 和约束明确的 Markdown/YAML
- GitHub Actions YAML 负责 PR 校验、主分支快照、Pages 和 tag 发布
- `unittest` 覆盖解析、校验、聚合、差异和生成流程

### Integration Points

| Integration | Type | Protocol |
|-------------|------|----------|
| Repository facts → Progress engine | File | JSON/Markdown/YAML |
| Progress engine → Dashboard | Generated file | JSON/HTML |
| GitHub event → Workflow | Event | push/PR/tag/workflow_dispatch |
| Workflow → Pages/Release | Artifact | GitHub Actions |
| Repository facts → Project view | Optional API | GitHub GraphQL |

### Data Storage

| Data | Type | Volume | Retention |
|------|------|--------|-----------|
| Tasks and templates | Versioned files | < 1,000 records in MVP | Permanent Git history |
| Events and changelog | Append-only files | < 10 MB/year expected | Permanent Git history |
| Snapshots | JSON/Markdown | One per key update or main push | Permanent or monthly compaction later |
| Dashboard artifacts | Generated static files | < 2 MB core | Replaceable per commit |

## Constraints

- 14 天内形成 v0.1；优先保障闭环而非章节数量。
- 核心进度生成不依赖网络、数据库或第三方包。
- GitHub Projects 是投影视图，不得成为唯一状态来源。
- 历史事件不可由普通生成流程覆盖或删除。
- 工作流采用最小权限，Fork 不得读取发布秘密。

## Success Criteria

### Functional

- [x] 14 天路线中所有任务都能由任务模型表示并通过校验。
- [x] 驾驶舱展示总览、时间线、章节/实验、阻塞和最近关键更新。
- [x] 关键状态变化自动生成事件、快照和人可读记录。
- [ ] PR、主分支和标签触发正确的校验、生成与发布流程。
- [ ] v0.1 包含样章、实验、核心图、构建产物、Release Notes 和反馈入口。

### Non-Functional

- [x] 关键事件记录完整率 100%，所有指标可追溯到事实源。
- [ ] MVP 校验和进度生成在 GitHub Runner 上 60 秒内完成。
- [x] 同一提交重复生成等价结果，失败不覆盖最后成功产物。
- [x] 页面核心资源小于 2 MB，并满足移动端和键盘可用要求。

### Quality

- [x] 关键解析、校验、聚合、事件和生成路径都有测试。
- [ ] 所有 Story 验收标准满足。
- [ ] 代码和内容经过 Pull Request 或等价人工审阅。

## Bolt Suggestions

| Bolt | Type | Stories | Objective |
|------|------|---------|-----------|
| 001 | Simple | Foundation stories | 仓库、14 天计划和写作事实源 |
| 002 | Simple | Progress stories | 聚合、事件、快照和驾驶舱 |
| 003 | Simple | GitHub stories | 协作、CI、Projects、Pages 和 Release 自动化 |
| 004 | Simple | Release stories | 审校反馈、v0.1 和下一周期 |

## Notes

虽然该 Unit 的总体复杂度较大，但部署边界单一、接口以文件为主，适合用四个相邻 Simple Bolts 控制风险。GitHub Project 自动写入权限是唯一高不确定集成，应采用“事实源优先、同步可降级”的策略。
