# Browser Automation — OpenClaw on ThinkPad

> **Status**: OPERATIONAL (2026-02-28)
> **Machine**: devops-ThinkPad-P52 (local dev workstation)
> **Tailscale IP**: 100.91.65.58
> **OpenClaw version**: v2026.2.1

---

## Overview

Browser automation runs on the **ThinkPad P52 local workstation**, not the VPS. This is by design — the Chrome extension relay must run on the same machine as the browser. The ThinkPad has its own OpenClaw gateway instance separate from `srv1216617`.

Two profiles are available:

| Profile | Command flag | Extension needed? | Has your logins? | Best for |
|---------|-------------|-------------------|-----------------|----------|
| `openclaw` | `--browser-profile openclaw` | No | No | Headless automation, always-on tasks |
| `chrome` | `--browser-profile chrome` | Yes (click icon on tab) | Yes | Tasks needing existing sessions |

---

## Running Services (ThinkPad)

| Service | Location | Port | Systemd unit |
|---------|----------|------|-------------|
| OpenClaw Gateway | `ws://127.0.0.1:18789` | 18789 | `openclaw-gateway.service` |
| Node Host | `ThinkPad-Chrome` | — | `openclaw-node.service` |
| CDP Relay | `http://127.0.0.1:18792` | 18792 | (managed by node host) |
| Chrome Extension | `~/.openclaw/browser/chrome-extension` | — | Loaded in Chrome |
| Managed Browser | `http://127.0.0.1:18800` (cdpPort) | 18800 | (on-demand) |

### Service management

```bash
# Gateway
openclaw gateway status
openclaw gateway restart

# Node host (browser relay)
openclaw node status
systemctl --user restart openclaw-node.service

# Check both
openclaw status
```

---

## Quick Start

### Managed browser (headless, no extension click needed)

```bash
# Start and open a page
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com

# Take a snapshot (AI element refs for clicking/typing)
openclaw browser --browser-profile openclaw snapshot

# Take a screenshot
openclaw browser --browser-profile openclaw screenshot

# List open tabs
openclaw browser --browser-profile openclaw tabs

# Click element by ref (get refs from snapshot)
openclaw browser --browser-profile openclaw click e6

# Type into element
openclaw browser --browser-profile openclaw type e3 "hello world"

# Navigate
openclaw browser --browser-profile openclaw navigate https://github.com

# Stop
openclaw browser --browser-profile openclaw stop
```

### Chrome relay (uses your existing Chrome + logins)

1. Click the **OpenClaw lobster icon** in the Chrome toolbar while on any regular tab (badge shows ON)
2. Then use:

```bash
openclaw browser --browser-profile chrome tabs
openclaw browser --browser-profile chrome snapshot
openclaw browser --browser-profile chrome screenshot
```

---

## Chrome Extension

**Extension ID**: `nohmhjibojecgcjfnpcckeegpoaokghn`
**Options page**: `chrome-extension://nohmhjibojecgcjfnpcckeegpoaokghn/options.html`
**Install path**: `~/.openclaw/browser/chrome-extension`
**Relay port**: 18792 (default, do not change)
**Status**: Relay reachable at `http://127.0.0.1:18792/`

To reload after reinstall:
1. `chrome://extensions` → Developer mode → Load unpacked
2. Select `~/.openclaw/browser/chrome-extension`
3. A Desktop shortcut at `~/Desktop/openclaw-extension` also points to the same files

---

## Snapshot Reference System

Snapshots return element refs (e.g. `e3`, `e12`) that can be passed to `click`, `type`, `hover`, etc:

```bash
# AI snapshot (default) — numeric refs
openclaw browser --browser-profile openclaw snapshot

# Role/accessibility snapshot
openclaw browser --browser-profile openclaw snapshot --format aria

# Efficient snapshot (reduced output)
openclaw browser --browser-profile openclaw snapshot --efficient

# Interactive only (actionable elements only)
openclaw browser --browser-profile openclaw snapshot --interactive
```

