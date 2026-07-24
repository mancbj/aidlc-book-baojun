# 第 6 章 · Exsecutio：把提议贯彻为交付候选

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-06 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D20-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；等待 D20-T02 扩展为完整可读稿 |
| Primary Question | 如何让 AI 沿计划、执行、验证、纠偏和 Walkthrough 持续推进，直到生成物满足完成定义并可被下一阶段接收？ |
| Reader Outcome | 能够运行完整 Bolt，并保留阶段决策、文件变化、测试结果、失败修正与完成凭证 |
| Related Experiments | `EXP-06-01`、`EXP-06-02`、`EXP-06-03` |

## 01 · Question：为什么执行不是“让 AI 一直做下去”

第 5 章回答了如何选择 Bolt：按领域复杂度、风险和可逆性，把工作切进 Simple 或 DDD 的执行轨道。第 6 章继续往前一步：**Bolt 已经选好之后，怎样让 AI 沿计划、执行、验证、纠偏和 Walkthrough 持续推进，直到生成物满足完成定义并可被下一阶段接收？**

这就是本书专用术语 `Exsecutio` 要表达的东西。它不是一般意义上的 execution，也不是让 AI 无限自治地“继续做”。在 AI-DLC 中，Exsecutio 是一种被工程化约束的贯彻能力：目标来自 Inception，边界来自 Memory Bank 与 Standards，范围来自 Bolt，执行必须持续回到计划、测试、失败修正、证据和交接。

如果只让 AI 持续生成，最容易出现三类问题。

第一，计划和实际脱节。AI 可能实现了计划之外的“顺手优化”，也可能遗漏计划内的关键产物。第二，失败没有被保存。测试失败、修复尝试和复测结果如果只停留在聊天里，下一次会话无法判断问题是否真的关闭。第三，完成定义被软化。AI 会倾向于在结果看起来合理时宣布完成，但工程交付需要可复核的凭证。

因此，本章的核心问题是：**如何让 AI 沿计划、执行、验证、纠偏和 Walkthrough 持续推进，直到生成物满足完成定义并可被下一阶段接收？**

读完本章，读者应能完成三个动作：

1. 为一个 Bolt 写出可执行的 Implementation Plan。
2. 在执行中保存文件变化、失败、修复和复测证据。
3. 用 Walkthrough 让陌生审阅者只凭工件复核 Bolt 是否完成。

### Gate

- [x] 核心问题只有一个：如何把 Bolt 从计划贯彻到可交付候选。
- [x] 读者结果可以观察：能运行完整 Bolt，并保留阶段决策、文件变化、测试结果、失败修正与完成凭证。
- [x] 本章不重新讨论 Bolt 类型选择；那是 CH-05 的重点。
- [x] 本章不把模型自评当成完成证据；验证机制留给 CH-07 深入展开。

## 02 · Framework：Exsecutio 的五段闭环

本章用五段闭环描述 Exsecutio：

```text
Plan
  写清楚要做什么、为什么做、改哪里、如何验收

Execute
  在范围内生成、修改、补充和整理产物

Verify
  运行确定性检查、测试、构建、链接或审校

Repair
  保存失败，修复问题，再次验证

Walkthrough
  解释实际变化、证据、偏差、风险和交接条件
```

### 2.1 Plan：计划不是仪式，是执行对照物

Implementation Plan 的价值不是让流程显得正式，而是给后续偏差审计提供对照物。计划至少应写清四件事：目标、范围、产物、验收。没有计划，AI 的每个新增文件都可能被解释成合理；有计划，执行后才能判断“做了什么、漏了什么、偏离了什么”。

### 2.2 Execute：执行必须受范围约束

执行阶段可以让 AI 快速生成和修改，但不能让它无限扩散。每次修改都应回到 Bolt 的输入边界、修改边界和完成边界。一个好的执行过程不是没有变化，而是变化可解释、可复核、可回滚。

### 2.3 Verify：验证先证明可继续，而不是证明完美

Verify 的目标不是证明系统永远正确，而是证明当前 Bolt 可以进入下一阶段。对于写作系统，验证可能是 `validate_project.py`、`generate_progress.py`、`ci_check.py`、链接检查、书稿构建或章节审校。对于软件系统，它可能是单元测试、集成测试、类型检查、冒烟测试或人工门禁。

### 2.4 Repair：失败是证据，不是噪音

失败日志、修复动作和复测结果必须被保存。没有失败记录，团队会误以为交付一次通过；没有复测记录，团队无法判断修复是否有效。AI-DLC 不要求过程没有失败，它要求失败能够被看见、被修正、被证明关闭。

### 2.5 Walkthrough：让陌生人可以复核

Walkthrough 是 Bolt 的交接界面。它应该回答：原计划是什么，实际改了什么，测试了什么，失败如何处理，有哪些偏差，剩余风险是什么，下一阶段如何接手。一个新会话或陌生审阅者不应只听 AI 说“完成了”，而应能沿 Walkthrough 复核证据链。

## 03 · Three-Part Argument：为什么 Exsecutio 是 AI-DLC 的贯彻层

### 第一段：AI 的提议需要被贯彻到工件

