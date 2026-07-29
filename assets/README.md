# Repository assets

Static images referenced from the README and docs.

| File | Source |
| --- | --- |
| `star-history-light.png` | `scripts/gen_star_history.py` (light theme) |
| `star-history-dark.png` | `scripts/gen_star_history.py` (dark theme) |
| `infographics/en/*.png` | `scripts/build_infographic_assets.py` (English chapter posters + cover) |

Charts refresh daily via `.github/workflows/star-history.yml`. Regenerate locally:

```bash
pip install -r scripts/requirements-star-history.txt
python3 scripts/gen_star_history.py --refresh
```
