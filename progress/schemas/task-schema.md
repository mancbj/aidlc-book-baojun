# Task Schema

> 版本：`1.0.0`  
> 事实源：`progress/tasks.json`  
> 可执行校验：`python3 scripts/validate_project.py`

本规范统一写作、实验、工程、审校和发布任务的数据结构。任务状态只能在事实源中修改；进度摘要、驾驶舱和 GitHub Projects 都是由事实源生成的投影，不能反向成为统计真相。

## 1. 顶层文档

`progress/tasks.json` 必须是一个 JSON object：

| 字段 | 类型 | 规则 |
|---|---|---|
| `schema_version` | string | 当前版本为 `1.0.0` |
| `source` | string | 任务计划的来源路径或标识 |
| `updated` | string | 最后一次事实更新，必须是带时区的 ISO 8601 时间 |
| `tasks` | array[Task] | 全部任务；空列表允许，但每条记录必须符合本规范 |

## 2. Task 必需字段

| 字段 | 类型 | 允许值或约束 | 用途 |
|---|---|---|---|
| `id` | string | 唯一；正则 `^D\d{2}-T\d{2}$`；ID 中 Day 必须等于 `day` | 稳定引用与事件主体 |
| `title` | string | 非空 | 面向作者的动作标题 |
| `type` | enum | `writing` / `experiment` / `engineering` / `review` / `release` | 按工作类型聚合 |
| `phase` | enum | `foundation` / `progress` / `github` / `release` | 按建设阶段聚合 |
| `status` | enum | 六种状态之一，见第 4 节 | 进度与下一动作 |
| `priority` | enum | `must` / `should` / `could` | 排序及加权进度 |
| `owner` | string | 非空 | 唯一责任人或角色 |
| `day` | integer | `1`–`99` | 路线图中的相对日；D01–D14 保留 v0.1，两周后续写作冲刺可继续递增 |
| `planned_date` | string | 有效日期，格式 `YYYY-MM-DD` | 日历锚点 |
| `dependencies` | array[string] | 只引用已知任务 ID；不得自引用或形成环 | 开始与完成门禁 |
| `artifacts` | array[Artifact] | 至少一项 | 可验证产物 |
| `acceptance` | array[Acceptance] | 至少一项 | 二元验收条件 |
| `updated` | string | 带时区 ISO 8601 时间 | 单任务关键更新时间 |

`blocker_reason` 和 `unblock_action` 是条件字段。当前事实源为便于阅读会始终保留它们；非 `blocked` 状态使用空字符串。

## 3. 嵌套对象

### 3.1 Artifact

| 字段 | 类型 | 规则 |
|---|---|---|
| `path` | string | 非空、仓库根目录相对路径；禁止绝对路径与 `..` 路径段 |
| `required` | boolean | `true` 表示进入 `done` 前该路径必须存在；`false` 表示可选产物 |

### 3.2 Acceptance

| 字段 | 类型 | 规则 |
|---|---|---|
| `text` | string | 非空、可由人或脚本作出“通过/未通过”判断 |
| `passed` | boolean | 未通过为 `false`；只有实际验收后才改为 `true` |

验收项应描述结果，不描述投入。例如使用“目录包含十章且顺序经确认”，而不是“花 30 分钟整理目录”。

## 4. 六种状态

| 状态 | 语义 | 进入条件 | 离开时的关键更新 |
|---|---|---|---|
| `backlog` | 已进入路线图，尚未作为当前工作 | 任务结构完整 | 依赖满足后可进入 `ready` 或直接开始 |
| `ready` | 依赖已满足，可立即领取 | 已知依赖均为 `done` | 开始工作时进入 `in-progress` |
| `in-progress` | 正在产出或修改产物 | 已明确负责人和下一动作 | 完成产出后进入 `review`，或在客观可验收的小任务中直接申请完成 |
| `review` | 产物已形成，等待审校或验收 | 产物可访问，验收项可检查 | 通过后进入 `done`；需修改则退回 `in-progress` |
| `done` | 任务已满足全部完成门禁 | 见第 5.1 节 | 原则上不静默重开；新增修订应产生新的任务或明确状态事件 |
| `blocked` | 当前无法继续 | 必须写明原因和解除动作 | 障碍解除后回到 `ready` 或 `in-progress` |

推荐主路径：

```text
backlog → ready → in-progress → review → done
                     ↑          │
                     └──────────┘

backlog / ready / in-progress / review → blocked → ready / in-progress
```

