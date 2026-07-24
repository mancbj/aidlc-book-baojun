# 第 5 章 · Bolts：为快速执行选择正确轨道

## Metadata

| Field | Value |
|-------|-------|
| Chapter ID | CH-05 |
| Status Source | `progress/chapters.json` |
| Writing Sprint Card | D19-T03 · 完成章节审校与证据对齐 |
| Draft Completeness | 正式十章生产线可读稿；D19-T03 五类审校已完成 |
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

## 04 · Example：本书项目中的四个 Bolt

我们用本书项目已经完成的四个 Bolt 作为例子。它们全部属于 `001-github-writing-system-ui` Unit，但每个 Bolt 的范围、依赖和风险面不同。

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

如果把这四件事塞进一个巨大 Bolt，AI 会同时处理事实源、驾驶舱、GitHub 自动化、发布、反馈和下一周期。看起来省事，实际上风险会级联：任务模型尚未稳定时，驾驶舱数字就没有可信来源；本地系统尚未验证时，GitHub Actions 和 Pages 就可能围绕错误事实发布；样章尚未审校时，发布门禁就只剩形式。

如果把它们拆成几十个碎片提示，另一个问题会出现：每次提示都很小，但系统失去批次感。AI 可能今天补一个 JSON 字段，明天改一段页面，后天补一个测试，却没有一个明确的交付边界说明“这一组变更共同完成了什么”。碎片提示看起来可控，但很难交接。

四个 Bolt 的顺序体现了风险传播控制。

**Bolt 001** 先建立仓库事实源、任务模型、章节模板和实验治理。它解决的是“后续所有状态从哪里来”。如果没有它，任何进度页面都只是手工文案。

**Bolt 002** 在事实源稳定后再做进度聚合、事件记录、快照和驾驶舱。它解决的是“关键更新如何自动可视化”。如果把它放在 Bolt 001 前面，页面会先于事实存在。

**Bolt 003** 在本地系统可验证后接入 GitHub 模板、PR 校验、Pages、Release 和 Projects。它解决的是“协作和发布如何接住事实源”。如果过早接 GitHub，远程自动化会把不稳定状态放大。

**Bolt 004** 最后处理样章审校、试读反馈、v0.1 发布和下一周期入口。它解决的是“系统如何形成一个可公开、可回收、可继续的闭环”。如果没有前三个 Bolt，它就只能靠人工清单发布，难以复现。

这个案例说明：Bolt 的价值不是把任务排成列表，而是把风险按可验证顺序切开。正确的 Bolt 既不是“大而全”，也不是“碎到失去意义”，而是能让 AI 在一个批次里完成真实增量，并留下足够证据交给下一个批次。

### 4.1 Simple Bolt 为什么足够

本书前四个 Bolt 都使用 Simple Construction。理由可以从四个维度判断：

| 判断维度 | 当前情况 | 结论 |
|---|---|---|
| 领域复杂度 | 主要是写作系统、事实源、静态页面和 GitHub 工作流 | 不需要完整领域建模 |
| 可逆性 | Markdown、JSON、HTML、YAML 变更都可由 Git 恢复 | 可以用较轻流程推进 |
| 验证方式 | 校验脚本、链接检查、构建、CI 能覆盖关键路径 | Test 门禁足够暴露多数错误 |
| 跨边界风险 | 不涉及真实用户数据迁移或生产数据库 | 不需要 ADR 级别的架构门禁 |

如果同样的项目开始处理付费读者数据、协作者权限、自动 Issue 同步写入、发布回滚和多仓库依赖，判断就会改变。那时，错误不再只是页面或 Markdown 错误，而可能涉及权限、数据一致性和长期架构，DDD Construction 就会更合适。

## 05 · Experiment：Bolt 选择的三个验证方向

本章实验入口包括三项：

- `EXP-05-01 · Bolt 尺寸估算器`：根据 Stories、复杂度、风险与依赖，生成 Bolt 范围、预计时长与拆分建议。
- `EXP-05-02 · DDD 与 Simple Bolt 选择器`：根据任务描述、领域复杂度、风险与可逆性，给出 Bolt 类型建议与选择依据。
- `EXP-05-03 · 官方 Bolt 类型检查点复现`：对照 specs.md 官方 Bolt 类型指南，复现 DDD 与 Simple 两条阶段记录。

