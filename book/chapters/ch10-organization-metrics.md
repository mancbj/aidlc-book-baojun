# 第 10 章 · 组织与度量：从 Agent 分工到研发操作系统

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-10 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D24-T03 · 完成章节审校与证据对齐 |
| Draft Completeness | 正式十章生产线可读稿；D24-T03 五类审校已完成 |
| Primary Question | 如何重构人、Agent、协作节奏与度量体系，并判断哪些 AI-DLC 实践值得在组织内规模化？ |
| Reader Outcome | 能够设计 Master/Inception/Construction/Operations 与人的责任图、Mob 协作节奏和业务价值记分卡 |
| Related Experiments | `EXP-10-01`、`EXP-10-02`、`EXP-10-03` |

## 01 · Question：为什么有了 Flow 还不够，还要组织与度量

第 9 章回答了方法适配：如何按风险在 Simple、FIRE 与 AI-DLC 之间选择治理强度。第 10 章继续问一个更组织化的问题：**即使选对了 Flow，人与 Agent 如何分工、如何协作、如何度量，才能判断哪些实践值得规模化？**

这就是“从 Agent 分工到研发操作系统”的范围。

AI-DLC 不是只给个人提速的技巧清单。当多个 Agent、多个会话、多个角色同时工作时，如果责任不清，AI 的速度会放大推诿；如果协作节奏不清，上下文会在交接中蒸发；如果度量只看“生成了多少”，组织会奖励噪音而不是价值。

个人层面的 Exsecutio 可以把提议贯彻为交付候选；组织层面还要把贯彻能力变成可复制的操作系统：谁负责什么，何时同步，怎样知道试点该扩大还是停用。这里的 `Exsecutio` 仍是指定术语，强调贯彻，而不是普通 execution。

因此，本章的核心问题是：**如何重构人、Agent、协作节奏与度量体系，并判断哪些 AI-DLC 实践值得在组织内规模化？**

读完本章，读者应能完成三个动作：

1. 为 Master／Inception／Construction／Operations 与人的关键决策画出责任边界。
2. 设计一套最小 Mob 协作节奏，使 elaboration 与 construction 可交接。
3. 用业务价值记分卡判断试点是否值得扩大，而不是只看产出数量。

### Gate

- [x] 核心问题只有一个：如何重构分工、节奏与度量以支撑规模化。
- [x] 读者结果可以观察：能设计责任图、Mob 节奏和价值记分卡。
- [x] 本章不重新展开单个 Flow 的内部实现；那是 CH-03～CH-09 的内容。
- [x] 三项 EXP-10 实验当前均为 planned，不得写成已验证结论。

## 02 · Framework：责任、节奏与价值三层

本章用三层框架描述组织化 AI-DLC：

```text
Responsibility
  人与四类 Agent 的决策、执行、审批与知会边界

Cadence
  Mob Elaboration、Mob Construction、异步审阅与交接节奏

Value Scorecard
  周期、质量、成本、可复现性、人工注意力与业务结果
```

没有责任层，Agent 只是更快的手指；没有节奏层，责任图只是墙上海报；没有记分卡，规模化只是感觉良好的扩张。

### 2.1 Responsibility：四 Agent 与人的责任图

specs.md 参考实现中的四类 Agent 提供了分工骨架：

```text
Master Agent
  路由、上下文判断、阶段导航

Inception Agent
  把意图变成可执行计划

Construction Agent
  沿 Bolt 推进到交付候选

Operations Agent
  发布、运行、观察与恢复
```

Agent 分工不等于人的责任消失。本章采用 RACI 思路：对关键活动标明 Responsible、Accountable、Consulted、Informed。

| 活动 | Agent 可 Responsible | 人必须 Accountable 的内容 |
|---|---|---|
| 路由到下一阶段 | Master 可提议 | 是否接受阶段切换与优先级 |
| 分解 Intent／Unit／Story | Inception 可起草 | 目标、边界、完成定义 |
| 执行 Bolt／修复失败 | Construction 可推进 | 风险接受、停手条件 |
| 发布与回滚 | Operations 可准备 | 发布后果与恢复授权 |

