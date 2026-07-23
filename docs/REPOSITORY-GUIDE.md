# AI-DLC Book Repository Guide

> D02-T01 仓库骨架与事实源边界  
> 核对时间：2026-07-22T05:55:46Z

## 1 · 核心原则

这个仓库不是一个大文档，而是一台由**书稿源、工程事实、研究资料、自动化和审计历史**组成的写作系统。

1. 内容写在内容源，状态写在状态源，统计只由生成器计算。
2. 同一个事实只有一个权威位置；README、Dashboard 和 GitHub Projects 都是入口或投影。
3. 当前投影可以重新生成，历史事件和快照不可手工重写。
4. 研究素材是证据入口，不因进入仓库就自动成为本书结论。
5. 所有声明完成的任务都必须同时满足依赖、验收和 required artifact。

## 2 · 仓库鸟瞰

```text
aidlc-book-baojun/
├── book/                 # 书稿源：Part 0、核心公式、目录、章节和视觉资产
├── docs/                 # 面向读者、协作者和维护者的长期说明
├── planning/             # 读者、路线、审校和版本计划；不保存聚合完成率
├── progress/             # 任务、章节、实验、周期事实及自动进度历史
├── feedback/             # 最小化、匿名化的反馈决策事实
├── releases/             # readiness、候选说明与真实发布回执
├── site/                 # 自动生成的静态鸟瞰驾驶舱
├── scripts/              # 校验、聚合、渲染、发布和同步工具
├── tests/                # 自动化测试
├── writer-chats/         # 清理隐私后的写作对话摘要与关键决策
├── memory-bank/          # specs.md AI-DLC 开发生命周期工件
├── .specsmd/             # specs.md 框架、Agent、Skill、模板与 Schema
├── .github/              # Issue/PR 模板和 GitHub Actions
├── .codex/               # 本项目本地 Codex Skills
├── specs.md-portal/      # 本地 specs.md 官网资料门户；不进入 GitHub
├── aidlc-book-content-resources/          # 书籍调研素材
├── github_repo_reference_ai-agent-book-main/ # 本地外部参考仓库；不进入 GitHub
├── working-book/         # 作者本地工作稿；不进入 GitHub
└── .artifacts/           # 本地运行或工具产生的临时产物
```

## 3 · 目录职责与编辑权限

| 路径 | 类型 | 职责 | 编辑规则 |
| --- | --- | --- | --- |
| `book/` | 人工内容源 | Part 0、十章正文、公式、目录、图片和章节模板 | 可人工编辑；观点需遵守证据规则 |
| `docs/` | 人工说明源 | 阅读、仓库、进度、CI、发布与协作说明 | 可人工编辑，不复制状态统计 |
| `planning/` | 人工计划源 | 读者、14 天路线、审校、反馈和版本规划 | 可人工编辑；任务状态仍以 `progress/tasks.json` 为准 |
| `progress/*.json` | 权威事实源 | 任务、章节、实验和周期状态 | 只按对应 Schema 编辑并通过校验 |
| `progress/generated/` | 可替换投影 | 当前聚合 JSON/Markdown 与成功基线 | 只由 `generate_progress.py` 更新 |
| `progress/events/events.jsonl` | 追加式历史 | 稳定 ID 的关键事件账本 | 只允许生成器追加；不得改序或回写 |
| `progress/snapshots/` | 不可变历史 | 各事实版本的完整快照 | 只由生成器创建；不得手工修改或覆盖 |
| `feedback/` | 权威事实源 | 匿名反馈及采用、拒绝、延后决定 | 最小化记录；禁止写入敏感原文 |
| `releases/` | 混合 | 版本门禁、候选 Notes、构建清单、发布回执 | readiness/Notes 可生成；receipt 只能来自真实发布 |
| `site/` | 可替换投影 | 任务、章节、事件、阻塞和下一动作的鸟瞰界面 | HTML/JSON 由生成器更新；CSS/JS 可人工维护 |
| `scripts/` | 工程源 | 校验、聚合、发布、Pages 和同步工具 | 可人工编辑；必须有相应测试 |
| `tests/` | 工程源 | 事实完整性、生成器、GitHub 和发布连续性测试 | 可人工编辑；不得为通过门禁而弱化断言 |
| `writer-chats/` | 人工记录源 | 写作提示、审校意见和取舍摘要 | 先清除 Token、隐私和不必要原文 |
| `memory-bank/` | AI-DLC 事实源 | Intent、Unit、Story、Bolt、Standards、Operations 和日志 | 由 specs.md Agent 流程维护，可人工审阅 |
| `.specsmd/` | 框架运行层 | AI-DLC Agent、Skill、模板和 Schema | 仅在升级或定制框架时修改 |
| `.github/` | 协作与自动化源 | Issue/PR、CI、Pages、Release 和 Project 同步 | 可人工维护；必须通过配置和权限校验 |
| `specs.md-portal/` | 本地只读资料 | 官网 50 页正文、索引和 22 张图片 | 被 `.gitignore` 排除；引用时记录抓取日期和来源页 |
| `aidlc-book-content-resources/` | 研究素材 | 作者收集的内容资料 | 按来源、许可和证据规则使用 |
| `github_repo_reference_ai-agent-book-main/` | 本地只读参考 | 外部书籍仓库结构和实验实现参考 | 被 `.gitignore` 排除；不得复制不兼容许可内容 |
| `working-book/` | 作者本地保留区 | 工作稿、培训 HTML、行动指南和视觉展示稿 | 被 `.gitignore` 排除；不得成为公开构建的必需依赖 |
| `.artifacts/` | 临时运行区 | 本地工具或测试产物 | 不作为完成证据或长期事实源 |

