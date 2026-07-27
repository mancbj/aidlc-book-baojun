# WORKING-WITH-AIDLC 与本书章节映射

> 操作指南全文见 [mancbj/aidlc-workflows · WORKING-WITH-AIDLC.md](https://github.com/mancbj/aidlc-workflows/blob/main/docs/WORKING-WITH-AIDLC.md)。  
> 本书仅摘要 + 链接，不复制该文档大段正文。

## 何时读哪份材料

| 你的目标 | 先读 | 再读 |
| --- | --- | --- |
| 理解「为什么重构 SDLC」 | 本书 CH-01、Part 0 | AWS [方法定义](https://prod.d13rzhkk8cj2z0.amplifyapp.com) 第二节原则 |
| 在仓库里跑通一次 Bolt | WORKING-WITH-AIDLC | 本书 CH-03–06 + 本映射表 |
| 组织级 Mob 与度量 | 本书 CH-10 | AWS 博文 + 白皮书 Adoption 节 |

## 概念映射（摘要级）

| WORKING-WITH-AIDLC 主题（摘要） | 本书章节 | 本书中的对应概念 |
| --- | --- | --- |
| Question → Doc → Approval | CH-02、CH-04 | Human Checkpoint、Memory Bank、Standards |
| Never Vibe Code | CH-04、CH-06 | 无批准计划不 Execute；Walkthrough 交接 |
| 阶段门控 / 清理 context | CH-04 | Update Protocol、新会话冷启动 |
| Vision + Tech Environment 双输入 | CH-03 | Intent + System Context |
| Inception 计划 md（批准后再做） | CH-03 | Bolt Plan、Human Checkpoints |
| Construction 两段式（plan → codegen） | CH-06 | Plan / Execute 分离 |
| `aidlc-docs/` 目录约定 | CH-04 | 本书用 `progress/`、`memory-bank/` 等事实源（结构可不同，原则相同） |
| Mob Elaboration / Mob Construction | CH-02、CH-03、CH-10 | 反向对话、Inception 仪式、协作节奏 |

## AWS 官方白皮书（Amplify）映射

| 白皮书节（摘要） | 本书落点 |
| --- | --- |
| II · Key Principles（十条） | CH-01 §2.5 |
| III · Artefacts（Intent/Unit/Bolt 等） | CH-03、CH-05 |
| III · Phases & Rituals | Part 0、CH-03、CH-06、CH-08 |
| IV–V · Green/Brown-field | CH-09（Flow 选型）；棕场建模见 CH-06 摘要 |
| VI · Adopting AI-DLC | CH-10 §2.4 |

## 证据边界（必读）

- 本书框架 `𝓔 = Engineering with Exsecutio` **不等于** AWS 官方唯一标准。
- specs.md、aidlc-workflows 为**参考实现/操作指南**；实验 triage（SHIP / KEEP-EXT / ALREADY）不因官方材料而改写。
- Operations Agent 与 AWS Deployment Units 描述**不得**被理解为本书或 specs.md 已具备同等成熟度的生产工具链。