一句话原则：**AI 可以 Responsible，人必须保留 Accountable。** 模型可以提出方案，但不能自动成为最终责任主体。

本层结论：**组织化的第一步，是让每个关键决策都有且只有一个最终责任人。**

### 2.2 Cadence：Mob 与工件驱动的协作节奏

协作节奏要回答“何时同步、何时异步、交接什么”。

```text
Mob Elaboration
  共同澄清意图、边界与计划

Mob Construction
  在关键门禁处共同推进或复核

Artifact-driven async review
  用仓库工件而不是聊天记录做异步审阅

Handoff log
  记录未决问题、证据位置和下一个可执行点
```

同步会议只应发生在高杠杆点：澄清意图、接受风险、批准发布、复盘事故。其余时间，协作应围绕可版本化工件：章节稿、tasks.json、审校记录、CI 结果、progress events、dashboard。

Dashboard（进度驾驶舱、Bird's-Eye 视图、事件与快照）属于节奏的观测面：它不替代责任，但让失步可见。如果驾驶舱显示 ready 任务、章节阶段和最近事件，下一班人就不需要重建聊天上下文。

本层结论：**节奏的产品是可交接状态，而不是更长的会议。**

### 2.3 Value Scorecard：用什么证明值得规模化

规模化不能只看“用了 AI-DLC”。最小记分卡至少覆盖：

| 维度 | 要看的信号 | 常见假信号 |
|---|---|---|
| Cycle time | 从意图到可审阅候选／可发布入口的时间 | 只统计生成字数或 commit 数 |
| Quality | 缺陷逃逸、返工、验证失败后的修复闭环 | 只看 CI 绿勾，不看内容与运行风险 |
| Cost / Attention | 人工审阅负担、仪式税、阻塞时间 | 把所有会议和检查都算成“质量投入” |
| Reproducibility | 跨会话恢复、证据完整、来源可追溯 | 个人笔记本里的“我记得” |
| Business result | 读者／用户／业务目标是否改善 | 内部满意度口号 |

记分卡的用法不是制造新 KPI 剧场，而是支持三个决定：扩大、收缩、停用。说不清这三者，就还不具备规模化资格。

本层结论：**只有能同时解释速度、质量与注意力成本的实践，才值得扩大。**

## 03 · Three-Part Argument：为什么组织层决定规模化成败

### 第一段：无人负责的自动化会制造系统性推诿

AI 可以提议、生成和修补，但不能自动承担组织后果。如果 Master／Inception／Construction／Operations 的活动没有人的 Accountable，团队会在事故后发现“每个人都参与了，没有人负责”。

速度越高，推诿越贵。因为错误会更快穿过更多环节，而责任空白会在事后同时暴露。

本段结论：**组织化 AI-DLC 的第一项价值，是把 Agent 能力嵌回明确的人责边界。**

### 第二段：没有交接节奏，上下文工程会在组织缝隙里失效

Memory Bank、任务事实源和审校记录解决的是工件层记忆；Mob 节奏解决的是人际与跨会话缝隙。两者缺一，组织就会反复冷启动：每个新会话都重新解释“我们做到哪了、为什么停在这里、下一步是什么”。

本段结论：**组织化 AI-DLC 的第二项价值，是让协作节奏保护上下文，而不是靠英雄记忆。**

### 第三段：没有价值记分卡，规模化会复制浪费

把一个本地有效的提示词技巧或流程模板直接推广，可能同时复制其仪式税和盲区。记分卡迫使团队回答：周期是否缩短、质量是否可维持、注意力是否被浪费、业务结果是否改善。

没有记分卡的推广，只是把个人习惯写成组织政策。

本段结论：**组织化 AI-DLC 的第三项价值，是用可比较信号决定扩大、收缩或停用。**

## 04 · Example：以本书写作系统试点为例

