# 第 3 章 · Inception：从 Intent 到可执行计划

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-03 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D17-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；v0.1 可读样章仍保留在 `book/chapters/sample.md` |
| Primary Question | AI 如何把一个高层 Intent 分解成可独立交付的 Unit、可验收的 Story 和可执行的 Bolt，而不丢失人的目标与边界？ |
| Reader Outcome | 能够完成 Intent、Requirements、System Context、Unit、Story 与 Bolt Plan 的可追溯分解 |
| Related Experiments | `EXP-03-01` |

## 01 · Question：为什么 Intent 不能直接交给 AI 执行

本章回答一个具体问题：**AI 如何把一个高层 Intent 分解成可独立交付的 Unit、可验收的 Story 和可执行的 Bolt，而不丢失人的目标与边界？**

高层 Intent 往往同时包含结果、时间、质量、边界、受众和隐含风险。它看起来像一句任务描述，但还不是可执行对象。如果直接让 AI 从 Intent 跳到代码、网页、脚本或书稿，速度会很快，偏差也会很快。AI 可能提前选择实现方案，却没有证明方案服务于原始目的；可能生成大量文件，却没有清晰依赖；也可能把人的判断点推迟到返工成本已经变高的时候。

本章的关键边界是：Inception 不负责完成实现，不负责发布，也不负责长期运行；它负责把“想要什么”转成“可以怎样被执行、被验收、被追踪”。读者读完后，应能拿自己的项目 Intent，分解出 2 个 Unit、3 到 5 个 Story，并解释每个 Story 服务于哪个上游目标、由哪个验收条件结束。

### Gate

- [x] 核心问题只有一个：Intent 如何被分解成不失真的可执行计划。
- [x] 读者结果可以观察：能产出一条 Intent → Requirements → Context → Units → Stories → Bolt Plan 的追踪链。
- [x] 本章不展开 Construction、Operations 或 Memory Bank 的完整实现细节。

## 02 · Framework：七级分解链

本章采用一条七级分解链组织论证：

```text
Intent
  → Requirements
  → System Context
  → Units
  → Stories
  → Bolt Plan
  → Human Checkpoints
```

**Intent** 描述结果，而不是预设方案。它回答“要达成什么”，不急于回答“用什么做”。  
**Requirements** 把 Intent 转成可检查的功能要求与非功能要求，尤其要显式写出边界、安全、可追溯性和质量约束。  
**System Context** 说明事实源、目录边界、工具假设、公开/本地资料边界和外部接口，让后续 Agent 不靠聊天记忆猜项目环境。  
**Units** 定义可独立交付的能力边界，避免 AI 把事实源、页面、发布和反馈系统混成一个不可验收的大任务。  
**Stories** 把 Unit 内的能力转成用户价值和二元验收，说明每个 Story 服务于哪个 Requirement。  
**Bolt Plan** 把 Stories 编排为小时到天级的执行批次，让实现能够沿着阶段门禁推进。  
**Human Checkpoints** 保留人的方向判断、边界确认、风险接受和发布授权，防止 AI 高速偏航。

这条链对应本书核心公式中的 `𝓔 = Engineering with Exsecutio`。在 Inception 阶段，Engineering 的作用是把意图、边界、依赖、验收和证据显式化；Exsecutio 的前提是形成一条 AI 能贯彻、而人仍能验证和纠偏的执行轨道。`Exsecutio` 是本书指定术语，不能替换为 `Execution`。

## 03 · Three-Part Argument：为什么 Inception 决定后续交付质量

### 第一段：Intent 混合了目的、边界与风险，必须先解耦

一句自然语言 Intent 往往并不“干净”。例如“从零建立一套在 GitHub 上写作和持续更新《深入理解 AI-DLC》的系统，两周形成可发布 v0.1，所有关键更新自动记录并可视化”，里面同时包含结果、时间、平台、质量要求和治理要求。AI 可以马上开始生成页面或脚本，但此时它还不知道哪些目录不能上传、哪些状态不能手工伪造、哪些证据才算发布完成。

本段结论：**Inception 的第一项价值，是把混合在 Intent 中的目的、边界、质量和风险拆出来，避免实现先于判断。**

### 第二段：任务不是越碎越好，而是要可追踪、可验收、可恢复

普通任务拆分容易停留在“做页面、写脚本、补文档”的动作列表。AI-DLC 要求每个 Story 能向上追到 Requirement，向下进入 Bolt，横向说明依赖，最后以可判断的验收结束。这样做的目的不是制造文档，而是让下一次会话、下一位协作者和下一轮发布都能恢复上下文。

