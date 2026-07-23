---
intent: 001-github-writing-system
phase: inception
status: complete
created: 2026-07-21T06:44:05.000Z
updated: 2026-07-22T03:42:12Z
---

# Requirements: GitHub Writing System

## Intent Overview

基于现有《AI-DLC 开源书写作行动指南》，建立一套从零启动、可持续运行的 GitHub 原生写作生产系统。系统把书稿规划、章节生产、实验治理、审校、发布和反馈变成可执行任务，并为每次关键更新提供可鸟瞰的进度展示和自动、可追溯的记录。

## Business Goals

| Goal | Success Metric | Priority |
|------|----------------|----------|
| 在 2 周内形成可公开试读的 v0.1 | 第 14 天前生成带版本号的 HTML/PDF、Release Notes 和 GitHub Release 候选产物 | Must |
| 让作者始终知道当前状态和下一步 | 100% 活跃任务具有状态、优先级、验收标准、产物和下一动作；作者可在 30 秒内找到下一项工作 | Must |
| 让整体进度可鸟瞰 | 静态看板同时展示阶段、14 天时间线、任务完成率、章节/实验状态、阻塞项、最近更新和里程碑 | Must |
| 让关键更新自动留痕 | 100% 已定义关键事件生成带时间、来源、变更前后状态和关联任务的版本化记录 | Must |
| 建立发布后的持续更新节奏 | v0.1 后每周至少完成一节、运行一次实验，每月至少发布一个可读版本 | Should |

---

## Functional Requirements

### FR-1: 建立写作仓库事实源

- **Description**：建立清晰的仓库目录和结构化事实源，分离书稿、章节实验、计划、进度、脚本、写作对话与生成产物。
- **Acceptance Criteria**：
  - 仓库至少包含 `book/`、`docs/`、`planning/`、`progress/`、`scripts/`、`tests/`、`writer-chats/` 和 `.github/workflows/` 的职责定义。
  - `README.md` 包含一句话定位、目标读者、核心公式、章节表、实验表、阅读/构建入口和贡献方式。
  - 任务和进度只从版本控制中的结构化文件聚合，不以手工修改看板统计数字作为事实源。
  - 人工编辑源文件与自动生成文件的目录或文件头明确区分。
- **Priority**：Must
- **Related Stories**：待定义

### FR-2: 生成 14 天 v0.1 路线图

- **Description**：把原指南的 8 周路线压缩成 2 周 MVP 路线，同时保留“核心公式—仓库—样章—实验—构建—审校—发布—反馈”的完整闭环。
- **Acceptance Criteria**：
  - 路线图覆盖 Day 1–14，每天都有目标、任务、依赖、产物和二元验收标准。
  - Day 1–7 至少完成核心公式、目标读者、10 章目录、仓库骨架、README、实验池、样章提纲、最小实验、样例产物、最小构建链和内部 `v0.0.1` 时间锚点。
  - Day 8–14 至少完成样章可读稿、核心图、学习路线、第一轮审校、实验治理、3 位试读者反馈入口、v0.1 构建、Release Notes 和下一轮计划。
  - v0.1 明确采用 MVP 边界：至少 1 个达到可读标准的样章、10 章结构、1 个可复现实验、1 张核心图和可运行构建链；不要求 10 章全部完成。
  - 任何延期任务必须标记影响、替代方案和新的落点，不允许静默滚动。
- **Priority**：Must
- **Related Stories**：待定义

### FR-3: 定义统一任务模型和状态流

- **Description**：所有写作、实验、审校、自动化和发布动作使用统一字段与有限状态流管理。
- **Acceptance Criteria**：
  - 每项任务至少包含唯一 ID、标题、类型、阶段、状态、优先级、负责人、计划日期、依赖、产物、验收标准和更新时间。
  - 状态限定为 `backlog`、`ready`、`in-progress`、`review`、`done`、`blocked`；非法状态使校验失败。
  - 任务只有在验收标准满足且产物存在时才能进入 `done`。
  - `blocked` 任务必须包含阻塞原因和解除阻塞的下一动作。
  - 支持按天、阶段、任务类型、章节、实验和里程碑聚合。
- **Priority**：Must
- **Related Stories**：待定义

### FR-4: 提供进度鸟瞰驾驶舱

- **Description**：基于作者本地 `working-book/ai_dlc_book_action_guide.html` 的视觉与信息架构，生成一个无需服务器且不依赖该本地文件的进度驾驶舱。
- **Acceptance Criteria**：
  - 页面展示总体完成率、当前 Day、v0.1 倒计时、阶段完成率、Must/Should 完成率和最新更新时间。
  - 页面提供 14 天时间线、任务状态分布、章节生产线、实验治理队列、阻塞项和最近关键更新。
  - 用户能从总览下钻到具体任务及其验收标准、产物路径和 GitHub 链接。
  - 桌面端与移动端均可阅读；无 JavaScript 时仍能看到核心进度摘要。
  - 每次事实源更新后可由同一命令重新生成，页面不要求人工同步数字。
