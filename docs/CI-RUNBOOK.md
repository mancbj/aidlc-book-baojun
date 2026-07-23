# CI Runbook

## 本地等价门禁

Pull Request 与本地使用同一个入口：

```text
python3 scripts/ci_check.py --budget-seconds 60
```

它依次检查任务/章节/实验事实、反馈/周期事实、GitHub 配置、全部 unittest、进度生成 dry-run 和仓库内链接。PR 环境还会从 GitHub event 校验 Task ID、测试、产物和验收字段。全链预算为 60 秒，不访问外部链接，也不构建 PDF。

需要在本地预检 PR 正文时：

```text
python3 scripts/validate_pr_metadata.py --body-file /path/to/pr-body.md --required
```

D11-T01 的负例/正例验收记录见 [`planning/reviews/pr-validation-gate.md`](../planning/reviews/pr-validation-gate.md)。

## 失败定位

| Check | 常见原因 | 修复入口 |
|---|---|---|
| `facts` | 重复 ID、未知依赖、非法状态、虚假完成 | `progress/schemas/` 与错误指出的 JSON 对象 |
| `continuity` | 反馈决策缺任务/理由、Reader 状态虚假、周期无首个 Must | feedback/cycle schema 与错误对象 |
| `github-config` | Action 未锁 SHA、权限扩大、模板字段或 Project 视图缺失 | `memory-bank/bolts/003-github-writing-system-ui/implementation-plan.md` |
| `tests` | 聚合、事件、快照或渲染回归 | 首个失败的 `tests/test_*.py` |
| `generation-dry-run` | 候选投影无法完整生成 | `docs/PROGRESS-AUTOMATION.md` |
| `internal-links` | 目标路径或 HTML fragment 不存在 | 错误中的来源文件和行号 |
| `pr-metadata` | PR 模板占位未替换、没有已确认验收 | `.github/pull_request_template.md` |

先修复输出中的第一个具体错误，再重跑完整命令。`--report .artifacts/ci-report.json` 可保存阶段耗时和返回码，但报告不是事实源。

## 安全与降级

- Fork PR 只使用 `contents: read`，不读取任何 secret。
- 外部 URL 不联网校验，避免网络波动阻断写作。
- Pages、Release 和 Project 的远程副作用不属于 PR 门禁。
- 核心门禁超过 60 秒会失败；重型构建应留在发布候选流程。
