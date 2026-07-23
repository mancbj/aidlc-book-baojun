---
stage: implement
bolt: 004-github-writing-system-ui
created: 2026-07-22T03:13:47Z
---

# Implementation Walkthrough: Review, v0.1 Gate and Continuous Update Cycle

## Summary

Bolt 004 已实现写作决策、五类审校、匿名反馈、发布 readiness 和发布后下一周期的完整能力链。系统可以自动把真实关键更新投影为事件、快照、变更日志和驾驶舱，但当前内容事实仍为 0/42，真实 v0.1 门禁保持 blocked；本阶段没有把模板、fixture 或系统能力冒充成已完成书稿。

## Structure Overview

人工写作与审阅记录进入版本化反馈事实，进度引擎把反馈和周期纳入统一来源指纹及鸟瞰页面。v0.1 readiness 从任务、章节、实验、核心图、审校与反馈入口生成稳定缺口；只有实时门禁通过且 source SHA 一致，Release 候选和真实发布后的 v0.2 激活才可继续。所有外部 GitHub 写操作仍位于显式 workflow 权限边界内。

## Completed Work

- [x] `writer-chats/template.md`、`planning/reviews/chapter-review-template.md`、`planning/reviews/sample-chapter.md` - 提供脱敏写作决策和五类审校入口，并明确当前没有可审样章。
- [x] `docs/LEARNING.md`、`docs/READER-GUIDE.md`、`planning/feedback-template.md`、`planning/reader-invitations.md` - 提供三条学习路径、匿名试读和反馈说明，不虚构邀请或响应。
- [x] `feedback/decisions.json`、`feedback/README.md`、`progress/schemas/feedback-schema.md` - 建立最小化、匿名、可校验的反馈决策事实。
- [x] `scripts/validate_feedback.py`、`scripts/record_feedback.py` - 校验决策、读者槽位和周期，默认 dry-run 并拒绝敏感字段或无验收的 accepted 反馈。
- [x] `progress/cycles.json`、`progress/schemas/cycle-schema.md`、`planning/releases/v0.2-draft.md` - 建立 inactive v0.2 preview、周/月节奏和首个可执行 Must。
- [x] `scripts/progress_core.py`、`scripts/generate_progress.py`、`scripts/progress_render.py` - 把反馈、周期、带入项和公开缺口接入来源指纹、事件、快照、文字摘要、驾驶舱和稳定下钻。
- [x] `scripts/audit_roadmap_evidence.py`、`planning/releases/roadmap-evidence.md` - 对 42 个任务分类审计证据，不自动修改任务状态。
- [x] `planning/releases/v0.1-policy.json`、`planning/releases/v0.1-checklist.md`、`planning/reviews/release-blockers.md` - 固化二元 Definition of Done 和人工关闭规则。
- [x] `scripts/check_release_readiness.py`、`releases/v0.1-rc/readiness.json`、`releases/v0.1-rc/readiness.md` - 无论通过或阻断都生成排序、可修复、可追溯的机器与人类报告。
- [x] `scripts/render_release_notes.py`、`releases/v0.1-rc/release-notes.md`、`planning/releases/v0.1.md` - 从当前事实生成候选说明，并明确未发布状态。
- [x] `scripts/prepare_release.py`、`.github/workflows/release.yml`、`docs/V0.1-RELEASE-RUNBOOK.md` - 强制同源 readiness，blocked 时保留诊断 artifact 并停止 build/publish。
- [x] `scripts/open_next_cycle.py`、`.github/workflows/post-release.yml` - 只接受真实、非 draft 的 v0.1 published event，并再次验证实时 readiness 和 source 后生成回执、带入项、事件与 PR/artifact。
- [x] `scripts/prepare_pages.py`、`scripts/check_internal_links.py` - 将只读 GitHub 配置纳入 Pages 下钻，避免 `.artifacts` 输出树被链接审计错误跳过。
- [x] `README.md`、`docs/REPOSITORY-GUIDE.md`、`docs/PROGRESS-AUTOMATION.md`、`docs/RELEASE-AUTOMATION.md`、`.github/workflows/README.md` - 记录本地运行、失败恢复、最小权限和发布后闭环。
- [x] `releases/README.md`、`releases/v0.1-rc/README.md`、`writer-chats/README.md` - 区分候选证据、真实发布回执和写作记录入口。

## Key Decisions

- **能力与内容分层**：系统 Story 可以通过自动化测试验收，但真实 v0.1 只有内容事实满足门禁时才称为可发布。
- **实时二次门禁**：发布后的周期激活不信任陈旧报告，必须重新计算 readiness 并匹配发布 SHA。
- **事实源优先**：反馈、周期和发布回执进入同一版本化事实链；GitHub Projects、Pages 和 Release 都是投影或交付面。
- **显式副作用**：反馈写入需要 `--apply`，周期开启需要真实 published receipt，远程变更通过最小权限 PR job 完成。
- **隐私最小化**：只保存匿名槽位和必要决策摘要，拒绝个人信息、凭证和完整原始对话字段。

## Deviations from Plan

- Pages 冒烟暴露 `.github` 下钻文件未进入发布树，已加入只读配置证据和 `.nojekyll`。
- 内部链接检查原先会因输出根位于 `.artifacts` 而跳过整棵树，已改为只忽略相对扫描根内部的缓存目录。
- 周期激活在原计划的 published receipt 校验之外增加实时 readiness 重算与 source SHA 比对，避免绕过 Release workflow 后误激活。

## Dependencies Added

- [x] None - 核心实现继续仅使用 Python 标准库和仓库已有静态技术栈。

## Developer Notes

实现阶段冒烟结果为 59/59 既有测试通过、共享 CI 低于 2 秒、47 个 Pages 范围文件的 221 条内部链接零错误、五条 workflow 通过 actionlint 1.7.12。真实 readiness 为 44 blockers 和 1 known gap；路线证据为 0 verified、23 artifact-present-review-required、10 missing、9 path-divergence。Stage 3 仍需新增 Bolt 004 专项正常、失败、幂等和安全测试后才能完成 Bolt。
