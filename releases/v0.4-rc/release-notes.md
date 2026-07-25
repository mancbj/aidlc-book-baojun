# v0.4 Release Notes Candidate

> Readiness: **READY** · Source `2238fd71b151302e5dff180435c01bbc630dc71a` · Generated `2026-07-25T07:35:00Z`

## 新增内容

- 四个目标实验转 verified：`EXP-03-02`、`EXP-06-01`、`EXP-02-01`、`EXP-04-02`，并由 CI 执行合同测试。
- CH-02～CH-10 九张独立可审计章节 SVG；CH-01 继续复用核心图 `fig0-1.svg`。
- 章节图注册表、构建哈希与 strict audit 门禁进入主线。
- Reader 反馈诚实重评：无真实回复时保留 `READER-RESPONSES` known-gap，不伪造 responded。

## 关键指标

- 任务：72/72（100.0%）
- Must：70/70
- 章节：10/10 六阶段完成
- 实验：SHIP 18 · KEEP-EXT 10 · ALREADY 2

## 已知缺口

- **known-gap · READER-RESPONSES** — `Reader-A/B/C`：保留反馈入口；真实邀请/响应后更新匿名槽位。

## 产物与来源

- Source commit/fingerprint：`2238fd71b151302e5dff180435c01bbc630dc71a`
- Pages HTML zip：候选 manifest 生成后填写文件名和 SHA-256。
- 书稿 HTML：通过 `--book-html` 纳入时记录文件名和 SHA-256。
- PDF：条件式；缺少经过验证的 PDF 时明确 skipped，不创建占位文件。
- 驾驶舱：`site/index.html`
- 反馈：`planning/feedback-template.md` 或 GitHub Feedback Issue Form

## 下一版本目标

v0.5：继续推进剩余 planned 实验，并在收到真实 Reader 回复后关闭反馈缺口。
