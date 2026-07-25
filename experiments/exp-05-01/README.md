# EXP-05-01 · Bolt 尺寸估算器

> 用确定性启发式根据 Stories、复杂度、风险与依赖，生成 Bolt 范围、预计时长与拆分建议。

## 目的

实验只提供可复现的尺寸信号，不预测真实交付：

1. 按固定系数汇总 Story 级预计工时；
2. 判断 Bolt 是否超过 `max_bolt_hours` 并计数范围溢出；
3. 对溢出 Bolt 给出按 Story ID 排序的贪心拆分建议；
4. 若输入提供 `actual_hours` baseline，计算工期估算误差百分比，否则为 `null`。

## 指标

| 指标 | 含义 |
|---|---|
| `schedule_estimation_error_percent` | 有 baseline 的 Story 上，估算总工时 vs 实际总工时的相对误差（%）；无 baseline 时为 `null` |
| `scope_overflow_count` | 预计工时超过 `max_bolt_hours` 的 Bolt 数 |

## 稳定代码

- `E_INVALID_JSON` — 输入不是合法 JSON
- `E_REQUIRED_FIELD` — 缺少必填字段或非空集合
- `E_INVALID_FIELD` — 字段类型或取值非法（如复杂度不在 1–5）
- `E_UNKNOWN_STORY` — Bolt 或依赖引用了未知 Story
- `E_DUPLICATE_ID` — Story 或 Bolt ID 重复
- `E_SCHEMA_VERSION` / `E_EXPERIMENT_ID` / `E_INVALID_ROOT`

## 运行

Python 3.9+，仅标准库，无网络、无模型、无密钥。

```bash
python3 experiments/exp-05-01/quickstart.py --sample
```

```bash
python3 -m unittest discover -s experiments/exp-05-01/tests -p 'test_*.py' -v
```

## 边界

- 启发式系数固定，不学习历史数据
- `limitation` 字段明确：**不证明真实世界排期准确性**
- 拆分建议只按工时上限贪心分组，不优化并行或团队负载
- 有 baseline 时误差仅覆盖提供了 `actual_hours` 的 Story
