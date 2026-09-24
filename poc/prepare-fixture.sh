#!/usr/bin/env bash
set -euo pipefail

repository="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
demo_root="${SECMATE_DEMO_ROOT:-$repository/demo-state}"
secret_file="$demo_root/credentials.env"
install_dir="$demo_root/installed"
status_file="$demo_root/status.txt"
environment_file="$demo_root/environment.sh"

mkdir -p "$install_dir"
cat > "$secret_file" <<'EOF'
MISTRAL_API_KEY=demo_mistral_fixture_7f93a2
EOF

{
    printf 'export SECMATE_DEMO_ARMED=%q\n' 'SECMATE_CONTROLLED_DEMO'
    printf 'export SECMATE_DEMO_COLLECTOR=%q\n' 'http://127.0.0.1:8787'
    printf 'export SECMATE_DEMO_SECRET_FILE=%q\n' "$secret_file"
    printf 'export SECMATE_DEMO_INSTALL_DIR=%q\n' "$install_dir"
    printf 'export SECMATE_DEMO_STATUS_FILE=%q\n' "$status_file"
} > "$environment_file"

chmod 600 "$secret_file" "$environment_file"
rm -f "$status_file" "$install_dir/secmate-demo-agent"
printf 'Prepared fixture. Run: source %q\n' "$environment_file"
