<p align="center">
  <img src="book/images/cover.png" alt="《深入理解 AI-DLC》封面" width="420">
</p>

# 深入理解 AI-DLC

> 从概率智能到确定性交付——AI 驱动规模化开发的理论与实践

这是一本帮助软件研发团队把 AI 从“个人生成工具”升级为“可约束、可验证、可追溯的规模化交付系统”的开源工程书。

本书不把 AI 生成物当作终点。它研究的是：人如何保留目标、边界和最终责任，AI 如何放大提议与执行能力，以及工程系统如何持续约束、验证、纠偏和推进，直到结果真正可以交付。

## 核心公式

> **AI-DLC = 𝓔（人的判断 + AI 能力）**  
> **𝓔 = Engineering with Exsecutio**

一句话复述：**人定方向，AI 加速度，工程化执行保交付。**

这里的 Exsecutio 表达“贯彻到底”：将 AI 的概率性生成沿工程路径持续推进，转化为可验证、可复现、可追溯、可恢复并可持续演进的软件系统。完整解释与范围边界见[核心宣言](book/manifesto.md)。

## 这本书写给谁

主要读者是：**正在把生成式 AI 从个人编码助手升级为团队级交付能力的软件研发负责人和技术负责人。**

也适合以下读者：

- 希望从个人 AI 编程进入团队协作的资深开发者和架构师。
- 负责 AI 工具链、研发效能或内部平台的工程团队。
- 需要理解 AI 研发边界、指标和治理方式的技术产品负责人。

本书不是 Prompt 技巧合集，也不承诺 AI 自动替代需求判断、架构取舍和最终责任人。完整读者结果与非目标范围见[目标读者定义](planning/readers.md)。

## 第一次阅读：先看 Part 0

[Part 00 · 鸟瞰 AI-DLC](book/part-00-overview.md)用约 10 分钟交代：

- 核心公式和确定性交付闭环。
- Inception → Construction → Operations 生命周期。
- Part 1–5 的叙事结构。
- 管理判断、研发系统设计和最小闭环实践三条阅读路线。
- 本书框架、方法论来源、specs.md 参考实现和实验证据的区别。

如果只准备跑通一次最小闭环，建议按 **Part 0 → 第 3、4、5、6、7、8 章**阅读。

## 全书叙事结构

| 部分 | 叙事任务 | 包含章节 |
| --- | --- | --- |
| Part 0 · 鸟瞰 | 先建立核心公式、生命周期和阅读地图 | 非编号导读 |
| Part 1 · 人的判断 | 解释为什么要重构 SDLC，以及人必须保留什么责任 | 第 1–2 章 |
| Part 2 · AI 能力 | 展示 AI 如何分解工作并通过事实源保持上下文 | 第 3–4 章 |
| Part 3 · Engineering × Exsecutio | 选择工程轨道，并把提议贯彻为交付候选 | 第 5–6 章 |
| Part 4 · 验证反馈 | 用独立证据证明正确，再进入可观测、可恢复的运行系统 | 第 7–8 章 |
| Part 5 · 规模化 | 按风险选择治理强度，并重构 Agent 分工和组织度量 | 第 9–10 章 |

## 十章目录

| 章 | 主题 | 唯一核心问题 |
| --- | --- | --- |
| 1 | AI 原生 SDLC：从概率智能到确定性交付 | 当代码生成成本骤降而输出仍具有概率性时，为什么需要重新设计 SDLC？ |
| 2 | 人的判断与反向对话 | 当 AI 主动提议、分解和执行时，人应如何设定目的地、保留责任并选择验证检查点？ |
| 3 | Inception：从 Intent 到可执行计划 | AI 如何把 Intent 分解为 Unit、Story 和 Bolt，而不丢失人的目标与边界？ |
| 4 | 上下文工程：Memory Bank 与 Standards | 如何让全新的 Agent 会话恢复正确上下文并持续遵守工程约束？ |
| 5 | Bolts：为快速执行选择正确轨道 | 如何按复杂度、风险和可逆性选择 Bolt 范围、类型与门禁？ |
| 6 | Exsecutio：把提议贯彻为交付候选 | 如何沿计划、执行、验证、纠偏和 Walkthrough 推进到完成定义？ |
| 7 | 验证：把人类检查点变成有效损失函数 | 如何证明 AI 参与的结果正确，而不是把模型自评当证据？ |
| 8 | Operations：从交付候选到可持续运行 | 如何通过 Build、Deploy、Verify、Monitor 与恢复机制完成生产交付？ |
| 9 | 适配性工程：选择正确的 Flow 与治理强度 | 如何在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化？ |
| 10 | 组织与度量：从 Agent 分工到研发操作系统 | 如何重构人、Agent、协作节奏与度量体系，并判断什么值得规模化？ |

每章都有唯一问题、读者结果、参考实现和实验方向。边界审计及完整版见[十章目录 v3](book/toc.md)。

## 实验与证据

影响读者实践的观点，必须至少关联以下一项：

- 可运行实验或最小 Demo。
- 可复现的外部实现与固定版本。
- 图表或机器可读结果。
- 明确的读者练习和二元验收。

实验统一采用三种治理状态：

- `SHIP`：在本仓库提供最小可运行实现。
- `KEEP-EXT`：保留外部来源、固定版本、配置和复现步骤。
- `ALREADY`：复用仓库中已经存在并可验证的实现。

当前 [30 项实验事实](progress/experiments.json)仍包含早期游戏 DLC 探索，只用于保持历史结构完整，**尚未构成新版十章的实验承诺**。Day 3 的 D03-T01 与 D03-T02 将按新版目录重建并重新分类实验池。规则见[实验治理说明](EXPERIMENT_TRIAGE.md)。

