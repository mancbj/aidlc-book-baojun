# v0.9.005 Release Candidate · Bilingual full book

GitHub Release 同时包含 **中文 + 英文** 各一份单页 HTML 与 PDF（共 4 个文件）。

## Assets

| File | Role |
| --- | --- |
| `aidlc-book-v0.9.005-book.html` | 中文 release-profile 单页 HTML |
| `aidlc-book-v0.9.005-en-book.html` | 英文 release-profile 单页 HTML |
| `aidlc-book-v0.9.005.pdf` | 中文 PDF |
| `aidlc-book-v0.9.005-en.pdf` | 英文 PDF |

## Build

```bash
python3 scripts/stage_release_rc_assets.py v0.9.005
python3 scripts/check_release_readiness.py --policy planning/releases/v0.9.005-policy.json \
  --json-report releases/v0.9.005-rc/readiness.json \
  --markdown-report releases/v0.9.005-rc/readiness.md
```

## Known gap

- `READER-RESPONSES` (policy known-gap)