- **Priority**：Must
- **Related Stories**：待定义

### FR-5: 自动记录关键更新和进度快照

- **Description**：在关键状态变化发生时生成机器可读事件和人可读快照，形成可审计时间线。
- **Acceptance Criteria**：
  - 关键事件至少包括任务开始、进入审阅、完成、阻塞/解除阻塞、里程碑完成、章节状态改变、实验状态改变、构建成功/失败和版本发布。
  - 每条事件至少记录 ISO 8601 时间、事件类型、关联任务/产物、变更前状态、变更后状态、来源提交和摘要。
  - 每次推送主分支或手动触发时生成当前汇总快照；发生关键事件时同时更新人可读变更日志。
  - 无状态变化时不得制造虚假关键事件，但允许记录工作流运行结果。
  - 历史记录保存在 Git 中，新的生成过程不得覆盖或删除既有事件。
- **Priority**：Must
- **Related Stories**：待定义

### FR-6: 接入 GitHub 协作与项目视图

- **Description**：使用 GitHub Issues、Pull Requests、Projects、Labels、Milestones 和 Releases 承载协作，并与仓库内事实源建立可追踪关联。
- **Acceptance Criteria**：
  - 提供 Issue 与 Pull Request 模板，要求填写任务 ID、产物和验收清单。
  - 提供标签体系，至少覆盖类型、优先级、状态或阶段、章节/实验和阻塞。
  - 建立 `v0.0.1` 与 `v0.1` 里程碑，并能从驾驶舱跳转到对应 GitHub 视图。
  - GitHub Projects 至少提供 Board、14 天 Roadmap 和按章节/实验分组的鸟瞰视图；如自动同步需要额外权限，仓库内事实源仍必须独立可用。
  - 合并 Pull Request 后，关联任务和快照能通过受控流程更新，避免仓库与 GitHub 状态静默分叉。
- **Priority**：Must
- **Related Stories**：待定义

### FR-7: 固化章节生产线

- **Description**：每章都按 Question、Framework、Example、Experiment、Figure、Review 六阶段生产线推进。
- **Acceptance Criteria**：
  - 提供统一章节模板，要求记录核心问题、读者结果、理论框架、场景例子、实验、图表、参考材料和读者练习。
  - 每章在鸟瞰页面中展示六阶段状态，并能指出下一缺口。
  - 影响读者实践的正文观点必须关联实验、复现指南、图表或明确练习之一。
  - 审校至少检查技术正确性、重复度、结构连贯性、术语一致性和实验对应关系。
- **Priority**：Must
- **Related Stories**：待定义

### FR-8: 管理实验证据与治理队列

- **Description**：所有实验先进入统一池，再按 `SHIP`、`KEEP-EXT`、`ALREADY` 分类，保证正文承诺与可运行证据一致。
- **Acceptance Criteria**：
  - 每个实验卡包含编号、名称、对应章节、分类、工作量、输入、输出、指标、运行命令和验收标准。
  - `SHIP` 实验必须在仓库内提供最小可运行实现、README、示例输入输出及测试。
  - `KEEP-EXT` 必须提供外部来源、固定版本、配置、复现步骤和样例结果。
  - `ALREADY` 必须指向可复用实现及跨章引用。
  - 无法验证的概念不得在正文中作为已实现能力承诺。
- **Priority**：Must
- **Related Stories**：待定义

### FR-9: 自动校验、构建和发布

- **Description**：提供本地与 GitHub Actions 一致的命令，完成数据校验、测试、进度生成、书稿构建和静态页面发布。
- **Acceptance Criteria**：
  - Pull Request 自动执行任务数据校验、Python 测试、内部链接检查和生成流程冒烟测试。
  - 主分支更新自动重建进度数据与驾驶舱；发布标签触发 v0.1 候选产物构建。
  - 构建失败返回非零状态，不发布旧数据冒充新结果，并在日志中给出文件与修复建议。
  - 提供单一入口命令或清晰命令集，可在本地复现 CI 的关键步骤。
  - GitHub Pages 发布内容至少包含行动/进度驾驶舱和可访问的书稿入口。
- **Priority**：Must
- **Related Stories**：待定义

### FR-10: 建立审校、反馈与持续发布闭环

- **Description**：把写作对话、审校意见、试读反馈和发布结果转回下一轮任务，而不是留在仓库外部。
- **Acceptance Criteria**：
  - 关键提示词、审校意见和修订结论以可检索文件保存在 `writer-chats/` 或决策记录中。
  - v0.1 前提供试读反馈模板，并邀请至少 3 位读者仅依靠 README 试读或复现实验。
  - 每条有效反馈能关联到接受、拒绝或延期决策；被接受项转成任务。
  - 每个 Release Notes 列出新增内容、实验状态、已知缺口、关键指标和下一版本目标。
  - v0.1 发布时自动生成下一周期入口，延续每周写/跑和每月发布节奏。
