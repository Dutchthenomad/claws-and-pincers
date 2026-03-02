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

# Convert json5 to normalized JSON (strip comments, fix bare keys, remove trailing commas)
python3 -c "
import re, json, sys

with open('$REPO_JSON5') as f:
    raw = f.read()

# Strip // comments
lines = raw.split('\n')
cleaned = []
for line in lines:
    result = []
    in_string = False
    escape = False
    i = 0
    while i < len(line):
        c = line[i]
        if escape:
            result.append(c)
            escape = False
            i += 1
            continue
        if c == '\\\\' and in_string:
            result.append(c)
            escape = True
            i += 1
            continue
        if c == '\"':
            in_string = not in_string
            result.append(c)
            i += 1
            continue
        if not in_string and c == '/' and i+1 < len(line) and line[i+1] == '/':
            break
        result.append(c)
        i += 1
    cleaned.append(''.join(result))

text = '\n'.join(cleaned)
text = re.sub(r'(?<=[{,\n])\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r' \"\1\":', text)
text = re.sub(r',\s*([}\]])', r' \1', text)

try:
    data = json.loads(text)
except json.JSONDecodeError as e:
    print(f'ERROR: Failed to parse json5: {e}', file=sys.stderr)
    sys.exit(2)

# Remove keys that the gateway manages (meta, wizard) for comparison
for k in ['meta', 'wizard']:
    data.pop(k, None)

# Remove keys known to be unsupported by current gateway version
# (these are in json5 as aspirational but get stripped before deploy)
for agent in data.get('agents', {}).get('list', []):
    if 'agentToAgent' in agent.get('tools', {}):
        del agent['tools']['agentToAgent']
if 'webhooks' in data.get('hooks', {}):
    del data['hooks']['webhooks']
if data.get('hooks') == {'enabled': True}:
    del data['hooks']
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
