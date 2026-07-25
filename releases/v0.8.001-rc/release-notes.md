# v0.8.001 Release Notes Candidate

> Readiness: **READY** · Source `46458b495107a55ae3f22e51763a35eae502a3ea` · Generated `2026-07-25T08:40:10Z`

## 新增内容

- 版本颗粒度改为 patch-grain：`v0.8.001`（见 `planning/releases/VERSIONING.md`）。
- 四个 KEEP-EXT 冻结复现转 verified：`EXP-01-03`、`EXP-02-03`、`EXP-03-03`、`EXP-06-03`（triage 不改写为 SHIP）。
- CI 合同测试覆盖全部 verified 的 SHIP / ALREADY / KEEP-EXT；SHIP 仍为 18/18。
- CH-01 / CH-02 / CH-03 / CH-06 证据边界收紧；Reader 无真实回复时保留 `READER-RESPONSES` known-gap。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`46458b495107a55ae3f22e51763a35eae502a3ea`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.8.002：消化真实 Reader 反馈，并推进剩余 KEEP-EXT（07-03 / 08-03 / 09-03 / 10-03）。
