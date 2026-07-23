# Scripts

当前入口：

- `build_book.sh`：一条命令调用 Pandoc 生成自包含 HTML，传入 `all` 时同时生成 PDF
- `build_book.py`：Pandoc/Mermaid/Tectonic 编排、依赖门禁、缺字检查与输入/输出哈希清单

完整构建依赖：`brew install pandoc mermaid-cli tectonic`。
- `validate_project.py`：校验任务、章节和实验事实源
- `validate_github_config.py`：校验 Issue/PR 模板、标签、工作流权限与 Action SHA、Project 字段/视图契约
- `validate_feedback.py`：校验匿名反馈决策、Reader 槽位和持续更新周期
- `record_feedback.py`：默认 dry-run 地追加 accepted/rejected/deferred/pending 决策
- `validate_pr_metadata.py`：校验 PR 的 Task ID、产物、测试与验收元数据
- `check_internal_links.py`：离线校验 Markdown/HTML 仓库内链接和锚点
- `ci_check.py`：在本地与 PR 中运行同一组 Must 门禁，并执行 60 秒预算
- `generate_progress.py`：校验、聚合、记录关键事件、保存快照并更新静态驾驶舱
- `record_events.py`：只比较状态差异并追加关键事件账本，不刷新驾驶舱或快照
- `progress_core.py`：确定性聚合、来源身份和事件差异核心
- `progress_render.py`：Markdown、Changelog 和 HTML 渲染
- `prepare_pages.py`：生成带来源清单的 GitHub Pages 发布树
- `prepare_release.py`：生成 HTML-first Release 候选、校验清单和说明
- `check_release_readiness.py`：按机器 policy 输出 v0.1 ready/blocked 与排序缺口
- `render_release_notes.py`：从 readiness、进度和实验事实生成 Release Notes
- `audit_roadmap_evidence.py`：只读审计 42 个任务证据，不自动改状态
- `open_next_cycle.py`：预览 v0.2；只从真实 release.published event 激活
- `sync_github_project.py`：将仓库任务单向投影到 GitHub Issues/Project V2；默认 dry-run

常用命令：

```text
python3 scripts/generate_progress.py
python3 scripts/generate_progress.py --dry-run
python3 scripts/generate_progress.py --actor "author"
python3 scripts/record_events.py --dry-run --actor "author"
python3 scripts/ci_check.py --budget-seconds 60
python3 scripts/sync_github_project.py --report .artifacts/project-sync-report.json
```

显式记录里程碑、构建或版本：

```text
python3 scripts/generate_progress.py \
  --event-type milestone_reached \
  --event-object v0.0.1 \
  --event-summary "Day 7 可读版本完成"
```

约束：

- Python 3.9+
- 优先仅使用标准库
- 错误输出包含文件、对象、字段和修复建议
- 阻断错误返回非零退出码
- 所有候选产物先在内存/临时文件完成验证
- 历史快照不覆盖，最后成功比较基线最后写入
