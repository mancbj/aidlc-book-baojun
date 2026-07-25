# EXP-10-03 · Mob 协作与 Agent 交接复现

KEEP-EXT：对照冻结 Mob 协作指南，核对 Mob Elaboration / Mob Construction 会话决策与交接日志。

## 运行

```bash
python3 experiments/exp-10-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.handoff_information_loss_percent` | 交接必填信息缺失率（%） |
| `metrics.decision_agreement_percent` | 会话决策与指南参考一致率（%） |
| `metrics.collaboration_seconds` | 输入 timing 计算的协作耗时（秒） |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-10-03/tests -p 'test_*.py' -v
```
