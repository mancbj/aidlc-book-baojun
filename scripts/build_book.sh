#!/usr/bin/env bash
set -euo pipefail

script_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
repo_root="$(cd -- "$script_dir/.." && pwd)"
output_dir="${1:-$repo_root/.artifacts/book}"
build_format="${2:-${BOOK_BUILD_FORMAT:-html}}"

args=(--root "$repo_root" --output "$output_dir" --format "$build_format")
if [[ -n "${BOOK_BUILD_GENERATED_AT:-}" ]]; then
  args+=(--generated-at "$BOOK_BUILD_GENERATED_AT")
fi

python3 "$script_dir/build_book.py" "${args[@]}"