---

## Form Automation Workflow

```bash
# 1. Navigate to form page
openclaw browser --browser-profile openclaw navigate https://example.com/form

# 2. Snapshot to identify fields
openclaw browser --browser-profile openclaw snapshot

# 3. Fill fields using refs from snapshot
openclaw browser --browser-profile openclaw type e5 "John Doe"
openclaw browser --browser-profile openclaw type e6 "john@example.com"
openclaw browser --browser-profile openclaw select e8 "United States"

# 4. Submit
openclaw browser --browser-profile openclaw click e12

# 5. Verify
openclaw browser --browser-profile openclaw screenshot
```

---

## Playwright

Playwright v1.58.2 is installed globally. Required for:
- `snapshot` (AI/role)
- `screenshot`
- `navigate`, `click`, `type`, `drag`, `select`
- PDF export

Check: `npx playwright --version`

If Playwright errors appear: `npm install -g playwright && npx playwright install chromium`

---

## Node Host Pairing

The node host `ThinkPad-Chrome` is permanently paired to the local gateway. To verify:

```bash
openclaw nodes status
# Should show: ThinkPad-Chrome · paired · connected
```

If it shows disconnected:
```bash
systemctl --user restart openclaw-node.service
sleep 5
openclaw nodes status
```

If pairing is broken entirely:
```bash
openclaw node uninstall
openclaw node install --host 127.0.0.1 --port 18789 --display-name "ThinkPad-Chrome"
systemctl --user start openclaw-node.service
openclaw nodes pending
# No manual approval needed for local gateway
```

---

## Gateway Auth Token

The gateway requires auth. The token is stored in `~/.openclaw/openclaw.json` (`gateway.auth.token`).

The node host and Chrome extension both read the token automatically from config. No manual token passing needed.

To retrieve: `openclaw config get gateway.auth.token`

---

## Relationship to VPS Gateway

These are **two separate OpenClaw instances**:

| | ThinkPad | VPS (srv1216617) |
|---|---|---|
| Purpose | Browser automation, local dev | 5 Discord agents |
| Gateway port | 18789 | 18789 |
| Auth | Separate token | Separate token (gateway-token.txt) |
| Agents | `main` (default) | orchestrator, researcher, developer, sysadmin, reviewer |
| Access | Local only (loopback) | Tailscale only (127.0.0.1 bound, tunnelled via 100.113.138.27) |

The ThinkPad gateway can be configured to connect to the VPS gateway via Tailscale if cross-machine browser tasking is needed (future work).

---

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `ECONNREFUSED 127.0.0.1:18789` | `openclaw gateway restart` |
| `Missing config` crash loop | `openclaw config set gateway.mode local && openclaw gateway restart` |
| Node host disconnected | `systemctl --user restart openclaw-node.service` |
| Extension badge shows `!` (red) | Node host not running — restart it |
| `No tabs` on `chrome` profile | Click extension icon on a real Chrome tab first |
| `EADDRINUSE 18792` | Another process holds the relay port — `fuser -k 18792/tcp` |
| Playwright missing | `npm install -g playwright && npx playwright install chromium` |
| `openclaw browser open` error on `chrome` profile | Use `openclaw` profile instead; `chrome` profile is relay-only |

---

## Files & Paths

```
~/.openclaw/
├── openclaw.json          # Gateway config (gateway.mode, gateway.auth.token, etc.)
├── browser/
│   └── chrome-extension/  # Extension source (background.js, manifest.json, icons)
├── media/browser/         # Screenshots saved here
└── agents/main/           # Default agent workspace

~/.config/systemd/user/
├── openclaw-gateway.service
└── openclaw-node.service

~/Desktop/
└── openclaw-extension/    # Convenience copy for Chrome "Load unpacked" dialog
```

---

*Commissioned: 2026-02-28 | OpenClaw v2026.2.1 | Playwright v1.58.2 | Chrome v145*
