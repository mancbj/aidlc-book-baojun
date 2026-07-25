# EXP-06-01 · Plan–Walkthrough 偏差审计器

> 用确定性规则比较 Implementation Plan、实际变更与 Walkthrough，生成可复核的偏差报告。

## 目的

实验把三份输入按 `path` 对齐：

1. `implementation_plan.deliverables`：计划交付项；
2. `actual_changes`：实际代码或文档变更；
3. `walkthrough.changes` 与 `walkthrough.deviations`：Walkthrough 已声明的正常变更和偏差。

输出 `audit_table` 即“计划项 / 实际变更 / 未声明偏差表”。每行保留三方证据、分类和稳定判定代码。

## 分类边界

- `aligned`：计划、实际变更和 Walkthrough 声明一致。
- `deviation`：存在未计划或未声明变更，需要审阅，但**不自动视为错误**。
- `failure`：计划交付项没有实际变更，或 Walkthrough 声明的变更没有实际证据。

稳定审计代码：

| 代码 | 分类 | 含义 |
|---|---|---|
| `UNPLANNED_CHANGE` | deviation | 实际变更不在计划中 |
| `UNDECLARED_CHANGE` | deviation | 实际变更未在 Walkthrough 中声明 |
| `PLAN_ITEM_MISSING` | failure | 计划交付项没有实际变更 |
| `WALKTHROUGH_CHANGE_NOT_FOUND` | failure | Walkthrough 声明没有实际变更证据 |

输入校验错误也使用稳定代码，例如 `E_INVALID_JSON`、`E_REQUIRED_FIELD`、`E_DUPLICATE_PATH` 和 `E_EXPERIMENT_ID`。

## 环境与运行

- Python 3.9+
- 仅使用标准库
- 无网络、无模型 API、无密钥

从仓库根目录运行样例：

```bash
python3 experiments/exp-06-01/quickstart.py --sample
```

等价的显式命令：

```bash
python3 experiments/exp-06-01/quickstart.py \
  --input experiments/exp-06-01/samples/input.json \
  --output experiments/exp-06-01/output/sample.json
```

运行专项测试：

```bash
python3 -m unittest discover \
  -s experiments/exp-06-01/tests \
  -p 'test_*.py' -v
```

## 指标

- `deliverable_coverage_percent`（交付项覆盖率）：有实际变更证据的计划项数 / 计划项总数。
- `undeclared_change_count`（未声明变更数）：没有出现在 Walkthrough 任一声明列表中的实际变更数。
- `deviation_count`：分类为 deviation 的表格行数。
- `failure_count`：分类为 failure 的表格行数。

报告在 `failure_count == 0` 时 `valid: true`。因此，未声明变更会影响偏差与未声明变更指标，但不会仅凭“未声明”导致命令失败。

## 样例与退出码

- `samples/input.json` 同时展示对齐变更、已声明计划外变更和未声明计划外变更。
- `samples/invalid/` 包含无效 JSON、缺少计划、重复实际路径和错误实验编号。
- `output/sample.json` 是 `--sample` 的确定性输出；相同输入重复运行产生字节一致结果。
- exit `0`：输入有效且无 failure；exit `1`：输入或文件错误；exit `2`：审计完成但发现 failure。
