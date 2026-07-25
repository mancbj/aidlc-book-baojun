# EXP-08-03 · Operations 四阶段复现

KEEP-EXT：对照冻结 Operations 指南，核对 Build / Deploy / Runtime Verify / Monitor 阶段凭证与回滚就绪清单。

## 运行

```bash
python3 experiments/exp-08-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.stage_completion_percent` | 必需阶段完成且凭证齐备比例（%） |
| `metrics.rollback_readiness_percent` | 回滚就绪清单满足比例（%） |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-08-03/tests -p 'test_*.py' -v
```