这些实验当前仍处于 `planned`，因此本章只把它们作为验证方向，不把指标写成已验证结论。这一点很重要：CH-05 可以基于本书四个已完成 Bolt 总结实践经验，但不能声称 `EXP-05-01` 或 `EXP-05-02` 已经证明了某个估算模型。

D19-T02 阶段可以先定义实验应该怎样支撑本章：

| Experiment | It should test | It must not overclaim |
|---|---|---|
| `EXP-05-01` | Bolt 范围和预计时长是否更接近实际执行 | 不证明所有项目都能准确估时 |
| `EXP-05-02` | Simple / DDD 类型选择是否接近专家判断 | 不证明选择器可以替代人工判断 |
| `EXP-05-03` | specs.md Bolt 类型检查点是否能被复现 | 不把外部参考实现写成本书唯一标准 |

这三项实验共同服务于一个问题：Bolt 不是靠感觉切分，而是应该能被复杂度、风险、依赖、可逆性和验证成本解释。真正的实验结果要等实验目录、样例输出和测试都准备好后，才能写成正文证据。

## 06 · Figure：Bolt 选择矩阵

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

这张图的核心不是画两个象限，而是帮助读者做选择。一个任务如果在左下角，Simple Construction 通常够用；如果在右上角，DDD Construction 更稳；如果落在中间灰区，常见处理不是拍脑袋二选一，而是先拆分 Bolt，或者给 Simple Bolt 增加额外门禁。

可以把中间灰区理解为一个提醒：

```text
如果你不知道该选 Simple 还是 DDD，
先问：能不能把高风险部分拆成单独 Bolt？
如果不能拆，再问：需要增加哪个门禁？
```

例如，给静态驾驶舱增加一个新指标也许是 Simple；但如果这个指标要改变任务状态模型、事件语义和发布门禁，它就不再只是页面改动。正确做法可能是拆成两个 Bolt：先修改事实源模型并验证，再更新页面展示。

## 07 · Boundary：本章不解决什么

第一，本章不教读者完整运行 Bolt。第 6 章会展开 Exsecutio：如何让 AI 沿计划、执行、验证、纠偏和 Walkthrough 推进到交付候选。

第二，本章不把 DDD 写成高级、Simple 写成低级。两者只是不同风险形态下的执行轨道。过度工程化和不足工程化都是错误。

第三，本章不把估算写成精确预测。Bolt 尺寸估算的意义是让风险显性化，而不是保证每个任务都按小时准确完成。

第四，本章不鼓励 AI 自己决定所有门禁。AI 可以建议门禁，但领域复杂度、风险接受和不可逆性判断仍需要人的确认。

## Reader Exercise

选择你自己的一个 Story，用 20 分钟设计两个 Bolt 方案。

1. 写出 Story 的目标和验收。
2. 写一个 Simple Bolt：Plan、Implement、Test 三阶段即可。
3. 写一个 DDD Bolt：Model、Design、ADR、Implement、Test 五阶段。
4. 为每个方案列出 Scope、Type、Gates、Evidence。
5. 标出最可能出错的位置：实现细节、领域模型、跨模块依赖、数据风险或发布风险。
6. 选择一个方案，并写一句选择理由。

如果你能解释“为什么这个 Story 不需要 DDD”，或者“为什么这个 Story 必须 DDD”，你已经开始把速度选择变成工程判断。

## References

- `memory-bank/bolts/001-github-writing-system-ui/bolt.md`：基础事实源与模板 Bolt。
- `memory-bank/bolts/002-github-writing-system-ui/bolt.md`：进度聚合、事件、快照和驾驶舱 Bolt。
- `memory-bank/bolts/003-github-writing-system-ui/bolt.md`：GitHub 协作与发布自动化 Bolt。
- `memory-bank/bolts/004-github-writing-system-ui/bolt.md`：样章审校、反馈、v0.1 发布与下一周期 Bolt。
- `progress/experiments.json`：`EXP-05-01`、`EXP-05-02`、`EXP-05-03` 实验治理状态。
- `book/toc.md`：CH-05 核心问题、读者结果和实验方向。
- `planning/reviews/ch-05-writing-review.md`：正式十章生产线 CH-05 五类审校记录。
