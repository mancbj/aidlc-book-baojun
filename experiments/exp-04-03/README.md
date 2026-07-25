# EXP-04-03 · 官方 Memory Bank 结构复现

KEEP-EXT 实验：在**不访问外部网络**的前提下，用仓库内冻结 pin 夹具与最小 Memory Bank 目录树，校验官方 Memory Bank 结构是否可被新会话加载。

## 运行

从仓库根目录：

```bash
python3 experiments/exp-04-03/quickstart.py --sample
```

## 输入

`samples/input.json` 包含：

- `pinned_version`：与 `fixtures/pin/frozen-structure.json` 一致的冻结 pin
- `memory_bank_root`：相对本实验目录的 Memory Bank 根路径（样例为 `fixtures/memory-bank-min`）
- `required_paths`：最小结构必需文件列表
- `declared_references`（可选）：应存在且可解析的引用路径

## 指标

- `required_file_completeness_percent`
- `reference_validity_percent`

## 限制

输出中的 `limitation` 明确：本实验只验证冻结 pin 夹具与给定目录树，**不**验证实时 specs.md portal，也不把 specs.md 当作唯一标准。

外部来源与人工复现步骤仍以 `progress/experiments.json` 中的 `external_source`、`reproduction_steps` 为准。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-04-03/tests -p 'test_*.py' -v
```
