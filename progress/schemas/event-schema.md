# Event Schema

> 版本：`1.0.0`  
> 事实源：`progress/events/events.jsonl`  
> 当前生成器：`python3 scripts/generate_progress.py`

本规范定义关键更新事件的机器记录格式与事件类型边界。事件账本是追加式审计记录，用来解释“进度为什么变成现在这样”；任务、章节、实验、反馈和周期 JSON 仍然是当前状态的权威事实源。

## 1. 事件账本

`progress/events/events.jsonl` 使用 JSON Lines 格式：

- 每一行是一条完整 JSON object。
- 空行不写入；读取时会忽略空行。
- 新事件只能追加，不能重排旧事件。
- 重复运行生成器时，使用稳定 `id` 去重。

## 2. Event 必需字段

| 字段 | 类型 | 规则 | 用途 |
|---|---|---|---|
| `id` | string | `EVT-` 加 16 位十六进制摘要；同一来源、对象、前后状态与类型必须稳定 | 去重与引用 |
| `occurred_at` | string | 带时区 ISO 8601 时间，格式 `YYYY-MM-DDTHH:MM:SSZ` | 时间线排序与展示 |
| `type` | enum | 见第 4 节 | 事件语义 |
| `object_type` | enum | `system` / `task` / `chapter_stage` / `experiment` / `feedback` / `cycle` / `project` | 被记录对象类别 |
| `object_id` | string | 稳定 ID；组合对象使用 `:`，如 `CH-03:experiment` | 可定位对象 |
| `before` | any | 变化前的值；首次或显式事件可为 `null` | 差异审计 |
| `after` | any | 变化后的值或显式摘要 | 差异审计 |
| `source_id` | string | 本次五类事实源的来源身份 | 防止不同事实源覆盖 |
| `actor` | string | 执行生成或显式记录的人/系统 | 责任线索 |
| `summary` | string | 非空、人可读中文摘要 | Changelog 与驾驶舱展示 |

事件对象必须可以被 `scripts/progress_core.py::canonical_json` 稳定序列化，不得包含当前机器绝对路径、随机数或不可复现字段。

## 3. ID 与幂等规则

事件 ID 由以下材料计算：

```text
[type, object_type, object_id, before, after, source_id]
```

这意味着：

- 同一事实源重复生成，不会追加重复事件。
- 同一个对象在不同来源身份下发生同一变化，会生成不同事件。
- 仅改变 `occurred_at` 或 `actor` 不会改变事件 ID。
- 事件一旦写入，不应为了改摘要而重写旧行；需要修订时追加新的事实变化或显式事件。

## 4. 事件类型

### 4.1 自动事件

这些事件由 `scripts/generate_progress.py` 比较 `last-successful-facts.json` 与当前事实源自动生成。

| 类型 | 覆盖对象 | 触发条件 | `object_type` | `before` / `after` |
|---|---|---|---|---|
| `system_initialized` | 进度系统 | 没有成功基线时首次生成 | `system` | `null` / `initialized` |
| `task_status_changed` | 任务 | 任一 Task 的 `status` 变化 | `task` | 旧状态 / 新状态 |
| `chapter_stage_changed` | 章节阶段 | 任一章节六阶段状态变化 | `chapter_stage` | 旧阶段状态 / 新阶段状态 |
| `experiment_changed` | 实验 | 实验 `triage` 或 `status` 变化 | `experiment` | 旧值 / 新值 |
| `feedback_decided` | 读者反馈 | 反馈 decision 从无记录或 pending 变为 `accepted` / `rejected` / `deferred` | `feedback` | 旧决定 / 新决定 |
| `cycle_opened` | 后续周期 | 周期由真实发布回执激活为 `active` | `cycle` | 旧状态 / `active` |

自动事件覆盖了任务、章节和实验三类日常进度变化；反馈与周期用于发布后的持续更新。

### 4.2 显式事件

这些事件不是普通状态字段，必须通过生成器参数显式记录。

| 类型 | 覆盖对象 | 典型命令 | `object_type` | `before` / `after` |
|---|---|---|---|---|
| `build_completed` | 构建 | `--event-type build_completed --event-object build:<id> --event-summary "<summary>"` | `project` | `null` / 摘要 |
| `milestone_reached` | 里程碑 | `--event-type milestone_reached --event-object v0.0.1 --event-summary "<summary>"` | `project` | `null` / 摘要 |
| `release_published` | 发布 | `--event-type release_published --event-object v0.1 --event-summary "<summary>"` | `project` | `null` / 摘要 |

显式事件必须同时提供 `--event-type`、`--event-object` 和 `--event-summary`。任一缺失时生成器必须失败且不写入新文件。

验收覆盖清单：

| 范畴 | 事件类型 |
|---|---|
| 任务 | `task_status_changed` |
| 章节 | `chapter_stage_changed` |
| 实验 | `experiment_changed` |
| 构建 | `build_completed` |
| 里程碑 | `milestone_reached` |
| 发布 | `release_published` |

## 5. 状态值约束

事件不重新定义对象状态，只引用对应事实源 schema：

- 任务状态见 `progress/schemas/task-schema.md`。
- 章节阶段状态见 `progress/schemas/chapter-schema.md`。
- 实验状态与 triage 见 `progress/schemas/experiment-schema.md`。
- 反馈 decision 见 `progress/schemas/feedback-schema.md`。
- 周期状态见 `progress/schemas/cycle-schema.md`。

如果某个事件的 `before` 或 `after` 与对应 schema 冲突，应修正事实源、生成器和测试，而不是手工编辑事件账本。

## 6. 最小示例

```json
{
  "id": "EVT-28563013d137eb81",
  "occurred_at": "2026-07-22T07:56:32Z",
  "type": "task_status_changed",
  "object_type": "task",
  "object_id": "D05-T03",
  "before": "in-progress",
  "after": "done",
  "source_id": "working-tree-a36db77e3fa7",
  "actor": "codex",
  "summary": "D05-T03 · 生成第一份进度聚合：in-progress → done"
}
```

## 7. 生成与验证协议

每次事实源发生关键更新时：

1. 修改权威事实源。
2. 运行 `python3 scripts/validate_project.py`。
3. 运行 `python3 scripts/generate_progress.py --actor <actor>`。
4. 审阅 `progress/events/events.jsonl`、`progress/CHANGELOG.md` 和驾驶舱最近更新。

没有事实变化或显式事件时，生成器不得追加事件。事件账本和 Changelog 只解释已经发生的关键变化，不能代替任务验收或发布回执。
