# v0.3 Release Notes Candidate

> Readiness: **READY** · Source `75b7b70f0cfde5e0b85643b1ab1324aed2abfbbc` · Generated `2026-07-25T00:14:43Z`

## 新增内容

- 出版质量 Loop：release profile 剥离 Metadata / Gate / Review Notes 等写作脚手架。
- 书稿 HTML 设计系统升级（品牌级标题、衬线字体、青绿强调与可读动效）。
- 书稿 PDF 章节分页与页边距优化；十章正式可读稿保持完整。
- 内容边界收紧：Runtime Verify 与 CH-07 验证区分；ready/planned 实验不再过宣称。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`75b7b70f0cfde5e0b85643b1ab1324aed2abfbbc`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.4：推进 planned 实验实现、独立章节 SVG，并消化 Reader 反馈缺口。