- **Priority**：Should
- **Related Stories**：待定义

---

## Non-Functional Requirements

### NFR-1: 可审计性

- **Metric**：关键事件记录完整率
- **Target**：已定义关键事件 100% 具有时间、来源提交、关联对象、前后状态和摘要；任意当前数字可追溯到版本化事实源。

### NFR-2: 自动化可靠性

- **Metric**：确定性与失败安全
- **Target**：同一提交重复生成得到等价结果；校验或生成失败时退出码非零，且不覆盖最后一次成功产物。

### NFR-3: 执行性能

- **Metric**：仓库校验与进度生成时间
- **Target**：在 GitHub 托管 Runner 上，MVP 规模的纯校验与进度生成在 60 秒内完成，不含 Pandoc/XeLaTeX 等外部书稿构建时间。

### NFR-4: 页面性能与可访问性

- **Metric**：静态页面大小、加载和键盘可用性
- **Target**：核心进度页面生成资源不超过 2 MB（书稿和下载产物除外）；普通宽带下 3 秒内可见核心摘要；主要导航和状态详情可通过键盘访问，颜色不是唯一状态信号。

### NFR-5: 易用性

- **Metric**：找到下一动作所需时间
- **Target**：首次使用者阅读 README 后，可在 30 秒内识别当前阶段、阻塞项和下一项 Must 任务；任务状态词和验收规则有一页说明。

### NFR-6: 可维护性与可移植性

- **Metric**：核心生成链依赖与运行环境
- **Target**：进度校验和生成优先仅使用 Python 标准库；同一命令可在 macOS、本地 Linux 和 GitHub Actions 运行；核心进度生成不依赖数据库或在线 API。

### NFR-7: 安全性

- **Metric**：GitHub Actions 权限与敏感信息处理
- **Target**：工作流使用最小权限；来自 Fork 的流程不能读取发布密钥；日志和生成文件不包含 Token、Cookie、API Key 或完整环境变量。

### NFR-8: 数据完整性

- **Metric**：任务引用、时间线和聚合一致性
- **Target**：重复 ID、未知依赖、非法状态、完成但产物缺失、时间倒序或聚合不一致均使校验失败；所有时间戳采用带时区的 ISO 8601 格式。

---

## Constraints

### Technical Constraints

**Project-wide standards**：Construction Agent 将从 `memory-bank/standards/` 加载技术栈和编码标准。

**Intent-specific constraints**：

- 作者本地 `working-book/ai_dlc_book_action_guide.html` 是历史内容与视觉基线；公开仓库只继承设计原则，不发布或依赖该文件。
- GitHub 是协作、版本和发布平台；核心进度事实源必须保存在仓库中。
- 首期不使用数据库、服务器端应用或自建身份验证。
- 所有自动记录都必须可由 Git 提交历史审计，不能只存在于 Actions 临时日志。

### Business Constraints

- 从正式执行起 14 天内形成可发布 v0.1。
- 默认投入为每日 60–120 分钟，并在两周内安排两次半天工程/审校窗口。
- 时间不足时优先缩小内容范围，不牺牲可运行实验、构建可复现性和关键更新留痕。
- 初期基础设施成本以 GitHub 免费或低成本能力为目标。

---

## Assumptions

| Assumption | Risk if Invalid | Mitigation |
|------------|-----------------|------------|
| 作者拥有目标 GitHub 仓库的管理权限 | 无法配置 Pages、Actions、Projects 或分支保护 | 先完成仓库内事实源和本地生成，再在取得权限后启用远程能力 |
| 两周内能保持每日 60–120 分钟并安排两次半天窗口 | v0.1 里程碑延期 | 以样章 + 单实验作为不可再缩 MVP，其余章节只保留结构 |
| v0.1 的目标是可公开试读和复现，而非全书完稿 | 对完成度预期不一致 | README 与 Release Notes 明确标注完成范围和已知缺口 |
| 现有 HTML 可继续作为驾驶舱视觉基线 | 页面耦合过高，动态数据难以接入 | 保留视觉语言，将事实数据外置为生成 JSON 或静态片段 |
| GitHub Projects 自动同步允许使用所需 Token 权限 | 无法自动写入 Project 字段 | 把 Projects 视为投影视图，仓库事实源与静态驾驶舱仍可完整工作 |

---

## Open Questions

| Question | Owner | Due Date | Resolution |
|----------|-------|----------|------------|
| 目标 GitHub 仓库的远程地址与公开性设置是什么？ | 作者 | Construction 开始前 | Pending；不阻塞 Inception |
| GitHub Projects 使用组织级还是仓库级 Project？ | 作者 | Project 自动化 Bolt 开始前 | Pending；默认优先仓库关联 Project |
| v0.1 样章最终选择第 2、3 或 4 章中的哪一章？ | 作者 | Day 3 | Pending；路线图保留选择任务 |