AI 很擅长提出方案、生成草案和解释错误。但交付候选不是提议本身，而是被写入仓库、通过验证、留下证据并能被下一阶段接收的工件。Exsecutio 把“AI 可以做”转成“系统已经接收了什么”。

本段结论：**Exsecutio 的第一项价值，是把模型提议贯彻成可版本化、可验证、可交接的工件。**

### 第二段：验证与修复必须进入同一个执行闭环

很多失败不是因为 AI 不能写，而是因为写完后没有把验证和修复放进同一条轨道。测试失败如果没有保存，修复就失去上下文；修复后如果没有复测，完成就是乐观假设。Exsecutio 要求执行、失败、修复和复测共同构成闭环。

本段结论：**Exsecutio 的第二项价值，是把失败—修复—复测变成交付证据，而不是聊天噪音。**

### 第三段：Walkthrough 让执行可以被恢复

AI-DLC 的连续交付依赖可恢复性。一个 Bolt 如果只有最终文件，没有计划、偏差、测试和交接说明，下一次会话仍然要重新猜。Walkthrough 让执行结果不仅能被使用，还能被复核、维护和继续推进。

本段结论：**Exsecutio 的第三项价值，是让执行过程从一次性会话变成可恢复的工程记录。**

## 04 · Example Skeleton：以写作系统 Bolt 为例

D20-T02 可读稿将复用本书项目已有 Bolt 记录作为案例，重点展示 Simple Construction 的三个阶段如何落成证据。

最小案例结构如下：

```text
Bolt
  002-github-writing-system-ui

Plan
  implementation-plan.md
  定义进度聚合、事件、快照、驾驶舱和下钻目标

Execute
  scripts/progress_core.py
  scripts/generate_progress.py
  site/index.html
  site/details.html

Verify
  test-walkthrough.md
  python3 scripts/ci_check.py

Walkthrough
  implementation-walkthrough.md
  说明实际变化、验证结果和交接状态
```

这个例子要回答一个关键问题：如果陌生审阅者只读取 Bolt 文件、实现 Walkthrough、测试 Walkthrough 和当前仓库状态，能不能复核“进度驾驶舱已经从事实源生成，而不是手工维护”？如果能，Exsecutio 就不仅是执行动作，而是留下了可恢复的执行证据。

## 05 · Experiment & Figure Entry

本章实验入口包括三项：

- `EXP-06-01 · Plan–Walkthrough 偏差审计器`：比较 Implementation Plan、代码变更与 Walkthrough，生成计划项、实际变更与未声明偏差表。
- `EXP-06-02 · 失败—修复—复测闭环记录器`：根据失败日志、修复提交和测试结果，生成按时间排序的修复证据链。
- `EXP-06-03 · 端到端 Bolt 执行复现`：参考官方 Bolt 教程与示例 Story，复现从计划到测试报告的完整 Bolt 工件。

这些实验当前仍处于 `planned`，因此本章骨架只把它们作为验证方向，不把指标写成已验证结论。D20-T02 可读稿可以先引用本项目已有 Bolt 工件作为实践案例；D20-T03 审校时必须确认没有把 planned 实验说成 verified。

本章图示方向为“Exsecutio 执行闭环”：

```text
Plan → Execute → Verify → Repair → Walkthrough
  ↑                                      ↓
  └──────────── Evidence / Feedback ─────┘
```

若后续生成独立 SVG，可命名为 `book/images/ch06-exsecutio-loop.svg`，采用宽屏闭环布局：主流程水平展开，Repair 作为低权重回路返回 Verify，Walkthrough 输出到下一阶段接收区。

## 06 · D20-T02 Writing Plan

D20-T02 将把本骨架扩展为完整可读稿。重点动作：

1. 扩写 Plan / Execute / Verify / Repair / Walkthrough 五段闭环。
2. 用 `memory-bank/bolts/002-github-writing-system-ui/` 展示计划、实现、测试与 Walkthrough 证据。
3. 写清 Exsecutio 与 Execution 的区别，保留 `𝓔 = Engineering with Exsecutio` 术语。
4. 将 `EXP-06-01`、`EXP-06-02`、`EXP-06-03` 保持为 planned 实验入口，不夸大结论。
5. 增加读者练习：用一个真实小任务写出 Plan、执行记录、失败修复和 Walkthrough。

## References

- `memory-bank/bolts/002-github-writing-system-ui/bolt.md`：进度聚合、事件、快照和驾驶舱 Bolt。
- `memory-bank/bolts/002-github-writing-system-ui/implementation-plan.md`：Bolt 计划证据。
- `memory-bank/bolts/002-github-writing-system-ui/implementation-walkthrough.md`：实现 Walkthrough。
- `memory-bank/bolts/002-github-writing-system-ui/test-walkthrough.md`：测试 Walkthrough。
- `memory-bank/bolts/001-github-writing-system-ui/bolt.md`：基础事实源 Bolt。
- `progress/experiments.json`：`EXP-06-01`、`EXP-06-02`、`EXP-06-03` 实验治理状态。
- `book/toc.md`：CH-06 核心问题、读者结果和实验方向。
