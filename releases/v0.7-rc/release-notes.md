# v0.7 Release Notes Candidate

> Readiness: **READY** · Source `a5355a0466f605bd7d845bd2ce8b1857ad07e873` · Generated `2026-07-25T08:40:00Z`

## 新增内容

- 四个冻结证据实验转 verified：`EXP-01-01`、`EXP-01-02`、`EXP-02-02`、`EXP-07-02`（无在线模型调用）。
- SHIP verified 达到 18/18；CI 合同测试覆盖全部 SHIP。
- CH-01 / CH-02 / CH-07 证据边界收紧，明确冻结夹具不等于生产模型保证。
- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`a5355a0466f605bd7d845bd2ce8b1857ad07e873`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.8：消化真实 Reader 反馈，并按需推进 KEEP-EXT / ALREADY 实验或新内容周期。
