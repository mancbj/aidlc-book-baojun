# Round 01 · Verified Experiment Governance

**Decision:** KEEP

## 目标

让 `verified` / `in-progress` SHIP 的声明路径成为事实门禁，并让所有 verified SHIP 的合同测试进入核心 CI。

## 变更

- `scripts/run_verified_experiments.py`
  - 读取 `progress/experiments.json`
  - 检查 verified SHIP 工件
  - 执行每个 `test_path`
- `scripts/ci_check.py`
  - 增加 `verified-experiments` 阶段
- 增加对应单元测试

## 评分

- Experiments: 12 / 35
- SVG: 3 / 30
- Reader feedback: 5 / 15
- Book integration: 9 / 10
- Release: 2 / 10
- **Total: 31 / 100**

下一轮：EXP-03-02 的数据合同、合法样例与失败样例。
