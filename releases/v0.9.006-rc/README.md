# v0.9.006 Release Candidate · Bilingual Markdown + HTML/PDF

## Assets (6 book files)

| File | 语言 / 格式 |
| --- | --- |
| `aidlc-book-v0.9.006-book.md` | 中文 Markdown 全书 |
| `aidlc-book-v0.9.006-en-book.md` | 英文 Markdown 全书 |
| `aidlc-book-v0.9.006-book.html` | 中文单页 HTML |
| `aidlc-book-v0.9.006-en-book.html` | 英文单页 HTML |
| `aidlc-book-v0.9.006.pdf` | 中文 PDF |
| `aidlc-book-v0.9.006-en.pdf` | 英文 PDF |

GitHub Release 标题（见 `release-title.txt`）：**v0.9.006 · 中英 Markdown 全书 + 双语 HTML/PDF**

## Build

```bash
python3 scripts/build_release_markdown.py v0.9.006
# HTML/PDF：scripts/stage_release_rc_assets.py v0.9.006
```
