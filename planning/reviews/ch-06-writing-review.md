# 章节五类审校 · CH-06

## 审校状态

- 章节：`CH-06`
- 章节路径：`book/chapters/ch06-exsecutio.md`
- 关联任务：`D20-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T09:20:00Z`

本轮审校目标是确认 CH-06 已达到“可读稿 + 证据对齐”标准：`Exsecutio` 作为本书专用术语被稳定保留，不被普通 `Execution` 概念替代；章节只回答“如何把 Bolt 贯彻为可交付候选”，不回退到 CH-05 的 Bolt 类型选择；计划、执行、验证、修复、Walkthrough 五段闭环结构清楚；本书 Bolt 002 案例能回到实际工件；`EXP-06-01`、`EXP-06-02`、`EXP-06-03` 仍为 planned，不被写成已验证结论。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：未发现发布阻断问题。
- 影响：无阻断影响。
- 建议：保持当前边界表述：三项 EXP-06 实验仍为 planned，只能作为验证方向；不能写成已经证明 Exsecutio 降低复核成本或提高修复准确率。
- 证据：
  - `book/chapters/ch06-exsecutio.md` 的 `01 · Question` 明确 Exsecutio 不是一般意义上的 execution，也不是让 AI 无限自治地“继续做”。
  - `book/chapters/ch06-exsecutio.md` 的 `06 · Experiment` 明确写出三项 EXP-06 实验当前仍处于 `planned`。
  - `book/chapters/ch06-exsecutio.md` 的 `08 · Boundary` 明确不把自动化测试等同于全部验证、不鼓励 AI 无限自治、不把 Walkthrough 当成文档表演。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：未发现明显重复段落或概念越界。
- 影响：无阻断影响。
- 建议：后续 CH-07 应承接“验证强度与证据链”，避免重复 CH-06 的执行闭环与 Walkthrough 叙述。
- 证据：
  - `book/toc.md` 中 CH-06 的独占对象是“Exsecutio：把提议贯彻为交付候选”。
  - CH-06 假设 Bolt 类型已经选好，只讨论 Plan、Execute、Verify、Repair、Walkthrough 如何运行到交付候选。
  - `book/chapters/ch06-exsecutio.md` 的 `08 · Boundary` 将 Simple / DDD Bolt 选择回指 CH-05，将验证分层留给 CH-07 深入展开。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：未发现结构跳跃。
- 影响：无阻断影响。
- 建议：D20-T03 后可以进入 CH-07；若后续润色，优先生成独立 `book/images/ch06-exsecutio-loop.svg` 提升图示质量。
- 证据：
  - 章节路径为：问题开场 → 核心公式与术语边界 → 五段闭环 → 三段论证 → Bolt 002 案例 → 可复用记录模板 → planned 实验方向 → 图示入口 → 边界 → 读者练习。
  - D20-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 已通过，说明正式 CH-06 可进入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 问题：未发现核心术语漂移。
- 影响：无阻断影响。
- 建议：继续保留 `𝓔 = Engineering with Exsecutio`，并在后续章节中把 `Exsecutio` 作为指定术语处理；若出现 `execution`，只用于边界说明，不能替代术语。
- 证据：
  - `book/chapters/ch06-exsecutio.md` 明确保留 `𝓔 = Engineering with Exsecutio`。
  - 自动检查结果：`has_formula=True`、`has_exsecutio=True`。
  - `execution` 仅出现在“不是一般意义上的 execution”的术语边界说明中，未把 `Exsecutio` 改写为普通 `Execution`。
  - Plan、Execute、Verify、Repair、Walkthrough 五个阶段名称在全文中保持稳定。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：未发现正文承诺与证据入口脱节。
- 影响：无阻断影响。
- 建议：后续若推进 `EXP-06-01` 或 `EXP-06-02`，应补齐实验目录、样例输出和测试，再把 planned 假设升级为证据。
- 证据：
  - Bolt 案例入口：`memory-bank/bolts/002-github-writing-system-ui/bolt.md`。
  - 计划证据：`memory-bank/bolts/002-github-writing-system-ui/implementation-plan.md`。
  - 实现证据：`memory-bank/bolts/002-github-writing-system-ui/implementation-walkthrough.md`。
  - 测试证据：`memory-bank/bolts/002-github-writing-system-ui/test-walkthrough.md`。
  - 实验治理入口：`progress/experiments.json#EXP-06-01`、`progress/experiments.json#EXP-06-02`、`progress/experiments.json#EXP-06-03`，当前均为 planned。
  - 图示入口：`book/chapters/ch06-exsecutio.md` 的 `07 · Figure`，后续独立图候选为 `book/images/ch06-exsecutio-loop.svg`。
  - 读者练习：`book/chapters/ch06-exsecutio.md` 的 `Reader Exercise`。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=78, internal=796, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/build-manifest.json
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] CH-06 已覆盖问题、框架、例子、实验/图入口和读者练习。
- [x] `EXP-06-01`、`EXP-06-02`、`EXP-06-03` 仍保持 planned，不作为已验证结论使用。
- [x] 已知非阻断缺口进入后续周期：可生成独立 `book/images/ch06-exsecutio-loop.svg` 提升图示质量。
