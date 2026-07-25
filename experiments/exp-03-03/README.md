# EXP-03-03 · Inception Agent 完整分解复现

KEEP-EXT：对照冻结 Inception 分解指南，校验 Requirements、System Context、Units、Stories、Bolt Plan 及登记追踪链接。

## 运行

```bash
python3 experiments/exp-03-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.artifact_completeness_percent` | 五类登记工件完整率（%） |
| `metrics.trace_link_coverage_percent` | 必需追踪链接覆盖率（%） |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-03-03/tests -p 'test_*.py' -v
```
