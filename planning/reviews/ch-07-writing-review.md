# 章节五类审校 · CH-07

## 审校状态

- 章节：`CH-07`
- 章节路径：`book/chapters/ch07-verification.md`
- 关联任务：`D21-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T10:50:00Z`

本轮审校目标是确认 CH-07 已达到“可读稿 + 证据对齐”标准：章节只回答“如何组合确定性检查、独立测试、模型评审和人工判断来证明 AI 参与的结果正确”，不回退到 CH-06 的 Exsecutio 执行闭环，也不提前展开 CH-08 的部署、监控和回滚；`EXP-07-01` 作为 already-ready 的项目内证据入口使用；`EXP-07-02`、`EXP-07-03` 仍为 planned，不被写成已验证结论；模型评审被定位为风险发现器，而不是最终裁判。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 问题：未发现发布阻断问题。
- 影响：无阻断影响。
- 建议：保持当前证据分层：`scripts/ci_check.py` 能证明工程门禁通过，但不能证明内容观点、读者理解或发布风险已经被完全验证。
- 证据：
  - `book/chapters/ch07-verification.md` 的 `01 · Question` 明确模型自评不是交付证据。
  - `book/chapters/ch07-verification.md` 的 `05 · Example` 明确 `ci_check.py` 能证明工程约束未破坏，不能证明内容价值已经被读者验证。
  - `book/chapters/ch07-verification.md` 的 `07 · Experiment` 明确 `EXP-07-01` 为 `ALREADY / ready`，`EXP-07-02` 与 `EXP-07-03` 仍为 `planned`。

## 2 · 重复内容与概念边界

- 结论：pass
- 问题：未发现明显重复段落或概念越界。
- 影响：无阻断影响。
- 建议：后续 CH-08 应承接“通过验证后的候选物如何进入运行”，避免重复 CH-07 的验证强度和证据链框架。
- 证据：
  - `book/toc.md` 中 CH-07 的独占对象是“验证：把人类检查点变成有效损失函数”。
  - CH-07 只讨论交付候选是否可以被批准，不展开 Build、Deploy、Monitor 和 Rollback。
  - `book/chapters/ch07-verification.md` 的 `09 · Boundary` 明确将部署、监控和回滚留给 CH-08。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 问题：未发现结构跳跃。
- 影响：无阻断影响。
- 建议：D21-T03 后可以进入 CH-08；若后续润色，优先生成独立 `book/images/ch07-verification-evidence-chain.svg` 提升图示质量。
- 证据：
  - 章节路径为：问题开场 → 四层证据链 → 验证强度选择 → 三段论证 → `ci_check.py` 案例 → 模型评审/人工判断协作 → 实验方向 → 图示入口 → 边界 → 读者练习。
  - D21-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 已通过，说明正式 CH-07 可进入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 问题：未发现核心术语漂移。
- 影响：无阻断影响。
- 建议：继续稳定使用 Deterministic Checks、Independent Tests、Model Review、Human Judgment 四层证据链；后续 CH-08 不应把 Verify 与 Monitor 混同。
- 证据：
  - `book/chapters/ch07-verification.md` 的 `02 · Framework` 稳定使用四层验证证据链。
  - `book/chapters/ch07-verification.md` 的 `03 · Verification Strength` 使用 Complexity、Reversibility、Safety / Impact、Data / State 四个风险判断维度。
  - 自动检查结果：`has_core_question=True`、`exp0701_ready=True`、`planned_kept=True`、`model_review_boundary=True`。

## 5 · 正文与实验/图/练习对应

- 结论：pass
- 问题：未发现正文承诺与证据入口脱节。
- 影响：无阻断影响。
- 建议：后续若推进 `EXP-07-02` 或 `EXP-07-03`，应补齐实验目录、样例输出和测试，再把 planned 方向升级为实验证据。
- 证据：
  - 确定性门禁入口：`scripts/ci_check.py`。
  - 事实源校验入口：`scripts/validate_project.py`。
  - 反馈连续性入口：`scripts/validate_feedback.py`。
  - GitHub 配置校验入口：`scripts/validate_github_config.py`。
  - 内部链接审计入口：`scripts/check_internal_links.py`。
  - 实验治理入口：`progress/experiments.json#EXP-07-01`、`progress/experiments.json#EXP-07-02`、`progress/experiments.json#EXP-07-03`。
  - 图示入口：`book/chapters/ch07-verification.md` 的 `08 · Figure`，后续独立图候选为 `book/images/ch07-verification-evidence-chain.svg`。
  - 读者练习：`book/chapters/ch07-verification.md` 的 `Reader Exercise`。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=80, internal=805, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: /Users/chenbaojun/Library/Mobile Documents/com~apple~CloudDocs/Baojun Page/aidlc-book-baojun/.artifacts/book/build-manifest.json
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] CH-07 已覆盖问题、框架、例子、实验/图入口和读者练习。
- [x] `EXP-07-01` 保持 `ALREADY / ready`，可作为项目内确定性门禁证据。
- [x] `EXP-07-02`、`EXP-07-03` 仍保持 planned，不作为已验证结论使用。
- [x] 已知非阻断缺口进入后续周期：可生成独立 `book/images/ch07-verification-evidence-chain.svg` 提升图示质量。
