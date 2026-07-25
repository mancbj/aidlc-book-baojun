# Round 07 · SVG Contract & Build Integration

**Decision:** KEEP

## 变更

- 新增 `book/images/chapter-figures.json` 章节图注册表
- `scripts/build_book.py` 的 `SUPPORT_FILES` 纳入注册表与九张章节 SVG
- 新增 `tests/test_chapter_figures.py`：存在性、正文引用、strict audit、术语边界

## 阶段评分

- Experiments: 33 / 35
- SVG: **12 / 30**
- Reader feedback: 5 / 15
- Book integration: **10 / 10**
- Release: 2 / 10
- **Total: 62 / 100**

下一阶段：按章嵌入并审校独立 SVG。
