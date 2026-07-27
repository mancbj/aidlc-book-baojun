# Book locales · zh / en

The repository supports two Pandoc build locales via `scripts/build_book.py --locale`.

| Locale | Source tree | Output HTML | Output PDF | Scope (v0.9.002) |
| --- | --- | --- | --- | --- |
| `zh` (default) | `book/` | `deep-understanding-ai-dlc.html` | `deep-understanding-ai-dlc.pdf` | Full Part 0 + 10 chapters |
| `en` | `book/en/` | `deep-understanding-ai-dlc-en.html` | `deep-understanding-ai-dlc-en.pdf` | Part 0 + CH01–03 + glossary; CH04–10 in v0.9.003+ |

## Commands

```bash
# Chinese (default)
python3 scripts/build_book.py --format html --locale zh

# English spine
python3 scripts/build_book.py --format html --locale en --output .artifacts/book-en

# Shell wrapper
BOOK_BUILD_LOCALE=en ./scripts/build_book.sh .artifacts/book-en html en
```

Release profile:

```bash
python3 scripts/build_release_book.py --locale en --output .artifacts/book-release-en --format html
```

## Authoring rules

1. **Chinese canonical:** substantive chapter edits land in `book/chapters/` first unless doing a deliberate EN-only addendum.
2. **English mirror:** chapter files under `book/en/chapters/`; `book/en/toc.md` marks available vs planned patches.
3. **Shared assets:** images, fonts, CSS, and Lua filters stay under `book/`; chapter markdown (zh and en) uses `images/...` targets so Pandoc `--resource-path` resolves to `book/images/`.
4. **Manifest:** every build writes `build-manifest.json` with `"locale": "zh"|"en"` and hashed sources.

## Roadmap

See [`planning/releases/v0.9-roadmap.md`](../planning/releases/v0.9-roadmap.md).
