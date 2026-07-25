# EXP-02-02 · 反向对话澄清收益实验

这个确定性实验对同一模糊需求的两组**冻结会话**（直接实现 vs 先澄清再实现）做对照：汇总需求决策日志、实现差异报告与指标。只使用 Python 标准库，不联网，不调用外部模型 API。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-02-02/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-02-02/quickstart.py \
  --input experiments/exp-02-02/samples/input.json \
  --output experiments/exp-02-02/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `ambiguous_requirement`：同一模糊需求描述
- `sessions.no_clarify` 与 `sessions.with_clarify`：两组冻结会话，各含
  - `clarification_rounds`（无澄清臂必须为 0，澄清臂必须 ≥ 1）
  - `session_transcript`（可选，非空时校验 role/content）
  - `decision_log`
  - `post_impl_requirement_changes`
  - `critical_omissions`
  - `implemented_items`（用于实现差异对照）

## 输出与指标

输出包含：

- `decision_log_by_arm`：两组会话的需求决策日志；
- `implementation_difference_report`：共享实现、各臂独有实现及独有项计数；
- `metrics.by_arm`：`clarification_rounds`、`post_impl_requirement_change_count`、`critical_omission_count`；
- `metrics.delta_no_clarify_minus_with_clarify`：上述两项指标的 no_clarify − with_clarify 差值。

重要限制：对照报告只反映输入中冻结会话的确定性差分；**它不证明澄清提问总能减少实现后需求变更**（样例中澄清臂可能遗漏更少，但实现后变更数仍可能更高）。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_MISSING_SESSION_ARM`：缺少 `no_clarify` 或 `with_clarify` 会话臂；
- `E_INVALID_CLARIFICATION_ROUNDS`：澄清轮次与臂类型不一致。

其他校验错误也使用稳定代码，例如 `E_DUPLICATE_ID`、`E_INVALID_FIELD` 和 `E_EXPERIMENT_ID`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-02-02/tests -p 'test_*.py' -v
```

测试验证决策日志、实现差异、各臂与差值指标、三类失败输入、`--sample` 和重复运行的字节级确定性。
