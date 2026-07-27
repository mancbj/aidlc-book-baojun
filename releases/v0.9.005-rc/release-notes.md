# v0.9.005 Release Notes Candidate

> Readiness: **READY** · Source `2f964824ba943bbede0ed7f6dd4cf2e35d5dce20` · Generated `2026-07-27T08:32:06Z`

## 新增内容

- **双语 Release 四类资产**：中文/英文各一份单页 HTML 与 PDF（`-book.html` / `-en-book.html` / `.pdf` / `-en.pdf`）。
- 构建：`scripts/stage_release_rc_assets.py v0.9.005`；Release workflow 在缺失 RC 文件时同源重构建。
- 继承 v0.9.004 英文全书与 v0.9.008 Pages 阅读站；实验 verified=30/30。
- Reader 仍为 known-gap。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`2f964824ba943bbede0ed7f6dd4cf2e35d5dce20`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.9.006+：阅读器与 Release 体验维护；见 planning/publication/v0.9-loop-orchestration.md。
