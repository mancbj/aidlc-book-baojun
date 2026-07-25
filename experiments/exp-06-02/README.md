# EXP-06-02 · 失败—修复—复测闭环记录器

> 根据失败日志、修复提交与测试结果，生成按时间排序的确定性修复证据链。

## 目的

实验把三类输入按 ID 与时间戳链接：

1. `failures`：失败日志条目；
2. `commits`：修复提交；
3. `tests`：复测结果。

输出 `evidence_chain` 即“失败 → 修复 → 复测”证据链。每一轮保留失败、关联提交、关联测试与稳定链接代码。

## 链接规则

- 证据链按 `failures` 的 `timestamp`、`id` 升序排列。
- 修复提交：优先匹配 `failure_id` 相同的提交；否则选取时间晚于失败且未绑定 `failure_id` 的最早提交。
- 复测：在已匹配修复提交之后，优先匹配 `commit_id` 相同的测试；否则匹配相同 `failure_id` 的测试。

稳定链接代码：

| 代码 | 含义 |
|---|---|
| `MISSING_FIX_COMMIT` | 未找到可关联的修复提交 |
| `MISSING_RETEST` | 有修复提交但未找到复测 |
| `CHAIN_COMPLETE` | 失败、修复与复测均已关联 |

输入校验错误也使用稳定代码，例如 `E_INVALID_JSON`、`E_REQUIRED_FIELD`、`E_DUPLICATE_ID`、`E_UNKNOWN_FAILURE_ID` 和 `E_EXPERIMENT_ID`。

## 环境与运行

- Python 3.9+
- 仅使用标准库
- 无网络、无模型 API、无密钥

从仓库根目录运行样例：

```bash
python3 experiments/exp-06-02/quickstart.py --sample
```

等价的显式命令：

```bash
python3 experiments/exp-06-02/quickstart.py \
  --input experiments/exp-06-02/samples/input.json \
  --output experiments/exp-06-02/output/sample.json
```

运行专项测试：

```bash
python3 -m unittest discover \
  -s experiments/exp-06-02/tests \
  -p 'test_*.py' -v
```

## 指标

- `repair_round_count`（修复轮次）：成功关联到修复提交的失败数。
- `regression_pass_rate`（回归通过率）：已关联复测中 `passed=true` 的比例（百分比，保留两位小数）。
- `evidence_completeness_percent`（证据完整率）：同时关联修复提交与复测的失败数 / 失败总数。

## 局限

`evidence_completeness_percent` 只表示证据是否齐全，**不等于**修复质量或一次通过优于多轮修复。详见输出中的 `limitation` 字段。

## 样例与退出码

- `samples/input.json` 展示完整闭环、回归失败与证据缺失三种情形。
- `samples/invalid/` 包含无效 JSON、缺少 failures、重复失败 ID、错误实验编号与未知失败引用。
- `output/sample.json` 是 `--sample` 的确定性输出；相同输入重复运行产生字节一致结果。
- exit `0`：输入有效并生成报告；exit `1`：输入或文件错误。
