# EXP-05-02 · DDD 与 Simple Bolt 选择器

这个确定性实验根据任务描述、领域复杂度、风险与可逆性，生成 Simple 或 DDD 的 Bolt 类型建议、选择依据，并在灰区给出拆分或门禁建议。只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-05-02/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-05-02/quickstart.py \
  --input experiments/exp-05-02/samples/input.json \
  --output experiments/exp-05-02/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `experiment_id`：固定为 `EXP-05-02`
- `task_description`：非空任务描述
- `domain_complexity`：`low` | `medium` | `high`
- `risk`：`low` | `medium` | `high`
- `reversibility`：`easy` | `moderate` | `hard`

可选字段：

- `cross_boundary_risk`：布尔值，默认 `false`
- `expert_label`：`Simple` | `DDD`，用于专家一致率与过度/不足工程化计数；缺省时一致率为 `null`

内置量表（优先级 DDD 强信号 > Simple 低仪式 > 灰区评分）示例：

- 低领域复杂度 + 低风险 + 易回退且无跨边界 → Simple
- 高领域复杂度、高风险、难回退或跨边界风险 → DDD
- 中间灰区 → 给出拆分或门禁建议，并按评分倾向 Simple 或 DDD

## 输出与指标

输出包含：

- `bolt_type_recommendation`：建议类型（`Simple` | `DDD`）
- `selection_rationale`：命中规则与选择理由
- `gray_zone` / 可选 `gray_zone_advice`：灰区标记与拆分或门禁建议
- `expert_agreement_rate`：与 `expert_label` 一致时为 `100.0`，否则 `0.0`；无标签时为 `null`
- `over_engineering_count` / `under_engineering_count`：相对专家标签的过度或不足工程化计数（无标签时为 `0`）

重要限制：Bolt 类型建议仅依据内置确定性量表生成；它不证明建议已达到专家级一致，也不能替代人工判断与领域评审。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误
- `E_INVALID_FIELD`：必填字符串缺失或为空
- `E_INVALID_ENUM`：枚举字段取值非法

其他校验错误也使用稳定代码，例如 `E_EXPERIMENT_ID`、`E_INVALID_ROOT` 和 `E_INPUT_NOT_FOUND`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-05-02/tests -p 'test_*.py' -v
```

测试验证 Bolt 建议、理由、灰区建议、三类指标、三类失败输入、`--sample` 与重复运行的字节级确定性。
