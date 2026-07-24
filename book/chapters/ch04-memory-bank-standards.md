# 第 4 章 · 上下文工程：Memory Bank 与 Standards

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-04 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D18-T02 · 完成章节可读稿 |
| Draft Completeness | 正式十章生产线可读稿；等待 D18-T03 审校与证据对齐 |
| Primary Question | 如何用版本化事实源和明确标准，让每次全新的 Agent 会话恢复正确上下文并持续遵守工程约束？ |
| Reader Outcome | 能够设计最小 Memory Bank、Standards 目录、工件引用和变更同步规则 |
| Related Experiments | `EXP-04-01` |

## 01 · Question：为什么 AI 需要可恢复的上下文

第 3 章解决的是“如何把 Intent 分解成可执行计划”。但计划一旦进入真实写作或开发，马上会遇到第二个问题：AI 会话是流动的，工程事实却必须连续。

一个人类工程师第二天回到项目时，会从仓库、文档、Issue、测试和最近的决策记录里恢复上下文。一个新的 Agent 会话也需要同样的入口。不同的是，Agent 的语言能力很强，记忆边界却更脆弱：它很容易根据聊天历史里的片段补全缺口，也很容易把旧假设当成当前事实。如果项目只依赖对话记忆，那么越到后期，越难回答三个基本问题。

第一，当前目标到底是什么？是继续 v0.1 发布，还是已经进入 v0.2？如果没有版本化事实源，Agent 可能继续执行已经完成的任务，或者跳过刚出现的阻塞。

第二，哪些文件属于公开仓库，哪些只是本地工作材料？在本书项目里，`specs.md-portal/`、`github_repo_reference_ai-agent-book-main/` 和散落的学习材料都被明确排除在后续 GitHub 上传对象之外。这个边界如果只存在于聊天里，下一次会话就可能误把本地参考材料纳入公开产物。

第三，什么规则不能被“顺手优化”？例如本书核心术语必须保留为 `𝓔 = Engineering with Exsecutio`，`Exsecutio` 不能被自动纠正为 `Execution`。这不是拼写问题，而是作者定义的专用术语。类似规则必须进入 Standards，而不能依赖模型每次都猜对作者意图。

所以，上下文工程的核心问题不是“怎样让 AI 记住更多”。记住更多往往只会扩大噪音。真正的问题是：**怎样把下一次会话必须继承的事实、标准和决策，压缩成可读取、可校验、可更新的工程工件。**

在 AI-DLC 中，Memory Bank 与 Standards 就是这个问题的最小答案。

```text
聊天历史       → 不可靠的回忆
版本化事实源   → 可恢复的当前状态
Standards     → 可继承的工程约束
事件与快照     → 可审计的变化路径
```

本章只回答“上下文如何恢复并约束下一次执行”。它不展开 Bolt 内部如何实现，也不讨论生产部署和监控；这些分别留给第 5、6、8 章。读完本章，读者应能为自己的项目写出一个最小 Memory Bank：至少包含目标、状态、标准、当前任务、证据链接和最近决策，并能解释为什么这些工件足以让一个新会话继续工作。

### 1.1 上下文丢失的三种典型故障

**故障一：目标漂移。**  
Agent 接到“继续下一任务”时，如果没有读取事实源，只能从最近聊天猜测下一步。猜测在短任务里也许够用，但在连续两周写作系统里会很快失真。v0.1 发布后，正确下一步已经从 `D14-T03` 切到 v0.2 周期任务 `C02-T01`；这件事必须由 `progress/cycles.json` 和 `progress/generated/current.json` 证明，而不是由语感决定。

**故障二：边界遗忘。**  
项目越真实，边界越多：哪些目录不上传，哪些素材只作参考，哪些输出可以发布，哪些凭证必须留痕。边界如果没有进入版本化规则，AI 的“整理能力”反而会变成风险，因为它会把看似相关的文件统一归档、移动或发布。

**故障三：标准漂移。**  
写作项目也有工程标准。图表风格、章节六阶段、发布 Definition of Done、GitHub 模板字段、SVG 中不得使用 `foreignObject`，都属于标准。标准漂移不是一次明显错误，而是一系列“看起来也可以”的小偏移。等偏移积累到一本书或一个系统里，读者会感到风格混乱，维护者会失去判断依据。

### 1.2 Memory Bank 不是资料库

很多团队第一次听到 Memory Bank，会把它理解成“把资料都放进去”。这恰恰是误区。资料库追求收集，Memory Bank 追求恢复；资料库可以很大，Memory Bank 应该尽量小；资料库回答“过去有什么”，Memory Bank 回答“下一次应该如何继续”。

一个有效的 Memory Bank 至少满足四个条件。

