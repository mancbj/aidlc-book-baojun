# v0.9.004 Release Notes Candidate

> Readiness: **READY** · Source `efeb1130122021cebe379b65037c53e9b1e215ed` · Generated `2026-07-27T07:00:00Z`

## 新增内容

- 首次 **英文全书** release-profile HTML/PDF（`build_book --locale en` / `build_release_book.py --locale en`）。
- 英文十章 + Part 0 与中文同构结构；术语 Exsecutio / Bolt / Memory Bank 边界一致。
- 资产示例：`aidlc-book-v0.9.004-en.pdf`、单页 HTML；content-audit 剥离 Metadata/Gate。
- 实验 verified=30/30；Reader 非发布驱动。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`efeb1130122021cebe379b65037c53e9b1e215ed`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.9.005–008：Carbon 可视化阅读站与 Pages/Release 同源（见 v0.9-roadmap.md）。
