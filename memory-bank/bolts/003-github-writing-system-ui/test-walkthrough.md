---
stage: test
bolt: 003-github-writing-system-ui
completed: 2026-07-22T02:35:33Z
---

# Test Walkthrough: GitHub Collaboration, Automation and Projection

## Verdict

Bolt 003 的协作模板、共享 CI、四条 GitHub workflow、Pages/Release 构建器和 Projects 单向同步器全部通过本地完整验收。最终 59 个测试全部通过，Actionlint v1.7.12 对四条 workflow 零报错，真实 42/10/30 事实源未被 Projects dry-run 修改。

本阶段验证的是仓库内实现和模拟 GitHub API。仓库仍没有 remote，因此没有声称远端 Actions、Pages、Release 或 Project 已实际运行；真实外部连通性将在用户明确目标仓库和权限后验证。

## Automated Test Result

```text
...........................................................
----------------------------------------------------------------------
Ran 59 tests in 0.943s

OK
```

其中 Bolt 001–002 的 32 项回归全部保留，Bolt 003 新增 27 项。

### Collaboration and Security · 6 Tests

- 当前 4 workflows、4 Issue Forms、17 labels、9 fields、4 views 契约通过。
- 任一 Action 改回浮动 tag 会被拒绝。
- 完整 PR metadata 通过；缺 Task ID、产物或已确认验收时失败并指出修复入口。
- 所有 workflow 禁止 `pull_request_target`。
- PR validate 不含 write 权限或 secret。
- Project dry-run 不声明 secret；只有显式 `apply=true` 步骤可读取 `PROJECT_TOKEN`。
- label 名称和 Carbon 色值均唯一。

### Links and Pages · 3 Tests

- 缺失文件和不存在的 HTML fragment 都能定位。
- Pages tree 包含驾驶舱、事实/历史、书稿、计划、文档和测试证据。
- 带人工文件且无生成标记的目录拒绝替换，原文件保持不变。

### Release · 6 Tests

- HTML-first 候选含 manifest、Release Notes 和 CRC 正常的 zip。
- 非法版本被拒绝。
- 仅把文本改名为 `.pdf` 的伪文件被拒绝。
- 具有 `%PDF-` header 和 `%%EOF` 的显式 PDF 被纳入并记录哈希。
- 无生成标记的人工目录拒绝覆盖。
- 固定事实、版本、commit 和生成时间两次构建得到逐字节相同的 HTML zip 与 SHA-256。

### Projects Projection · 12 Tests

- 缺目标配置、缺 Token 和普通 dry-run 均不创建客户端、不访问网络。
- dry-run 输出稳定 Task ID。
- 重复 Issue marker 被报告。
- 远端 Status 分歧默认停止且零写入。
- 显式 `--force-reproject` 后只把仓库权威状态投影到远端。
- 远端缺字段形成 divergence。
- 已存在稳定 Issue/item 时不重复创建。
- 新任务恰好创建一个 Issue 和一个 Project item，并投影 9 个字段。
- 403 权限错误生成 degraded 报告，不泄露 Token。
- 写入中途失败会标记“可能存在部分远端变更”，要求按 Task ID 审计。
- Project 超过当前 100 item 安全读取上限时停止，不冒险重复创建。
- 所有路径均验证三个权威 JSON 前后 SHA-256 相同。

## Workflow Syntax and Supply Chain

使用 actionlint 官方 v1.7.12 Darwin ARM64 发布包；下载的 archive SHA-256 与同一 GitHub Release 的 checksums 文件一致后才执行。四条 workflow 零输出、退出码 0。

所有 Action 继续固定到 40 位 commit SHA。普通 YAML 解析还覆盖 10 个 `.github/**/*.yml` 文件，全部通过。

官方参考：

- [actionlint](https://github.com/rhysd/actionlint)
- [GitHub workflow permissions](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions#permissions)
- [GitHub Pages deployment](https://github.com/actions/deploy-pages)

## Real Repository CI

```text
[INFO] validation summary: tasks=42, chapters=10, experiments=30, errors=0, warnings=0
Ran 59 tests in 0.782s
OK
[DRY-RUN] ... tasks=42 chapters=10 experiments=30 new_events=0 total_events=1
[INFO] link summary: files=24, internal=186, external-not-fetched=2, errors=0
[INFO] CI summary: checks=5, seconds=1.232, budget=60.0, ok=True
```

核心门禁只用了预算的约 2.1%。相同事实没有生成第二条事件或第二份快照。

## Final Pages and Release Audit

固定来源 `bolt003-test` 的最终候选：

| Check | Result |
|---|---|
| Pages files | 45 |
| Published internal links | 189，零错误 |
| External links | 2，仅列出、不联网阻断 |
| Release zip entries | 46 |
| HTML | included |
| PDF | skipped，未伪造 |
| ZIP CRC | 通过 |
| Repeated build | 字节一致 |
| Deterministic SHA-256 | `9b6dc1123688b7be68893edb35b3a7b4f9cf777f2045e3d92eb3749c14da569b` |

## Failure Injection and Fixes

### Published evidence link

首次实现冒烟发现驾驶舱链接到 `tests/test_validate_project.py`，Pages tree 却未包含测试证据。发布树现纳入 `tests/`，最终 189 个内部链接零错误。

### Fake PDF

原实现只验证文件存在和 `.pdf` 后缀，普通文本仍可能混入候选。现增加 PDF header/EOF 基础结构检查，并由失败测试锁定。

### Remote permission degradation

原实现遇到 403/网络错误只返回失败，无法留下结构化投影报告。现返回 `degraded`、错误和下一动作；如果错误发生在部分写入后，明确标记需要远端审计，同时保证事实源零反写。

### Dry-run secret isolation

原 Project workflow 的单一步骤在 dry-run 时也声明 Token。现拆为互斥 dry-run/apply 步骤，只有 `apply=true` 读取 secret。

### Reproducible zip

原 zip 继承临时文件系统 mtime，不保证固定输入逐字节一致。现全部 entry 使用 manifest 的 UTC 生成时间和固定文件权限，两次构建 SHA-256 一致。

### Label identity

两组重复色值已改为独立 Carbon 色值，并加入名称、格式和颜色唯一性自动校验。

## Security and Integrity Audit

- Token、GitHub PAT、AWS key 和私钥 header 模式：0 命中。
- Project dry-run：42 个期望任务，零网络，三个事实 SHA-256 前后一致。
- `git diff --check`：通过。
- Python `py_compile`：scripts/tests 全部通过。
- `.artifacts/` 被 `.gitignore` 排除，仅保存可删除测试报告。

## Final Commands

```text
python3 scripts/validate_github_config.py
python3 -m unittest discover -s tests
python3 scripts/ci_check.py --budget-seconds 60
python3 scripts/sync_github_project.py --report .artifacts/project-sync-report.json
actionlint .github/workflows/*.yml
git diff --check
```

全部成功。Stage 3 没有创建 commit、remote、GitHub 仓库、标签、里程碑、Pages 部署、Release 或 Project 远端变更。
