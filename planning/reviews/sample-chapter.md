# 样章第一轮审校

> D12-T01 产物：对 CH-03《Inception：从 Intent 到可执行计划》完成第一轮五类审校。  
> 样章路径：[`book/chapters/sample.md`](../../book/chapters/sample.md)  
> 审校时间：2026-07-23T03:51:08Z  
> 结论：第一轮审校通过；保留非阻断改进建议。

## 审校范围

- 章节：`CH-03`
- 关联实验：`EXP-03-01`
- 关联样例输出：[`experiments/sample/output/sample.json`](../../experiments/sample/output/sample.json)
- 关联实验说明：[`planning/sample-experiment.md`](../sample-experiment.md)
- 章节事实源：[`progress/chapters.json`](../../progress/chapters.json)
- 当前样章长度：约 7950 个字符

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：正文在实验段落中使用 `valid: true` 和四项 100% 指标，容易被匆忙读者误读为“业务语义正确”。
- 影响：如果读者把结构追踪实验当作语义正确性证明，会高估自动化门禁能力，削弱本书“人类判断仍需保留”的核心立场。
- 建议：保留并强化第 04 节已经写出的边界句：“这四个数字只证明结构，不证明语义。”后续二轮润色时，可在表格后增加一句“语义判断必须由 Human Checkpoint 完成”。
- 对应文件：[`book/chapters/sample.md`](../../book/chapters/sample.md)，第 112–145 行。
- 决策：本轮不阻断。正文已经明确“不调用模型、不联网、不判断业务语义”，且实验说明中也声明结构校验边界。
- 负责人：author
- 关闭证据：`python3 experiments/sample/quickstart.py --input experiments/sample/samples/input.json --output experiments/sample/output/sample.json` 通过；`python3 -m unittest discover -s experiments/sample/tests -p 'test_*.py'` 通过。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：CH-03 同时提到 Memory Bank、Bolt、Release、Progress Events，存在向 CH-04、CH-06 和 CH-08 外溢的风险。
- 影响：如果样章把后续章节机制讲满，读者会失去章节递进感，也会让本章“从 Intent 到计划”的唯一问题被稀释。
- 建议：保持当前边界：第 01 节说明不展开 Bolt 内部执行、跨会话 Memory Bank 和部署监控；第 06 节继续把这些内容标成后续章节，而不是在本章补长。
- 对应文件：[`book/chapters/sample.md`](../../book/chapters/sample.md)，第 34 行、第 178–190 行。
- 决策：本轮不阻断。正文已经把本章边界压在 Inception 分解链，不把 Operations 或 Bolt 执行细节前置。
- 负责人：author
- 关闭证据：目录事实源仍将 CH-04、CH-06、CH-08 保持为独立章节；CH-03 只引用这些机制作为边界提示。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：开头提出三类失败后果，其中“人的判断点太晚”在 Framework 中由 Human Checkpoints 回应，但 Example 部分没有列出一个具体 Checkpoint 示例。
- 影响：管理者读者可能理解“检查点很重要”，但还不能立即模仿一个检查点写法。
- 建议：二轮润色时在 Example 的修正任务后追加一个短行，例如 `Checkpoint: 样章发布前由作者确认读者对象、证据边界和不可发布目录`。
- 对应文件：[`book/chapters/sample.md`](../../book/chapters/sample.md)，第 16–34 行、第 54 行、第 93–110 行。
- 决策：本轮不阻断。读者练习第 6 步已经要求写下一个必须由人判断的 Checkpoint，能够支撑当前可读稿。
- 负责人：author
- 关闭证据：样章保留了从 Question → Framework → Example → Experiment → Figure → Review → Reader Exercise 的连续路径。

## 4 · 术语一致性

- 结论：pass
- 问题：正文同时出现 Intent、Requirements、Requirement、System Context、Units、Stories、Bolt Plan、Human Checkpoints；中英文混排密度较高。
- 影响：非工程背景读者可能在第一次阅读时把 Requirement、Story 和 Task 混为一类对象。
- 建议：当前首处定义已经足够；二轮润色时可在第 02 节前增加一个 6 行术语速查表，但不要引入新同义词。
- 对应文件：[`book/chapters/sample.md`](../../book/chapters/sample.md)，第 24–32 行、第 40–54 行。
- 决策：本轮不阻断。术语首次出现时有定义，后文没有把 `Exsecutio` 改写为其他词，核心公式保持为 `𝓔 = Engineering with Exsecutio`。
- 负责人：author
- 关闭证据：样章全文稳定使用 Intent、Requirement、System Context、Unit、Story、Bolt、Checkpoint；未发现关键术语漂移。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：本章已经有 Mermaid 局部图和全书核心图引用，但尚未生成 CH-03 专属 `book/images/ch03-intent-to-bolt.svg`。
- 影响：v0.1 可读稿可以成立；但若要达到“高级技术专著”质感，本章专属 SVG 会比 Mermaid 更适合正式版排版。
- 建议：将 CH-03 专属 SVG 作为 v0.2 或发布前增强项；当前 v0.1 继续使用 Mermaid 结构图和 `book/images/fig0-1.svg` 作为证据入口。
- 对应文件：[`book/chapters/sample.md`](../../book/chapters/sample.md)，第 147–176 行；[`book/images/fig0-1.svg`](../../book/images/fig0-1.svg)。
- 决策：本轮不阻断。正文中的实验命令、指标、失败样例、测试入口、读者练习和核心图路径均有对应产物。
- 负责人：author
- 关闭证据：`experiments/sample/output/sample.json` 为合法输出；`experiments/sample/output/README.md` 记录成功与失败样例；样章 References 已列出实验、输出、核心图和章节事实源。

## 发布门禁结论

- [x] 五类审校均为 pass。
- [x] 每个问题均包含影响、建议和对应文件。
- [x] 非阻断建议已说明取舍，不冒充已完成增强。
- [x] 当前样章引用主实验、样例输出、失败案例、测试命令、读者练习和核心图。
- [x] 章节 review 阶段可从 `pending` 更新为 `done`。

## 后续建议

1. D13-T02 处理发布阻断反馈时，优先确认是否需要把 Human Checkpoint 示例补进正文。
2. v0.2 规划中可新增 CH-03 专属 SVG：`book/images/ch03-intent-to-bolt.svg`。
3. 正式发布前可做一次语言层润色，目标是降低中英文术语密度，而不是改变术语体系。
