# 第 9 章 · 适配性工程：选择正确的 Flow 与治理强度

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-09 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D23-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；等待 D23-T02 扩展为完整可读稿 |
| Primary Question | 如何根据任务复杂度、代码库现状、监管要求和团队规模，在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化？ |
| Reader Outcome | 能够使用风险—仪式矩阵选择 Flow、检查点数量与运行范围，并解释选择代价 |
| Related Experiments | `EXP-09-01`、`EXP-09-02`、`EXP-09-03` |

## 01 · Question：为什么“正确的方法”取决于风险，而不是口号

第 8 章回答了运行问题：通过验证的候选物如何进入可观测、可回滚的 Operations。第 9 章把镜头从单次交付拉远一层：**当任务、代码库、监管约束和团队规模不同时，团队该如何选择治理强度，而不是默认一套流程通吃？**

这就是适配性工程的范围。

在 AI-DLC 中，方法不是装饰，而是风险对冲。Simple Flow 用更少仪式换更快启动；FIRE 用自适应检查点和动态 Run 处理棕地与不确定边界；完整 AI-DLC Flow 用 Intent、Unit、Bolt、Memory Bank、验证和 Operations 换取可追溯与可恢复。三者都有价值，也都有代价。

如果没有适配性选择，团队会在两个方向翻车。

第一，过度工程化。一个可逆的小改动被要求完整 Intent 分解、多层 Bolt、完整 Operations Runbook，结果仪式成本高于风险本身，AI 速度优势被流程吞掉。第二，不足工程化。一个高影响、低可逆、受监管或多人交接的任务只靠聊天式生成和临场判断，结果错误级联、证据缺失、回滚困难。

因此，本章的核心问题是：**如何根据任务复杂度、代码库现状、监管要求和团队规模，在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化？**

读完本章，读者应能完成三个动作：

1. 用一组可观察维度评估任务风险与治理需求。
2. 在 Simple、FIRE 与 AI-DLC 之间作出有依据的 Flow 选择，并写出不适用条件。
3. 解释该选择带来的检查点数量、运行范围和审阅代价，而不是只说“感觉适合”。

### Gate

- [x] 核心问题只有一个：如何按风险选择 Flow 与治理强度。
- [x] 读者结果可以观察：能使用风险—仪式矩阵选择 Flow、检查点数量与运行范围并解释代价。
- [x] 本章不重新展开单次 Operations 运行链；那是 CH-08 的重点。
- [x] 本章不提前重构组织角色与价值度量；那是 CH-10 的重点。
- [x] 三项 EXP-09 实验当前均为 planned，骨架阶段不得写成已验证结论。

## 02 · Framework：风险—仪式矩阵

本章用“风险—仪式矩阵”作为 Flow 选择框架：先判断风险与约束，再匹配仪式强度，最后显式承担代价。

```text
Risk Dimensions
  Complexity · Codebase State · Compliance · Team Scale · Reversibility

Ceremony Budget
  Checkpoints · Artifacts · Approvals · Traceability · Runtime Scope

Flow Options
  Simple Flow
  FIRE Flow
  AI-DLC Flow
```

矩阵的左边不是偏好，而是约束；右边不是荣誉，而是成本。选择 Flow，就是在“错误代价”和“仪式代价”之间做可解释权衡。

### 2.1 五个风险维度

选择前至少评估五个维度：

| 维度 | 要问的问题 | 高信号 |
|---|---|---|
| Complexity | 任务是否跨越多个领域概念、接口或不确定需求？ | 多 Unit、多边界、需求仍在漂移 |
| Codebase State | 是绿地、棕地，还是 monorepo / 遗留耦合系统？ | 高耦合、缺少测试、局部改动影响面不清 |
| Compliance | 是否有审计、安全、监管或客户合同要求？ | 变更必须留痕、批准、可回放 |
| Team Scale | 是单人推进，还是跨角色、跨会话、跨班次交接？ | 多人并行、上下文易丢失 |
| Reversibility | 出错后能否快速撤回，数据或用户影响是否可恢复？ | 低可逆、影响生产入口或历史版本 |

本层结论：**先刻画风险，再谈方法；否则 Flow 选择只是口味争论。**

### 2.2 三种 Flow 的治理强度

三种参考 Flow 可以先按仪式强度粗分：

```text
Simple
  Requirements → Design → Tasks
  适合低复杂度、高可逆、边界清楚的任务

FIRE
  动态 Run、自适应检查点、Brownfield / Monorepo 友好
  适合不确定边界、需要边走边确认的任务

AI-DLC
  Intent → Units → Stories → Bolts → Memory Bank → Verify → Operations
  适合需要完整追溯、多人交接和持续恢复能力的任务
```

这里的 Simple、FIRE 与 AI-DLC 是治理强度选项，不是身份标签。同一产品在不同任务上可以选用不同 Flow；同一团队也可以在试点中从 Simple 升到 AI-DLC，或从 AI-DLC 降到 FIRE，只要选择理由和不适用条件被写下来。

本层结论：**Flow 是风险对冲工具，不是团队站队旗帜。**

### 2.3 仪式预算：检查点、范围与代价

选完 Flow 还不够，还要决定仪式预算：

- Checkpoints：哪些点必须停下来确认、验证或批准？
- Artifacts：哪些对象必须进入仓库事实源？
- Runtime scope：只做到交付候选，还是必须进入 Pages／Release／监控？
- Review cost：预计增加多少人工注意力？

