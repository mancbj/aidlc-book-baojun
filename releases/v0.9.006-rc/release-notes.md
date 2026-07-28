# v0.9.006 Release Notes Candidate

> Readiness: **READY** · Source `795c1f0ad55725814b09c84ba6f601c2df9a583e` · Generated `2026-07-28T00:16:48Z`

## 新增内容

- **新增双语 Markdown 全书**：`aidlc-book-v0.9.006-book.md`（中文）与 `-en-book.md`（英文），与 HTML/PDF 同源章节拼接。
- 继续包含 v0.9.005 四类 HTML/PDF 资产 + Pages zip；GitHub Release **标题**含本版摘要。
- 构建：`scripts/build_release_markdown.py` + `stage_release_rc_assets.py`；实验 verified=30/30。
- Reader 仍为 known-gap。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`795c1f0ad55725814b09c84ba6f601c2df9a583e`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.9.007+：阅读体验与 Release 维护；见 planning/publication/v0.9-loop-orchestration.md。
