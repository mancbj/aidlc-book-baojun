# Round 02 · Structure Noise (References)

**Decision:** KEEP

## 目标

发布产物中移除章末内部路径型 `References`，避免读者在正式书稿里看到生产线文件清单。

## 变更

- `book/filters/release-profile.lua`：额外剥离 `## References` / `## 参考文献`
- 单测同步断言：章末内部引用不再进入 release 文本；`Reader Exercise` 保留

## 验证

- HTML 卫生审计 PASS
- `References` 标题计数：0
- `写作任务卡`：0
- 正文案例中的 `progress/tasks.json`、组织层责任表示例保留（属方法论案例，非脚手架）

## 评分

- Content: **38 / 50**
- HTML: **12 / 25**
- PDF: **14 / 25**
- **Total: 64 / 100**

## 下一轮

Round 03：证据边界——扫描并修正把 `planned` 写成已验证的表述。
