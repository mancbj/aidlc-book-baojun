# Book locales · zh / en

The repository supports two Pandoc build locales via `scripts/build_book.py --locale`.

| Locale | Source tree | Output HTML | Output PDF | Scope (v0.9.001) |
| --- | --- | --- | --- | --- |
| `zh` (default) | `book/` | `deep-understanding-ai-dlc.html` | `deep-understanding-ai-dlc.pdf` | Full Part 0 + 10 chapters |
| `en` | `book/en/` | `deep-understanding-ai-dlc-en.html` | `deep-understanding-ai-dlc-en.pdf` | Part 0 + front matter + glossary; chapters in v0.9.002+ |

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
2. **English mirror:** chapter files appear under `book/en/chapters/` starting v0.9.002; until then, `book/en/toc.md` lists planned chapters.
3. **Shared assets:** images, fonts, CSS, and Lua filters stay under `book/`; English markdown uses `../images/...` where needed.
4. **Manifest:** every build writes `build-manifest.json` with `"locale": "zh"|"en"` and hashed sources.

## Roadmap

See [`planning/releases/v0.9-roadmap.md`](../planning/releases/v0.9-roadmap.md).