1. **当前性**：它描述当前项目状态，而不是历史愿望。已完成、阻塞、下一动作和发布源必须能从事实源直接读出。
2. **可追溯性**：每个状态变化都能回到文件、事件、快照或发布回执，避免“我记得已经做了”。
3. **可执行性**：它不仅记录背景，还告诉下一次会话能安全执行什么，不能越界做什么。
4. **可收敛性**：它能被脚本校验。格式、状态枚举、依赖、链接和证据路径不靠人工肉眼长期维护。

本书项目当前的最小上下文就由几类文件组成：`progress/tasks.json` 记录 14 天任务事实，`progress/cycles.json` 记录 v0.2 持续更新周期，`progress/chapters.json` 记录十章六阶段生产线，`progress/events/events.jsonl` 记录关键变化，`memory-bank/standards/` 保存项目标准。它们合在一起，才构成“新会话可以接着干”的上下文。

### 1.3 Standards 是人的判断的固化形式

Standards 的价值不在于显得正式，而在于把人类判断提前放进轨道。人的判断不可能每次都重新解释一遍；一旦解释靠口头补充，AI 的执行速度越快，偏差扩散也越快。

例如，本书已经形成几条强约束：

- 核心公式必须保留 `𝓔 = Engineering with Exsecutio`。
- 图表默认采用技术专著级、瑞士网格、IBM Carbon 倾向的克制风格。
- 公开 GitHub 仓库不纳入本地爬取资料、参考仓库和 working-book 工作材料。
- 每个关键更新都必须进入事件、快照、驾驶舱或发布回执。
- 章节进度必须按 `question / framework / example / experiment / figure / review` 六阶段推进。

这些规则看似分散，其实都在回答同一个问题：当人没有在每个 token 旁边盯着时，AI 如何仍然沿着人的判断前进？

### 1.4 本节完成定义

本节完成后，读者应能复述三句话：

1. Memory Bank 不是“让 AI 记住全部资料”，而是让新会话恢复当前状态、边界和下一动作。
2. Standards 不是文档装饰，而是把人的判断固化成 AI 必须继承的执行约束。
3. 上下文工程的目标不是更长上下文，而是更可靠、更可校验、更能持续更新的事实源。

如果读者能带着这三句话进入第 4 章后续部分，就已经越过了上下文工程最容易误解的一道门：AI-DLC 不追求把聊天变长，而是把工程事实变硬。

## 02 · Framework：最小可恢复上下文栈

CH-04 的框架不是“把所有资料都喂给 AI”，而是设计一组足够小、足够硬、足够可验证的上下文工件，让一个全新会话能恢复当前状态，并继续遵守人的判断与工程标准。

本章采用五层上下文栈：

```text
Current State
  当前周期、下一动作、完成/阻塞状态

Intent & Scope
  目标、边界、不做什么、公开/本地资料边界

Standards
  技术栈、编码规则、术语、视觉风格、发布门禁

Evidence Links
  任务、章节、实验、事件、快照、构建清单、审校记录

Update Protocol
  何时更新、谁更新、如何校验、如何生成可视化记录
```

这五层共同回答新会话的五个恢复问题：

1. 我现在处在什么周期，下一步是什么？
2. 这个任务服务于哪个 Intent，边界在哪里？
3. 哪些规则不能被“顺手优化”？
4. 我做出的判断和变更应该落到哪些证据入口？
5. 我完成后如何让下一次会话也能恢复？

在这套框架中，Memory Bank 负责保存可恢复事实，Standards 负责保存可继承约束，事件与快照负责保存变化路径。它们共同构成 `𝓔 = Engineering with Exsecutio` 在上下文层面的实现：人的判断不只是说出来，而是固化为下一次 AI 执行必须继承的轨道。

### Gate

- [x] 核心问题只有一个：新会话如何恢复正确上下文并持续遵守工程约束。
- [x] 读者结果可以观察：能设计最小 Memory Bank、Standards 目录、工件引用和变更同步规则。
- [x] 本章不把 Memory Bank 写成“更长聊天历史”或“万能长期记忆”。
- [x] 本章不展开 Bolt 内部执行、发布监控或多 Agent 组织治理。

## 03 · Three-Part Argument：为什么上下文工程决定连续交付

### 第一段：聊天历史不能承担工程事实源

聊天历史适合交流，却不适合承担持续交付的事实源。它缺少稳定结构，难以被脚本校验，也无法天然区分“已完成事实”“旧计划”“临时想法”和“作者最终判断”。如果 Agent 只依赖聊天印象继续推进，最容易出现目标漂移、边界遗忘和状态误判。

本段结论：**上下文工程的第一项价值，是把必须继承的当前事实从聊天历史中抽离出来，放进版本化、可校验、可追踪的工件。**

### 第二段：Standards 把人的判断变成可继承约束

