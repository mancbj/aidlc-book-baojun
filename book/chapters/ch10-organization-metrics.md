# 第 10 章 · 组织与度量：从 Agent 分工到研发操作系统

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-10 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D24-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；等待 D24-T02 扩展为完整可读稿 |
| Primary Question | 如何重构人、Agent、协作节奏与度量体系，并判断哪些 AI-DLC 实践值得在组织内规模化？ |
| Reader Outcome | 能够设计 Master/Inception/Construction/Operations 与人的责任图、Mob 协作节奏和业务价值记分卡 |
| Related Experiments | `EXP-10-01`、`EXP-10-02`、`EXP-10-03` |

## 01 · Question：为什么有了 Flow 还不够，还要组织与度量

第 9 章回答了方法适配：如何按风险在 Simple、FIRE 与 AI-DLC 之间选择治理强度。第 10 章继续问一个更组织化的问题：**即使选对了 Flow，人与 Agent 如何分工、如何协作、如何度量，才能判断哪些实践值得规模化？**

这就是“从 Agent 分工到研发操作系统”的范围。

AI-DLC 不是只给个人提速的技巧清单。当多个 Agent、多个会话、多个角色同时工作时，如果责任不清，AI 的速度会放大推诿；如果协作节奏不清，上下文会在交接中蒸发；如果度量只看“生成了多少”，组织会奖励噪音而不是价值。

因此，本章的核心问题是：**如何重构人、Agent、协作节奏与度量体系，并判断哪些 AI-DLC 实践值得在组织内规模化？**

读完本章，读者应能完成三个动作：

1. 为 Master／Inception／Construction／Operations 与人的关键决策画出责任边界。
2. 设计一套最小 Mob 协作节奏，使 elaboration 与 construction 可交接。
3. 用业务价值记分卡判断试点是否值得扩大，而不是只看产出数量。

### Gate

- [x] 核心问题只有一个：如何重构分工、节奏与度量以支撑规模化。
- [x] 读者结果可以观察：能设计责任图、Mob 节奏和价值记分卡。
- [x] 本章不重新展开单个 Flow 的内部实现；那是 CH-03～CH-09 的内容。
- [x] 三项 EXP-10 实验当前均为 planned，骨架阶段不得写成已验证结论。

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

但 Agent 分工不等于人的责任消失。本章采用 RACI 思路：对关键活动标明 Responsible、Accountable、Consulted、Informed。人至少保留 Accountable：目标、风险接受、完成定义和发布后果。

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

Dashboard（进度驾驶舱、Bird's-Eye 视图、事件与快照）属于节奏的观测面：它不替代责任，但让失步可见。

本层结论：**节奏的产品是可交接状态，而不是更长的会议。**

### 2.3 Value Scorecard：用什么证明值得规模化

规模化不能只看“用了 AI-DLC”。最小记分卡至少覆盖：

| 维度 | 要看的信号 |
|---|---|
| Cycle time | 从意图到可审阅候选／可发布入口的时间 |
| Quality | 缺陷逃逸、返工、验证失败后的修复闭环 |
| Cost / Attention | 人工审阅负担、仪式税、阻塞时间 |
| Reproducibility | 跨会话恢复、证据完整、来源可追溯 |
| Business result | 读者／用户／业务目标是否改善 |

本层结论：**只有能同时解释速度、质量与注意力成本的实践，才值得扩大。**

## 03 · Three-Part Argument：为什么组织层决定规模化成败

### 第一段：无人负责的自动化会制造系统性推诿

AI 可以提议、生成和修补，但不能自动承担组织后果。如果 Master／Inception／Construction／Operations 的活动没有人的 Accountable，团队会在事故后发现“每个人都参与了，没有人负责”。

本段结论：**组织化 AI-DLC 的第一项价值，是把 Agent 能力嵌回明确的人责边界。**

### 第二段：没有交接节奏，上下文工程会在组织缝隙里失效

Memory Bank、任务事实源和审校记录解决的是工件层记忆；Mob 节奏解决的是人际与跨会话缝隙。两者缺一，组织就会反复冷启动。