预算的目标不是“越多越专业”，而是“刚好覆盖关键风险”。多出来的检查点是税；少掉的检查点是债。

本层结论：**适配性工程的产品，是可解释的仪式预算，而不只是选一个名词。**

## 03 · Three-Part Argument：为什么方法必须可适配

### 第一段：统一流程会同时制造浪费和空洞

如果所有任务都走完整 AI-DLC，低风险改动会浪费注意力；如果所有任务都走聊天式 Simple，高风险改动会失去追溯和恢复能力。统一流程看起来公平，实际上对风险不公平。

本段结论：**适配性工程的第一项价值，是避免用同一套仪式处理不同量级的风险。**

### 第二段：代码库状态会改变同一方法的真实成本

同样叫“加一个发布检查”，在绿地小仓和棕地 monorepo 中的成本完全不同。Brownfield 会放大隐藏依赖、测试缺口和回归面；此时 FIRE 的动态 Run 与自适应检查点，或 AI-DLC 的更强追溯，可能比表面简单的线性流程更便宜。

本段结论：**适配性工程的第二项价值，是把代码库现状算进 Flow 选择，而不是假装所有仓库一样干净。**

### 第三段：选择必须带着代价和不适用条件

只说“我们选 AI-DLC”没有工程内容。真正有用的选择要说明：为什么这套仪式能覆盖哪些风险，哪些任务不该用它，检查点预算是多少，以及如果判断错了如何降级或升级。

本段结论：**适配性工程的第三项价值，是让 Flow 选择成为可审阅决策，而不是口号。**

## 04 · Example Skeleton：三类任务的 Flow 对照

D23-T02 可读稿将用三类不同风险任务做对照，并演示“选错 Flow”时会发生什么。

最小案例结构如下：

```text
Task A · 低风险文案修正
  维度：低复杂度、高可逆、单人、无强监管
  倾向：Simple
  不适用：为它建立完整 Operations Runbook 和多层 Bolt

Task B · 棕地发布门禁改造
  维度：中高复杂度、Brownfield、影响发布入口、需可回滚
  倾向：FIRE 或局部 AI-DLC
  不适用：无检查点的一次性大改

Task C · 多角色写作系统冲刺
  维度：多会话交接、事实源约束、验证与发布连续、团队协作
  倾向：AI-DLC
  不适用：只靠聊天记录保存状态

Swap Test
  把 Task A 套进 AI-DLC，观察仪式税
  把 Task C 套进无追溯 Simple，观察证据空洞
```

这个例子要回答一个关键问题：如果团队不能说明“为什么选这个 Flow、检查点花在哪里、什么情况下不该用”，那么他们拥有的不是适配性工程，只是流程偏好。

## 05 · Experiment & Figure Entry

本章实验入口包括三项：

- `EXP-09-01 · Simple/FIRE/AI-DLC Flow 选择器`：根据任务复杂度、代码库状态、团队规模与合规要求，生成 Flow 建议、理由与不适用条件。
- `EXP-09-02 · 风险到检查点预算模拟器`：根据风险清单、可逆性、影响范围与自治偏好，生成检查点数量、位置与成本收益估算。
- `EXP-09-03 · Brownfield Flow 选择案例复现`：参考官方 Flow 决策指南与棕地项目案例，复现 Simple、FIRE、AI-DLC 三方案对照决策。

三项实验当前均为 `planned`。本章骨架只把它们作为验证方向，不把专家一致率、检查点覆盖率或流程开销写成已得到验证的事实。后续若升级为正文证据，至少需要补齐实验目录、样例输入、样例输出、测试和结果记录；`EXP-09-03` 还需保留外部来源与 pinned version 边界。

本章图示方向为“风险—仪式矩阵”：

```text
                Low Ceremony ---- High Ceremony
High Risk       FIRE / AI-DLC     AI-DLC
Medium Risk     FIRE              FIRE / AI-DLC
Low Risk        Simple            Simple / FIRE
```

若后续生成独立 SVG，可命名为 `book/images/ch09-risk-ceremony-matrix.svg`，采用宽屏矩阵布局：横轴为仪式强度，纵轴为风险等级，三个 Flow 以克制色块标注典型落点，并在旁侧列出五个风险维度与不适用条件。

## 06 · D23-T02 Writing Plan

D23-T02 将把本骨架扩展为完整可读稿。重点动作：

1. 扩写五个风险维度与三种 Flow 的匹配规则，避免把矩阵写成机械查表。
2. 用三类任务对照和一次 Swap Test 展示选对／选错 Flow 的代价差异。
3. 写清 CH-08 Operations 与 CH-09 Flow 选择的边界，以及 CH-10 组织度量尚未展开。
4. 将 `EXP-09-01`、`EXP-09-02`、`EXP-09-03` 保持为 planned 验证方向，不提前宣称已验证。
5. 增加读者练习：为一个真实任务填写风险维度、Flow 选择、检查点预算、不适用条件与代价说明。

## References

- `book/toc.md`：CH-09 核心问题、读者结果、参考实现与实验方向。
- `book/part-00-overview.md`：规模层问题与 AI-DLC Flow 参考路径。
- `progress/experiments.json`：`EXP-09-01`、`EXP-09-02`、`EXP-09-03` 实验治理状态。
- `progress/chapters.json`：CH-09 六阶段生产线状态。
- `https://specs.md/architecture/choose-flow`：`EXP-09-03` 外部决策指南入口；本地 portal 副本不进入仓库。
