# EXP-02-01 · 不可委托判断清单生成器

这个确定性实验将项目目标、风险、约束和责任角色转换为“人类判断点与责任边界清单”。它只使用 Python 标准库，不联网，也不需要密钥。

## 运行

要求 Python 3.9+。从仓库根目录运行样例：

```bash
python3 experiments/exp-02-01/quickstart.py --sample
```

或指定路径：

```bash
python3 experiments/exp-02-01/quickstart.py \
  --input experiments/exp-02-01/samples/input.json \
  --output experiments/exp-02-01/output/sample.json
```

## 输入与规则

输入 JSON 必须包含：

- `project_name`
- 非空的 `goals`、`risks`、`constraints`
- 非空的 `responsibility_roles`

每个目标、风险和约束会分别命中固定规则 `GOAL_APPROVAL`、`RISK_ACCEPTANCE`、`CONSTRAINT_EXCEPTION`。`owner_role` 可为 `null`，表示该判断点尚未归属；非空值必须引用已声明角色。

## 输出与指标

输出包含：

- `human_judgment_checkpoints`：需要人最终决定的事项、来源及 AI 不得越过的边界；
- `responsibility_boundaries`：角色声明边界及其负责的判断点；
- `judgment_point_coverage_percent`：命中内置规则的输入条目数 / 候选输入条目数；
- `unassigned_responsibility_count`：未指定责任角色的判断点数量。

重要限制：判断点覆盖率只是规则覆盖率，表示输入条目命中了本工具的三条内置规则；它不证明已发现或覆盖项目中的全部不可委托判断。

## 稳定错误代码

失败时程序返回 exit `1`，向标准错误输出 `[ERROR <code>]`，且不生成报告。样例覆盖：

- `E_INVALID_JSON`：JSON 语法错误；
- `E_REQUIRED_COLLECTION`：必需集合缺失或为空；
- `E_UNKNOWN_ROLE`：条目引用未声明角色。

其他校验错误也使用稳定代码，例如 `E_DUPLICATE_ID`、`E_INVALID_FIELD` 和 `E_EXPERIMENT_ID`。

## 测试

```bash
python3 -m unittest discover -s experiments/exp-02-01/tests -p 'test_*.py' -v
```

测试验证清单、责任边界、两个指标、三类失败输入、`--sample` 和重复运行的字节级确定性。
