# EXP-07-03 · 分层验证检查点复现

KEEP-EXT：对照冻结 CH-07 分层验证指南，核对注入缺陷在各层的首次发现位置与逃逸数；`verification_seconds` 来自输入。

## 运行

```bash
python3 experiments/exp-07-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.escaped_defect_count` | 未在任何层被发现的缺陷数 |
| `metrics.first_discovery_stage` | 各缺陷首次发现层（映射） |
| `metrics.verification_seconds` | 输入记录的验证耗时（秒） |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-07-03/tests -p 'test_*.py' -v
```
