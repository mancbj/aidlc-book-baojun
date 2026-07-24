# 章节五类审校 · CH-09

## 审校状态

- 章节：`CH-09`
- 章节路径：`book/chapters/ch09-adaptive-engineering.md`
- 关联任务：`D23-T03`
- 结论：`pass`
- 审校时间：`2026-07-24T13:35:57Z`

本轮审校目标是确认 CH-09 已达到“可读稿 + 证据对齐”标准：章节只回答“如何根据任务复杂度、代码库现状、监管要求和团队规模，在 Simple、FIRE 与 AI-DLC 之间选择，而不过度或不足工程化”；风险—仪式矩阵与三类任务对照清楚；不回退到 CH-08 Operations 运行链，也不提前展开 CH-10 组织度量；`EXP-09-01`、`EXP-09-02`、`EXP-09-03` 均为 planned，不被写成已验证结论。

## 1 · 技术正确性与过度承诺

- 结论：pass
- 检查范围：三种 Flow 表述、风险维度、Swap Test、实验状态与项目内参照（发布门禁脚本／workflow）。
- 发现的问题：未发现把 planned 实验写成已验证事实，或把 Flow 选择写成可替代人工判断的自动黑盒。
- 实际修改：更新章节 Metadata 为 D23-T03 审校完成；将 `book/README.md` 中 CH-09 标为可读稿与审校记录入口。
- 保留的风险或限制：三项 EXP-09 仍缺实验目录与样例结果；矩阵落点是典型倾向，不是强制法令。
- 审校结论：技术边界清楚，过度承诺风险受控。
- 证据：
  - `progress/experiments.json`：EXP-09-01/02/03 均为 `planned`。
  - 正文 `06 · Experiment` 与 `08 · Boundary` 明确不把专家一致率、覆盖率或流程开销写成已验证结论。
  - Task B 参照 `scripts/check_release_readiness.py` 与 `.github/workflows/release.yml` 存在且可核对。

## 2 · 重复内容与概念边界

- 结论：pass
- 检查范围：与 CH-08 Operations、CH-10 组织／度量，以及 CH-07 验证强度选择的边界。
- 发现的问题：未发现明显重复段落或概念越界。
- 实际修改：无结构性改写。
- 保留的风险或限制：后续若写 CH-10，应引用 CH-09 的 Flow 决策卡，而不是重写选型矩阵。
- 审校结论：章节独占“方法适配与治理强度”，边界清楚。
- 证据：
  - Gate／Boundary 明确不展开 Operations 五段链，不讨论 Mob／记分卡。
  - `book/toc.md` 去重表：CH-09 不展开组织角色重构。

## 3 · 结构连贯性与读者路径

- 结论：pass
- 检查范围：问题 → 框架 → 三段论证 → 案例／Swap Test → 决策卡 → 实验 → 图示 → 边界 → 练习。
- 发现的问题：未发现结构跳跃。
- 实际修改：无。
- 保留的风险或限制：独立 SVG `book/images/ch09-risk-ceremony-matrix.svg` 尚未生成。
- 审校结论：读者路径完整，满足 D23-T02 验收覆盖要求。
- 证据：上述各节均存在；`scripts/build_book.sh .artifacts/book html` 可将 CH-09 纳入书稿候选。

## 4 · 术语一致性

- 结论：pass
- 检查范围：Simple／FIRE／AI-DLC、风险—仪式矩阵、仪式预算、Checkpoint／Runtime scope，以及不误用 Execution。
- 发现的问题：未发现核心术语漂移。
- 实际修改：无术语替换。
- 保留的风险或限制：FIRE 的 Autopilot／Confirm／Validate 仅作为对照提示，不在本章展开完整 FIRE 手册。
- 审校结论：术语稳定。
- 证据：事实核对 `flows_named=True`、`planned_kept=True`、`matrix_term=True`、`no_execution_drift=True`。

## 5 · 正文与实验、图示、练习、证据入口对应

- 结论：pass
- 检查范围：References、三类任务案例、实验入口、图示方向、Reader Exercise。
- 发现的问题：README 在 D23-T02 后仍可进一步标明审校入口。
- 实际修改：更新 `book/README.md` CH-09 描述为“正式十章生产线可读稿与审校记录入口”。
- 保留的风险或限制：EXP-09 仍为方向入口；独立 SVG 未生成。
- 审校结论：正文承诺与现有入口对齐。
- 证据：
  - 实验治理：`progress/experiments.json#EXP-09-01` 等。
  - 图示入口：`07 · Figure`。
  - 读者练习：Flow 决策卡七步。
  - 内部链接检查通过。

## 校验记录

```text
python3 scripts/check_internal_links.py --root .
scripts/build_book.sh .artifacts/book html
python3 scripts/validate_project.py
python3 scripts/generate_progress.py --generated-at <UTC>
python3 scripts/ci_check.py
```

## 发布阻断结论

- [x] 五类结论均为 pass。
- [x] 本轮无 blocked 项。
- [x] CH-09 已覆盖问题、框架、例子、实验/图入口和读者练习。
- [x] EXP-09-01/02/03 仍保持 planned。
- [x] 已知非阻断缺口：可生成独立 `book/images/ch09-risk-ceremony-matrix.svg`。
