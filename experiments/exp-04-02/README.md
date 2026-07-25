# EXP-04-02 · Standards 漂移检测器

> 用确定性规则比较版本化 Standards 与生成工件，输出规则违反项、版本差异和指标。

## 目的

实验检查三类问题：

1. 工件是否违反声明的 Standards 规则；
2. Standards 版本之间是否存在字段/规则漂移；
3. 误报率只在有人工基准标签时计算，避免空标签把噪声写成精度。

## 指标

- `rule_coverage_percent`：被至少一个工件或基准引用覆盖的规则比例
- `false_positive_rate_percent`：仅基于带 `expected_violation=false` 的基准标签计算
- `drift_item_count`：规则违反项与版本差异项总数

## 边界

- 漂移检测不证明规则适用于所有仓库
- 没有基准标签时，误报率记为 `null`，不得伪装成 0
- 不调用模型，不联网，不读取真实密钥

## 运行

```bash
python3 experiments/exp-04-02/quickstart.py --sample
python3 -m unittest discover -s experiments/exp-04-02/tests -p 'test_*.py' -v
```
