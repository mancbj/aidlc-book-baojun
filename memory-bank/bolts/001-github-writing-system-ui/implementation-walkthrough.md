---
stage: implement
bolt: 001-github-writing-system-ui
created: 2026-07-21T07:14:12Z
---

# Implementation Walkthrough: GitHub Writing System Foundation

## Summary

Bolt 001 的基础层已经落地。工作区现已初始化为本地 Git 仓库，并建立了书稿、规划、进度事实源、脚本、测试、写作对话和未来 GitHub 工作流的职责边界。

14 天计划已转换为 42 个机器可读任务；十章各自具有固定六阶段；实验池包含 30 个候选实验。纯 Python 标准库校验器能够在不依赖网络或数据库的情况下检查真实事实源。

## Structure Overview

仓库采用三层结构：

1. 人工内容层：书稿、路线、模板和说明。
2. 运行事实层：任务、章节和实验 JSON。
3. AI-DLC 审计层：Intent、Stories、Bolts 和 Construction Log。

Markdown 不保存手工聚合统计，未来驾驶舱和 GitHub Projects 都从运行事实层投影。

## Completed Work

- [x] `.git/` - 初始化本地 main 分支；没有 commit、remote 或推送。
- [x] `.gitignore` - 忽略系统文件、Python 缓存、虚拟环境和秘密。
- [x] `README.md` - 提供定位、核心公式、14 天目标、事实源、章节、实验和校验入口。
- [x] `docs/REPOSITORY-GUIDE.md` - 说明目录职责、权威源、生成边界和安全规则。
- [x] `book/README.md` - 书稿目录入口。
- [x] `book/manifesto.md` - 核心公式、五条边界和 Day 1 验收。
- [x] `book/toc.md` - 十章主题、唯一问题和实验方向。
- [x] `book/chapter-template.md` - Question、Framework、Example、Experiment、Figure、Review 六阶段模板。
- [x] `planning/README.md` - 规划目录入口和事实源说明。
- [x] `planning/14-day-v0.1.md` - Day 1–14 人类可读导航。
- [x] `planning/experiment-card-template.md` - 三类实验通用卡片。
- [x] `EXPERIMENT_TRIAGE.md` - SHIP、KEEP-EXT、ALREADY 治理规则。
- [x] `progress/README.md` - 运行事实目录说明。
- [x] `progress/tasks.json` - 42 个稳定任务，每天三项。
- [x] `progress/chapters.json` - 10 章固定六阶段状态。
- [x] `progress/experiments.json` - 20 个 SHIP、9 个 KEEP-EXT、1 个 ALREADY 候选。
- [x] `progress/schemas/task-schema.md` - 任务字段、六种状态、blocked 和 done 门禁。
- [x] `progress/schemas/chapter-schema.md` - 章节阶段和下一缺口规则。
- [x] `progress/schemas/experiment-schema.md` - 三类实验条件式字段。
- [x] `scripts/README.md` - 自动化入口说明。
- [x] `scripts/validate_project.py` - 任务、章节、实验和依赖完整性校验。
- [x] `tests/README.md` - 测试运行入口。
- [x] `tests/test_validate_project.py` - 正常、边界和失败数据测试。
- [x] `writer-chats/README.md` - 对话摘要、决策和隐私规则。
- [x] `.github/workflows/README.md` - 未来 PR、快照、Pages 和 Release 工作流职责。

## Validation Performed During Implementation

- [x] Python 语法编译检查通过。
- [x] 真实事实源校验通过。
- [x] 任务数量为 42，Day 1–14 每天恰好三项。
- [x] 章节数量为 10，每章恰好六阶段。
- [x] 实验数量为 30，三类治理规则均有实例。
- [x] Git remote 为空，没有远程副作用。

正式 unittest、失败用例和 Story 验收将在 Stage 3 执行并记录。

## Key Decisions

- **JSON 是运行事实源**：Python 标准库可直接解析，适合 Git diff 和确定性生成。
- **Markdown 是解释和导航**：避免人工维护完成率造成两套数字。
- **memory-bank 是审计层**：不与作者的 14 天任务共用状态源。
- **GitHub Projects 是未来投影**：权限或同步失败不能破坏仓库事实源。
- **保留 working-book**：现有空目录没有迁移或删除。
- **不引入第三方依赖**：校验器和测试仅使用 Python 3.9 标准库。

## Deviations from Plan

None。交付范围、数据数量、技术约束和远程边界均按批准计划执行。

## Dependencies Added

- [x] None - 未安装第三方包、Pandoc 或 XeLaTeX。

## Developer Notes

- 当前根仓库尚无 commit；Git 初始化只是为了建立后续 GitHub 工作基础。
- `progress/tasks.json` 的第一个任务为 ready，其余任务按依赖链保持 backlog。
- 所有新任务验收初始为未通过；模板存在不代表对应写作任务已经完成。
- PDF、驾驶舱、事件、快照和 GitHub Actions 分别留给后续 Bolts。
- 正式连接 GitHub 前仍需确定远程仓库地址、公开性和 Project 范围。
