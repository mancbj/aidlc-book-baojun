---
id: 006-create-experiment-governance
unit: 001-github-writing-system-ui
intent: 001-github-writing-system
status: complete
priority: must
created: 2026-07-21T06:52:22.000Z
assigned_bolt: 001-github-writing-system-ui
implemented: true
---

# Story: 006-create-experiment-governance

## User Story

**As a** 技术作者
**I want** 把实验按 SHIP、KEEP-EXT、ALREADY 分类并验收
**So that** 正文承诺始终有可运行或可复现证据

## Acceptance Criteria

- [ ] **Given** 实验进入池时，**When** 执行对应动作，**Then** 编号、章节、分类、工作量、输入、输出、指标、运行命令和验收标准均存在
- [ ] **Given** 实验分类为 SHIP 时，**When** 执行对应动作，**Then** 仓库内实现、README、样例输入输出和测试均被要求
- [ ] **Given** 实验分类为 KEEP-EXT 时，**When** 执行对应动作，**Then** 外部来源、固定版本、配置、步骤和样例结果均被要求
- [ ] **Given** 实验分类为 ALREADY 时，**When** 执行对应动作，**Then** 复用实现和跨章引用均可解析
- [ ] **Given** 无法验证的概念被标记为未承诺，**When** 执行对应动作，**Then** 不能显示为已完成实验

## Technical Notes

- **Related Requirements**: FR-8
- 治理队列对应现有 EXPERIMENT_TRIAGE.md 思路
- 工作量使用 S/M/L，并在 14 天 MVP 中优先 SHIP 单一实验

## Dependencies

### Requires

- 001-scaffold-repository-fact-source

### Enables

- 016-establish-writing-review-feedback-loop
- 017-prepare-v0-1-release

## Edge Cases

| Scenario | Expected Behavior |
|----------|-------------------|
| 分类值未知 | 校验失败并列出三种允许值 |
| 外部实验需要秘密 | 只提交 env.example，不提交真实密钥 |

## Out of Scope

- 实现所有实验
- 运行重型商业引擎或训练任务
