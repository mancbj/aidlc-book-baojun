# EXP-09-03 · Brownfield Flow 选择案例复现

KEEP-EXT：对照冻结 choose-flow 指南，核对 Simple / FIRE / AI-DLC 三方案棕地决策案例与依据维度覆盖。

## 运行

```bash
python3 experiments/exp-09-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.decision_rationale_coverage_percent` | 必填决策依据维度覆盖率（%） |
| `metrics.estimated_process_overhead_score` | 所选 Flow 的确定性流程开销分 |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-09-03/tests -p 'test_*.py' -v
```