人的判断如果只停留在一轮对话里，就会在下一轮执行中衰减。术语不能改、目录不能上传、图表风格不能漂移、发布状态不能手工伪造，这些都不是模型通过“聪明”就能稳定猜中的偏好，而是需要被明确写入 Standards 的工程约束。

本段结论：**上下文工程的第二项价值，是把人的判断固化成新会话必须读取并遵守的标准。**

### 第三段：更新协议让上下文持续变硬，而不是持续变脏

Memory Bank 和 Standards 如果只新增不整理，很快会退化成噪音库。AI-DLC 需要把更新动作本身工程化：状态变化进入事实源，关键变化进入事件账本，阶段结果生成快照，驾驶舱从事实源投影，审校记录回到章节证据链。这样，上下文不是越积越重，而是随着每次交付变得更可恢复。

本段结论：**上下文工程的第三项价值，是让上下文在持续更新中保持可恢复、可审计和可执行。**

## 04 · Example：本书项目的最小 Memory Bank

我们用本书项目自身作为例子。假设一个全新的 Agent 会话只收到一句话：“继续下一任务。”如果它只依赖聊天印象，很容易把“下一任务”理解成最近提到过的任务、v0.1 发布尾声，甚至重复已经完成的工作。要让它稳定接住工作，项目必须把“继续”翻译成可读取的事实。

当前最小 Memory Bank 可以分为五类入口：

```text
Current State
  progress/generated/current.json
  progress/tasks.json
  progress/cycles.json

Intent & Scope
  memory-bank/intents/001-github-writing-system/requirements.md
  memory-bank/story-index.md

Standards
  memory-bank/standards/coding-standards.md
  memory-bank/standards/tech-stack.md
  working-book/SVG_STYLE_GUIDE.md

Evidence Links
  progress/events/events.jsonl
  progress/snapshots/
  planning/reviews/
  .artifacts/book/build-manifest.json

Update Protocol
  validate_project.py
  generate_progress.py
  ci_check.py
```

第一类是 Current State。`progress/tasks.json` 告诉 Agent 哪些任务已经 done，哪个任务 ready，依赖是否满足；`progress/chapters.json` 告诉它每一章的六阶段生产线状态；`progress/generated/current.json` 是面向驾驶舱和下一动作的聚合投影。没有这类事实源，“继续”就只能靠猜。

第二类是 Intent & Scope。`memory-bank/intents/001-github-writing-system/requirements.md` 和 `memory-bank/story-index.md` 让 Agent 知道当前系统最初服务于什么目标：不是单纯写几章文章，而是建立一套可在 GitHub 上持续写作、自动记录、可视化追踪和发布的系统。Scope 也包括“不做什么”：`specs.md-portal/`、`github_repo_reference_ai-agent-book-main/`、`working-book/` 不作为后续 GitHub 仓库对象上传。

第三类是 Standards。`memory-bank/standards/coding-standards.md` 规定了任务、JSON、链接、生成文件和测试的基本约束；`memory-bank/standards/tech-stack.md` 规定了本项目的静态技术栈；`working-book/SVG_STYLE_GUIDE.md` 则保存了图表风格判断。它们共同防止 AI 把“我觉得也不错”当成项目标准。

第四类是 Evidence Links。任务完成不能只停留在一句“已完成”。它应该能回到事件账本、快照、审校记录、实验输出和构建清单。例如 D17-T03 关闭 CH-03 时，证据同时落在 `planning/reviews/ch-03-writing-review.md`、`progress/events/events.jsonl`、`progress/snapshots/` 和驾驶舱对象下钻里。这样，新会话不必信任上一轮 Agent 的自述，可以沿着证据复核。

第五类是 Update Protocol。`validate_project.py` 负责检查事实源，`generate_progress.py` 负责从事实源生成事件、快照和页面，`ci_check.py` 负责把校验串成持续集成门禁。上下文不是人工整理出来的一页“项目简介”，而是每次任务推进后自动变硬的一组工件。

所以，一个带 Memory Bank 的会话会这样理解“继续下一任务”：

```text
读取事实源
  → 找到 ready 任务
  → 检查依赖与边界
  → 修改对应章节或产物
  → 更新任务/章节事实源
  → 生成事件、快照、驾驶舱
  → 运行校验并提交证据
```

没有 Memory Bank 的会话也许能写出流畅文本，但它不知道自己是否在正确任务上；有 Memory Bank 的会话不只是更“有记性”，而是拥有恢复、执行和交接的轨道。

## 05 · Experiment：冷启动恢复 A/B 检查

本章证据入口是 `EXP-04-01 · Memory Bank 冷启动恢复 A/B 实验`。它比较两组候选首轮行动：

- `with_memory_bank`：读取版本化事实源、周期、章节、标准和排除边界后行动。
- `without_memory_bank`：只依赖聊天印象和模糊项目背景行动。

当前样例输出显示：

