#!/usr/bin/env bash
set -euo pipefail

repository="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo_root="${SECMATE_DEMO_ROOT:-$repository/demo-state}"

rm -rf -- "$demo_root"
printf 'Removed %s\n' "$demo_root"
