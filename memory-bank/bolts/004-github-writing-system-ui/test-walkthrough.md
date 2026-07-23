---
stage: test
bolt: 004-github-writing-system-ui
created: 2026-07-22T03:34:29Z
---

# Test Report: Review, v0.1 Release Gate and Continuous Update Cycle

## Summary

- **Tests**: 76/76 passed
- **Bolt 004专项测试**: 17/17 passed
- **Coverage**: 未配置行覆盖率工具；计划中的反馈、门禁、候选、周期、事件、幂等、失败安全、隐私和 workflow 权限场景均有自动化覆盖
- **Shared CI**: 5.985 秒 / 60 秒预算
- **Real repository verdict**: `blocked`，44 blockers，1 known gap
- **Complete fixture verdict**: `ready`，可生成同源 HTML 候选，PDF 明确 skipped

## Test Files

- [x] `tests/test_release_continuity.py` - 17 项 Bolt 004 正常、失败、幂等、安全和发布后连续性测试。
- [x] `tests/test_generate_progress.py` - 8 项生成器、历史保护和快照回归测试。
- [x] `tests/test_github_automation.py` - 27 项 GitHub 配置、Pages、Release 与 Projects 回归测试。
- [x] `tests/test_progress_core.py` - 13 项聚合、下一动作和事件稳定性测试。
- [x] `tests/test_validate_project.py` - 11 项任务、章节、实验和依赖校验测试。

## Acceptance Criteria Validation

- ✅ **Writer Chat 保存关键取舍**：模板字段覆盖 Task ID、上下文摘要、采用/放弃方案、理由、影响文件和下一动作，并明确删除凭证及私密原文。
- ✅ **五类审校均有结论入口**：技术、重复、结构、术语和正文/实验/图/练习对应五类契约被专项断言；真实样章审校仍保持 blocked。
- ✅ **反馈决策可追溯**：accepted、rejected、deferred、pending 的必需字段、匿名读者状态、冲突独立性和敏感字段拒绝均通过。
- ✅ **accepted 反馈关联任务**：缺少任务或二元验收时失败；完整 fixture 将 `FB-001` 稳定带入 `C02-T04`。
- ✅ **三位试读入口存在**：Reader A/B/C 说明、反馈模板和隐私边界通过；真实槽位仍为 not-invited，没有伪造响应。
- ✅ **未满足 Must 时阻止发布**：真实仓库返回非零门禁，报告保留 44 个 blocker；blocked readiness 无法创建候选。
- ✅ **完整 v0.1 Definition of Done 可通过**：临时 fixture 完成 Must、样章、SHIP 实验、核心图和五类审校后得到 ready。
- ✅ **Release Notes 与同源候选**：完整 fixture 生成事实化 Notes、HTML archive 和 manifest；错误 source、假 PDF 和未标记覆盖均被拒绝。
- ✅ **真实发布才可开周期**：无 receipt、draft Release、blocked readiness 或 source 不一致均不能激活。
- ✅ **下一周期可持续且幂等**：published fixture 生成 v0.2、带入未完成 Should、accepted feedback 和 known gap；重复处理字节等价。
- ✅ **v0.1 历史不重置**：周期开启前后 `progress/tasks.json` SHA-256 完全一致。
- ✅ **发布后下一动作正确**：active cycle 优先指向 `C02-T01`，不会被已带入的旧 Should 抢占。
- ✅ **关键更新自动可视记录**：fixture 生成且只生成 `release_published` 与 `cycle_opened` 两类新事件，并产生不覆盖旧快照的新 source 身份。
- ✅ **Pages 与 GitHub 下钻完整**：发布树包含 `.github` 和 `.nojekyll`；47 个可读文件中的 221 条内部链接零错误。

## Failure Injection

- [x] accepted 缺关联任务或验收时拒绝。
- [x] PII/凭证字段和伪 reader response 时拒绝。
- [x] blocked readiness 保留报告但拒绝候选。
- [x] readiness source 与当前事实不一致时拒绝候选。
- [x] 无真实 receipt、draft Release 或未完成 Must 时拒绝激活周期。
- [x] `.artifacts` 内发布树不再被链接检查器错误跳过。
- [x] 同一 Git `HEAD` 下事实变更获得独立 working-tree source，避免快照冲突覆盖。
- [x] 重复 published event 不重复任务、反馈、回执或周期事实。

## Quality and Security Checks

- [x] Python scripts/tests 全部通过语法编译。
- [x] 5 条 GitHub workflow 通过 actionlint 1.7.12。
- [x] 11 个 GitHub YAML 文件通过解析。
- [x] GitHub Actions 均固定 40 位 commit SHA，PR workflow 不使用 write 权限、secret 或 `pull_request_target`。
- [x] 系统范围凭证模式扫描零命中；外部教学参考目录中的演示假密钥不进入系统/发布范围。
- [x] Pages 核心站点约 109 KB，低于 2 MB 目标。
- [x] 进度重复生成保持 1 个真实初始化事件和 2 份既有快照，无伪造历史。

## Issues Found

测试阶段发现并修复六项问题：Pages 缺少 `.github` 下钻证据、`.artifacts` 输出树被审计器跳过、active cycle 被旧 Should 抢占、dirty facts 与 `HEAD` 共用 source 导致快照冲突、Release 候选信任陈旧 current projection、macOS `/var` 与 `/private/var` 导致 policy 相对路径失败。每项均有回归测试。

## Notes

本报告证明闭环能力可运行，不代表真实书稿已经满足 v0.1。当前事实仍是 0/42、Reader A/B/C 未邀请、无 verified SHIP 实验、无可读样章、无核心图和无公开 Release；因此真实 readiness 保持 blocked 是正确结果。没有创建 commit、remote、tag、Pages deployment、GitHub Release、Project item 或外部消息。
