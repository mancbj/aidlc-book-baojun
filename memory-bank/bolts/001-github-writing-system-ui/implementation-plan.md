---
stage: plan
bolt: 001-github-writing-system-ui
created: 2026-07-21T07:08:32Z
---

# Implementation Plan: GitHub Writing System Foundation

## Objective

在不破坏现有 HTML、参考仓库、内容研究资料和 memory-bank 的前提下，把当前目录变成可用 Git 管理的写作仓库，并建立后续进度引擎、驾驶舱和 GitHub 自动化能够依赖的稳定事实源。

本 Bolt 交付 Day 1–4 的基础层：仓库职责、14 天任务、任务状态规则、完整性校验、章节生产线和实验治理。它不实现驾驶舱、关键事件、GitHub Actions 或正式发布，这些属于后续 Bolts。

## Current State

- 当前工作区根目录尚未初始化 Git。
- Python 3.9.6 可用，适合标准库脚本和 unittest。
- Pandoc 与 XeLaTeX 当前不可用；PDF 构建不属于本 Bolt。
- 作者本地行动指南、参考仓库和工作稿必须保留在被忽略的本地资料区；内容研究资料和 memory-bank 按仓库规则维护。
- `working-book/` 当前为空；本 Bolt 不删除或迁移它。
- 尚未配置 GitHub remote、仓库可见性、Pages 或 Projects。

## Deliverables

### 1. Repository Foundation

- `README.md`：定位、目标读者、核心公式、章节、实验、14 天路线、校验与贡献入口。
- `.gitignore`：忽略系统文件、Python 缓存、虚拟环境、秘密文件和可再生成临时产物。
- 本地 Git 元数据：初始化仓库，但不创建远程、不推送、不提交用户未确认的历史。
- `book/`：书稿入口、核心公式、十章目录、章节模板。
- `docs/`：仓库职责、事实源与生成文件边界说明。
- `planning/`：14 天 v0.1 人类可读计划和实验卡模板。
- `progress/`：机器可读事实源和格式说明。
- `scripts/`：校验入口及使用说明。
- `tests/`：标准库测试。
- `writer-chats/`：写作对话保存规则。
- `.github/workflows/README.md`：说明未来工作流职责；本 Bolt 不创建实际 workflow。

### 2. Versioned Fact Sources

- `progress/tasks.json`：Day 1–14 的 42 个任务，使用稳定 ID `D01-T01` 至 `D14-T03`。
- `progress/chapters.json`：10 个章节及 Question、Framework、Example、Experiment、Figure、Review 六阶段状态。
- `progress/experiments.json`：至少 30 个候选实验，包含章节、分类、工作量、输入、输出、指标、命令和验收。
- `progress/schemas/task-schema.md`：任务字段、类型、状态、转换和完成门禁。
- `progress/schemas/chapter-schema.md`：章节六阶段与“下一缺口”规则。
- `progress/schemas/experiment-schema.md`：SHIP、KEEP-EXT、ALREADY 的条件式必需字段。

### 3. Human-Readable Planning Assets

- `planning/14-day-v0.1.md`：引用任务 ID 的每日行动表，不复制机器统计数字。
- `book/manifesto.md`：核心公式占位、五条“不是”与填写提示。
- `book/toc.md`：十章建议目录和每章唯一核心问题。
- `book/chapter-template.md`：统一章节生产线模板。
- `planning/experiment-card-template.md`：实验卡模板。
- `EXPERIMENT_TRIAGE.md`：实验治理规则和事实源入口，不手工维护与 JSON 重复的统计。

### 4. Integrity Validator

- `scripts/validate_project.py`：仅用 Python 标准库加载并校验任务、章节和实验事实源。
- 校验任务必需字段、允许值、唯一 ID、已知依赖、循环依赖、ISO 8601 时区时间、blocked 信息、done 验收与产物。
- 校验章节六阶段、状态值和下一未完成阶段。
- 校验实验基础字段，以及 SHIP、KEEP-EXT、ALREADY 的条件式字段。
- 集中报告可预期问题；存在阻断错误时返回非零退出码。
- 错误包含文件、对象 ID、字段、错误值和修复建议。

### 5. Tests

- `tests/test_validate_project.py`：覆盖合法数据、重复 ID、未知依赖、循环依赖、非法状态、缺少 blocked 信息、虚假 done、无时区时间戳和三类实验条件。
- 使用临时目录和最小夹具，不修改真实事实源。
- `python3 -m unittest discover -s tests` 为统一测试入口。

## Story-to-Deliverable Mapping

| Story | Planned Files | Completion Evidence |
|-------|---------------|---------------------|
| 001 · 仓库事实源 | README、目录 README、`.gitignore`、Git 初始化 | 所有要求目录存在；事实源/生成文件边界可读 |
| 002 · 14 天路线 | `planning/14-day-v0.1.md`、`progress/tasks.json` | Day 1–14 均有任务、产物和二元验收；D7/D14 里程碑完整 |
| 003 · 任务模型 | `task-schema.md`、任务示例 | 必需字段和六种状态可校验；blocked/done 门禁有效 |
| 004 · 完整性校验 | `validate_project.py`、测试 | 重复、断链、循环、虚假完成和时间戳错误均被阻止 |
| 005 · 章节生产线 | `chapter-template.md`、`chapters.json`、chapter schema | 六阶段齐全；可计算首个未完成阶段 |
| 006 · 实验治理 | `EXPERIMENT_TRIAGE.md`、模板、`experiments.json`、experiment schema | 三类实验字段规则可验证；至少 30 个候选实验入池 |

## Data Authority Rules

