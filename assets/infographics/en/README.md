# English chapter infographics

High-resolution PNG posters for quick browsing (cover + CH-01–CH-10). Simplified Chinese versions will land under `assets/infographics/zh/` in a later release.

| File | Chapter |
| --- | --- |
| `cover-understanding-ai-dlc.png` | Book overview · *Understanding AI-DLC* |
| `ch01-ai-native-sdlc-infographic.png` | CH-01 |
| `ch02-human-judgment-reverse-conversation.png` | CH-02 |
| `ch03-inception-executable-plan.png` | CH-03 |
| `ch04-context-engineering-memory-bank.png` | CH-04 |
| `ch05-bolts-fast-execution.png` | CH-05 |
| `ch06-exsecutio-delivery-candidate.png` | CH-06 |
| `ch07-verification-loss-functions.png` | CH-07 |
| `ch08-operations-sustainable-runtime.png` | CH-08 |
| `ch09-adaptive-engineering-flow-governance.png` | CH-09 |
| `ch10-organization-metrics-operating-system.png` | CH-10 |

Canonical list: [`manifest.json`](manifest.json).

**Build / Release zip**

```bash
python3 scripts/build_infographic_assets.py --force --zip-version v0.9.007
```

Cover PNG is author-facing art; chapter PNGs are exported from `book/images/*.svg` at 1920px width unless replaced manually in this directory.
