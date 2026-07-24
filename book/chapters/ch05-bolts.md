# 第 5 章 · Bolts：为快速执行选择正确轨道

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-05 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D19-T01 · 锁定章节论证骨架 |
| Draft Completeness | 正式十章生产线论证骨架；等待 D19-T02 扩展为完整可读稿 |
| Primary Question | 如何按领域复杂度、风险和可逆性选择 Bolt 范围、类型与阶段门禁，使速度提高而错误不级联？ |
| Reader Outcome | 能够拆分小时到天级 Bolt，并在 DDD Construction 与 Simple Construction 之间作出有依据的选择 |
| Related Experiments | `EXP-05-01`、`EXP-05-02`、`EXP-05-03` |

## 01 · Question：为什么快执行也需要轨道

第 3 章讲 Inception：把 Intent 分解成 Requirements、Units、Stories 和 Bolt Plan。第 4 章讲上下文工程：让新会话能从 Memory Bank 与 Standards 恢复当前事实。到了第 5 章，问题变成：**恢复了正确上下文之后，怎样把工作切成既足够快、又不会让错误级联的执行批次？**

AI-DLC 把这种执行批次称为 Bolt。Bolt 不是普通任务，也不是传统 Sprint 的缩小版。普通任务常常只描述“做什么”；Sprint 常常承载一到两周的计划、协作和排期；Bolt 则更接近一个小时到数天级的工程执行轨道：它必须有清楚范围、输入、输出、阶段门禁、验收标准和完成证据。

如果 Bolt 切得太大，AI 会在一个长执行链里积累假设，错误会从设计扩散到实现、测试和文档。等人类发现方向错了，已经不只是改一段代码，而是要拆掉一串相互依赖的产物。如果 Bolt 切得太小，系统又会退化为碎片化提示：上下文切换变多，设计无法沉淀，验证成本反而上升。

因此，本章的核心问题是：**如何按领域复杂度、风险和可逆性选择 Bolt 范围、类型与阶段门禁，使速度提高而错误不级联？**

读完本章，读者应能完成三个动作：

1. 把一个 Story 拆成小时到天级的 Bolt。
2. 判断它更适合 Simple Construction 还是 DDD Construction。
3. 为 Bolt 设计最小阶段门禁，让 AI 可以高速推进，但不能无证据地跨过风险点。

### Gate

- [x] 核心问题只有一个：如何选择 Bolt 范围、类型与阶段门禁。
- [x] 读者结果可以观察：能拆分小时到天级 Bolt，并在 DDD 与 Simple 之间作出有依据的选择。
- [x] 本章不展开完整执行日志和 Walkthrough；那是第 6 章的重点。
- [x] 本章不把 Bolt 写成传统 Sprint、普通任务或无限自治 Agent。

## 02 · Framework：Bolt 的四个设计旋钮

本章用四个设计旋钮描述 Bolt：

```text
Scope
  一次 Bolt 应该覆盖多少 Story、文件和风险面？

Type
  应该走 Simple Construction，还是 DDD Construction？

Gates
  哪些阶段必须停下来验证、记录或让人确认？

Evidence
  什么产物证明 Bolt 可以关闭并交给下一阶段？
```

### 2.1 Scope：把工作切到错误可逆

Bolt 的范围不是越小越好，而是要小到错误可逆，大到足以形成可交付增量。一个好的 Bolt 通常具备三条边界：

- 输入边界：它从哪些 Story、Requirements、Standards 或事实源开始。
- 修改边界：它允许改哪些文件、目录、接口或内容。
- 完成边界：什么证据出现后可以停止，而不是继续“顺手优化”。

这三条边界让 AI 的速度有容器。没有容器，速度会变成扩散；有容器，速度才会变成推进。

### 2.2 Type：Simple 与 DDD 的选择

并非所有 Bolt 都需要完整 DDD。对于低领域复杂度、低不确定性、低风险、可快速回滚的任务，Simple Construction 足够：Plan → Implement → Test。比如更新进度投影、补一个页面下钻、生成章节骨架，通常不需要沉重设计。

但当任务涉及领域模型、跨模块依赖、不可逆迁移、安全边界、复杂状态机或长期维护成本时，就应考虑 DDD Construction。它通常需要 Model → Design → ADR → Implement → Test，把关键概念、关系和取舍前置。

判断句可以很朴素：

```text
如果错误主要是局部实现错误，用 Simple。
如果错误会来自概念建模、边界选择或跨对象协作，用 DDD。
```

### 2.3 Gates：阶段门禁防止错误级联

Bolt 的门禁不是为了让 AI 慢下来，而是为了让错误在局部暴露。一个 Simple Bolt 至少要有 Plan、Implement、Test 三个可见阶段；一个 DDD Bolt 则需要更早暴露领域模型和架构取舍。门禁的关键不是阶段名称，而是每个阶段是否有可检查证据。

例如，“实现任务状态推进”这个 Bolt，如果没有测试门禁，AI 很容易把状态从 `backlog` 直接改成 `done`，却没有生成事件、快照和驾驶舱更新。如果门禁要求“事实源校验通过、事件生成、下钻页面更新、CI 通过”，错误就会在交付前显性化。

### 2.4 Evidence：关闭 Bolt 必须留下证据

Bolt 完成不能只靠一句“已完成”。它至少要留下四类证据：

- 计划证据：为什么这样切、依赖是什么、范围在哪里。
- 实现证据：哪些文件改变、为什么改变。
- 验证证据：测试、链接检查、构建、失败样例或人工审校。
- 交接证据：下一步是什么，哪些风险被接受，哪些缺口留给后续 Bolt。

这些证据让 Bolt 既能被关闭，也能被恢复。没有证据的完成，只是聊天里的乐观判断。