1. `progress/*.json` 是运行状态、章节状态和实验状态的权威事实源。
2. `planning/*.md`、README 和模板用于解释与导航，不人工维护聚合统计。
3. `memory-bank/` 是 AI-DLC 规划与执行审计源，不作为未来驾驶舱的直接业务数据输入。
4. 未来生成的 current、snapshot、dashboard 数据必须标注生成来源，不反向覆盖事实源。
5. GitHub Projects 在 Bolt 003 中作为投影视图接入，不成为唯一权威源。

## Task Model

每项任务包含：

- `id`、`title`、`type`、`phase`、`status`、`priority`
- `owner`、`day`、`planned_date`、`dependencies`
- `artifacts`、`acceptance`、`updated`
- blocked 时的 `blocker_reason` 和 `unblock_action`

允许状态：

1. `backlog`
2. `ready`
3. `in-progress`
4. `review`
5. `done`
6. `blocked`

完成规则：

- 所有验收项为通过状态。
- 声明为必需的产物路径存在。
- 依赖任务已完成。
- updated 使用带时区 ISO 8601。

## Experiment Governance

所有实验共有：ID、章节、名称、分类、工作量、输入、输出、指标、运行命令和验收。

1. `SHIP`：另需仓库实现路径、README、样例输入、样例输出和测试路径。
2. `KEEP-EXT`：另需外部来源、固定版本、配置、复现步骤和样例结果。
3. `ALREADY`：另需复用实现和跨章引用。

无法满足所选分类字段的实验保留为未完成，不得展示为已验证证据。

## Technical Approach

1. 先创建目录和说明文件，再初始化事实源，避免脚本依赖不存在的路径。
2. JSON 用作机器事实源，因为 Python 标准库可直接解析且 Git diff 清晰。
3. 校验器按“加载 → 结构校验 → 引用/依赖校验 → 条件规则 → 汇总错误”分层。
4. 循环依赖使用深度优先遍历检测，并返回可读依赖链。
5. 路径验证以仓库根目录为基准，防止工作目录变化造成误判。
6. 章节和实验规则保留独立验证函数，为 Bolt 002 的聚合器复用。
7. 所有文件创建均为增量操作；若目标已存在，先读取并保留用户内容。

## Dependencies

- Python 3.9.6：本地校验和 unittest。
- Git：初始化版本控制；远程仓库和推送待 Bolt 003 或用户提供目标地址后处理。
- Inception artifacts：需求、18 Stories 和 14 天路线作为实施依据。
- 现有行动指南：核心内容和视觉/信息基线。

## Constraints

- 不删除或覆盖现有 HTML、图片、参考仓库、研究资料、memory-bank 和 working-book。
- 不安装第三方 Python 包。
- 不配置 GitHub remote、Token、Pages、Projects 或 Actions。
- 不声称已生成 PDF；Pandoc/XeLaTeX 当前不可用。
- 不实现进度聚合、事件、快照或驾驶舱；这些由 Bolt 002 交付。
- 不完成十章正文或全部实验实现。

## Implementation Sequence

1. 创建目录、职责说明、`.gitignore` 和根 README。
2. 创建 manifesto、十章目录、章节模板、实验模板与治理说明。
3. 创建 42 个 14 天任务事实记录和对应人类可读路线。
4. 创建 10 章六阶段事实记录与至少 30 个实验事实记录。
5. 实现标准库校验器。
6. 编写 unittest 夹具和失败用例。
7. 初始化本地 Git，运行校验与基础语法检查；正式测试结论留到 Stage 3。

## Acceptance Criteria

- [ ] 根目录已成为本地 Git 仓库，且没有远程副作用。
- [ ] 所有职责目录存在并包含可理解的入口说明。
- [ ] README 能引导作者找到当前计划、下一任务、章节、实验和校验命令。
- [ ] Day 1–14 每天恰有三项种子任务，合计 42 项；每项都有依赖、产物和验收。
- [ ] Day 7 的 v0.0.1 和 Day 14 的 v0.1 闭环可由任务依赖追踪。
- [ ] 任务只接受六种状态；blocked 和 done 满足额外门禁。
- [ ] 十章记录均包含六阶段并能识别下一缺口。
- [ ] 实验池不少于 30 项，三类治理规则均有合法样例。
- [ ] 校验器对重复、未知依赖、循环、虚假完成和无时区时间戳返回失败。
- [ ] 所有自动化仅依赖 Python 标准库，现有用户文件保持不变。

## Stage 3 Verification Plan

1. 运行 Python 语法编译检查。
2. 运行 unittest 全套测试。
3. 对真实 `progress/*.json` 运行校验器。
4. 检查 42 个任务、14 个 Day、10 章、30 个以上实验和稳定唯一 ID。
5. 检查所有 Markdown 内部相对路径。
6. 抽查 Story 001–006 的验收标准与实际产物。

## Decisions Requiring No Additional Authority

- 使用 JSON 作为机器事实源，符合已批准的轻量标准库方案。
- 新建标准 `book/`，保留空的 `working-book/`，不做迁移或删除。
- 初始化本地 Git，但不创建 commit、不设置 remote、不向 GitHub 推送。
- PDF 构建依赖留到后续 Bolt；本 Bolt 只提供结构和计划入口。

## Open Implementation Risks

- 42 项任务和 30 项实验的初始内容较多，必须通过脚本校验避免人工编号或引用错误。
- 任务事实源与 memory-bank Stories 属于不同层级，需要在文档中清楚解释，避免双重状态源。
- `ALREADY` 实验需要真实复用路径；若当前没有实现，只能创建少量指向参考资产的合法记录，其余使用 SHIP 或 KEEP-EXT。
- 本地 Git 初始化后仍需用户确定远程仓库地址和公开性，才能进入真正的 GitHub 协作阶段。