本书的 GitHub 写作系统是一个小而完整的组织试点：有分工，有节奏，有观测面，也有明确的完成与发布门禁。它不是大企业 RACI 全手册，但足以演示三层框架如何落地。

### 4.1 责任图：谁对什么负责

| 活动 | Responsible（可含 Agent） | Accountable（人） | 关键工件 |
|---|---|---|---|
| 路由下一张 Dxx 卡片 | Master-like 路由／状态分析 | 作者／Maintainer | `progress/tasks.json` |
| 锁定章节骨架／可读稿 | Construction-like 写作执行 | 作者 | `book/chapters/*.md` |
| 五类审校 | 审校执行者／Agent 辅助 | 作者 | `planning/reviews/*` |
| 校验与进度生成 | 脚本与 CI | 作者／Maintainer | `scripts/*`、`progress/generated/` |
| Pages／Release | Operations-like workflow | Maintainer | workflows、manifest、release |

这里的关键约束是：Agent 可以帮助写稿、改脚本、跑校验，但“是否关闭任务、是否接受审校结论、是否发布”仍由人 Accountable。

### 4.2 节奏：冲刺卡片、PR 与驾驶舱

本书试点的最小节奏可以写成：

```text
1. 从 ready 任务开始（单一焦点）
2. 在独立分支完成产物
3. 跑 links / build / validate / generate_progress / ci_check
4. 用 PR 提交审阅，不自动合并
5. 让 events、snapshots、dashboard 记录状态变化
6. 下一会话先读事实源，再继续
```

这对应了 Mob Elaboration（明确任务与边界）、Mob Construction（在门禁处共同或连续复核）、以及工件驱动异步审阅（PR + review + CI）。交接日志不一定单独成文；`tasks.json`、审校记录和 progress events 共同承担 handoff。

### 4.3 记分卡种子：如何判断试点是否值得继续

| 维度 | 本书试点可观察信号 |
|---|---|
| Cycle time | 一张 Dxx 卡片从 ready 到 done 的关闭速度 |
| Quality | CI、内部链接、五类审校、release readiness |
| Attention | blocked 项、返工次数、无证据的大段返修 |
| Reproducibility | events／snapshots／source identity 是否可回看 |
| Business result | 可读章节增加、试读反馈、发布入口是否可用 |

若周期变长却没有质量或可复现性收益，就应收缩仪式；若质量门禁总被跳过，就应停止扩大，先修责任与节奏。

## 05 · Pattern：一份最小组织操作系统清单

| 层 | 最小产物 | 失败信号 |
|---|---|---|
| Responsibility | 一页 RACI／责任图 | 事故后找不到 Accountable |
| Cadence | 同步点清单 + 异步工件约定 | 每个会话都冷启动 |
| Scorecard | 5 维试点记分卡 | 只会说“我们用了 AI” |
| Observation | Dashboard／事件／快照 | 状态只存在聊天里 |
| Scale decision | 扩大／收缩／停用规则 | 无证据地全面推广 |

这张表可以直接用于小团队试点。大组织可以扩展角色和指标，但不应删掉 Accountable、交接工件和停用条件。

## 06 · Experiment：三个验证方向

本章实验入口包括三项：

- `EXP-10-01 · 人–Agent 责任 RACI 生成器`：根据研发活动、四类 Agent 与团队角色，生成责任、审批、协作和知会矩阵。运行：`python3 experiments/exp-10-01/quickstart.py --sample`。
- `EXP-10-02 · AI-DLC 价值记分卡`：根据交付基线、运行记录、缺陷与业务结果，生成周期、质量、审阅负担与业务价值看板。
- `EXP-10-03 · Mob 协作与 Agent 交接复现`：参考官方 AI-DLC 与 Agile 对照及团队协作案例，复现 Mob Elaboration、Mob Construction 与交接日志。