## 03 · Three-Part Argument：为什么 Bolt 是速度的工程单位

### 第一段：AI 的速度需要批次边界

AI 可以快速生成多个方案、文件和测试，但真实交付不能让所有生成物混在同一个执行流里。范围越大，隐含假设越多；链路越长，错误越晚暴露。Bolt 通过小时到天级批次，把高速执行限制在一个可理解、可验证、可回滚的范围内。

本段结论：**Bolt 的第一项价值，是把 AI 的生成速度装进错误可逆的工程批次。**

### 第二段：不同风险需要不同执行类型

同样是“做一个功能”，有的任务只是局部页面或文案改动，有的任务会影响领域模型、数据一致性和长期架构。如果所有任务都走 Simple，就会低估复杂度；如果所有任务都走 DDD，又会把小任务过度工程化。Bolt 类型选择的本质，是让执行流程与风险形态匹配。

本段结论：**Bolt 的第二项价值，是按复杂度、风险和可逆性选择合适的执行轨道。**

### 第三段：门禁和证据让 Bolt 可以被交接

AI-DLC 的连续性来自可交接。一个 Bolt 如果没有阶段记录、测试结果、失败修正和完成凭证，下一次会话就只能信任上一轮叙述。门禁和证据让 Bolt 成为可审计对象：它为什么开始，怎样推进，凭什么结束，下一步接哪里。

本段结论：**Bolt 的第三项价值，是把执行从一次性会话变成可恢复、可审计、可继续的交付单位。**

## 04 · Example Skeleton：本书项目中的四个 Bolt

D19-T02 可读稿将用本书项目已经完成的四个 Bolt 作为案例。它们全部属于 `001-github-writing-system-ui` Unit，但范围和目的不同：

```text
Bolt 001
  建立仓库事实源、任务模型、章节模板、实验治理

Bolt 002
  聚合进度、记录事件、生成快照、渲染驾驶舱

Bolt 003
  接入 GitHub 模板、PR 校验、Pages、Release、Projects

Bolt 004
  完成样章审校、试读反馈、v0.1 发布和下一周期入口
```

这四个 Bolt 都选择 Simple Construction，并不是因为项目不重要，而是因为每个 Bolt 的领域复杂度可控、输入输出明确、失败可回滚，且主要风险可以通过事实源校验、链接检查、构建和 CI 暴露。

D19-T02 需要把这个案例写成两层对照：

1. 为什么这些工作没有被塞进一个巨大 Bolt。
2. 为什么它们也没有被拆成几十个碎片提示。

关键观察是：Bolt 001 先建事实源，Bolt 002 才能聚合；Bolt 003 依赖本地系统已经可验证；Bolt 004 才进入发布与反馈闭环。顺序不是排期偏好，而是风险传播控制。

## 05 · Experiment & Figure Entry

本章实验入口包括三项：

- `EXP-05-01 · Bolt 尺寸估算器`：根据 Stories、复杂度、风险与依赖，生成 Bolt 范围、预计时长与拆分建议。
- `EXP-05-02 · DDD 与 Simple Bolt 选择器`：根据任务描述、领域复杂度、风险与可逆性，给出 Bolt 类型建议与选择依据。
- `EXP-05-03 · 官方 Bolt 类型检查点复现`：对照 specs.md 官方 Bolt 类型指南，复现 DDD 与 Simple 两条阶段记录。

这些实验当前仍处于 `planned`，因此本章骨架只把它们作为实验方向，不把指标写成已验证结论。D19-T02 可读稿可以先引用项目中已经完成的四个 Simple Bolt 作为实践案例；D19-T03 审校时必须确认没有把 planned 实验说成 verified。

本章图示方向为“Bolt 选择矩阵”：

```text
Low Complexity / Low Risk / Reversible
  → Simple Construction
  → Plan → Implement → Test

High Domain Complexity / Cross-boundary Risk / Hard to Reverse
  → DDD Construction
  → Model → Design → ADR → Implement → Test
```

若后续生成独立 SVG，可命名为 `book/images/ch05-bolt-selection-matrix.svg`，采用宽屏矩阵布局：横轴为领域复杂度，纵轴为风险/不可逆性；左下为 Simple，右上为 DDD，中间区域标注“拆分 Bolt 或增加门禁”。

## 06 · D19-T02 Writing Plan

D19-T02 将把本骨架扩展为完整可读稿。重点动作：

1. 扩写 Bolt 与 Task、Sprint、Agent Session 的区别。
2. 把 Scope / Type / Gates / Evidence 四个旋钮写成可操作判断表。
3. 用本书四个已完成 Bolt 展示范围、依赖和交接证据。
4. 将 `EXP-05-01`、`EXP-05-02`、`EXP-05-03` 保持为 planned 实验入口，不夸大结论。
5. 增加读者练习：为一个 Story 设计 Simple 与 DDD 两种 Bolt 切法，并说明取舍。

## References

- `memory-bank/bolts/001-github-writing-system-ui/bolt.md`：基础事实源与模板 Bolt。
- `memory-bank/bolts/002-github-writing-system-ui/bolt.md`：进度聚合、事件、快照和驾驶舱 Bolt。
- `memory-bank/bolts/003-github-writing-system-ui/bolt.md`：GitHub 协作与发布自动化 Bolt。
- `memory-bank/bolts/004-github-writing-system-ui/bolt.md`：样章审校、反馈、v0.1 发布与下一周期 Bolt。
- `progress/experiments.json`：`EXP-05-01`、`EXP-05-02`、`EXP-05-03` 实验治理状态。
- `book/toc.md`：CH-05 核心问题、读者结果和实验方向。
