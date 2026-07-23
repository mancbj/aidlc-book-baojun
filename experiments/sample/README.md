# EXP-03-01 · Intent 到 Story 追踪链生成器

> **状态：VERIFIED**  
> 本目录由 D04-T02 建立结构；D05-T01 已实现 `quickstart.py`，D05-T02 已保存成功/失败样例并补齐单元测试。

## 实验目的

读取一份由 AI 或人提出的 Inception 候选分解，确定性检查 `Intent → Requirements → Units → Stories` 的结构追踪性，并输出：

- Requirement 到 Unit、Story 的双向链路；
- 需求覆盖率；
- 孤立 Story 数；
- 验收完整率；
- 无效引用数及稳定错误代码。

它只证明结构引用和验收字段完整，不证明业务语义正确。最终判断仍由人负责。

完整实验合同见 [planning/sample-experiment.md](../../planning/sample-experiment.md)。

## 环境

- Python 3.9+
- 只使用标准库
- 不联网
- 不需要模型 API、Token 或其他密钥
- 不读取作者本地 `specs.md-portal/`

[`env.example`](env.example) 只记录“无环境变量依赖”的边界，不包含秘密或占位密钥。运行实验不需要复制为 `.env`。

## 目录骨架

```text
experiments/sample/
├── README.md                       # 当前文件：目标、接口和状态
├── env.example                     # 无密钥、无环境变量声明
├── samples/
│   ├── README.md                   # 样例职责与失败夹具清单
│   └── input.json                  # 合法候选分解输入
├── output/
│   ├── sample.json                 # D05-T01 已由命令生成
│   ├── README.md                   # D05-T02 保存成功/失败说明
│   └── invalid/                    # D05-T02 生成的五类失败报告
├── tests/
│   └── test_demo.py                # D05-T02 验证合同与确定性
└── quickstart.py                   # D05-T01 实现
```

当前实现已经包含最小可运行路径、失败夹具、输出证据和自动测试。

## 输入

合法样例路径：[`samples/input.json`](samples/input.json)

输入必须包含：

1. 一个带结果和约束的 Intent；
2. 至少一个 functional 与一个 non-functional Requirement；
3. 至少一个引用已知 Requirement 的 Unit；
4. 至少一个引用已知 Unit、Requirement 且带二元验收的 Story。

输入是结构化候选分解，不是自然语言 Prompt。实验不会调用模型替读者生成需求。

## 输出

生成路径：`experiments/sample/output/sample.json`

输出合同：

```json
{
  "schema_version": "1.0.0",
  "experiment_id": "EXP-03-01",
  "source_digest": "sha256:<canonical-input-hash>",
  "valid": true,
  "metrics": {
    "requirement_coverage_percent": 100.0,
    "orphan_story_count": 0,
    "acceptance_completeness_percent": 100.0,
    "invalid_reference_count": 0
  },
  "traces": [],
  "errors": []
}
```

`output/sample.json` 是由 `samples/input.json` 实际生成的结果，不手写。相同输入的重复运行应得到字节一致输出。

## 运行命令

从仓库根目录运行：

```bash
python3 experiments/sample/quickstart.py \
  --input experiments/sample/samples/input.json \
  --output experiments/sample/output/sample.json
```

合法样例预期以 exit `0` 结束，并生成 `valid: true`、四项指标为 `100.0 / 0 / 100.0 / 0` 的报告。

## 失败样例接口

计划目录：`experiments/sample/samples/invalid/`

| 文件 | 稳定错误代码 | 责任任务 |
|---|---|---|
| `missing-nfr.json` | `E_MISSING_NFR` | D05-T02 已完成 |
| `duplicate-id.json` | `E_DUPLICATE_ID` | D05-T02 已完成 |
| `unknown-reference.json` | `E_UNKNOWN_REF` | D05-T02 已完成 |
| `orphan-story.json` | `E_ORPHAN_STORY` | D05-T02 已完成 |
| `empty-acceptance.json` | `E_ACCEPTANCE` | D05-T02 已完成 |

## 测试接口

运行：

```bash
python3 -m unittest discover \
  -s experiments/sample/tests \
  -p 'test_*.py'
```

测试必须覆盖合法输入、五类坏样例、退出码和相同输入的字节级确定性。

## 状态门禁

| 阶段 | 当前状态 | 进入下一阶段的条件 |
|---|---|---|
| 实验合同 | 完成 | `planning/sample-experiment.md` 字段齐全 |
| Demo 骨架 | 完成 | README、`env.example`、合法输入与输出路径明确 |
| 最小实现 | 完成 | `quickstart.py` 可生成稳定 `output/sample.json` |
| 结果与测试 | 完成 | D05-T02 已保存成功/失败证据并通过测试 |
| `verified` | 达到 | 实验合同的六项二元验收全部满足 |

事实状态以 `progress/experiments.json` 为准。当前 `EXP-03-01` 已达到 `verified`。
