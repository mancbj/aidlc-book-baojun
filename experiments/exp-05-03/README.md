# EXP-05-03 · 官方 Bolt 类型检查点复现

对照 **冻结 pin** 的 Bolt 类型检查点指南（Simple / DDD 两轨阶段定义），核对输入中的两条 `stage_records` 是否满足阶段完整率与检查点遵循率。仅使用 Python 标准库，**不联网**，不调用外部模型。

## 目的

1. 加载仓库内 `fixtures/bolt_type_checkpoint_guide.json`（登记 pin：`sha256:32d73fc5…`）；
2. 校验输入 `pinned_version` 与指南 pin 一致；
3. 分别评估 Simple 与 DDD 对照任务的阶段完整率、检查点遵循率；
4. 输出总体指标（两轨算术平均）与各轨明细。

## 指标

| 字段 | 含义 |
|---|---|
| `metrics.stage_completeness_percent` | Simple 与 DDD 两轨 **必需阶段** 完成率（%）的算术平均 |
| `metrics.checkpoint_adherence_percent` | 两轨 **必需阶段** 上 `human_validation` 等登记检查点遵循率（%）的算术平均 |
| `tracks.<simple\|ddd>.stage_completeness_percent` | 单轨必需阶段完成率 |
| `tracks.<simple\|ddd>.checkpoint_adherence_percent` | 单轨必需阶段检查点遵循率 |

DDD 轨中 `adr-analysis` 为可选阶段，不计入必需阶段完整率分母；未出现在记录中视为跳过。

## 运行

Python 3.9+：

```bash
python3 experiments/exp-05-03/quickstart.py --sample
```

```bash
python3 experiments/exp-05-03/quickstart.py \
  --input experiments/exp-05-03/samples/input.json \
  --output experiments/exp-05-03/output/sample.json
```

## 输入

- `experiment_id`：`EXP-05-03`
- `pinned_version`：必须与实验登记及冻结指南一致
- `stage_records.simple` / `stage_records.ddd`：各含 `bolt_id` 与 `stages[]`（`stage_id`、`status`、`checkpoints[]`）

## 稳定错误代码

- `E_INVALID_JSON` / `E_INPUT_NOT_FOUND` / `E_INPUT_READ`
- `E_EXPERIMENT_ID` / `E_INVALID_ROOT` / `E_PIN_MISMATCH`
- `E_MISSING_TRACK` / `E_UNKNOWN_TRACK` / `E_UNKNOWN_STAGE`
- `E_MISSING_CHECKPOINT` / `E_DUPLICATE_STAGE` / `E_INVALID_ENUM` / `E_INVALID_FIELD`

## 边界

`limitation` 字段明确：**冻结指南复现不等于唯一标准；不替代人工 Bolt 类型选择**。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-05-03/tests -p 'test_*.py' -v
```