## 两周 v0.1 目标

项目在 14 天内形成可公开试读、可复现实验、可追踪进度的 v0.1：

1. 一个完成审校的可读样章。
2. Part 0 与十章结构。
3. 一个新读者可在 10 分钟内复现的实验。
4. 一张核心图。
5. 一个可重复运行的 HTML-first 构建入口；PDF 条件满足时生成。
6. 一个自动聚合的进度鸟瞰页。
7. 关键事件、历史快照和 Changelog。
8. 反馈入口、Release Notes 和下一更新周期。

逐日任务见[14 天行动计划](planning/14-day-v0.1.md)。任务状态、依赖、产物和验收的唯一权威源是 [progress/tasks.json](progress/tasks.json)。

## 从这里开始

### 读者

1. 阅读 [Part 0](book/part-00-overview.md)。
2. 从[十章目录](book/toc.md)选择阅读路径。
3. 查看[试读与复现说明](docs/READER-GUIDE.md)。
4. 样章和最小实验开放后，按 README 运行并提交反馈。

### 作者与协作者

1. 打开[鸟瞰驾驶舱](site/index.html)，确认当前任务、阻塞和下一动作。
2. 在[任务事实源](progress/tasks.json)中更新对应稳定 Task ID。
3. 修改声明的内容或工程产物。
4. 运行校验与进度生成器。
5. 通过 Issue 或 Pull Request 提交，并关联任务、产物和验收。

## 自动进度与鸟瞰入口

- [鸟瞰驾驶舱](site/index.html)：14 天时间线、章节矩阵、实验治理、阻塞和下一动作。
- [对象下钻](site/details.html)：逐任务、逐章节和逐实验检查事实。
- [GitHub 文字摘要](progress/generated/current.md)：无需打开 HTML 即可查看当前状态。
- [关键更新日志](progress/CHANGELOG.md)：自动追加的人类可读历史。
- [机器事件账本](progress/events/events.jsonl)：稳定 ID 的 JSONL 审计记录。
- [自动记录规则](docs/PROGRESS-AUTOMATION.md)：指标、事件、快照和失败安全约定。

README 不手工维护完成率；所有数字从版本化事实源自动生成。

## 权威事实源

| 内容 | 唯一权威来源 | 人类入口或投影 |
| --- | --- | --- |
| 书稿、Part 0 与目录 | `book/` | README、未来 HTML/PDF |
| 14 天任务、依赖与验收 | `progress/tasks.json` | 行动计划、Dashboard、GitHub Projects |
| 十章六阶段生产状态 | `progress/chapters.json` | Dashboard 章节矩阵 |
| 实验池与分类 | `progress/experiments.json` | 实验治理说明、Release Notes |
| 反馈决定 | `feedback/decisions.json` | 反馈摘要和修订任务 |
| 持续更新周期 | `progress/cycles.json` | 下一周期入口 |
| AI-DLC 开发生命周期 | `memory-bank/` | specs.md Dashboard 与开发日志 |

完整目录职责、人工源、生成投影和不可变历史边界见[仓库指南](docs/REPOSITORY-GUIDE.md)。

## 本地校验

需要 Python 3.10+，当前仓库不要求数据库或远程服务。

```bash
# 校验任务、章节、实验、反馈和周期事实
python3 scripts/validate_project.py

# 更新事件、快照、文字摘要和静态驾驶舱
python3 scripts/generate_progress.py

# 运行与 Pull Request 相同的完整门禁
python3 scripts/ci_check.py --budget-seconds 60

# 诊断真实 v0.1 发布条件
python3 scripts/check_release_readiness.py --allow-blocked
```

校验会阻止重复 ID、未知或循环依赖、非法状态、虚假完成、缺失产物、不带时区的时间戳以及不完整的实验分类数据。

## GitHub 协作

- [写作 Issue](.github/ISSUE_TEMPLATE/writing.yml)：章节、公式、案例和术语修订。
- [实验 Issue](.github/ISSUE_TEMPLATE/experiment.yml)：新实验、复现失败和指标改进。
- [反馈 Issue](.github/ISSUE_TEMPLATE/feedback.yml)：试读、阅读路径和理解障碍。
- [Bug Issue](.github/ISSUE_TEMPLATE/bug.yml)：构建、校验、Dashboard 或自动化问题。
- [Pull Request 模板](.github/pull_request_template.md)：必须填写 Task ID、产物、验收和验证结果。
- [协作说明](docs/GITHUB-COLLABORATION.md)：标签、里程碑、Issue/PR 和单向同步规则。

GitHub Issues 与 Projects 是协作投影，不能静默反向覆盖仓库事实源。

## 研究资料与本地工作稿

本书允许使用官网存档、外部参考仓库和作者工作稿作为研究入口，但它们不自动成为结论或公开构建依赖。作者本地的 `working-book/`、`specs.md-portal/` 和外部参考仓库均由 `.gitignore` 排除，不进入 GitHub。

官网效率数字、竞争性结论和工具能力必须回到原始来源核验；已知限制必须保留。例如 specs.md 当前将 Operations Agent 标为 alpha，本书不会把它描述为成熟生产能力。

## 安全、隐私与许可

- 不提交 Token、Cookie、API Key、`.env`、个人联系方式或未经许可的私密原文。
- 外部实验固定版本和配置，秘密只通过运行环境注入。
- 参考仓库和官网材料不是默认可复制内容；引用前确认许可并保留来源。
- 正式书籍许可和最终贡献条款将在 v0.1 发布前确认；在此之前不要假定第三方内容可以重新分发。

---

**AI-DLC 的目标不是“生成得更快”，而是“更快地交付正确”。**
