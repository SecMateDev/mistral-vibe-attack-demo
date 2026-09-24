#!/usr/bin/env bash
set -euo pipefail

repository="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository"

./poc/cleanup.sh >/dev/null
./poc/prepare-fixture.sh >/dev/null
source demo-state/environment.sh

python3 poc/collector.py >demo-state/collector.log 2>&1 &
collector_pid=$!
cleanup() {
    kill "$collector_pid" 2>/dev/null || true
    wait "$collector_pid" 2>/dev/null || true
}
trap cleanup EXIT

for _ in {1..50}; do
    if python3 - <<'PY' >/dev/null 2>&1
from urllib.request import urlopen
with urlopen("http://127.0.0.1:8787/api/events", timeout=0.2) as response:
    response.read()
PY
    then
        break
    fi
    sleep 0.05
done

PATH="./.ci/bin:$PATH" cat README.md >demo-state/cat-output.txt

test "$(cat demo-state/status.txt)" = "callback_sent"
test -f demo-state/installed/secmate-demo-agent
cmp -s .ci/bin/cat demo-state/installed/secmate-demo-agent
python3 - <<'PY'
import json
from urllib.request import urlopen

with urlopen("http://127.0.0.1:8787/api/events", timeout=1) as response:
    events = json.load(response)["events"]
assert len(events) == 1, events
event = events[0]
assert event["event"] == "host_compromised"
assert event["credential_masked"] is True
assert event["credential"].endswith("93a2")
assert "demo_mistral_fixture_7f93a2" not in json.dumps(event)
PY

printf 'payload check: PASS\n'
