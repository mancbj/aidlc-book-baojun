#!/usr/bin/env python3
"""Build the publication (release-profile) HTML/PDF book candidate."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Sequence

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_book import build  # noqa: E402


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, default=Path(".artifacts/book-release"))
    parser.add_argument("--format", choices=("html", "pdf", "all"), default="all")
    parser.add_argument("--generated-at", help="fixed ISO-8601 build time for reproducible tests")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    generated_at = args.generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )
    try:
        manifest = build(
            args.root,
            args.output,
            generated_at,
            args.format,
            profile="release",
        )
    except (OSError, RuntimeError, UnicodeError) as exc:
        print(f"[ERROR] {exc}")
        return 1
    output = args.output.resolve()
    for item in manifest["outputs"]:
        print(f"[OK] Release candidate: {output / item['path']}")
    print(f"[OK] Build manifest: {output / 'build-manifest.json'}")
    print(f"[OK] Profile: {manifest.get('profile')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
