# 章节五类审校 · CH-08

## 审校状态

- 章节：`CH-08`
- 章节路径：`book/chapters/ch08-operations.md`
- 关联任务：`D22-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T13:24:18Z`

本轮审校目标是确认 CH-08 已达到“可读稿 + 证据对齐”标准：章节只回答“如何通过 Build、Deploy、Verify、Monitor 与恢复机制，让通过测试的候选物成为可运行、可观测、可回滚的系统”，不回退到 CH-07 的验证强度选择，也不提前展开 CH-09 的 Flow 选择；CH-07 Verify 与 CH-08 Runtime Verify／Monitor 被明确拆开；`EXP-08-01` 作为 already-ready 的项目内证据入口使用；`EXP-08-02`、`EXP-08-03` 仍为 planned，不被写成已验证结论；当前仓库没有正式 `memory-bank/operations/` 目录，不被写成成熟生产能力。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 检查范围：五段运行链表述、Pages／Release 案例、实验状态、`memory-bank/operations/` 边界，以及对“生产成熟度”的措辞。
- 发现的问题：
  - Release 案例原先只按逻辑顺序列出 job，未标明 `needs` 依赖；YAML 声明顺序实为 `validate`、`build`、`readiness`、`publish`，容易被误读成执行顺序。
  - 除此之外，未发现把 planned 实验写成已验证事实、或把当前系统写成生产级 Operations 的阻断问题。
- 实际修改：
  - 在 `book/chapters/ch08-operations.md` 的 `4.2 Release` 中改为“核心 job 依赖顺序”，并补上 `needs: validate` / `needs: [validate, readiness]` / `needs: [validate, readiness, build]`。
- 保留的风险或限制：
  - 本项目 Pages／Release 链路仍是最小参考实现，不等于完整生产 Runbook。
  - `EXP-08-02`、`EXP-08-03` 仍缺实验目录与样例结果，不能支撑回滚耗时或阶段完成率结论。
- 审校结论：技术边界清楚，过度承诺风险受控。
- 证据：
  - `progress/experiments.json`：`EXP-08-01` 为 `ALREADY / ready`；`EXP-08-02`、`EXP-08-03` 为 `planned`。
  - `test -d memory-bank/operations` 为假；正文 `08 · Boundary` 明确不把该目录写成已存在成熟目录。
  - `.github/workflows/release.yml` 中 `build.needs = [validate, readiness]`，`publish` 拒绝覆盖并创建 `--draft`。
  - `scripts/prepare_release.py` 拒绝非 ready readiness、拒绝 source 不一致，并在无 `--pdf` 时记录 `pdf.status = skipped`。

## 2 · 重复内容与概念边界

- 结论：pass
- 检查范围：与 CH-07 验证链、CH-09 Flow 选择、以及正文内部 Build／Deploy／Runtime Verify／Monitor／Recover 的边界。
- 发现的问题：未发现明显重复段落或概念越界。
- 实际修改：无结构性改写；仅在技术正确性项中澄清 Release job 依赖表述。
- 保留的风险或限制：后续 CH-09 若讨论发布治理，应引用 CH-08 的运行链，而不是重写 Build／Deploy／Monitor。
- 审校结论：章节独占对象清楚，承接 CH-07、预留 CH-09。
- 证据：
  - `01 · Question` 与 `02 · Framework` 明确：CH-07 问“候选物是否可被批准”，CH-08 问“批准后能否运行、观察和恢复”。
  - Gate 与 `08 · Boundary` 明确不重新讨论验证强度，不讨论组织规模化治理。
  - Runtime Verify 专指部署后的目标环境验证，不与 CH-07 交付前验证混同。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 检查范围：问题 → 框架 → 三段论证 → 案例 → 清单 → 实验 → 图示 → 边界 → 练习是否形成可读路径。
- 发现的问题：未发现结构跳跃。
- 实际修改：更新章节 Metadata 中的 Writing Sprint Card 与 Draft Completeness，标记 D22-T03 审校完成。
- 保留的风险或限制：图示仍为正文 ASCII 入口，尚未生成独立 `book/images/ch08-operations-loop.svg`。
- 审校结论：读者可按“为什么需要 Operations → 五段链 → 为何构成闭环 → 本书案例 → 最小清单 → 实验／图／练习”完成阅读。
- 证据：
  - D22-T02 验收要求“章节正文覆盖问题、框架、例子、实验/图入口和读者练习”，上述结构已覆盖。
  - `scripts/build_book.sh .artifacts/book html` 可将正式 CH-08 纳入内部书稿候选。

