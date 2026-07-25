# v0.8.004 Release Notes Candidate

> Readiness: **READY** · Source `596ea9eb489aa56edcfb803ec0e24bbd9ace0839` · Generated `2026-07-25T10:09:47Z`

## 新增内容

- PDF 封面改为按 A4 页面高度铺满、水平居中裁切，消除底部白带。
- 公式等号后 `𝓔（人的判断 + AI 能力）` 提升到主公式同级字号，并按共同视觉中线对齐。
- 保持实验 verified=30/30 与既有术语/证据边界，不覆盖已发布 v0.8.003 资产。
- Reader 无真实回复时继续保留 `READER-RESPONSES` known-gap。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`596ea9eb489aa56edcfb803ec0e24bbd9ace0839`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.8.005：消化真实 Reader 反馈，或开启新内容周期。
