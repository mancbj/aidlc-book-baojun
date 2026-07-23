# 章节五类审校 · CH-01

## 审校状态

- 章节：`CH-01`
- 章节路径：`book/chapters/ch01-ai-native-sdlc.md`
- 关联任务：`D15-T03`
- 结论：`pass`
- 审校时间：`2026-07-23T10:30:00Z`

本轮审校目标是确认 CH-01 已达到“可读稿 + 证据对齐”标准：技术描述不过度承诺，结构服务唯一核心问题，术语与全书一致，正文承诺能够回到图示、实验入口、任务事实源和构建/链接校验。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：未发现发布阻断问题。
- 影响：无阻断影响。
- 建议：保持当前边界表述：AI-DLC 不是 AI 替代 SDLC，也不是 specs.md 的同义词；specs.md 仅作为参考实现。
- 证据：
  - `book/chapters/ch01-ai-native-sdlc.md` 的 `03 · Core Formula` 明确区分人的判断、AI 能力与 `𝓔`。
  - `book/chapters/ch01-ai-native-sdlc.md` 的 `06 · Experiment` 明确说明三个实验仍处于治理队列，未把 planned 实验写成已验证结论。
  - `book/chapters/ch01-ai-native-sdlc.md` 的 `08 · Boundary` 明确不抢第 2–10 章的展开对象。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：未发现明显重复段落或概念越界。
- 影响：无阻断影响。
- 建议：后续 CH-02 应接续“人的判断不可委托”展开，避免重复 CH-01 的三范式总论。
- 证据：
  - `book/toc.md` 中 CH-01 的独占对象是“新生命周期的必要性与理论边界”。
  - `book/chapters/ch01-ai-native-sdlc.md` 的 `02 · Framework` 只建立 AI-Assisted / AI-Driven / Agentic 区分，不展开各阶段工件细节。
  - `book/chapters/ch01-ai-native-sdlc.md` 的 `08 · Boundary` 将责任分配、Intent 分解、Memory Bank、Bolt、验证与 Operations 分别留给后续章节。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：未发现结构跳跃。
- 影响：无阻断影响。
- 建议：D15-T03 后可以进入 CH-02；若后续做语言润色，优先压缩局部重复句，而不是改变章节结构。
- 证据：
  - 章节路径为：问题开场 → 三范式框架 → 核心公式 → 三段论证 → 同一 Intent 对照案例 → 实验入口 → 图示入口 → 边界 → 读者练习。
  - D15-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 已通过，说明章节可进入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 问题：未发现核心术语漂移。
- 影响：无阻断影响。
- 建议：继续把 `Exsecutio` 作为指定术语处理，不自动改为 `Execution`。
- 证据：
  - 章节正文保留 `AI-DLC = 𝓔（人的判断 + AI 能力）`。
  - 章节正文保留 `𝓔 = Engineering with Exsecutio`。
  - 自动检查结果：`has_exsecutio=True`，`wrong_execution_phrase=False`。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：未发现正文承诺与证据入口脱节。
- 影响：无阻断影响。
- 建议：后续若引用实验结论，必须等 `EXP-01-01`、`EXP-01-02` 或 `EXP-01-03` 从 planned 进入可验证状态。
- 证据：
  - 图示入口：`book/images/fig0-1.svg`。
  - 实验入口：`progress/experiments.json#EXP-01-01`、`progress/experiments.json#EXP-01-02`、`progress/experiments.json#EXP-01-03`。
  - 读者练习：`book/chapters/ch01-ai-native-sdlc.md` 的 `09 · Reader Exercise`。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=69, internal=755, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: .artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: .artifacts/book/build-manifest.json
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] 已知非阻断缺口进入下一周期；CH-01 三个实验仍为 planned，后续不得提前写成已验证证据。