## 4 · 术语一致性

- 结论：pass
- 检查范围：Operations 五段链术语、Runtime Verify 与 CH-07 Verify 的区分、Recover／Runbook、以及不引入错误的 Execution 替代。
- 发现的问题：未发现核心术语漂移；本章不展开 `Exsecutio`／`𝓔`，也未把 Exsecutio 误写成 Execution。
- 实际修改：无术语替换。
- 保留的风险或限制：官方 Operations Agent 常用 Build／Deploy／Verify／Monitor 四阶段；本书正文保留 Recover 第五段，并在 `EXP-08-03` 中把四阶段复现标为 planned，避免两套术语互相覆盖。
- 审校结论：术语稳定，CH-07／CH-08 边界可维持。
- 证据：
  - 稳定使用 Build、Deploy、Runtime Verify、Monitor、Recover。
  - 明确区分交付前 Verify 与运行后 Runtime Verify／Monitor。
  - 事实核对：`exp0801_ready=True`、`planned_kept=True`、`ops_dir_absent=True`、`verify_boundary=True`。

## 5 · 正文与实验、图示、练习、证据入口对应

- 结论：pass
- 检查范围：References、实验入口、案例脚本／工作流、图示方向、Reader Exercise 与事实源是否对齐。
- 发现的问题：`book/README.md` 仍将 CH-08 描述为“论证骨架”，落后于 D22-T02 可读稿状态。
- 实际修改：
  - 将 `book/README.md` 中 CH-08 更新为“正式十章生产线可读稿与审校记录入口”。
- 保留的风险或限制：独立 SVG 尚未生成；`EXP-08-02`／`EXP-08-03` 仍为方向入口。
- 审校结论：正文承诺与现有证据入口对齐，无脱节阻断。
- 证据：
  - 发布候选入口：`scripts/check_release_readiness.py`、`scripts/prepare_release.py`。
  - Pages 发布入口：`scripts/prepare_pages.py`、`.github/workflows/pages.yml`。
  - Release 链路入口：`.github/workflows/release.yml`、`planning/releases/v0.1-policy.json`。
  - 实验治理入口：`progress/experiments.json#EXP-08-01`、`#EXP-08-02`、`#EXP-08-03`。
  - 图示入口：`07 · Figure`；后续独立图候选为 `book/images/ch08-operations-loop.svg`。
  - 读者练习：`Reader Exercise` 覆盖来源、Build、Deploy、Runtime Verify、Monitor、Recover 与最终判定。
  - 内部链接检查：`python3 scripts/check_internal_links.py --root .` 通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
[INFO] link summary: files=83, internal=817, external-not-fetched=3, errors=0

scripts/build_book.sh .artifacts/book html
[OK] Candidate: /workspace/.artifacts/book/deep-understanding-ai-dlc.html
[OK] Build manifest: /workspace/.artifacts/book/build-manifest.json

python3 scripts/validate_project.py
[INFO] validation summary: tasks=72, chapters=10, experiments=30, errors=0, warnings=0
[INFO] validation passed

python3 scripts/generate_progress.py --generated-at 2026-07-24T13:25:13Z
[OK] source=aae4fb4d21a3-working-tree-9543d484106c tasks=72 chapters=10 experiments=30 new_events=3 total_events=204

python3 scripts/ci_check.py
Ran 98 tests in 8.934s
OK (skipped=1)
[INFO] link summary: files=83, internal=817, external-not-fetched=3, errors=0
[INFO] CI summary: checks=6, seconds=9.314, budget=60.0, ok=True
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] blocked 项均有负责人和关闭证据；本轮无 blocked 项。
- [x] CH-08 已覆盖问题、框架、例子、实验/图入口和读者练习。
- [x] `EXP-08-01` 保持 `ALREADY / ready`，可作为项目内发布候选来源证据。
- [x] `EXP-08-02`、`EXP-08-03` 仍保持 planned，不作为已验证结论使用。
- [x] 当前仓库没有正式 `memory-bank/operations/` 目录；正文未将其写成成熟生产能力。
- [x] CH-07 Verify 与 CH-08 Runtime Verify／Monitor 未被混同。
- [x] 已知非阻断缺口进入后续周期：可生成独立 `book/images/ch08-operations-loop.svg` 提升图示质量。
