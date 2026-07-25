# v0.8 Release Notes Candidate

> Readiness: **READY** · Source `06f01bcf41c376dc9bb84d63709f498a71128bf8` · Generated `2026-07-25T08:24:02Z`

## 新增内容

- 两个 ALREADY 实验转 verified：`EXP-07-01`、`EXP-08-01`（triage 保持 ALREADY，不改写为 SHIP）。
- 两个 KEEP-EXT 冻结复现转 verified：`EXP-04-03`、`EXP-05-03`（仅消费仓库内 pin 夹具，CI 不抓外网）。
- CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT；SHIP 仍为 18/18。
- CH-04 / CH-05 / CH-07 / CH-08 证据边界收紧；Reader 无真实回复时保留 `READER-RESPONSES` known-gap。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`06f01bcf41c376dc9bb84d63709f498a71128bf8`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.9：消化真实 Reader 反馈，并按需推进剩余 KEEP-EXT 或新内容周期。
