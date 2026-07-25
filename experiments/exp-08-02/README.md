# EXP-08-02 · 回滚桌面演练模拟器

> 根据部署拓扑、故障场景、监控信号与 Runbook 步骤，生成发现、决策、回滚和恢复的确定性演练时间线。

## 目的

实验把四类 Operations 输入结构化链接：

1. `deployment_topology`：环境与组件版本、回滚目标；
2. `fault_scenario`：故障发生时刻、影响组件与是否有数据影响；
3. `monitoring_signals`：带时间戳的监控/告警信号；
4. `runbook_steps`：detect / decide / rollback / recover 各阶段步骤（含 `duration_minutes`）。

输出 `drill_timeline` 即 **detect → decide → rollback → recover** 桌面演练时间线，并列出 Runbook 缺口与三项指标。

## 锚定规则

- **detect**：优先取链接到故障的最早 `monitoring_signals.observed_at`；若无信号则取 detect 阶段 Runbook；仍无则回退到 `fault_scenario.occurred_at`。
- **decide / rollback / recover**：各取对应 `phase` 中 `started_at`、`id` 最早的 Runbook 步骤；`ended_at = started_at + duration_minutes`。
- **Runbook 缺口**：缺少阶段步骤、rollback 未声明目标、受影响组件未被 rollback 覆盖、rollback 目标组件缺少 `rollback_target` 等，按稳定代码写入 `runbook_gaps`。

稳定阶段代码示例：

| 代码 | 含义 |
|---|---|
| `DETECT_FROM_MONITORING` | detect 由监控信号锚定 |
| `DETECT_FROM_RUNBOOK_ONLY` | 无监控信号，detect 由 Runbook 锚定 |
| `DETECT_INFERRED_FROM_FAULT` | 无监控与 detect Runbook，由故障时刻推断 |
| `PHASE_ANCHORED` | 该阶段存在 Runbook 步骤 |
| `MISSING_PHASE_*` | 缺少对应阶段 Runbook |

输入校验错误使用稳定 `E_*` 代码，例如 `E_INVALID_JSON`、`E_REQUIRED_FIELD`、`E_DUPLICATE_ID`、`E_UNKNOWN_FAULT_ID`、`E_UNKNOWN_COMPONENT_ID` 和 `E_EXPERIMENT_ID`。

## 环境与运行

- Python 3.9+
- 仅使用标准库
- 无网络、无模型 API、无密钥

从仓库根目录运行样例：

```bash
python3 experiments/exp-08-02/quickstart.py --sample
```

等价的显式命令：

```bash
python3 experiments/exp-08-02/quickstart.py \
  --input experiments/exp-08-02/samples/input.json \
  --output experiments/exp-08-02/output/sample.json
```

运行专项测试：

```bash
python3 -m unittest discover \
  -s experiments/exp-08-02/tests \
  -p 'test_*.py' -v
```

## 指标

- `detect_to_rollback_minutes`（发现到回滚耗时）：detect 起点至 rollback 步骤 `started_at` 的分钟数（保留两位小数）；无 rollback 步骤时为 `null`。
- `data_loss_window_minutes`（数据损失窗口）：当 `data_impact=true` 时为故障发生至 rollback 结束的分钟数；否则为 `null`。
- `runbook_gap_count`（Runbook 缺口数）：`runbook_gaps` 条目数量。

## 局限

桌面演练时间线只表示演练脚本与 Runbook 缺口可复现，**不等于**生产环境真实恢复能力或数据零损失。Recover 步骤中的 **Runtime Verify** 指 CH-08 运行态核验，**不等于** CH-07 的交付候选 Verify。详见输出中的 `limitation` 字段。

## 样例与退出码

- `samples/input.json` 展示完整四阶段演练、监控锚定与 Runbook 覆盖缺口。
- `samples/invalid/` 包含无效 JSON、缺少 fault_scenario、重复信号 ID、错误实验编号与未知故障引用。
- `output/sample.json` 是 `--sample` 的确定性输出；相同输入重复运行产生字节一致结果。
- exit `0`：输入有效并生成报告；exit `1`：输入或文件错误。
