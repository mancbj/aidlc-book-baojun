# EXP-06-03 · 端到端 Bolt 执行复现

KEEP-EXT：对照冻结 Bolt 执行指南，核对 plan→implement→test 阶段工件；`completion_seconds` 由输入 `timing.started_at_epoch` 与 `completed_at_epoch` 差值得出。

## 运行

```bash
python3 experiments/exp-06-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.completion_seconds` | 输入 timing 字段计算的执行耗时（秒） |
| `metrics.artifact_completeness_percent` | 必需阶段完成且工件齐备的比例（%） |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-06-03/tests -p 'test_*.py' -v
```
