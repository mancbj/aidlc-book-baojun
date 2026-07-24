# 章节五类审校 · CH-05

## 审校状态

- 章节：`CH-05`
- 章节路径：`book/chapters/ch05-bolts.md`
- 关联任务：`D19-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T07:50:00Z`

本轮审校目标是确认 CH-05 已达到“可读稿 + 证据对齐”标准：Bolt 作为小时到天级执行批次的边界清楚，不被混同为普通任务、Sprint 或无限自治 Agent；Simple / DDD 选择不带价值高低判断；planned 实验不被写成 verified 证据；章节结构服务唯一核心问题；正文承诺能够回到 Bolt 事实源、实验治理状态、图示入口和构建/链接校验。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：未发现发布阻断问题。
- 影响：无阻断影响。
- 建议：保持当前边界表述：`EXP-05-01`、`EXP-05-02`、`EXP-05-03` 仍为 planned，只能作为验证方向；不能写成已验证估算模型或自动选择器。
- 证据：
  - `book/chapters/ch05-bolts.md` 的 `01 · Question` 明确 Bolt 是小时到天级工程执行轨道，不是普通任务或传统 Sprint。
  - `book/chapters/ch05-bolts.md` 的 `05 · Experiment` 明确写出三项 EXP-05 实验当前仍处于 `planned`，不把指标写成已验证结论。
  - `book/chapters/ch05-bolts.md` 的 `07 · Boundary` 明确不教完整运行 Bolt、不把 DDD 写成高级、不把估算写成精确预测、不鼓励 AI 自行决定所有门禁。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：未发现明显重复段落或概念越界。
- 影响：无阻断影响。
- 建议：后续 CH-06 应承接“如何运行一个 Bolt 并留下 Walkthrough”，避免重复 CH-05 的 Bolt 选择矩阵和四个设计旋钮。
- 证据：
  - `book/toc.md` 中 CH-05 的独占对象是“Bolts：为快速执行选择正确轨道”。
  - CH-05 只回答 Bolt 范围、类型、阶段门禁和证据如何选择，不展开完整执行日志。
  - `book/chapters/ch05-bolts.md` 的 `07 · Boundary` 将完整 Bolt 运行和 Walkthrough 留给 CH-06。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：未发现结构跳跃。
- 影响：无阻断影响。
- 建议：D19-T03 后可以进入 CH-06；若后续润色，优先生成独立 `ch05-bolt-selection-matrix.svg`，不改变章节主结构。
- 证据：
  - 章节路径为：问题开场 → Bolt 定义与边界 → 四个设计旋钮 → 三段论证 → 本书四个 Bolt 案例 → planned 实验方向 → 选择矩阵图示入口 → 边界 → 读者练习。
  - D19-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 已通过，说明正式 CH-05 可进入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 问题：未发现核心术语漂移。
- 影响：无阻断影响。
- 建议：继续保留 `Exsecutio` 作为指定术语，不自动改为 `Execution`；Bolt、Simple Construction、DDD Construction、Gate、Evidence 等术语后续应保持稳定。
- 证据：
  - 章节正文使用 Simple Construction 与 DDD Construction，并明确两者只是不同风险形态下的执行轨道。
  - 章节正文在 `02 · Framework` 中稳定使用 Scope、Type、Gates、Evidence 四个设计旋钮。
  - 自动检查结果：`has_exsecutio=True`，`wrong_execution_phrase=False`。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：未发现正文承诺与证据入口脱节。
- 影响：无阻断影响。
- 建议：后续若推进 `EXP-05-01` 或 `EXP-05-02`，应补齐实验目录、样例输出和测试，再把 planned 结论升级为证据。
- 证据：
  - Bolt 案例入口：`memory-bank/bolts/001-github-writing-system-ui/bolt.md` 至 `memory-bank/bolts/004-github-writing-system-ui/bolt.md`。
  - 实验治理入口：`progress/experiments.json#EXP-05-01`、`progress/experiments.json#EXP-05-02`、`progress/experiments.json#EXP-05-03`，当前均为 planned。
  - 图示入口：`book/chapters/ch05-bolts.md` 的 `06 · Figure`，后续独立图候选为 `book/images/ch05-bolt-selection-matrix.svg`。
  - 读者练习：`book/chapters/ch05-bolts.md` 的 `Reader Exercise`。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=76, internal=787, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/build-manifest.json
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] CH-05 已覆盖问题、框架、例子、实验/图入口和读者练习。
- [x] `EXP-05-01`、`EXP-05-02`、`EXP-05-03` 仍保持 planned，不作为已验证结论使用。
- [x] 已知非阻断缺口进入后续周期：可生成独立 `book/images/ch05-bolt-selection-matrix.svg` 提升图示质量。
