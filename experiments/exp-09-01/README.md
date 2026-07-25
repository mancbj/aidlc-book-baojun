# EXP-09-01 · Simple/FIRE/AI-DLC Flow 选择器

这个确定性实验根据任务复杂度、代码库状态、团队规模与合规要求，生成 Simple、FIRE 或 AI-DLC 的 Flow 建议、理由与不适用条件。只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-09-01/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-09-01/quickstart.py \
  --input experiments/exp-09-01/samples/input.json \
  --output experiments/exp-09-01/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `experiment_id`：固定为 `EXP-09-01`
- `task_name`：非空任务名称
- `task_complexity`：`low` | `medium` | `high`
- `codebase_state`：`greenfield` | `brownfield`
- `team_scale`：`small` | `medium` | `large`
- `compliance_requirements`：`none` | `moderate` | `high`

可选字段 `expert_label`（`Simple` | `FIRE` | `AI-DLC`）用于计算专家判断一致率；缺省时该指标为 `null`。

内置量表（优先级 AI-DLC > FIRE > Simple）示例：

- 低复杂度 + 绿地 + 小团队 + 无合规 → Simple
- 中等复杂度、棕地、中等合规或大型团队 → FIRE
- 高复杂度、高合规，或大型团队棕地非低复杂度 → AI-DLC

## 输出与指标

输出包含：

- `flow_recommendation`：建议 Flow（`Simple` | `FIRE` | `AI-DLC`）
- `reasons`：命中规则与选择理由
- `inapplicable_conditions`：未选 Flow 的不适用说明
- `expert_agreement_rate`：与 `expert_label` 一致时为 `100.0`，否则 `0.0`；无标签时为 `null`
- `reason_completeness_rate`：理由条目字段完整率

重要限制：Flow 建议仅依据内置确定性量表生成，不构成强制选型法令；它不证明建议已达到专家级一致，最终责任仍在人工判断。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误
- `E_INVALID_FIELD`：必填字符串缺失或为空
- `E_INVALID_ENUM`：枚举字段取值非法

其他校验错误也使用稳定代码，例如 `E_EXPERIMENT_ID`、`E_INVALID_ROOT` 和 `E_INPUT_NOT_FOUND`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-09-01/tests -p 'test_*.py' -v
```

测试验证 Flow 建议、理由、不适用条件、两类指标、三类失败输入、`--sample` 与重复运行的字节级确定性。
