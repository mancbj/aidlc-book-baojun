# v0.1 Release Candidate Workspace

状态：**RC PREFLIGHT GENERATED / RELEASE BLOCKED**。此目录是候选证据区，不是已发布版本声明。

- [`readiness.md`](readiness.md)：按优先级排序的人类可读缺口。
- [`readiness.json`](readiness.json)：供工作流和候选构建使用的机器门禁。
- [`release-notes.md`](release-notes.md)：从当前事实生成的候选说明；blocked 时不可作为正式 Notes。
- [`planning/releases/v0.1-checklist.md`](../../planning/releases/v0.1-checklist.md)：人工发布清单。

## D13-T03 Local RC Preflight

本地已生成 HTML-first 预检候选包：

- Version: `v0.1-rc.1`
- Output: `.artifacts/release/v0.1-rc.1/`
- Manifest: `.artifacts/release/v0.1-rc.1/release-manifest.json`
- HTML zip: `.artifacts/release/v0.1-rc.1/aidlc-book-v0.1-rc.1-html.zip`
- PDF: `.artifacts/release/v0.1-rc.1/aidlc-book-v0.1-rc.1.pdf`
- Notes: `.artifacts/release/v0.1-rc.1/release-notes.md`

该预检包用于验证打包、哈希、页面入口、PDF 附件和 Release Notes 链路。因为当前 `readiness` 仍被 D14 发布前任务阻断，它不能冒充正式可发布候选，也不能用于 GitHub Release 上传。

门禁通过后，使用同一 source 的 `readiness=ready` 与 Release Notes 重新构建正式候选。不要手工把本目录状态改为 ready。
