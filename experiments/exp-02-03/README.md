# EXP-02-03 · 四 Agent 人机检查点会话复现

KEEP-EXT：对照冻结的四 Agent 检查点指南，核对路由、提议、人工审批与交接记录。**无依据批准** = 缺少 `evidence` 或 `rationale` 的 `human_approval`。

## 运行

```bash
python3 experiments/exp-02-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.checkpoint_adherence_percent` | 必需会话检查点覆盖率（%） |
| `metrics.ungrounded_approval_count` | 无证据/理由的人工批准次数 |

## 测试

```bash
python3 -m unittest discover -s experiments/exp-02-03/tests -p 'test_*.py' -v
```
