# 第 9 章 · 适配性工程：选择正确的 Flow 与治理强度

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-09 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D23-T03 · 完成章节审校与证据对齐 |
| Draft Completeness | 正式十章生产线可读稿；D23-T03 五类审校已完成 |
| Primary Question | 如何根据任务复杂度、代码库现状、监管要求和团队规模，在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化？ |
| Reader Outcome | 能够使用风险—仪式矩阵选择 Flow、检查点数量与运行范围，并解释选择代价 |
| Related Experiments | `EXP-09-01`、`EXP-09-02`、`EXP-09-03` |

## 01 · Question：为什么“正确的方法”取决于风险，而不是口号

第 8 章回答了运行问题：通过验证的候选物如何进入可观测、可回滚的 Operations。第 9 章把镜头从单次交付拉远一层：**当任务、代码库、监管约束和团队规模不同时，团队该如何选择治理强度，而不是默认一套流程通吃？**

这就是适配性工程的范围。

在 AI-DLC 中，方法不是装饰，而是风险对冲。Simple Flow 用更少仪式换更快启动；FIRE 用自适应检查点和动态 Run 处理棕地与不确定边界；完整 AI-DLC Flow 用 Intent、Unit、Bolt、Memory Bank、验证和 Operations 换取可追溯与可恢复。三者都有价值，也都有代价。

如果没有适配性选择，团队会在两个方向翻车。

第一，过度工程化。一个可逆的小改动被要求完整 Intent 分解、多层 Bolt、完整 Operations Runbook，结果仪式成本高于风险本身，AI 速度优势被流程吞掉。第二，不足工程化。一个高影响、低可逆、受监管或多人交接的任务只靠聊天式生成和临场判断，结果错误级联、证据缺失、回滚困难。

AI 参与后，这个问题会更尖锐。AI 让草案、代码和文档变得便宜，于是团队更容易误以为“流程也可以更随便”，或者反过来误以为“既然 AI 很快，就该把所有仪式都叠上去”。两种反应都错了。便宜的是提议，不便宜的是错误代价和人工注意力。适配性工程要保护的，正是这两种稀缺资源。

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
- [x] 三项 EXP-09 实验当前均为 planned，不得写成已验证结论。

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

这些维度不是打分游戏。不必假装能量化到小数点后两位。有用的做法是：对每个维度写出“当前证据是什么”“若判断错了会怎样”。例如，Codebase State 的证据可能是测试覆盖、模块耦合、最近回归事故；Reversibility 的证据可能是能否 draft 发布、能否回滚、是否触及不可逆数据。

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

匹配时不要机械查表，而要看“哪个风险最贵”。

- 如果最大风险是需求不清、边界漂移，FIRE 的动态 Run 与 Autopilot / Confirm / Validate 类自适应检查点往往更贴合。
- 如果最大风险是多人交接、跨会话失忆、发布后不可恢复，AI-DLC 的 Memory Bank、Bolt、验证与 Operations 更值。
- 如果最大风险只是把一个清楚小改动做完，Simple 的短链路通常更诚实。

这里的 Simple、FIRE 与 AI-DLC 是治理强度选项，不是身份标签。同一产品在不同任务上可以选用不同 Flow；同一团队也可以在试点中升级或降级，只要选择理由和不适用条件被写下来。

本层结论：**Flow 是风险对冲工具，不是团队站队旗帜。**

### 2.3 仪式预算：检查点、范围与代价

选完 Flow 还不够，还要决定仪式预算：

- Checkpoints：哪些点必须停下来确认、验证或批准？
- Artifacts：哪些对象必须进入仓库事实源？
- Runtime scope：只做到交付候选，还是必须进入 Pages／Release／监控？
- Review cost：预计增加多少人工注意力？

预算的目标不是“越多越专业”，而是“刚好覆盖关键风险”。多出来的检查点是税；少掉的检查点是债。

一个可用的最小写法是：

```text
Decision Record
  Task:
  Top risks:
  Chosen flow:
  Why not the other two:
  Checkpoint budget:
  Runtime scope:
  Upgrade / downgrade trigger:
```

本层结论：**适配性工程的产品，是可解释的仪式预算，而不只是选一个名词。**

## 03 · Three-Part Argument：为什么方法必须可适配

### 第一段：统一流程会同时制造浪费和空洞

如果所有任务都走完整 AI-DLC，低风险改动会浪费注意力；如果所有任务都走聊天式 Simple，高风险改动会失去追溯和恢复能力。统一流程看起来公平，实际上对风险不公平。

AI 不会自动纠正这种不公平。它只会让错误的流程跑得更快：该省的地方被仪式拖慢，该留痕的地方被速度冲掉。

本段结论：**适配性工程的第一项价值，是避免用同一套仪式处理不同量级的风险。**

### 第二段：代码库状态会改变同一方法的真实成本

