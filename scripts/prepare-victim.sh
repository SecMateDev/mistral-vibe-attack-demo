#!/usr/bin/env bash
set -euo pipefail

collector="${1:-http://127.0.0.1:8787}"
demo_root="${SECMATE_DEMO_ROOT:-$HOME/.secmate-vibe-demo}"
secret_file="$demo_root/credentials.env"
install_dir="$demo_root/installed"
environment_file="$demo_root/environment.sh"

mkdir -p "$demo_root"
cat > "$secret_file" <<'EOF'
MISTRAL_API_KEY=demo_mistral_sk_video_fixture_7f93a2
EOF

cat > "$environment_file" <<EOF
export SECMATE_DEMO_ARMED=SECMATE_CONTROLLED_DEMO
export SECMATE_DEMO_COLLECTOR=$collector
export SECMATE_DEMO_SECRET_FILE=$secret_file
export SECMATE_DEMO_INSTALL_DIR=$install_dir
EOF

chmod 600 "$secret_file" "$environment_file"
printf 'Prepared controlled victim fixture.\nRun: source %q\n' "$environment_file"

