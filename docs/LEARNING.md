# AI-DLC Book 学习路线

> 目标：让第一次打开仓库的读者，不依赖聊天记录，也能知道先读什么、怎么跑实验、如何判断当前 v0.1 是否可发布。

## 0 · 先建立方向感

如果你只有 5 分钟，按这个顺序看：

1. [根 README](../README.md)：理解核心公式 `AI-DLC = 𝓔（人的判断 + AI 能力）` 与两周 v0.1 目标。
2. [Part 00 · 鸟瞰 AI-DLC](../book/part-00-overview.md)：看本书叙事地图、生命周期和三条阅读路线。
3. [鸟瞰驾驶舱](../site/index.html)：确认当前任务、阻塞、下一动作和来源。
4. [当前文字摘要](../progress/generated/current.md)：不用打开 HTML，也能看当前进度与最近事件。

看到这里，你应该能回答三个问题：

- 这本书解决什么问题？
- 当前 v0.1 还差什么？
- 下一步应该读、跑或反馈哪一个对象？

## 1 · 入门路线：从概念到样章

适合读者：第一次接触 AI-DLC，想先理解方法，而不是马上改代码。

| 顺序 | 阅读对象 | 读完应获得 |
|---:|---|---|
| 1 | [核心宣言](../book/manifesto.md) | 核心公式、Exsecutio 的含义和方法边界 |
| 2 | [十章目录](../book/toc.md) | Part 0–5 的叙事结构和每章唯一问题 |
| 3 | [CH-03 样章](../book/chapters/sample.md) | Inception 如何把 Intent 分解为 Requirement、Unit、Story 和 Bolt Plan |
| 4 | [样章第一轮审校](../planning/reviews/sample-chapter.md) | 当前样章哪些地方已通过、哪些建议留到后续 |
| 5 | [读者试读说明](READER-GUIDE.md) | 如何提交最小反馈，以及不要提交哪些敏感信息 |

建议节奏：

- 10 分钟读 Part 0。
- 30 分钟读 CH-03 样章。
- 5 分钟看样章审校报告，确认当前稿件不是“无门禁草稿”。
- 5 分钟写一条反馈：哪里读懂了，哪里卡住了，是否影响 v0.1 发布。

## 2 · 实践路线：跑通一个最小实验

适合读者：想验证本书不是只讲概念，而是能把观点落到可复现实验。

当前 v0.1 的主实验是 `EXP-03-01 · Intent 到 Story 追踪链生成器`，状态为 `SHIP / verified`。

### 2.1 读实验说明

先看：

- [实验合同](../planning/sample-experiment.md)
- [实验 README](../experiments/sample/README.md)
- [成功与失败样例说明](../experiments/sample/output/README.md)

### 2.2 运行合法样例

从仓库根目录运行：

```bash
python3 experiments/sample/quickstart.py \
  --input experiments/sample/samples/input.json \
  --output experiments/sample/output/sample.json
```

预期结果：

- 退出码为 `0`。
- 输出文件为 [`experiments/sample/output/sample.json`](../experiments/sample/output/sample.json)。
- `valid` 为 `true`。
- 四项指标为 `100.0 / 0 / 100.0 / 0`。

### 2.3 运行测试

```bash
python3 -m unittest discover \
  -s experiments/sample/tests \
  -p 'test_*.py'
```

预期结果：全部通过。当前 D12-T02 前置验证为 4 个实验测试通过。

### 2.4 读懂边界

这个实验只证明结构追踪性：

- Requirement 是否有下游 Unit 和 Story。
- Story 是否有上游目标。
- 验收是否存在。
- 引用是否有效。

它不证明业务语义正确，也不替代人的目标判断。读者复现实验后，应回到 [CH-03 样章](../book/chapters/sample.md) 的实验段，检查正文是否诚实表达了这个边界。

## 3 · 可跳读路径：按你的角色选择

### A · 管理者 / 技术负责人

目标：判断 AI-DLC 是否值得引入团队研发系统。

1. [Part 00](../book/part-00-overview.md)
2. [目标读者定义](../planning/readers.md)
3. [CH-03 样章](../book/chapters/sample.md)
4. [v0.1 Definition of Done](../planning/releases/v0.1-checklist.md)
5. [Release readiness 报告](../releases/v0.1-rc/readiness.md)

重点看：人的判断点、事实源、发布门禁和不可伪造证据。

### B · 开发者 / 架构师

目标：理解如何把一个模糊 Intent 变成可执行计划。

1. [仓库指南](REPOSITORY-GUIDE.md)
2. [CH-03 样章](../book/chapters/sample.md)
3. [样章实验合同](../planning/sample-experiment.md)
4. [实验实现](../experiments/sample/quickstart.py)
5. [实验测试](../experiments/sample/tests/test_demo.py)

重点看：ID、引用、验收、错误代码和确定性输出。

### C · 写作者 / 内容协作者

目标：参与章节、案例、审校或图示生产。

1. [章节模板](../book/chapter-template.md)
2. [十章目录](../book/toc.md)
3. [CH-03 样章](../book/chapters/sample.md)
4. [五类审校模板](../planning/reviews/chapter-review-template.md)
5. [样章第一轮审校](../planning/reviews/sample-chapter.md)

重点看：每章唯一问题、读者结果、证据入口和审校格式。

### D · 只关心项目状态的人

目标：快速判断当前能不能发布 v0.1。

1. [鸟瞰驾驶舱](../site/index.html)
2. [对象下钻](../site/details.html)
3. [当前文字摘要](../progress/generated/current.md)
4. [Release readiness](../releases/v0.1-rc/readiness.md)
5. [Release Notes 候选](../releases/v0.1-rc/release-notes.md)

重点看：Must 任务、blocker、known gap、来源提交和下一动作。

## 4 · 最小闭环路线：60 分钟完成一次体验

如果你想快速体验 AI-DLC 的“读 → 跑 → 查 → 反馈”闭环：

1. 读 [Part 00](../book/part-00-overview.md) 的核心公式和生命周期。
2. 读 [CH-03 样章](../book/chapters/sample.md) 的 Question、Framework、Experiment 三节。
3. 运行 `EXP-03-01` 合法样例。
4. 打开 [实验输出](../experiments/sample/output/sample.json)，核对四项指标。
5. 打开 [驾驶舱](../site/index.html)，查看当前下一动作。
6. 用 [反馈模板](../planning/feedback-template.md) 写一条最小反馈。

完成这 6 步后，你已经走过本书 v0.1 的最小试读路径。

## 5 · 何时不要继续往下读

遇到以下情况，先停下来查事实源：

- 页面进度和 [`progress/tasks.json`](../progress/tasks.json) 不一致。
- 样章说实验已验证，但 [`progress/experiments.json`](../progress/experiments.json) 不是 `verified`。
- Release Notes 说 ready，但 [`releases/v0.1-rc/readiness.json`](../releases/v0.1-rc/readiness.json) 仍是 `blocked`。
- GitHub Project、Issue 或 PR 与仓库事实源冲突。

本书的原则是：读者入口可以很多，事实源只能有一个。

## 6 · 贡献前检查

提交改动前，至少运行：

```bash
python3 scripts/ci_check.py --budget-seconds 60
```

如果只改学习路线或文档，也建议运行：

```bash
python3 scripts/check_internal_links.py --scope docs/LEARNING.md
```

PR 需要关联 Task ID、产物、测试与验收。协作规则见 [GitHub Collaboration](GITHUB-COLLABORATION.md)。
