# Round 01 · Release Content Hygiene

**Decision:** KEEP

## 目标

发布产物剥离写作/生产元信息；源稿保留脚手架。

## 变更

- 新增 `book/filters/release-profile.lua`
- `scripts/build_book.py` 支持 `--profile release`
- 新增 `scripts/build_release_book.py`
- 新增 `scripts/audit_release_content.py`
- 新增 `tests/test_release_profile.py`；更新 source 计数为 19

剥离范围：

- `## Metadata` 整段
- 精确标题 `### Gate`（保留正文 `Gates：阶段门禁...`）
- `Review Notes` / `Review：` 审校段
- 宣言 `D01-Txx 验收`、`来源记录`
- 目录 `核心问题去重审计`、`v0.1 边界`、`D01-T03 持续验收`
- 保留：`来源与证据规则`、章节 References、正文中的方法论叙述

## 验证

```bash
python3 -m unittest tests.test_release_profile -v
python3 scripts/build_release_book.py --format all ...
python3 scripts/audit_release_content.py --html ... --pdf-text ...
```

结果：

- HTML/PDF 卫生审计：**PASS**
- 关键泄漏标记计数均为 0
- `阶段门禁防止错误级联`、`来源与证据规则`、`Exsecutio`、第 10 章均保留
- PDF 页数：112 → **103**

## 评分

- Content: **34 / 50**（卫生硬门禁通过；边界/术语/视觉仍待后续轮）
- HTML: **12 / 25**
- PDF: **14 / 25**
- **Total: 60 / 100**

## 下一轮

Round 02：清理正文 References / 叙述中仍偏“生产线内部”的噪音，但不削弱方法论证据链。
