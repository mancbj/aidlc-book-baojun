# EXP-03-02 · Unit 与 Bolt 依赖 DAG 校验器

> 用确定性图规则检查 Unit、Story 与 Bolt 依赖清单，生成依赖图与异常报告。

## 目的

实验只检查结构合法性，不判断计划是否最优：

1. Story / Bolt 是否引用已知 Unit、Story、Bolt；
2. Bolt 依赖图是否存在循环；
3. 跨 Unit 耦合边与未满足前置是否被计数并警告。

输出包含 `dependency_graph`、`anomalies` 与三项指标。`plan_optimal=false` 明确表示：结构合法不代表调度最优。

## 指标

| 指标 | 含义 |
|---|---|
| `cycle_count` | 循环依赖分量数 |
| `cross_unit_coupling_edge_count` | 跨 Unit 依赖边数 |
| `unmet_prerequisite_count` | 已完成 Bolt 的前置尚未完成的边数 |

## 稳定代码

错误（使 `structural_valid=false`，exit `2`）：

- `E_CYCLE`
- `E_DUPLICATE_ID`
- `E_UNKNOWN_BOLT`
- `E_UNKNOWN_UNIT`
- `E_UNKNOWN_STORY`
- `E_UNASSIGNED_STORY`
- `E_STORY_UNIT_MISMATCH`
- `E_SCHEMA` / `E_SCHEMA_VERSION`

警告（不阻断结构合法）：

- `W_CROSS_UNIT_COUPLING`
- `W_UNMET_PREREQUISITE`

## 运行

Python 3.9+，仅标准库，无网络、无模型、无密钥。

```bash
python3 experiments/exp-03-02/quickstart.py --sample
```

```bash
python3 -m unittest discover -s experiments/exp-03-02/tests -p 'test_*.py' -v
```

## 边界

- DAG 合法 ≠ 计划最优
- 跨 Unit 耦合被计数，但不自动判死刑
- 未满足前置是警告，提示完成顺序风险
- 不证明业务语义、工期或并行调度正确