其中 `EXP-10-01` 已 verified：样例报告在 `experiments/exp-10-01/output/sample.json`。它证明关键活动可生成 RACI，并暴露无 Accountable 与责任冲突；Accountable 必须是人，Agent 可以 Responsible。它不证明生成矩阵适合所有组织。`EXP-10-02` 与 `EXP-10-03` 仍为 `planned`；`EXP-10-03` 还需保留外部来源与 pinned version 边界。

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-10-01` | 关键活动是否都有 Accountable，且冲突可见 | 不证明生成的 RACI 已适合所有组织 |
| `EXP-10-02` | 记分卡是否同时覆盖周期、质量、注意力与业务结果 | 不证明某次试点的业务价值已被因果证实 |
| `EXP-10-03` | Mob 与交接日志是否降低信息损失 | 不把外部对照复现写成已完成生产验证 |

## 07 · Figure：研发操作系统三层图

本章图示为“研发操作系统三层图”：

![图 10-1 · 研发操作系统三层图](images/ch10-org-operating-system.svg){.core-figure width=100%}

源文件：`book/images/ch10-org-operating-system.svg`。三层结构：

```text
People & Agents  →  Responsibility (RACI)
        ↓
Collaboration    →  Cadence (Mob + async review)
        ↓
Evidence & Value →  Scorecard + Dashboard
```

图中必须标出：Accountable 属于人；Agent 可以 Responsible；Dashboard 是观测面而不是责任本身；记分卡输出是扩大／收缩／停用，而不是更多虚荣指标。右侧保留 Scale Decision。

## 08 · Boundary：本章不解决什么

第一，本章不重新展开单个 Flow 的内部实现。Simple／FIRE／AI-DLC 的选型属于 CH-09；Inception、Bolt、Exsecutio、验证与 Operations 的机制属于前面章节。

第二，本章不提供企业变革全方案。它只给小团队试点所需的责任图、节奏和记分卡最小集。

第三，本章不把 Dashboard 写成管理控制台神话。驾驶舱让状态可见，但不自动产生正确决策。

第四，本章不承诺 `EXP-10-01` 已证明组织落地效果；也不把仍为 `planned` 的 `EXP-10-02`、`EXP-10-03` 写成已验证。

第五，本章不允许把最终责任外包给模型。AI proposes，human remains accountable。

## Reader Exercise

用 30 分钟为你的团队设计一个最小 AI-DLC 组织操作系统。

1. 列出 5 个关键活动（例如：选题、分解、实现、审校、发布）。
2. 为每个活动填写 R／A／C／I，并检查是否恰好有一个 Accountable。
3. 设计一周节奏：哪些点必须 Mob，哪些点必须异步围绕工件审阅。
4. 写出交接最小集：下一班人打开哪些文件就能继续。
5. 填写 5 维记分卡的当前基线（可先用估计，但要标明是估计）。
6. 写出三条规模化规则：何时扩大、何时收缩、何时停用。
7. 最后用一句话判定：这个试点现在是 Expand、Hold、Shrink，还是 Stop。

如果你能说清“谁负责、如何交接、凭什么扩大”，你就已经从使用 Agent 进入了组织化 AI-DLC。

## References

- `book/toc.md`：CH-10 核心问题、读者结果与参考实现。
- `book/part-00-overview.md`：规模层与阅读路线。
- `book/chapters/ch02-human-judgment.md`：四 Agent 与人机责任前置讨论。
- `book/chapters/ch06-exsecutio.md`：`Exsecutio` 指定术语与贯彻层。
- `book/chapters/ch09-adaptive-engineering.md`：Flow 选择边界；本章不重写选型矩阵。
- `progress/tasks.json` / `progress/chapters.json` / `progress/events/events.jsonl`：组织试点中的事实源节奏。
- `site/`：进度驾驶舱作为观测面参考。
- `progress/experiments.json`：`EXP-10-01`、`EXP-10-02`、`EXP-10-03`。
- `https://specs.md/methodology/ai-dlc-vs-agile`：`EXP-10-03` 外部对照入口；本地 portal 副本不进入仓库。
