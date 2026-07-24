# 章节五类审校 · CH-02

## 审校状态

- 章节：`CH-02`
- 章节路径：`book/chapters/ch02-human-judgment.md`
- 关联任务：`D16-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T03:20:00Z`

本轮审校目标是确认 CH-02 已达到“可读稿 + 证据对齐”标准：人的判断边界清晰，不把 AI 主动性写成 AI 负责一切；结构服务唯一核心问题；术语与全书一致；正文承诺能够回到实验入口、任务事实源、引用文件和构建/链接校验。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：未发现发布阻断问题。
- 影响：无阻断影响。
- 建议：保持当前表述：AI 可以提出路线、风险和检查点，但不可替代人的目标、边界、取舍和责任。
- 证据：
  - `book/chapters/ch02-human-judgment.md` 的 `01 · Question` 明确反对“人逐步提示一切”和“AI 自己决定一切”两个极端。
  - `book/chapters/ch02-human-judgment.md` 的 `02 · Framework` 将人的判断拆成 Intent、Boundary、Non-delegable Judgment、Human Checkpoint、Accountability 五件套。
  - `book/chapters/ch02-human-judgment.md` 的 `06 · Experiment` 明确说明三个 CH-02 实验仍处于治理队列，未写成已验证结论。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：未发现明显重复段落或概念越界。
- 影响：无阻断影响。
- 建议：后续 CH-03 可以承接 Intent 到 Requirement / Unit / Story / Bolt Plan 的工件化分解，避免重复 CH-02 的“人的判断五件套”。
- 证据：
  - `book/toc.md` 中 CH-02 的独占对象是“人机责任、反向对话与检查点选择”。
  - `book/chapters/ch02-human-judgment.md` 的 `08 · Boundary` 明确不展开第 3 章的 Intent 分解工件细节。
  - CH-02 只从人的判断角度使用 Master/Inception/Construction/Operations，不展开四 Agent 的完整工程实现。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：未发现结构跳跃。
- 影响：无阻断影响。
- 建议：D16-T03 后可以进入 CH-03；若后续润色，优先强化案例与五件套之间的回指，不改变章节主结构。
- 证据：
  - 章节路径为：问题开场 → 人的判断五件套 → 反向对话 → 三段论证 → 模糊需求案例 → 实验入口 → 图示入口 → 边界 → 读者练习。
  - D16-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 已通过，说明章节可进入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 问题：未发现核心术语漂移。
- 影响：无阻断影响。
- 建议：继续保留 `Exsecutio` 作为指定术语，不自动改为 `Execution`；CH-02 应持续归属于公式中的“人的判断”部分。
- 证据：
  - 章节正文保留 `𝓔 = Engineering with Exsecutio`。
  - 自动检查结果：`has_formula=True`，`wrong_execution_phrase=False`。
  - `book/manifesto.md` 中人的判断职责为定方向、定边界、做取舍并承担最终责任；CH-02 的五件套与此一致。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：未发现正文承诺与证据入口脱节。
- 影响：无阻断影响。
- 建议：后续若引用实验结论，必须等 `EXP-02-01`、`EXP-02-02` 或 `EXP-02-03` 从 planned 进入可验证状态。
- 证据：
  - 实验入口：`progress/experiments.json#EXP-02-01`、`progress/experiments.json#EXP-02-02`、`progress/experiments.json#EXP-02-03`。
  - 图示入口：`book/chapters/ch02-human-judgment.md` 的 `07 · Figure`。
  - 读者练习：`book/chapters/ch02-human-judgment.md` 的 `09 · Reader Exercise`。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=71, internal=764, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: .artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: .artifacts/book/build-manifest.json
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] 已知非阻断缺口进入下一周期；CH-02 三个实验仍为 planned，后续不得提前写成已验证证据。

