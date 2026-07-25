# EXP-09-02 · 风险到检查点预算模拟器

这个确定性实验根据风险清单、可逆性、影响范围与自治偏好，生成检查点数量、位置建议与成本收益估算。只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-09-02/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-09-02/quickstart.py \
  --input experiments/exp-09-02/samples/input.json \
  --output experiments/exp-09-02/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `experiment_id`：固定为 `EXP-09-02`
- `task_name`：非空任务名称
- `risks`：非空数组；每项含唯一 `id`、非空 `statement`、`severity`（`critical` | `major` | `minor`）、`phase`（`design` | `implement` | `verify` | `release`）
- `reversibility`：`high` | `medium` | `low`
- `impact_scope`：`local` | `team` | `organization` | `external`
- `autonomy_preference`：`minimal` | `balanced` | `maximal`

内置加权规则（确定性）示例：

- 所有 `critical` 风险在其 `phase` 强制检查点（`R-CP-MANDATORY-CRITICAL`）
- `major` 风险在可逆性低、影响面达 team 及以上，或自治偏好 minimal 时加闸门（`R-CP-MAJOR-GUARDRAIL`）
- `minimal` 自治 + 低可逆性时为 `minor` 风险加确认点（`R-CP-MINOR-GUARDRAIL`）
- 上下文基线：`minimal` 设计对齐、`balanced` 实施中期同步、低可逆性验证回滚、organization/external 发布闸门

## 输出与指标

输出包含：

- `checkpoint_count` 与 `checkpoint_placements`：检查点数量与位置建议（含 `rule_id`、触发与确认内容）
- `cost_benefit_estimate`：预计审阅成本（小时）、风险削减得分与收益成本比
- `metrics.critical_risk_coverage_percent`：关键风险被检查点覆盖的比例
- `metrics.nonessential_checkpoint_count`：非必要（非关键风险闸门）检查点数
- `metrics.estimated_review_cost`：预计审阅成本（小时，与成本收益块一致）

重要限制：检查点预算仅依据内置确定性加权规则生成，不构成强制治理法令；它不证明所有风险都能被预算公式穷尽，未建模风险仍需人工补充。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误
- `E_INVALID_FIELD`：必填字符串缺失或为空
- `E_INVALID_ENUM`：枚举字段取值非法
- `E_REQUIRED_COLLECTION`：`risks` 缺失或为空

其他校验错误也使用稳定代码，例如 `E_EXPERIMENT_ID`、`E_INVALID_ROOT`、`E_DUPLICATE_ID` 和 `E_INPUT_NOT_FOUND`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-09-02/tests -p 'test_*.py' -v
```

测试验证检查点预算、成本收益、三类指标、三类失败输入、`--sample` 与重复运行的字节级确定性。
