# Repository Guide

## 核心原则

仓库不是一个大文档，而是由内容源、运行事实、自动化和审计记录组成的生产系统。任何数字都必须能追溯到一个版本化事实源。

## 目录职责

| Path | Responsibility | Editable |
|------|----------------|----------|
| `book/` | 书稿、核心公式、目录和章节模板 | 人工编辑 |
| `docs/` | 阅读、协作和仓库说明 | 人工编辑 |
| `planning/` | 路线图和可复用行动模板 | 人工编辑，不保存聚合统计 |
| `progress/` | 任务、章节、实验事实及事件/快照投影 | 事实按 Schema 编辑；投影由生成器更新 |
| `feedback/` | 匿名试读反馈决策事实 | 只保存最小摘要；按 Schema 编辑 |
| `releases/` | readiness、候选 Notes 和真实发布回执 | readiness/Notes 可生成；receipt 只来自发布事件 |
| `site/` | 静态鸟瞰驾驶舱及发布数据 | 由生成器更新 HTML/JSON，人工维护 CSS/JS |
| `scripts/` | 校验、聚合和生成工具 | 人工编辑 |
| `tests/` | 自动化脚本测试 | 人工编辑 |
| `writer-chats/` | 写作对话摘要和决策 | 人工编辑，先清理秘密和隐私 |
| `.github/` | Issue/PR 模板、标签与 GitHub 自动化 | 人工维护，必须通过配置安全校验 |
| `memory-bank/` | AI-DLC Intent、Story、Bolt 和日志 | 由 AI-DLC 流程维护 |
| `working-book/` | 已有用户工作区 | 保留，不在 Bolt 001 中迁移 |
| `github_repo_reference_ai-agent-book-main/` | 参考仓库 | 只读参考 |
| `aidlc-book-content-resources/` | 调研素材 | 只读或按来源规则引用 |

## 事实源与投影

1. `progress/tasks.json` 是任务状态的权威源。
2. `progress/chapters.json` 是章节六阶段状态的权威源。
3. `progress/experiments.json` 是实验治理状态的权威源。
4. `feedback/decisions.json` 是匿名反馈决策的权威源。
5. `progress/cycles.json` 是持续更新周期的权威源；preview 不成为当前下一动作。
6. README、计划、驾驶舱和 GitHub Projects 都是导航或投影，不得静默反向覆盖事实源。
7. `memory-bank/` 记录开发生命周期，不与日常写作任务共用状态字段。
8. GitHub Issues 与 Projects 是协作投影；只允许仓库事实源单向投影，远端状态分歧必须报告并停止。

## 人工源与生成源

人工源可以直接修改，但必须通过校验。未来生成文件必须在文件头声明：

- 生成器名称
- 来源文件
- 来源提交
- 生成时间

普通生成过程不得覆盖历史事件和历史快照。当前投影可替换，比较基线只在整条生成链成功后更新。

## 安全边界

- 只提交 `env.example`，不提交真实 `.env`。
- 不记录 Token、Cookie、密钥或完整环境变量。
- 外部实验固定版本和配置，秘密在运行环境注入。
- Fork Pull Request 不获得发布秘密。

## 本地工作流

1. 修改事实源或内容。
2. 运行 `python3 scripts/generate_progress.py`，它会先执行事实校验。
3. 运行 `python3 scripts/ci_check.py --budget-seconds 60`，执行事实、GitHub 配置、测试、生成和链接的同一组门禁。
4. 审阅 Git diff。
5. 提交或发起 Pull Request。