本段结论：**组织化 AI-DLC 的第二项价值，是让协作节奏保护上下文，而不是靠英雄记忆。**

### 第三段：没有价值记分卡，规模化会复制浪费

把一个本地有效的提示词技巧或流程模板直接推广，可能同时复制其仪式税和盲区。记分卡迫使团队回答：周期是否缩短、质量是否可维持、注意力是否被浪费、业务结果是否改善。

本段结论：**组织化 AI-DLC 的第三项价值，是用可比较信号决定扩大、收缩或停用。**

## 04 · Example Skeleton：以本书写作系统试点为例

D24-T02 可读稿将以本书 GitHub 写作系统为最小组织试点案例。

最小案例结构如下：

```text
Responsibility map
  作者 / Maintainer：Accountable for 发布与事实源
  Master-like routing：任务路由与阶段判断
  Inception-like planning：Dxx 任务与章节骨架
  Construction-like execution：可读稿、脚本、校验
  Operations-like release：Pages / Release / dashboard

Cadence
  每日一章冲刺卡片
  PR 审阅与五类审校
  progress events / snapshots / dashboard
  handoff via tasks.json + reviews

Scorecard seeds
  Cycle: Dxx 卡片关闭速度
  Quality: CI / links / review gates
  Attention: 返工与 blocked 项
  Reproducibility: 事件、快照、source identity
  Business: 可读章节与试读反馈
```

这个例子要回答：一个小团队如何用责任图、节奏和记分卡，判断“十章生产线 + 进度驾驶舱”是否值得继续投入，而不是只看写了多少字。

## 05 · Experiment & Figure Entry

本章实验入口包括三项：

- `EXP-10-01 · 人–Agent 责任 RACI 生成器`：根据研发活动、四类 Agent 与团队角色，生成责任、审批、协作和知会矩阵。
- `EXP-10-02 · AI-DLC 价值记分卡`：根据交付基线、运行记录、缺陷与业务结果，生成周期、质量、审阅负担与业务价值看板。
- `EXP-10-03 · Mob 协作与 Agent 交接复现`：参考官方 AI-DLC 与 Agile 对照及团队协作案例，复现 Mob Elaboration、Mob Construction 与交接日志。

三项实验当前均为 `planned`。本章骨架只把它们作为验证方向，不把无负责人决策数、缺陷逃逸率或交接信息损失率写成已验证结论。后续升级需补齐实验目录、样例、测试与结果；`EXP-10-03` 还需保留外部来源与 pinned version 边界。

本章图示方向为“研发操作系统三层图”：

```text
People & Agents  →  Responsibility (RACI)
        ↓
Collaboration    →  Cadence (Mob + async review)
        ↓
Evidence & Value →  Scorecard + Dashboard
```

若后续生成独立 SVG，可命名为 `book/images/ch10-org-operating-system.svg`，采用宽屏三层布局：上层责任，中层节奏，下层度量与驾驶舱，右侧标注 Accountable 仍属于人。

## 06 · D24-T02 Writing Plan

D24-T02 将把本骨架扩展为完整可读稿。重点动作：

1. 扩写四 Agent 与人的 RACI 示例，强调 Accountable 不可外包给模型。
2. 用本书写作系统试点写清 Mob／异步审阅／dashboard 交接节奏。
3. 给出最小价值记分卡，并说明哪些信号能支持扩大或停用。
4. 将 EXP-10-01／02／03 保持为 planned。
5. 增加读者练习：为一支小队画出责任图、一周节奏和试点记分卡。

## References

- `book/toc.md`：CH-10 核心问题、读者结果与参考实现。
- `book/part-00-overview.md`：规模层与阅读路线。
- `book/chapters/ch02-human-judgment.md`：四 Agent 与人机责任前置讨论。
- `book/chapters/ch09-adaptive-engineering.md`：Flow 选择边界；本章不重写选型矩阵。
- `progress/experiments.json`：`EXP-10-01`、`EXP-10-02`、`EXP-10-03`。
- `site/`：进度驾驶舱作为组织观测面参考。
- `https://specs.md/methodology/ai-dlc-vs-agile`：`EXP-10-03` 外部对照入口；本地 portal 副本不进入仓库。
