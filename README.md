<p align="center">
  <img src="book/images/cover.png" alt="《深入理解 AI-DLC》封面" width="420">
</p>

<h1 align="center">深入理解 AI-DLC</h1>

<p align="center">
  <strong>Open-source AI-DLC book for deterministic, team-scale software delivery.</strong><br>
  从概率智能到确定性交付：面向研发团队的 AI-DLC 开源工程书。
</p>

<p align="center">
  <a href="https://github.com/mancbj/aidlc-book-baojun/actions/workflows/validate.yml"><img alt="CI" src="https://github.com/mancbj/aidlc-book-baojun/actions/workflows/validate.yml/badge.svg"></a>
  <a href="https://github.com/mancbj/aidlc-book-baojun/releases/latest"><img alt="Latest Release" src="https://img.shields.io/github/v/release/mancbj/aidlc-book-baojun"></a>
  <a href="https://github.com/mancbj/aidlc-book-baojun/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/mancbj/aidlc-book-baojun?style=flat"></a>
  <a href="https://github.com/mancbj/aidlc-book-baojun/commits/main"><img alt="Last commit" src="https://img.shields.io/github/last-commit/mancbj/aidlc-book-baojun"></a>
</p>

AI 可以快速生成代码，却不会自动带来正确、可审计、可恢复的交付。本书面向正在把 AI 从个人助手升级为团队级工程能力的研发负责人、架构师和资深开发者，给出从 **Inception → Construction → Operations** 的完整方法、30 项可复现实验与持续验证机制。

AI can generate code quickly, but speed alone does not make delivery correct, auditable, or recoverable. This book turns AI-assisted development into an engineering lifecycle with explicit human judgment, executable evidence, and production feedback.

<p align="center">
  <a href="#3-分钟开始"><strong>立即开始阅读</strong></a>
  ·
  <a href="https://github.com/mancbj/aidlc-book-baojun/releases/latest"><strong>下载最新版</strong></a>
  ·
  <a href="site/index.html"><strong>查看项目驾驶舱</strong></a>
</p>

<p align="center">
  <a href="https://github.com/mancbj/aidlc-book-baojun">
    <img src="book/images/star-this-repo.gif" alt="如果本书对你有帮助，欢迎 Star" width="520">
  </a>
</p>

## 3 分钟开始

### 只想读书

