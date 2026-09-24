#!/usr/bin/env bash
set -euo pipefail

repository="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cache_dir="${UV_CACHE_DIR:-$repository/demo-state/uv-cache}"

run_check() {
    local version="$1"
    local expected="$2"
    UV_CACHE_DIR="$cache_dir" uv run --isolated --no-project \
        --with "mistral-vibe==$version" \
        python "$repository/poc/resolve_permission.py" --expect "$expected"
}

run_check 2.25.0 always
run_check 2.25.8 ask
