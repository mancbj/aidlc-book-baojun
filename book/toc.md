# 《深入理解 AI-DLC》十章目录

> 副标题：从概率智能到确定性交付——AI 驱动规模化开发的理论与实践  
> v3 依据：作者五编骨架 + specs.md 官网存档 + Part 0 鸟瞰导读  
> 优化时间：2026-07-22T05:47:09Z

## 全书主线

全书沿着一条确定性交付链展开：**人设定目的地 → AI 提议与执行 → 工程事实源约束上下文 → Bolt 分阶段推进 → 人与机器共同验证 → Operations 完成交付 → 组织按风险规模化**。

`𝓔 = Engineering with Exsecutio` 是本书的解释框架；specs.md 的三阶段、Memory Bank、Bolts 和 Agents 是贯穿全书的参考实现，不被描述为 AI-DLC 的唯一实现。

## Part 00 · 鸟瞰 AI-DLC：读懂这本书的地图

**导读问题：AI-DLC 由哪些关键部分构成，这十章为什么按当前顺序展开？**

- 阅读时间：约 10 分钟。
- 读者结果：能够复述核心公式、三阶段生命周期、五编叙事弧，并选择适合自己的阅读路线。
- 视觉地图：人的判断 → AI 能力 → Engineering with Exsecutio → 确定性交付 → 反馈与规模化。
- 正文入口：[part-00-overview.md](part-00-overview.md)。

Part 00 是非编号导读，不计入十章正文，也不改变 CH-01 至 CH-10 的章节事实源。

## Part 01 · 人的判断

### 第 1 章 · AI 原生 SDLC：从概率智能到确定性交付

**唯一核心问题：当代码生成成本骤降而输出仍具有概率性时，为什么需要重新设计 SDLC，而不只是给旧流程增加 AI？**

- 读者结果：能够区分 AI-Assisted、AI-Driven 与 Agentic 三种范式，并用核心公式解释 AI-DLC 的必要性和边界。
- 参考实现：specs.md 对 AI-DLC、Bolt 与传统 Sprint 的定位。
- 实验方向：让同一需求分别走“对话式生成”和“AI-DLC 闭环”，比较交付周期、返工、缺陷和证据完整度。

### 第 2 章 · 人的判断与反向对话

**唯一核心问题：当 AI 主动提议、分解和执行时，人应如何设定目的地、保留责任并选择验证检查点？**

- 读者结果：能够定义意图、边界、不可委托判断、人工检查点和最终责任人。
- 参考实现：AI proposes, human validates；Mob Elaboration；Master Agent 路由。
- 实验方向：比较“人逐步提示 AI”和“AI 提议、人验证”的需求澄清质量与人工注意力消耗。

## Part 02 · AI 能力

### 第 3 章 · Inception：从 Intent 到可执行计划

**唯一核心问题：AI 如何把一个高层 Intent 分解成可独立交付的 Unit、可验收的 Story 和可执行的 Bolt，而不丢失人的目标与边界？**

- 读者结果：能够完成 Intent → Requirements/System Context → Unit → Story → Bolt Plan 的可追溯分解。
- 参考实现：Inception Agent、Intent、Unit、Story、Bolt Planning。
- 实验方向：对同一模糊目标进行自由分解与工件化分解，比较边界冲突、循环依赖和验收遗漏。

### 第 4 章 · 上下文工程：Memory Bank 与 Standards

**唯一核心问题：如何用版本化事实源和明确标准，让每次全新的 Agent 会话恢复正确上下文并持续遵守工程约束？**

- 读者结果：能够设计最小 Memory Bank、Standards 目录、工件引用和变更同步规则。
- 参考实现：Memory Bank、Tech Stack、Coding Standards、Architecture、跨工件追溯。
- 实验方向：让新会话只依赖版本化工件恢复任务，与依赖聊天历史的会话比较遗漏、冲突和恢复时间。

## Part 03 · Engineering × Exsecutio

### 第 5 章 · Bolts：为快速执行选择正确轨道

**唯一核心问题：如何按领域复杂度、风险和可逆性选择 Bolt 范围、类型与阶段门禁，使速度提高而错误不级联？**

- 读者结果：能够拆分小时到天级 Bolt，并在 DDD Construction 与 Simple Construction 之间作出有依据的选择。
- 参考实现：Bolt vs Sprint；DDD 的 Model → Design → ADR → Implement → Test；Simple 的 Plan → Implement → Test。
- 实验方向：用两类 Bolt 处理同一中等复杂度需求，比较设计收益、额外负担与缺陷前移程度。

### 第 6 章 · Exsecutio：把提议贯彻为交付候选

**唯一核心问题：如何让 AI 沿计划、执行、验证、纠偏和 Walkthrough 持续推进，直到生成物满足完成定义并可被下一阶段接收？**

- 读者结果：能够运行一个完整 Bolt，保留输入、阶段决策、文件变化、测试结果、失败修正与完成凭证。
- 参考实现：Construction Agent、Bolt stage progression、Walkthrough 和状态记录。
- 实验方向：从一个小型需求出发，运行可中断、可恢复、可验收的 Bolt，并由陌生审阅者仅凭 Walkthrough 复核。

