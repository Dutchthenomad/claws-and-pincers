#!/usr/bin/env bash
# config-drift-check.sh — Detect drift between repo openclaw.json5 and live openclaw.json
# Exit 0 = no drift, Exit 1 = drift detected, Exit 2 = error
set -euo pipefail

REPO_JSON5="/root/claws-and-pincers/openclaw.json5"
LIVE_JSON="/opt/openclaw/config/openclaw.json"
TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"' EXIT

if [[ ! -f "$REPO_JSON5" ]]; then
  echo "ERROR: Repo config not found: $REPO_JSON5" >&2
  exit 2
fi

if [[ ! -f "$LIVE_JSON" ]]; then
  echo "ERROR: Live config not found: $LIVE_JSON" >&2
  exit 2
fi

# Convert json5 to normalized JSON
python3 -c "
import json, json5, sys

with open('$REPO_JSON5') as f:
    data = json5.load(f)

# Remove keys that the gateway manages (meta, wizard) for comparison
for k in ['meta', 'wizard']:
    data.pop(k, None)

# Remove keys known to be unsupported by current gateway version
# (these are in json5 as aspirational but get stripped before deploy)
for agent in data.get('agents', {}).get('list', []):
    tools = agent.get('tools', {})
    if 'agentToAgent' in tools:
        del tools['agentToAgent']
    if 'profile' in tools:
        del tools['profile']

# Remove hooks section (requires token not yet configured)
if 'hooks' in data:
    del data['hooks']

# Remove gateway.openaiApi (not yet supported)
if 'openaiApi' in data.get('gateway', {}):
    del data['gateway']['openaiApi']

# Normalize developer sandbox to 'off' (lenient not supported)
for agent in data.get('agents', {}).get('list', []):
    if agent.get('id') == 'developer' and agent.get('sandbox', {}).get('mode') == 'lenient':
        agent['sandbox']['mode'] = 'off'

json.dump(data, open('$TMP_DIR/repo.json', 'w'), indent=2, sort_keys=True, ensure_ascii=False)
" || exit 2

# Normalize live JSON (remove gateway-managed keys)
python3 -c "
import json
with open('$LIVE_JSON') as f:
    data = json.load(f)
for k in ['meta', 'wizard']:
    data.pop(k, None)
json.dump(data, open('$TMP_DIR/live.json', 'w'), indent=2, sort_keys=True, ensure_ascii=False)
" || exit 2

# Diff
if diff -u "$TMP_DIR/repo.json" "$TMP_DIR/live.json" > "$TMP_DIR/drift.diff" 2>&1; then
  echo "No config drift detected."
  exit 0
else
  echo "CONFIG DRIFT DETECTED:"
  echo "--- repo (source of truth)"
  echo "+++ live (gateway)"
  cat "$TMP_DIR/drift.diff"
  exit 1
fi