## 4 · 七个权威事实源

| 事实 | 唯一权威源 | 常见投影 |
| --- | --- | --- |
| 14 天任务、依赖和验收 | `progress/tasks.json` | Dashboard、README、GitHub Projects |
| 十章生产阶段 | `progress/chapters.json` | Dashboard 章节矩阵 |
| 实验分类和状态 | `progress/experiments.json` | 实验表、Release Notes |
| 持续更新周期 | `progress/cycles.json` | 下一周期入口 |
| 反馈决定 | `feedback/decisions.json` | 反馈摘要、修订任务 |
| 写作正文与目录 | `book/` | HTML/PDF/Pages 构建物 |
| AI-DLC 开发生命周期 | `memory-bank/` | specs.md Dashboard、开发日志 |

规则：投影只能从权威源生成或单向同步。若 GitHub Issue、Project、README 或 Dashboard 与权威源冲突，停止同步、报告差异，以仓库事实源为准。

## 5 · 人工源、生成源和历史源

### 人工源

可以直接修改，但修改后必须通过校验：

- `book/`
- `docs/`
- `planning/`
- `progress/tasks.json`、`chapters.json`、`experiments.json`、`cycles.json`
- `feedback/decisions.json`
- `scripts/`、`tests/`

### 可替换生成源

失败时可以从权威源重建，不应手工修补：

- `progress/generated/current.json`
- `progress/generated/current.md`
- `site/index.html`、`site/details.html`、`site/data/progress.json`
- `releases/v0.1-rc/readiness.*`
- `releases/v0.1-rc/release-notes.md`

### 追加或不可变历史

- `progress/events/events.jsonl`：只追加，不改序。
- `progress/snapshots/*.json`：创建后不覆盖。
- 真实发布 receipt：只能由真实发布工作流产生。

## 6 · 常见修改应该去哪里

| 要做的事 | 正确位置 |
| --- | --- |
| 修改核心公式、Part 0 或章节正文 | `book/` |
| 修改目标读者、审校规则或版本范围 | `planning/` |
| 改变任务状态或二元验收 | `progress/tasks.json` |
| 改变章节六阶段状态 | `progress/chapters.json` |
| 新增或重分类实验 | `progress/experiments.json`，并同步实验目录 |
| 记录关键状态变化 | 修改事实源后运行生成器；里程碑使用显式事件参数 |
| 保存外部资料 | 对应研究目录，保留来源、日期与许可 |
| 修改 Dashboard 统计 | 修改事实源或生成器，禁止直接改生成 HTML 数字 |
| 修改 GitHub Project 状态 | 先改仓库事实源，再执行单向同步 |

## 7 · 本地工作流

1. 在正确的人工源或权威事实源中修改内容。
2. 运行 `python3 scripts/validate_project.py` 检查依赖、验收、Schema 和产物。
3. 运行 `python3 scripts/generate_progress.py` 更新事件、快照、摘要和 Dashboard。
4. 运行 `python3 scripts/ci_check.py --budget-seconds 60` 执行与 Pull Request 相同的门禁。
5. 审阅 Git diff，确认没有手工生成统计、秘密或无来源复制内容。
6. 提交或发起 Pull Request，并关联稳定 Task ID。

## 8 · 安全与许可边界

- 只提交 `env.example`，不提交 `.env`、Token、Cookie、API Key 或完整环境变量。
- 外部实验固定版本和配置，秘密通过运行环境注入。
- Fork Pull Request 不获得发布秘密。
- 参考仓库和官网存档不是默认可复制内容；引用前确认许可并保留来源。
- 写作对话和反馈只保存完成决策所需的最小信息。

## D02-T01 验收

- [x] 仓库主要目录均有唯一职责。
- [x] 人工源、权威事实源、可替换投影和不可变历史已经区分。
- [x] GitHub 与 Dashboard 的单向投影边界已经说明。
- [x] 外部资料、作者保留区和临时产物不会被自动化误当成完成证据。
