# Progress Snapshots

本目录保存写作系统的不可变整体快照。快照用于回答：在某个 Git 提交或工作树事实版本上，42 项任务、10 章、30 项实验、阻塞、下一动作和最近事件分别处于什么状态。

当前状态请看 [`../generated/current.md`](../generated/current.md)；历史变化请看 [`../CHANGELOG.md`](../CHANGELOG.md)。不要手工编辑本目录中的 JSON 快照。

## 生成入口

```bash
python3 scripts/generate_progress.py --actor <actor>
```

生成器按固定顺序执行：

1. 校验任务、章节、实验、反馈和周期五类事实源。
2. 计算来源身份、指标、状态差异和稳定事件 ID。
3. 在内存中生成并校验快照、Changelog、当前摘要和驾驶舱候选。
4. 候选全部通过后才原子更新可替换投影。
5. 最后更新 `progress/generated/last-successful-facts.json` 比较基线。

## 文件名与来源关联

快照文件名格式为：

```text
YYYYMMDDTHHMMSSZ-<source-id>.json
```

`source_id` 同时写入快照内容：

- 五类事实与 Git `HEAD` 一致时，使用完整 commit SHA。
- 已有 commit 但事实存在未提交变化时，使用 commit 前缀与事实指纹组合的 `working-tree-*` 身份。
- 尚无 commit 时，对规范化事实计算 SHA-256 摘要，形成 `working-tree-*` 身份。

因此，正式提交后的快照可以直接追溯到 commit；本地进行中的关键更新也不会错误复用旧提交身份。

## 不可变与幂等规则

- 不同 `source_id` 必须生成不同快照，不得覆盖历史文件。
- 同一 `source_id` 重复运行时复用并验证已有快照，不制造重复副本。
- 已存在快照若内容与候选冲突，生成器立即失败并返回非零状态。
- `events/events.jsonl` 只追加；`CHANGELOG.md` 只追加新关键事件。
- `generated/current.*` 和 `site/` 属于可替换投影，不具备历史权威性。

## 失败安全保证

事实校验、JSON/HTML 候选校验或快照冲突发生时：

- 不覆盖已有历史快照；
- 不推进最后成功比较基线；
- 不把失败候选冒充为当前成功状态；
- 修复问题后可安全重试，事件稳定 ID 会避免重复记录。

以上行为由 `tests/test_generate_progress.py` 覆盖，包括重复运行、状态变化生成新快照、冲突快照拒绝覆盖和失败后保持成功产物。

## 单个快照至少包含

- `generated_at`：带时区生成时间；
- `source_id`：Git commit 或工作树事实身份；
- `metrics`：总进度、加权进度、Must/Should/Could 等；
- `blockers`：阻塞任务与解除动作；
- `next_actions`：依赖满足后的下一步；
- 任务、章节、实验、反馈和周期的完整聚合投影。

字段来源和失败安全细节见 [`../../docs/PROGRESS-AUTOMATION.md`](../../docs/PROGRESS-AUTOMATION.md)。

## 人工复核

每次关键更新后检查：

1. `generated/current.json` 的 `latest_snapshot` 指向本目录中的真实文件。
2. 新快照的 `source_id` 与本次事实版本一致。
3. `CHANGELOG.md` 仅增加预期事件。
4. 重复执行生成命令不会增加重复事件或快照。
5. `python3 scripts/ci_check.py` 全部通过。
