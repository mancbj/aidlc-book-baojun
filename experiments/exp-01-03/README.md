# EXP-01-03 · AI-DLC 三阶段官方流程复现

KEEP-EXT：对照仓库内冻结的 Inception / Construction / Operations 指南，核对输入轨迹中的必需工件与检查点。**Python 标准库、不联网。**

## 运行

```bash
python3 experiments/exp-01-03/quickstart.py --sample
```

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.artifact_completeness_percent` | 三阶段登记必需工件完整率（%）的算术平均 |
| `metrics.checkpoint_count` | 指南登记的全部检查点数量（分阶段合计） |

## 限制

输出 `limitation` 明确：冻结 pin ≠ 唯一标准，且不抓取实时 specs.md portal。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-01-03/tests -p 'test_*.py' -v
```
