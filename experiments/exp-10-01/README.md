# EXP-10-01 · 人–Agent 责任 RACI 生成器

这个确定性实验将研发活动、四类 Agent 与团队角色转换为 RACI 矩阵（Responsible / Accountable / Consulted / Informed）。它只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-10-01/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-10-01/quickstart.py \
  --input experiments/exp-10-01/samples/input.json \
  --output experiments/exp-10-01/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `project_name`
- 恰好四类的 `agents`（`master`、`inception`、`construction`、`operations`）
- 非空的 `team_roles`（人类角色）
- 非空的 `development_activities`

每个活动通过 `pattern_id` 命中内置模板（路由、分解、执行、发布、独立评审等），并声明 `accountable_role`（可为 `null` 表示尚未归属）。可选字段 `additional_accountable_roles`、`consulted_roles`、`informed_roles` 与 `responsible_agents` 覆盖默认 Responsible / Consulted / Informed。

硬规则：**Accountable 必须为人类角色，不得为 Agent**；Agent 可以担任 Responsible。

## 输出与指标

输出包含：

- `raci_matrix`：每个活动的 RACI 分配、Accountable 状态与冲突代码；
- `participants`：人类角色与四类 Agent 的清单；
- `unassigned_accountable_decisions_count`：缺少 Accountable 的活动数；
- `responsibility_conflict_count`：存在冲突代码（例如多个 Accountable）的活动数。

重要限制：本工具只让无负责人决策与责任冲突可见；它不证明生成的 RACI 已适合所有组织。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_REQUIRED_COLLECTION`：必需集合缺失或为空；
- `E_UNKNOWN_ROLE`：活动引用未声明团队角色；
- `E_ACCOUNTABLE_AGENT`：Accountable 引用了 Agent。

其他校验错误也使用稳定代码，例如 `E_DUPLICATE_ID`、`E_INVALID_FIELD`、`E_EXPERIMENT_ID` 与 `E_AGENT_SET`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-10-01/tests -p 'test_*.py' -v
```

测试验证 RACI 矩阵、Accountable 硬规则、两个指标、四类失败输入、`--sample` 和重复运行的字节级确定性。
