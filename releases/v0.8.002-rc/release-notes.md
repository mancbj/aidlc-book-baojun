# v0.8.002 Release Notes Candidate

> Readiness: **READY** · Source `e5f278e71d0cae22e52a3bddd20ed671917d3e3b` · Generated `2026-07-25T08:59:27Z`

## 新增内容

- 四个 KEEP-EXT 收尾转 verified：`EXP-07-03`、`EXP-08-03`、`EXP-09-03`、`EXP-10-03`（triage 不改写为 SHIP）。
- 全部实验 verified=30/30；CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT。
- CH-07 / CH-08 / CH-09 / CH-10 证据边界收紧；明确 CH-07 Verify ≠ CH-08 Runtime Verify。
- Reader 无真实回复时保留 `READER-RESPONSES` known-gap；下一版默认 `v0.8.003`。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`e5f278e71d0cae22e52a3bddd20ed671917d3e3b`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.8.003：消化真实 Reader 反馈，或开启新内容/度量周期。
