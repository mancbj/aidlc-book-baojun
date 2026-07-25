# EXP-08-01 · 发布候选来源清单校验器

> 校验 readiness 来源、必需 manifest 资产与 sha256 格式是否一致，输出可追溯校验报告。

## 目的

实验把发布候选核对建模为确定性 JSON 输入：

1. `readiness`：`status` 与 `source_id`；
2. `expected_source_id`：候选必须对齐的事实源；
3. `required_assets`：manifest 必须覆盖的资产名称；
4. `candidate_assets`：每项含 `name`、`sha256`、`bytes`。

输出报告包含 `source_completeness_percent` 与 `hash_mismatch_count`，并声明 **limitation**：不证明生产可观测成熟。

本实验 **ALREADY** 复用仓库内 `scripts/check_release_readiness.py` 与 `scripts/prepare_release.py` 所代表的发布 readiness / manifest 思路；合同 quickstart 提供可执行、无网络的独立校验面。

## 校验规则

- `readiness.source_id` 必须等于 `expected_source_id`，否则 `E_SOURCE_MISMATCH`。
- `required_assets` 中每个名称必须出现在 `candidate_assets`，否则 `E_MISSING_ASSET`。
- 每个 `candidate_assets.sha256` 必须为 `sha256:<64 位小写十六进制>`，否则 `E_INVALID_HASH`。
- `source_completeness_percent = 100 × (来源一致 + 已覆盖必需资产数) / (1 + 必需资产数)`。

## 环境与运行

- Python 3.9+
- 仅标准库
- 无网络

```bash
python3 experiments/exp-08-01/quickstart.py --sample
```

```bash
python3 experiments/exp-08-01/quickstart.py \
  --input experiments/exp-08-01/samples/input.json \
  --output experiments/exp-08-01/output/sample.json
```

```bash
python3 -m unittest discover \
  -s experiments/exp-08-01/tests \
  -p 'test_*.py' -v
```

## 指标

| 指标 | 含义 |
|---|---|
| `source_completeness_percent` | 来源一致性与必需 manifest 资产覆盖率 |
| `hash_mismatch_count` | `candidate_assets` 中 sha256 格式无效的数量（合法样例为 0） |
