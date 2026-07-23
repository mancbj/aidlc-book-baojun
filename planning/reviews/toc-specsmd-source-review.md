# 基于 specs.md 官网存档的目录审视报告

> 资料范围：`specs.md-portal/`（作者本地资料，不进入 GitHub）  
> 官网抓取日期：2026-07-03  
> 审视日期：2026-07-22T05:39:06Z

## 资料库鸟瞰

本地存档共约 3.5 MB，包含 50 个官网正文页面、22 张图片、站点索引和两份全文合集。

```text
specs.md-portal/
├── README.md                 # 总索引与抓取说明
├── llms.txt                  # 官网页面索引
├── llms-full.txt             # 官网原始全文
├── specs.md-全站合集.md       # 50 页正文合集
├── 图片资源清单.md            # 22 张图的来源和用途
├── images/                   # Dashboard、Flow、命令等图片
└── pages/
    ├── methodology/          # AI-DLC、三阶段、AI-DLC vs Agile
    ├── aidlc/                # AI-DLC Flow 总览
    ├── core-concepts/        # Intent、Unit、Bolt、Memory Bank、Standards
    ├── agents/               # Master、Inception、Construction、Operations
    ├── architecture/         # 可插拔 Flow 与选择指南
    ├── simple-flow/          # Requirements → Design → Tasks
    ├── fire-flow/            # 自适应检查点、Brownfield、Monorepo
    ├── getting-started/      # 安装、IDE、Dashboard
    ├── guides/               # Bolt 类型选择
    ├── compare/              # 与其他 Spec 工具对比
    └── learn/                # 视频教程
```

## 从官网资料提取的七条结构事实

1. AI-DLC 的核心交互是 **AI proposes, human validates**，不是简单增加一个编码助手。
2. 生命周期明确分为 **Inception → Construction → Operations**。
3. AI-DLC Flow 的工作层级是 **Intent → Unit → Story → Bolt → Stages**。
4. **Memory Bank + Standards** 是跨会话上下文、约束和追溯的事实源。
5. Bolt 取代 Sprint，按小时或天推进；specs.md 实现包含 DDD 与 Simple 两类 Bolt。
6. 人类检查点的数量和位置必须与复杂度、可逆性及风险匹配，不能只强调“越多越安全”。
7. specs.md 同时提供 Simple、FIRE、AI-DLC 三种独立 Flow，说明方法选择本身也是工程判断。

## 原目录审视

### 已经正确的部分

- “人的判断 + AI 能力 + Engineering with Exsecutio”能够容纳官网的“AI 提议、人来验证”。
- 五编从判断、能力、工程、验证走向规模化，宏观递进合理。
- 独立验证、恢复、平台治理和价值度量比官网工具说明更完整，应该保留为本书原创扩展。

### 需要修正的部分

| 缺口 | 原目录表现 | 优化动作 |
| --- | --- | --- |
| 三阶段缺席 | 只有抽象闭环，没有 Inception/Construction/Operations | 分别落入第 3、5–6、8 章 |
| 核心工件缺席 | Intent、Unit、Story、Bolt 没有章节落点 | 第 3 章专门讲 AI 驱动分解 |
| 上下文机制过泛 | 只讲上下文与 Agent，没有事实源和 Standards | 第 4 章改为 Memory Bank 与 Standards |
| Construction 不够具体 | Engineering 与 Exsecutio 缺少 Bolt 类型和阶段 | 第 5、6 章形成“静态轨道 + 动态贯彻” |
| Operations 被弱化 | 反馈恢复没有 Build/Deploy/Verify/Monitor | 第 8 章补全生产闭环 |
| 方法适配缺席 | 容易把完整 AI-DLC 当成所有任务的唯一答案 | 第 9 章加入 Simple/FIRE/AI-DLC 适配 |
| 组织协作悬空 | Agent 角色、Mob ritual 与度量分散 | 第 10 章统一承接规模化操作系统 |

## 知识分层规则

书中必须区分四种知识，避免把某个工具实现等同于完整理论：

| 标签 | 含义 | 示例 |
| --- | --- | --- |
| 本书框架 | 作者提出并负责论证的概念 | `𝓔 = Engineering with Exsecutio` |
| 方法论来源 | AWS AI-DLC、V-Bounce 等方法或研究 | 反向对话、人类验证者 |
| 参考实现 | specs.md 对方法的具体实现 | Memory Bank、四 Agent、Bolt 类型 |
| 实验证据 | 本书可复现或引用的观察结果 | 缺陷发现率、返工、交付周期 |

不得把官网的宣传性判断直接写成已经证实的普遍事实。官网当前还明确标注 Operations Agent 为 alpha；相关章节必须把“方法目标”和“工具成熟度”分开。

## 优化后的章节覆盖

| 章 | 新增的官网核心覆盖 | 主要本地来源 |
| --- | --- | --- |
| 1 | AI-Assisted → AI-Driven → Agentic；重新设计 SDLC | `pages/methodology/sdlc-reimagined.md` |
| 2 | 反向对话、人类验证、Mob Elaboration | `pages/methodology/what-is-ai-dlc.md` |
| 3 | Inception；Intent → Unit → Story → Bolt | `pages/methodology/three-phases.md`、`pages/core-concepts/` |
| 4 | Memory Bank、Standards、跨会话上下文 | `pages/core-concepts/memory-bank.md`、`standards.md` |
| 5 | Bolt vs Sprint、DDD/Simple Bolt、阶段门禁 | `pages/core-concepts/bolts.md` |
| 6 | Construction 的动态执行、Walkthrough 与追溯 | `pages/agents/construction-agent.md` |
| 7 | 人类检查点与独立交付证据 | `pages/core-concepts/bolts.md`、FIRE execution modes |
| 8 | Build、Deploy、Verify、Monitor、Runbook | `pages/agents/operations-agent.md` |
| 9 | Simple/FIRE/AI-DLC 选择、Brownfield、Monorepo | `pages/architecture/choose-flow.md`、`pages/fire-flow/` |
| 10 | 四 Agent、Mob rituals、业务价值度量 | `pages/agents/overview.md`、`pages/methodology/` |

## 结论

优化不增加章节数量，而是提高每章的工程承载力。新版目录既能解释 AI-DLC 为什么成立，也能让读者沿一个真实的 specs.md 参考实现走完“意图—上下文—分解—构建—验证—运行—规模化”，同时保留对工具实现的批判距离。

后续在十章之前增加非编号的 Part 0 鸟瞰导读，用核心公式、三阶段、五编叙事地图和三条阅读路线降低首次阅读门槛；该导读不改变十章编号和章节事实源。
