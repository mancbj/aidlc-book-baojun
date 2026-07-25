# EXP-07-02 · 独立评审分歧矩阵

> 在 CH-07 **交付候选验证（Verify）** 语境下，比较冻结的测试证据、独立模型评审与人工 Rubric，生成多方判断及分歧归因矩阵。

## 目的

实验把四类输入对齐到同一组 Rubric 维度与模型风险项：

1. `delivery_candidate`：待验证交付候选标识与摘要；
2. `test_evidence`：独立测试证据摘要与关联 Rubric；
3. `independent_model_reviews`：**冻结**的独立模型评审夹具（不调用外部模型）；
4. `human_rubric`：人工 Rubric 维度判断与总体裁决。

输出 `disagreement_matrix` 记录各方信号、发布立场（approve / reject / defer）及稳定归因代码。`multi_party_summary` 汇总测试、各模型与人工的总体立场。

## 边界

- 本实验属于 **CH-07 Verify**（候选能否被批准），**不是** CH-08 **Runtime Verify**（运行态核验）。
- 夹具中的模型评审是历史冻结记录，运行时不发起任何模型或 API 调用。
- `limitation` 明确：**不证明**模型评审可以替代人工判断。

稳定归因代码：

| 代码 | 含义 |
|---|---|
| `ALIGNED_ALL` | 测试、全部模型与人工在该维度信号一致 |
| `TEST_HUMAN_DISAGREEMENT` | 测试信号与人工 Rubric 不一致 |
| `TEST_MODEL_DISAGREEMENT` | 测试信号与至少一个模型维度评审不一致 |
| `MODEL_MODEL_DISAGREEMENT` | 独立模型评审之间不一致 |
| `HUMAN_OVERRIDES_AUTOMATED` | 人工与测试+模型的一致自动化信号相反 |
| `MODEL_ONLY_RISK` | 行来自模型风险发现，而非 Rubric 维度 |
| `HUMAN_DEFERS_RISK` | 人工对模型风险行标记为 `na`（未确认） |

输入校验错误使用稳定 `E_*` 代码，例如 `E_INVALID_JSON`、`E_REQUIRED_FIELD`、`E_DUPLICATE_ID` 和 `E_EXPERIMENT_ID`。

## 环境与运行

- Python 3.9+
- 仅使用标准库
- 无网络、无模型 API、无密钥

从仓库根目录运行样例：

```bash
python3 experiments/exp-07-02/quickstart.py --sample
```

等价的显式命令：

```bash
python3 experiments/exp-07-02/quickstart.py \
  --input experiments/exp-07-02/samples/input.json \
  --output experiments/exp-07-02/output/sample.json
```

运行专项测试：

```bash
python3 -m unittest discover \
  -s experiments/exp-07-02/tests \
  -p 'test_*.py' -v
```

## 指标

- `review_agreement_rate`（评审一致率）：独立模型评审两两在 Rubric 维度上信号一致的比例（%）。
- `new_risk_count`（新增风险数）：模型风险 ID 既不在 `test_evidence.confirmed_risk_ids` 也不在 `human_rubric.acknowledged_risk_ids` 的条目数。
- `human_override_rate`（人工推翻率）：Rubric 行中触发 `HUMAN_OVERRIDES_AUTOMATED` 的比例（%）。

合法输入成功生成报告时 `valid: true`；分歧本身是预期输出，不导致命令失败。

## 样例与退出码

- `samples/input.json` 展示模型间维度分歧、人工维持通过与模型-only 新风险。
- `samples/invalid/` 包含无效 JSON、错误实验编号、空模型评审数组与重复评审者 ID。
- `output/sample.json` 是 `--sample` 的确定性输出；相同输入重复运行产生字节一致结果。
- exit `0`：输入有效且报告已写入；exit `1`：输入或文件错误（不写入输出）。