本段结论：**Inception 的第二项价值，是把任务拆成有上游目标、下游执行、验收门槛和证据路径的对象。**

### 第三段：人的判断必须前置到计划形成阶段

如果人的判断只出现在最后审查，AI 已经可能生成了大量错误方向上的产物。Inception 要把人的判断点放到更早的位置：目标是否正确，边界是否清楚，哪些风险不能接受，哪些检查点必须停下来确认，哪些任务进入 Bolt 前还缺验收条件。

本段结论：**Inception 的第三项价值，是让人的判断在错误可逆时介入，而不是在产物堆积后再返工。**

## 04 · Example Skeleton：以本书项目自身为例

本章正式可读稿将沿用 v0.1 样章中的项目例子：从“在 GitHub 上持续写作并两周发布 v0.1”这个 Intent 出发，逐级生成 Requirements、System Context、Unit、Story 与 Bolt Plan。

最小例子结构如下：

```text
Intent
  从零建立一套在 GitHub 上写作和持续更新《深入理解 AI-DLC》的系统，
  两周形成可发布 v0.1，所有关键更新自动记录并可视化。

Requirements
  FR-001：提供可读样章
  FR-002：提供可运行实验
  FR-003：提供进度驾驶舱
  NFR-001：所有进度可追溯
  NFR-002：公开仓库不包含本地工作资料

System Context
  Git 仓库是事实源；progress/*.json 是状态事实；
  specs.md-portal/ 与 working-book/ 不作为公开仓库对象上传。

Unit
  GitHub 写作系统 UI / 事实源 / 自动化

Story
  渲染驾驶舱核心指标：数字来自 progress/generated/current.json，
  且无 JavaScript 时仍可读。

Bolt Plan
  先定义事实源与校验，再生成聚合，再渲染驾驶舱，最后进入发布门禁。
```

可读稿需要把这个例子写成一条“错误路径 vs AI-DLC 路径”的对照：错误路径直接做漂亮页面；AI-DLC 路径先定义事实源、依赖、验收和事件记录。

## 05 · Experiment & Figure Entry

本章证据入口是 `EXP-03-01 · Intent 到 Story 追踪链生成器`。它检查候选 Inception 分解是否满足结构追踪性：Requirement 是否有下游 Unit 和 Story，Story 是否有上游目标，验收是否存在，引用是否有效。

当前 v0.1 样章已保存完整实验说明、运行命令、成功样例和失败样例，路径包括：

- `experiments/sample/README.md`
- `experiments/sample/output/sample.json`
- `experiments/sample/samples/invalid/`
- `planning/sample-experiment.md`
- `planning/sample-chapter-decision.md`

本章图示方向为“向下分解、向上追踪”：

```text
Intent → Requirements → Context → Units → Stories → Bolt Plan
   ↑             ↑                         ↑
   └──────── Evidence / Acceptance / Human Checkpoints ────────┘
```

若后续生成本章独立 SVG，应命名为 `book/images/ch03-intent-to-bolt.svg`，并遵循 `svg-technical-diagram` 现行规约：宽屏优先、严格网格、白色卡片、浅灰边框、语义色竖线、可编辑文本、无外围装饰边框。

## 06 · D17-T02 Writing Plan

D17-T02 将把本骨架推进为正式可读稿。重点动作：

1. 合并并精炼 `book/chapters/sample.md` 中已经通过 v0.1 审校的内容。
2. 保留“结构检查不等于业务正确”的边界说明。
3. 增加错误分解与修正分解的并列表述。
4. 补齐读者练习，让读者能在 20 分钟内完成自己的最小 Inception。
5. 决定是否在 D17-T02 将书稿构建入口从 `sample.md` 切换到 `ch03-inception.md`，避免同一书稿中出现两个 CH-03。

## References

- `book/chapters/sample.md`：CH-03 v0.1 可读样章与第一轮审校后的正文基础。
- `planning/sample-chapter-decision.md`：CH-03 样章选择与六阶段拆解。
- `planning/sample-experiment.md`：`EXP-03-01` 实验合同、指标和边界。
- `experiments/sample/README.md`：实验运行说明与 verified 状态。
- `experiments/sample/output/sample.json`：合法样例输出证据。
- `planning/reviews/sample-chapter.md`：v0.1 样章第一轮五类审校记录。
- `progress/chapters.json`：章节事实源与阶段状态。