同样叫“加一个发布检查”，在绿地小仓和棕地 monorepo 中的成本完全不同。Brownfield 会放大隐藏依赖、测试缺口和回归面；此时 FIRE 的动态 Run 与自适应检查点，或 AI-DLC 的更强追溯，可能比表面简单的线性流程更便宜。

便宜不是少写文档，而是少踩未知耦合。如果仓库本身不干净，假装自己在跑 Simple，通常只是把复杂性推到事故发生之后。

本段结论：**适配性工程的第二项价值，是把代码库现状算进 Flow 选择，而不是假装所有仓库一样干净。**

### 第三段：选择必须带着代价和不适用条件

只说“我们选 AI-DLC”没有工程内容。真正有用的选择要说明：为什么这套仪式能覆盖哪些风险，哪些任务不该用它，检查点预算是多少，以及如果判断错了如何降级或升级。

没有不适用条件的方法选择，最后都会变成宗教。适配性工程要求每次选择都能被下一班人审阅：他们不一定同意，但必须看得懂。

本段结论：**适配性工程的第三项价值，是让 Flow 选择成为可审阅决策，而不是口号。**

## 04 · Example：三类任务的 Flow 对照与 Swap Test

本书写作系统本身就可以当作三类任务的对照样本。它们不是实验室虚构题，而是同一仓库里真实出现过的风险差异。

### 4.1 Task A · 低风险文案修正

假设只修正某章一个术语说明，不改脚本、不改发布链路、不影响 Pages 入口。

| 维度 | 判断 |
|---|---|
| Complexity | 低：局部文案 |
| Codebase State | 无关或弱相关 |
| Compliance | 低：无额外审计要求 |
| Team Scale | 单人即可 |
| Reversibility | 高：易于回退 |

倾向选择：**Simple**。仪式预算可以是：写清改动意图、改正文、跑内部链接或相关门禁、提交审阅。不适用条件：为它建立完整 Intent 分解、多层 Bolt 或完整 Operations Runbook。

如果给 Task A 套上完整 AI-DLC，最常见的结果不是质量更高，而是仪式税：大量工件只为证明“我们很规范”，却不覆盖任何额外关键风险。

### 4.2 Task B · 棕地发布门禁改造

假设要改 `scripts/check_release_readiness.py` 或 Release workflow，使 readiness 与候选资产来源更严格。

| 维度 | 判断 |
|---|---|
| Complexity | 中高：门禁逻辑与发布语义耦合 |
| Codebase State | Brownfield：已有脚本、workflow、政策文件互相依赖 |
| Compliance | 中：影响版本发布可信度 |
| Team Scale | 可能跨会话、需后人接手 |
| Reversibility | 中低：错误门禁会阻断或误放行发布 |

倾向选择：**FIRE**，或在关键路径上局部升到 **AI-DLC**。仪式预算应包括：先确认现有 readiness / prepare_release 边界、改动前后对照、失败样例、是否允许覆盖、如何回滚 workflow 行为。不适用条件：无检查点的一次性大改，或只在聊天里“觉得改对了”。

### 4.3 Task C · 多角色写作系统冲刺

假设要连续推进十章生产线、进度事实源、驾驶舱和审校闭环，并在多个 Agent／会话间交接。

| 维度 | 判断 |
|---|---|
| Complexity | 高：章节、任务、实验、事件、站点耦合 |
| Codebase State | 持续演进的写作系统，不是一次性脚本 |
| Compliance | 中高：需要可审计状态和发布证据 |
| Team Scale | 跨会话、跨角色、跨天 |
| Reversibility | 中：错误状态会污染 tasks／chapters／dashboard |

倾向选择：**AI-DLC**。仪式预算包括 Intent／任务事实源、章节六阶段、验证门禁、进度事件和必要时的 Operations 入口。不适用条件：只靠聊天记录保存状态，或把“模型说完成了”当作完成。

### 4.4 Swap Test：把选错的代价写出来

| 交换 | 典型代价 |
|---|---|
| Task A × AI-DLC | 仪式税：注意力被工件淹没，交付变慢，但风险并未降低 |
| Task C × 无追溯 Simple | 证据空洞：状态不可交接，回归难定位，发布理由说不清 |
| Task B × 无检查点冲刺 | 回归债：门禁看似通过，来源混杂或回滚路径缺失 |

这个对照要回答一个关键问题：如果团队不能说明“为什么选这个 Flow、检查点花在哪里、什么情况下不该用”，那么他们拥有的不是适配性工程，只是流程偏好。

## 05 · Pattern：一份最小 Flow 决策卡

读者可以把本章案例收成一张决策卡：

| 字段 | 最小写法 |
|---|---|
| Task | 一句话任务 |
| Top 2 risks | 最贵的两个风险维度 |
| Chosen flow | Simple / FIRE / AI-DLC |
| Why this flow | 覆盖了哪些风险 |
| Why not others | 明确不适用条件 |
| Checkpoint budget | 停哪里、谁确认、确认什么 |
| Runtime scope | 到候选、到 Pages、到 Release，还是到监控 |
| Upgrade / downgrade | 什么信号触发加重或减轻仪式 |