## Part 04 · 验证反馈

### 第 7 章 · 验证：把人类检查点变成有效损失函数

**唯一核心问题：如何组合确定性检查、独立测试、模型评审和人工判断，证明 AI 参与的结果正确，而不是把模型自评当证据？**

- 读者结果：能够按复杂度、可逆性、安全影响和数据风险选择验证强度，并建立分层交付证据链。
- 参考实现：AI-DLC 固定检查点；FIRE 的 Autopilot、Confirm、Validate 自适应检查点作为对照。
- 实验方向：向同一实现注入缺陷，比较模型自评、自动测试、独立评审和人工门禁的发现率与成本。

### 第 8 章 · Operations：从交付候选到可持续运行

**唯一核心问题：如何通过 Build、Deploy、Runtime Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统？**

- 读者结果：能够定义构建凭证、环境门禁、部署策略、冒烟验证、监控指标和回滚 Runbook。
- 参考实现：Operations Agent 与 `memory-bank/operations/`；同时记录该实现当前为 alpha，而非假定工具已经成熟。
- 实验方向：在隔离环境完成构建、部署、故障注入、检测和回滚，验证交付凭证是否足够复现。

## Part 05 · 规模化

### 第 9 章 · 适配性工程：选择正确的 Flow 与治理强度

**唯一核心问题：如何根据任务复杂度、代码库现状、监管要求和团队规模，在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化？**

- 读者结果：能够使用风险—仪式矩阵选择 Flow、检查点数量与运行范围，并解释选择代价。
- 参考实现：Simple 的 Requirements → Design → Tasks；FIRE 的动态 Run、Brownfield/Monorepo 与自适应检查点；AI-DLC 的完整追溯。
- 实验方向：为三个不同风险任务分别选择 Flow，再交换 Flow 执行，比较摩擦、遗漏与可追溯性。

### 第 10 章 · 组织与度量：从 Agent 分工到研发操作系统

**唯一核心问题：如何重构人、Agent、协作节奏与度量体系，并判断哪些 AI-DLC 实践值得在组织内规模化？**

- 读者结果：能够设计 Master/Inception/Construction/Operations 与人的责任图、Mob 协作节奏和业务价值记分卡。
- 参考实现：四 Agent 架构、Mob Elaboration、Mob Construction、Dashboard 与工件驱动异步审阅。
- 实验方向：用交付周期、质量、成本、可复现性、人工注意力和业务价值评估一次团队试点。

## 核心问题去重审计

| 章 | 本章独占对象 | 明确不展开的相邻问题 |
| --- | --- | --- |
| 1 | 新生命周期的必要性与理论边界 | 不展开责任分配和具体工件 |
| 2 | 人机责任、反向对话与检查点选择 | 不展开工作分解结构 |
| 3 | Intent 到 Bolt Plan 的 AI 驱动分解 | 不展开跨会话上下文保存 |
| 4 | 事实源、标准与上下文持久化 | 不展开 Bolt 执行阶段 |
| 5 | Bolt 范围、类型和静态门禁结构 | 不展开动态执行与审阅记录 |
| 6 | 从计划到交付候选的动态贯彻 | 不展开验证方法比较和生产部署 |
| 7 | 验证强度与独立证据 | 不展开部署、监控与回滚操作 |
| 8 | 生产交付、观测与恢复 | 不展开 Flow 选型 |
| 9 | 方法适配、Brownfield 与治理强度 | 不展开组织角色重构 |
| 10 | Agent 分工、团队节奏与价值度量 | 不展开单个 Flow 的内部实现 |

## 来源与证据规则

1. `𝓔 = Engineering with Exsecutio` 标注为本书框架。
2. AWS AI-DLC、V-Bounce 等标注为方法论或研究来源。
3. Memory Bank、四 Agent 和具体 Bolt 类型标注为 specs.md 参考实现。
4. 官网的效率数字和竞争性结论必须回到原始研究核验，不能只引用产品页面。
5. 工具已知限制必须保留；尤其不能把 alpha 状态的 Operations 实现写成成熟生产能力。

## v0.1 边界

- v0.1 固化十章结构、唯一核心问题和读者结果，不承诺十章完稿。
- 第 3 章已由 D03-T03 选为 v0.1 样章；第 6 章保留为理解执行机制的后续核心章。
- 30 项实验池已在 D03-T01 按本版目录重建，并由 D03-T02 完成初步分类；只有达到验收门禁的实验才可进入 `verified`。
- 至少一个实验达到新读者可复现标准，其余进入治理队列。

## D01-T03 持续验收

- [x] 十章与核心公式、目标读者和五编骨架一致。
- [x] 十个核心问题没有重复。
- [x] specs.md 的三阶段、核心工件、Agent、Flow 与 Operations 均有明确落点。
- [x] 本书框架、方法来源、参考实现和实验证据已经分层。
