# EXP-01-01 · 同一 Intent 多次生成方差基线

这个确定性实验读取**冻结的多次生成 JSON 快照**（同一 Intent、固定模型与提示元数据），输出结构化差异报告与方差指标。只使用 Python 标准库，不联网，不调用任何在线模型或 API。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-01-01/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-01-01/quickstart.py \
  --input experiments/exp-01-01/samples/input.json \
  --output experiments/exp-01-01/output/sample.json
```

## 输入

输入 JSON 必须包含：

- `experiment_id`: `EXP-01-01`
- `intent`: 非空 `id` 与 `statement`
- `generation_context`: 非空 `model`、`prompt_id`；可选 `temperature`
- `generations`: 至少 2 条冻结生成，每条含：
  - `id`（唯一）
  - `structured_output`：结构化字段/AST 快照（对象或嵌套对象）
  - 可选 `test_pass`（布尔）：该次生成对应测试是否通过

## 输出与指标

输出包含：

- `structure_difference_report`：无序生成对 × 并集 canonical 路径的逐对比较；
- `metrics.structure_difference_rate`：`differing_pairs / total_pairs`（路径值不等或一侧缺失计为差异）；
- `metrics.test_pass_rate`：含 `test_pass` 的生成中通过比例；
- `metrics.test_pass_rate_variance`：对上述 0/1 序列的**总体方差**（除以 N，不是样本 `n-1` 方差）。

重要限制：冻结方差基线只度量夹具内快照差异；**不证明**模型或流程已“足够稳定”可依赖单次生成交付。

## 稳定错误代码

失败时 exit `1`，stderr 输出 `[ERROR <code>]`，且不写报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_INSUFFICIENT_GENERATIONS`：`generations` 少于 2 条；
- `E_DUPLICATE_ID`：生成 `id` 重复。

其他校验亦使用稳定代码，例如 `E_EXPERIMENT_ID`、`E_INVALID_FIELD`、`E_REQUIRED_COLLECTION`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-01-01/tests -p 'test_*.py' -v
```

测试验证差异报告、两个指标、三类失败输入、`--sample` 与重复运行的字节级确定性。
