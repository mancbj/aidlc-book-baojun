# GitHub Workflows

仓库使用五条自动化流水线。所有第三方 Action 都锁定到完整提交 SHA，并保留可读版本注释。

| Workflow | Trigger | Default permission | Result |
|---|---|---|---|
| `validate.yml` | Pull Request、手动 | `contents: read` | 事实、配置、测试、生成、链接和 PR 元数据门禁 |
| `pages.yml` | `main` push、手动 | `contents: read` | 生成驾驶舱，上传并部署 Pages；关键记录可恢复 |
| `release.yml` | `v*` tag、手动 | `contents: read` | 构建不可变候选；授权后创建 draft Release |
| `project-sync.yml` | 仅手动 | `contents: read` | 默认 dry-run 的仓库→GitHub Project 单向投影 |
| `post-release.yml` | `release.published` | `contents: read` | 生成发布回执、v0.2 周期和可视事件；以 PR 或 artifact 交付 |
| `star-history.yml` | 每日 cron、手动 | `contents: read` | 渲染 Star History PNG 并提交 `assets/`（`[skip ci]`） |

写权限只在具体 job 提升：进度记录与 Release 使用 `contents: write`，Pages 部署使用 `pages: write` / `id-token: write`，Star History 更新 job 使用 `contents: write`。PR 门禁不使用秘密，也不使用 `pull_request_target`，因此 Fork 代码不会进入特权上下文。Project dry-run 与 apply 是互斥步骤，只有显式 `apply=true` 的步骤声明 `PROJECT_TOKEN`。

本地等价门禁：

```text
python3 scripts/ci_check.py --budget-seconds 60
```

分支保护阻止机器人写入时，`pages.yml` 会保留 `progress-record` artifact，维护者可下载后通过 PR 合并。Pages 未启用时见 [Pages 启用与排障](../../docs/GITHUB-PAGES-SETUP.md)；`deploy` job 会尝试 `configure-pages` 自动启用。Project 缺少目标或 Token 时只输出降级报告；PDF 未提供或未验证时 Release 明确标记为跳过，不伪造 PDF。

`release.yml` 会在候选构建前运行 v0.1 readiness。blocked 报告总会保留，但 build/publish 不继续。只有维护者把 draft v0.1 真正公开后，`post-release.yml` 才在特权 job 中申请 `contents: write` / `pull-requests: write`。

配置、权限和故障路径详见 [GitHub 协作说明](../../docs/GITHUB-COLLABORATION.md)、[发布自动化](../../docs/RELEASE-AUTOMATION.md) 与 [Projects 投影](../../docs/GITHUB-PROJECTS.md)。
