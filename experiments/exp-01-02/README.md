# EXP-01-02 · AI-Assisted 与 AI-Driven 对照实验

这个确定性实验读取同一小型功能的**冻结**两套工作流交付记录（AI-Assisted 对话式生成 vs AI-DLC 闭环），生成并排对照报告与指标差分。它只使用 Python 标准库，不联网，不调用任何模型 API。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-01-02/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-01-02/quickstart.py \
  --input experiments/exp-01-02/samples/input.json \
  --output experiments/exp-01-02/output/sample.json
```

## 输入

输入 JSON 必须包含：

- `experiment_id`：`EXP-01-02`
- `feature`：`id`、`name`、`intent_summary`
- `workflow_records`：恰好两条记录，分别对应 `ai_assisted` 与 `ai_driven`

每条交付记录包含：

- `record_id`
- `human_roundtrips`（非负整数）
- `escaped_defects`（非负整数）
- `elapsed_minutes`（正数，端到端耗时）
- `evidence_links`（非空字符串数组，证据链引用）

## 输出与指标

输出包含：

- `comparison`：两套工作流的并排交付摘要与 `evidence_links`；
- `metrics.ai_assisted` / `metrics.ai_driven`：各自的 `human_roundtrips`、`escaped_defects`、`end_to_end_minutes`；
- `metrics.delta`：`human_roundtrip_delta`、`escaped_defect_delta`、`end_to_end_minutes_delta`（均为 AI-Driven 减 AI-Assisted）。

重要限制：对照报告只汇总输入中的冻结记录；**它不证明**某一工作流在全部团队、任务或约束下更优。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_EXPERIMENT_ID`：`experiment_id` 不匹配；
- `E_DUPLICATE_WORKFLOW_MODE`：重复的 `workflow_mode`。

其他校验错误也使用稳定代码，例如 `E_INVALID_FIELD`、`E_INVALID_NUMBER`、`E_MISSING_WORKFLOW_MODE` 和 `E_REQUIRED_COLLECTION`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-01-02/tests -p 'test_*.py' -v
```

测试验证对照报告、三类指标与差分、三类失败输入、`--sample` 和重复运行的字节级确定性。