1. 用 10 分钟阅读 [Part 00 · 鸟瞰 AI-DLC](book/part-00-overview.md)。
2. 从[最新 Release](https://github.com/mancbj/aidlc-book-baojun/releases/latest)下载 PDF 或 HTML。
3. 按你的目标选择[管理者、研发系统设计者或实践者路线](docs/READER-GUIDE.md)。

### 想复现实验或参与写作

需要 Python 3.10+；无需数据库或远程服务。

```bash
git clone https://github.com/mancbj/aidlc-book-baojun.git
cd aidlc-book-baojun
python3 experiments/exp-01-01/quickstart.py --sample
python3 scripts/ci_check.py --budget-seconds 60
```

## 你会得到什么

- **不再把一次生成当成交付** —— 用独立验证、失败—修复—复测和 Walkthrough 形成证据链。
- **不再让 AI 猜目标和边界** —— 把 Intent、Requirements、Stories 与人的判断点连接起来。
- **不再靠聊天记录恢复上下文** —— 用 Memory Bank、Standards 和版本化事实源接续工作。
- **不再用同一种流程处理所有任务** —— 按复杂度、风险和可逆性选择 Simple、FIRE 或 AI-DLC。
- **不止讨论方法论** —— 30 项实验均有确定性合同测试、样例输出与明确的证据边界。
- **不在部署前结束** —— 把 Build、Deploy、Runtime Verify、Monitor 和恢复纳入交付闭环。

## 核心公式

> **AI-DLC = 𝓔（人的判断 + AI 能力）**  
> **𝓔 = Engineering with Exsecutio**

一句话复述：**人定方向，AI 加速度，工程化执行保交付。**

这里的 Exsecutio 表达“贯彻到底”：将 AI 的概率性生成沿工程路径持续推进，转化为可验证、可复现、可追溯、可恢复并可持续演进的软件系统。完整解释与范围边界见[核心宣言](book/manifesto.md)。

## 生命周期与阅读路径

```mermaid
flowchart LR
    A[人的判断] --> B[Inception]
    B --> C[Construction]
    C --> D[独立验证]
    D --> E[Operations]
    E --> F[运行反馈]
    F --> A
```

| 如果你是… | 建议路径 | 你将解决 |
| --- | --- | --- |
| 研发负责人 / 管理者 | Part 0 → 第 1、2、9、10 章 | 责任边界、Flow 选型、组织与度量 |
| 架构师 / 平台负责人 | Part 0 → 第 3–8 章 | 上下文、执行、验证与运行闭环 |
| 想跑最小闭环的实践者 | Part 0 → 第 3、4、5、6、7、8 章 | 从 Intent 到可验证、可运行交付 |

<details>
<summary><strong>展开全书结构（Part 0 + 10 章）</strong></summary>

| 部分 | 内容 |
| --- | --- |
| Part 0 · 鸟瞰 | 核心公式、生命周期和阅读地图 |
| Part 1 · 人的判断 | 第 1–2 章：SDLC 重构、人的责任与反向对话 |
| Part 2 · AI 能力 | 第 3–4 章：Inception、Memory Bank 与 Standards |
| Part 3 · Engineering × Exsecutio | 第 5–6 章：Bolt 选型与执行闭环 |
| Part 4 · 验证反馈 | 第 7–8 章：独立验证与 Operations |
| Part 5 · 规模化 | 第 9–10 章：适配性工程、组织与度量 |

</details>

每章都有唯一问题、读者结果、实验和证据边界。详见[完整目录](book/toc.md)与[读者指南](docs/READER-GUIDE.md)。

## 实验与证据

本书不是只靠观点成立。当前 30 项实验均为 `verified`，并进入统一合同测试：

- **18 × SHIP** —— 仓库内提供最小可运行实现。
- **10 × KEEP-EXT** —— 对外部参考固定版本、配置与证据边界。
- **2 × ALREADY** —— 复用仓库中已存在且可验证的实现。

每项实验都说明“证明什么”与“不能证明什么”，避免把冻结样例、外部参考或模型评审写成普遍结论。查看[实验事实源](progress/experiments.json)、[治理规则](EXPERIMENT_TRIAGE.md)与[样例输出](experiments/)。

## 当前状态

| 信号 | 当前事实 | 查看 |
| --- | --- | --- |
| 正式书稿 | Part 0 + 10 章 | [书稿目录](book/) |
| 章节生产线 | 10 / 10 完成六阶段 | [章节事实](progress/chapters.json) |
| 可复现实验 | 30 / 30 verified | [实验事实](progress/experiments.json) |
| 自动化门禁 | facts、tests、links、generation、实验合同 | [CI workflow](.github/workflows/validate.yml) |
| 可下载版本 | PDF、单页 HTML、站点 zip | [Latest Release](https://github.com/mancbj/aidlc-book-baojun/releases/latest) |

完成率不在 README 手工维护；权威数字来自版本化事实源并投影到[鸟瞰驾驶舱](site/index.html)、[对象下钻](site/details.html)和[文字摘要](progress/generated/current.md)。事实源边界见[仓库指南](docs/REPOSITORY-GUIDE.md)。

## 维护者验证

修改书稿、实验或事实源后，按以下顺序验证：

```bash
python3 scripts/validate_project.py
python3 scripts/generate_progress.py --dry-run --actor readme
python3 scripts/ci_check.py --budget-seconds 60
```

完整门禁会检查事实一致性、单元测试、30 项实验合同、内部链接和生成投影。

## GitHub 协作

- [写作 Issue](.github/ISSUE_TEMPLATE/writing.yml)：章节、公式、案例和术语修订。
- [实验 Issue](.github/ISSUE_TEMPLATE/experiment.yml)：新实验、复现失败和指标改进。
- [反馈 Issue](.github/ISSUE_TEMPLATE/feedback.yml)：试读、阅读路径和理解障碍。
- [Bug Issue](.github/ISSUE_TEMPLATE/bug.yml)：构建、校验、Dashboard 或自动化问题。
- [Pull Request 模板](.github/pull_request_template.md)：必须填写 Task ID、产物、验收和验证结果。
- [协作说明](docs/GITHUB-COLLABORATION.md)：标签、里程碑、Issue/PR 和单向同步规则。

GitHub Issues 与 Projects 是协作投影，不能静默反向覆盖仓库事实源。

## 研究资料与本地工作稿

本书允许使用官网存档、外部参考仓库和作者工作稿作为研究入口，但它们不自动成为结论或公开构建依赖。作者本地的 `working-book/`、`specs.md-portal/` 和外部参考仓库均由 `.gitignore` 排除，不进入 GitHub。

官网效率数字、竞争性结论和工具能力必须回到原始来源核验；已知限制必须保留。例如 specs.md 当前将 Operations Agent 标为 alpha，本书不会把它描述为成熟生产能力。

## 安全、隐私与许可

- 不提交 Token、Cookie、API Key、`.env`、个人联系方式或未经许可的私密原文。
- 外部实验固定版本和配置，秘密只通过运行环境注入。
- 参考仓库和官网材料不是默认可复制内容；引用前确认许可并保留来源。
- 正式书籍许可和最终贡献条款将在 v0.1 发布前确认；在此之前不要假定第三方内容可以重新分发。

---

**AI-DLC 的目标不是“生成得更快”，而是“更快地交付正确”。**