状态路径是协作约定；当前校验器检查的是提交后的状态不变量，状态变化本身由 `scripts/generate_progress.py` 与上一份成功事实源比较并自动记录。

## 5. 条件门禁

### 5.1 `done` 门禁

任务只有同时满足以下条件才能设为 `done`：

1. `acceptance` 非空，并且每一项的 `passed` 都严格为 `true`。
2. 每个 `required: true` 的产物路径都真实存在。
3. `dependencies` 中每个任务都已经是 `done`。
4. `updated` 与顶层 `updated` 更新为本次变更时间。

任何一项不满足，`scripts/validate_project.py` 都必须失败；不得通过手工修改驾驶舱绕过门禁。

### 5.2 `blocked` 门禁

`status` 为 `blocked` 时必须同时提供：

- `blocker_reason`：当前不能继续的客观原因。
- `unblock_action`：可执行的解除动作，最好包含责任人或所需输入。

解除阻塞时清空这两个字段，并将状态改为 `ready` 或 `in-progress`。生成器会把阻塞与解除阻塞作为关键事件记录。

### 5.3 依赖门禁

- 无依赖必须显式写为 `[]`，不能省略字段。
- 依赖必须是当前文档内存在的任务 ID。
- 依赖图不得有循环。
- 任务可在事实源中提前定义，但只有依赖完成后才应进入 `ready`。
- `done` 任务不能依赖尚未完成的任务。

## 6. 下一动作与鸟瞰规则

驾驶舱将 `done` 和 `blocked` 排除出普通下一动作列表，并只显示依赖已经完成的候选任务。时间线按事实源中的最小/最大 `day` 动态生成，不再假定只存在 14 天。候选排序为：

1. 状态：`review` → `in-progress` → `ready` → `backlog`。
2. 优先级：`must` → `should` → `could`。
3. `day`、`planned_date`、`id` 依次升序，保证生成结果稳定。

任务可以按 `day`、`phase`、`type`、`priority`、`status` 聚合；章节、实验和里程碑的进度分别从 `progress/chapters.json`、`progress/experiments.json` 与相关任务/发布事实联合投影，不在任务记录中重复维护百分比。

## 7. 最小合法示例

```json
{
  "id": "D02-T03",
  "title": "定义任务模型",
  "type": "engineering",
  "phase": "foundation",
  "status": "in-progress",
  "priority": "must",
  "owner": "author",
  "day": 2,
  "planned_date": "2026-07-22",
  "dependencies": ["D02-T02"],
  "artifacts": [
    {
      "path": "progress/schemas/task-schema.md",
      "required": true
    }
  ],
  "acceptance": [
    {
      "text": "必需字段、六种状态和条件门禁已定义",
      "passed": false
    }
  ],
  "blocker_reason": "",
  "unblock_action": "",
  "updated": "2026-07-22T06:23:26Z"
}
```

## 8. 更新协议

每次关键更新按同一顺序执行：

1. 只修改事实源：状态、验收结果、产物路径和时间戳。
2. 运行 `python3 scripts/validate_project.py`，先验证状态不变量。
3. 运行 `python3 scripts/generate_progress.py --actor <actor>`。
4. 提交事实源及生成的事件、快照、摘要和站点投影。

生成器检测到任务开始、审阅、完成、阻塞或解除阻塞时，会追加事件并刷新 `progress/generated/` 与 `site/data/progress.json`；没有状态变化时不会制造虚假任务事件。

## 9. 规则与实现映射

| 规范规则 | 执行位置 |
|---|---|
| 必需字段、枚举、日期、时间戳 | `scripts/validate_project.py::validate_tasks` |
| ID 与 Day 一致、依赖存在且无环 | `scripts/validate_project.py::validate_tasks` |
| 产物与验收对象结构 | `validate_artifacts` / `validate_acceptance` |
| `blocked` 条件字段 | `validate_task_conditionals` |
| `done` 验收、产物、依赖门禁 | `validate_done_task` |
| 下一动作与聚合 | `scripts/progress_core.py::aggregate_progress` |
| 状态变化事件与可视化投影 | `scripts/generate_progress.py` |

这份 Markdown 是人可读合同；校验脚本和测试是机器可执行合同。二者发生冲突时，必须在同一次变更中修正规范、实现和测试，不能只更新其中一处。
