# EXP-03-01 输出证据

本目录保存 D05-T02 生成的成功与失败样例结果。所有报告均由 `experiments/sample/quickstart.py` 从 `samples/` 输入实际生成，不手写。

## 成功样例

命令：

```bash
python3 experiments/sample/quickstart.py \
  --input experiments/sample/samples/input.json \
  --output experiments/sample/output/sample.json
```

结果：

| 文件 | 退出码 | valid | 指标 |
|---|---:|---|---|
| `sample.json` | `0` | `true` | coverage `100.0`；orphan stories `0`；acceptance `100.0`；invalid refs `0` |

稳定性证据：

- `sample.json` SHA-256：`9e2d9611ea47e0b8a9a36a6a0581c06b934cb8dd893f6d11a52ca8b36bbcab0a`
- 相同输入重复运行后输出字节一致。

## 失败样例

五个坏样例均预期以 exit `2` 结束，并写入 `valid: false` 报告。

| 输入 | 输出 | 主要错误代码 | 失败含义 |
|---|---|---|---|
| `samples/invalid/missing-nfr.json` | `invalid/missing-nfr.json` | `E_MISSING_NFR` | 缺少 non-functional Requirement |
| `samples/invalid/duplicate-id.json` | `invalid/duplicate-id.json` | `E_DUPLICATE_ID` | 同类对象 ID 重复 |
| `samples/invalid/unknown-reference.json` | `invalid/unknown-reference.json` | `E_UNKNOWN_REF` | Unit 或 Story 指向未知 ID |
| `samples/invalid/orphan-story.json` | `invalid/orphan-story.json` | `E_ORPHAN_STORY` | Story 没有可贯通的 Unit → Requirement 上游路径 |
| `samples/invalid/empty-acceptance.json` | `invalid/empty-acceptance.json` | `E_ACCEPTANCE` | Story 验收为空 |

## 测试命令

```bash
python3 -m unittest discover \
  -s experiments/sample/tests \
  -p 'test_*.py'
```

D05-T02 运行结果：4 tests passed。

## 边界

`valid: true` 只表示结构追踪、引用和验收字段满足实验合同；它不证明需求语义正确，也不替代作者对 Intent、Requirement 和 Story 内容的判断。
