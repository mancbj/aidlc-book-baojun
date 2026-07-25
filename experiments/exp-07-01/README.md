# EXP-07-01 · 仓库确定性门禁组合器

> **ALREADY** 实验：合同化证明 `scripts/ci_check.py` 聚合了仓库 Must 确定性检查，而不是重新实现一套 CI。

## 目的

输入 `expected_checks` 与从 `scripts/ci_check.py` **静态解析**出的 `configured_checks` 对照，输出：

- `configured_check_count` / `passed_check_count` / `failed_check_count`
- `missing_checks` / `extra_checks`
- `reused_implementation` 指向既有组合器

默认 **composition** 模式只解析源码，不执行完整 `ci_check`（避免合同测试过慢）。可选 `--live` 会实际运行 `scripts/ci_check.py`；**合同测试不得使用 `--live`**。

## 边界与限制

- **证明**：Must 门禁可被单一入口稳定组合与复用（CH-04 / CH-06 / CH-08 交叉引用）。
- **不证明**：书稿内容质量、读者理解、模型输出正确性或生产运行态。
- 报告中的 `limitation` 字段重复声明上述边界。

## 环境与运行

- Python 3.9+
- 标准库；composition 模式无子进程（`--live` 除外）

```bash
# 生成仓库内样例报告
python3 experiments/exp-07-01/quickstart.py --sample

# 自定义输入/输出
python3 experiments/exp-07-01/quickstart.py \
  --input experiments/exp-07-01/samples/input.json \
  --output /tmp/exp-07-01-report.json

# 合同测试
python3 experiments/exp-07-01/tests/test_demo.py
```

## 输入

| 字段 | 说明 |
|---|---|
| `experiment_id` | 必须为 `EXP-07-01` |
| `expected_checks` | 非空、无重复的门禁名称列表 |

## 输出

| 字段 | 说明 |
|---|---|
| `valid` | 期望列表与解析配置完全一致时为 `true` |
| `configured_checks` | 自 `ci_check.py` 解析的核心门禁顺序 |
| `composition` | `missing_checks` / `extra_checks` 及计数指标 |
| `metrics` | 与 `composition` 对齐的三项计数 |

稳定错误码：`E_INVALID_JSON`、`E_EXPERIMENT_ID`、`E_REQUIRED_FIELD`、`E_REQUIRED_COLLECTION`、`E_DUPLICATE_ID`、`E_COMPOSITION_MISMATCH`。
