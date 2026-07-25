# Round 02 · EXP-03-02 Contract and Samples

**Decision:** KEEP

## 变更

- 固化 `experiments/exp-03-02/samples/input.json`
- 增加失败样例：cycle / duplicate-id / unknown-bolt / unknown-unit
- 明确指标：`cycle_count`、`cross_unit_coupling_edge_count`、`unmet_prerequisite_count`
- 边界：`structural_valid` 与 `plan_optimal` 分离

## 评分增量

实验合同与样例齐备，实现验证见 Round 03。
