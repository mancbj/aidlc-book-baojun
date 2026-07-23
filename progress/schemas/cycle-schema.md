# Update Cycle Schema

Cycle 使用版本目标作为稳定 ID，例如 `v0.2-draft`。状态只允许 preview / active / complete。

每个周期必须记录来源 Release、月度目标和每周内容/实验/构建审校节奏。Cycle Task 使用 `C02-TNN`，包含 kind、priority、status、dependencies 和二元验收。

激活时还记录 `accepted_feedback`、`carried_tasks` 和 `carried_gaps`。未完成项来自 v0.1 原任务的只读投影，不能重置或改写原任务；公开缺口来自同一 source 的实时 readiness。

preview 不进入驾驶舱下一动作；只有真实 v0.1 published receipt、`status=ready` 的实时门禁和一致 source SHA 才能把周期设为 active。激活不得重置或修改 v0.1 的 `progress/tasks.json`。
