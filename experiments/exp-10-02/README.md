# EXP-10-02 · AI-DLC 价值记分卡

这个确定性实验将交付基线、AI-DLC 运行记录、缺陷与业务结果汇总为试点价值记分卡，并给出扩大／收缩／停用（expand／shrink／stop）建议。它只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-10-02/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-10-02/quickstart.py \
  --input experiments/exp-10-02/samples/input.json \
  --output experiments/exp-10-02/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `experiment_id`：`EXP-10-02`
- `pilot_name`
- `delivery_baseline`：`median_cycle_time_hours`（正数）、`human_review_minutes_per_delivery`（非负数）
- 非空的 `aidlc_runs`（每项含 `id`、`cycle_time_hours`、`human_review_minutes`）
- 可选 `defects`（每项含 `id`、`run_id`、`escaped` 布尔值；`run_id` 必须引用已声明运行）
- 可选 `business_outcomes`：`baseline_value` 与 `current_value` 必须同时提供，或整段省略／为 `null`

## 输出与指标

输出包含四维 `scorecard`（周期、质量、审阅负担、业务结果）、汇总 `metrics` 与 `scale_decision`：

| 指标字段 | 含义 | 空值规则 |
|---|---|---|
| `cycle_time_change_percent` | 运行周期中位数相对基线的百分比变化 | 始终计算 |
| `defect_escape_rate` | 逃逸缺陷数／交付次数（运行条数） | 无缺陷时为 `0` |
| `human_review_burden` | 观测平均审阅分钟／基线审阅分钟 | 基线为 `0` 时输出绝对平均分钟 |
| `business_result_change` | 业务结果百分比变化 | 未提供业务输入时为 `null` |

重要限制：记分卡让周期、质量、注意力与业务信号可并排比较；**它不证明某次试点的业务价值已被因果证实**。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_REQUIRED_COLLECTION`：例如 `aidlc_runs` 为空；
- `E_UNKNOWN_RUN`：缺陷引用未声明的运行 ID；
- `E_INVALID_NUMBER`：基线或运行数值非法。

其他校验错误也使用稳定代码，例如 `E_DUPLICATE_ID`、`E_INVALID_FIELD`、`E_EXPERIMENT_ID` 与 `E_INCOMPLETE_BUSINESS`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-10-02/tests -p 'test_*.py' -v
```

测试验证记分卡四维、四个指标、规模决策、四类失败输入、`--sample` 与重复运行的字节级确定性。