| Group | Context Recovery | First Action Error | Clarification Questions |
|---|---:|---:|---:|
| with_memory_bank | 100.0% | false | 0 |
| without_memory_bank | 0.0% | true | 3 |

从仓库根目录运行：

```bash
python3 experiments/exp-04-01/quickstart.py --sample
```

输出位于 `experiments/exp-04-01/output/sample.json`。实验只用 Python 标准库，不联网，不调用模型。它检查五件事：当前周期、下一动作、证据路径、排除目录和专用术语是否恢复正确。

这组结果不能证明所有项目都会得到同样数字，也不能证明 AI 一定理解了业务语义。它只能支撑一个更窄、也更可靠的结论：**当关键上下文被写成版本化事实源和 Standards 时，新会话更容易恢复正确行动边界；当上下文只存在于聊天印象里，首个动作错误和术语漂移会更容易出现。**

这正是 AI-DLC 需要实验的地方。我们不要求实验证明“Memory Bank 永远有效”，只要求它把一个可观察差异放到桌面上：同样一句“继续下一任务”，有无工程化上下文，恢复质量可以完全不同。

## 06 · Figure：新会话冷启动恢复栈

本章图示方向为“新会话冷启动恢复栈”：

```text
New Agent Session
  ↓
Read Current State + Intent + Standards + Evidence
  ↓
Derive Next Safe Action
  ↓
Execute and Update Facts
  ↓
Events / Snapshots / Dashboard
  ↺
Next Session Recovers from Updated Facts
```

这张图要强调一个闭环，而不是一个资料夹。新会话先读取 Current State、Intent & Scope、Standards 和 Evidence Links，推导出下一步安全动作；执行后，它必须通过 Update Protocol 把变化写回事实源，并触发 Events、Snapshots 和 Dashboard。下一次会话再从更新后的事实源恢复。

图中至少应有三层视觉权重：

1. 一级：`New Session → Next Safe Action → Updated Facts` 的主流程。
2. 二级：Current State、Intent & Scope、Standards、Evidence Links 四类输入。
3. 三级：Events、Snapshots、Dashboard 等审计输出。

若后续生成独立 SVG，可命名为 `book/images/ch04-memory-bank-stack.svg`，保持技术专著级、宽屏、瑞士网格、IBM Carbon 倾向的克制风格，并避免把 Memory Bank 画成普通资料库。

## 07 · Boundary：本章不解决什么

为了避免 Memory Bank 变成一个装万物的篮子，本章必须划清边界。

第一，本章不讨论“无限长期记忆”。AI-DLC 关注的是工程恢复，不是让模型保存所有对话、资料和偏好。长期记忆如果没有结构、校验和更新规则，只会把旧假设保存得更久。

第二，本章不替代第 5、6 章的 Bolt 执行机制。Memory Bank 告诉 Agent 当前状态和约束，Bolt 决定某个执行批次怎样被设计、实现、测试和验收。上下文正确不等于执行正确。

第三，本章不替代第 8 章的 Operations。事件、快照和驾驶舱可以支撑发布前后的可追踪性，但部署验证、监控和恢复策略仍需要单独展开。

第四，本章不要求所有团队复制本书目录。读者要复制的是原则：当前状态版本化，人的判断标准化，证据路径可追踪，更新协议可自动校验。具体文件名可以不同，但四件事不能缺。

## Reader Exercise

选择你自己的一个项目，用 20 分钟设计一个 6 文件以内的最小 Memory Bank。

1. 写一个 `current-state` 文件：说明当前周期、下一动作、已完成/阻塞状态。
2. 写一个 `intent-and-scope` 文件：说明目标、边界和明确不做的事。
3. 写一个 `standards` 文件：列出 5 条 AI 不能“顺手优化”的规则。
4. 写一个 `evidence-index` 文件：列出任务、实验、审校、发布或构建证据入口。
5. 写一个 `update-protocol` 文件：说明完成任务后必须更新哪些事实源。
6. 删除一个不必要文件，确保 Memory Bank 不是资料库。

完成后，用一句话测试它：让一个完全不了解项目的新会话只读取这组文件，然后回答“下一步安全动作是什么？”如果它还需要大量猜测，你的 Memory Bank 不是太小，而是还不够硬。

## References

- `progress/cycles.json`：v0.2 active cycle 与下一动作来源。
- `progress/generated/current.json`：当前进度聚合与驾驶舱数据。
- `progress/chapters.json`：十章六阶段生产线事实源。
- `memory-bank/standards/coding-standards.md` 与 `memory-bank/standards/tech-stack.md`：当前项目 Standards 入口。
- `planning/releases/v0.2-draft.md`：v0.2 持续更新周期草案。
- `experiments/exp-04-01/README.md`：Memory Bank 冷启动恢复 A/B 实验说明。
- `experiments/exp-04-01/output/sample.json`：C02-T02 生成的可复现实验输出。