这张卡可以直接进 PR 描述或任务笔记。它不替代 CH-07 的验证强度选择，也不替代 CH-08 的运行链；它只决定“这次用多强的方法骨架”。

## 06 · Experiment：三个验证方向

本章实验入口包括三项：

- `EXP-09-01 · Simple/FIRE/AI-DLC Flow 选择器`：根据任务复杂度、代码库状态、团队规模与合规要求，生成 Flow 建议、理由与不适用条件。
- `EXP-09-02 · 风险到检查点预算模拟器`：根据风险清单、可逆性、影响范围与自治偏好，生成检查点数量、位置与成本收益估算。
- `EXP-09-03 · Brownfield Flow 选择案例复现`：参考官方 Flow 决策指南与棕地项目案例，复现 Simple、FIRE、AI-DLC 三方案对照决策。

三项实验当前均为 `planned`。本章只把它们作为验证方向，不把专家判断一致率、检查点覆盖率或流程开销写成已得到验证的事实。后续如果要把它们升级为正文证据，至少需要补齐实验目录、样例输入、样例输出、测试和结果记录；`EXP-09-03` 还需保留外部来源与 pinned version 边界。

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-09-01` | Flow 建议是否带理由和不适用条件 | 不证明建议已达到专家级一致 |
| `EXP-09-02` | 检查点预算是否覆盖关键风险且不过度 | 不证明所有风险都能被预算公式穷尽 |
| `EXP-09-03` | Brownfield 场景能否对照三种 Flow 做决策 | 不把外部指南复现写成已完成生产验证 |

## 07 · Figure：风险—仪式矩阵

本章图示为“风险—仪式矩阵”：

![图 9-1 · 风险—仪式矩阵](images/ch09-risk-ceremony-matrix.svg){.core-figure width=100%}

源文件：`book/images/ch09-risk-ceremony-matrix.svg`。矩阵读法：

```text
                Low Ceremony -------- High Ceremony
High Risk       FIRE / AI-DLC         AI-DLC
Medium Risk     FIRE                  FIRE / AI-DLC
Low Risk        Simple                Simple / FIRE
```

旁侧同时列出五个风险维度：Complexity、Codebase State、Compliance、Team Scale、Reversibility。矩阵中的落点是典型倾向，不是强制法令；每个落点都应能追问：为什么、为什么不、检查点预算是什么。右侧保留不适用条件与升级／降级触发器。

## 08 · Boundary：本章不解决什么

第一，本章不重新展开 Operations 五段运行链。Build、Deploy、Runtime Verify、Monitor、Recover 的细节属于 CH-08；这里只决定某次任务要不要进入完整运行范围。

第二，本章不讨论组织角色重构、Mob 节奏和价值记分卡。那是 CH-10 的重点。

第三，本章不把 Simple、FIRE、AI-DLC 写成互相消灭的阵营。它们是不同治理强度，可以并存于同一产品的不同任务。

第四，本章不承诺 `EXP-09-01`、`EXP-09-02`、`EXP-09-03` 已经验证选型质量。它们仍是 planned。

第五，本章不提供可替代人工判断的自动选型黑盒。矩阵帮助组织问题，最终责任仍在人。

## Reader Exercise

选择一个你正在做或即将做的真实任务，用 30 分钟填写一张 Flow 决策卡。

1. 用一句话写出任务，并标出最贵的两个风险维度。
2. 在 Simple、FIRE、AI-DLC 中选出一个 Flow，并写清为什么。
3. 分别写一句：为什么不选另外两个。
4. 列出检查点预算：至少两个必须停下的点，以及谁来确认什么。
5. 写出 Runtime scope：到候选、到验证、到发布，还是到监控。
6. 写出升级／降级触发器：什么信号出现时你会加重或减轻仪式。
7. 最后做一次微型 Swap Test：如果选错，最可能付出的代价是什么。

如果你能回答“这个任务为什么配这个 Flow，以及什么情况下不该用它”，你就已经从方法偏好进入了适配性工程。

## References

- `book/toc.md`：CH-09 核心问题、读者结果、参考实现与实验方向。
- `book/part-00-overview.md`：规模层问题与 AI-DLC Flow 参考路径。
- `book/chapters/ch08-operations.md`：运行链边界；本章只决定是否进入完整运行范围。
- `scripts/check_release_readiness.py`：Task B 类发布门禁改造的项目内参照。
- `.github/workflows/release.yml`：发布语义与 draft／拒绝覆盖的项目内参照。
- `progress/experiments.json`：`EXP-09-01`、`EXP-09-02`、`EXP-09-03` 实验治理状态。
- `progress/chapters.json`：CH-09 六阶段生产线状态。
- `https://specs.md/architecture/choose-flow`：`EXP-09-03` 外部决策指南入口；本地 portal 副本不进入仓库。
