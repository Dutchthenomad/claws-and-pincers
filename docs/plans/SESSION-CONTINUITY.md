# Session Continuity Document — Claws & Pincers

> **Purpose**: Single source of truth for fresh Claude Code sessions. Read this to understand the complete project state and pick up where the last session left off.
> **Last Updated**: 2026-02-28
> **Updated By**: Claude Sonnet 4.6 + Devin
> **Repo**: https://github.com/Dutchthenomad/claws-and-pincers
> **Local Path**: `/root/claws-and-pincers`

---

## Quick Status

| Item | Status |
|------|--------|
| Phase 1 (Foundation) | DONE |
| Phase 1F (Deployment Fix) | DONE — Single gateway architecture |
| Phase 2A (Laws Enforcement) | IN PROGRESS — Core trio deployed |
| All 5 Discord agents | DEPLOYED via single `openclaw-gateway` on port 18789 |
| OpenClaw version | v2026.2.26 (updated from v2026.2.9) |
| Architecture | Single gateway container (was 5 separate containers on 8081-8085) |
| Container count | 19 (reduced from 23 — 5 agents → 1 gateway) |
| Agent directory scaffolding | DONE (workspace/, sessions/, skills/ per agent) |
| Discord channel structure | DONE (27 channels, 8 categories, permissions set) |
| Telegram references | REMOVED (commit 5e16445, 2026-02-27) |
| Repo sync (local ↔ remote) | SYNCED as of 2026-02-28 |
| CLAUDE.md | WRITTEN (project root) |
| This document | WRITTEN |

---

## What Was Completed This Session (2026-02-28, continued)

### VPS Browser Integration — Partially Complete

**Done:**
- SSH tunnel service `openclaw-vps-tunnel.service` created on ThinkPad (autossh, ThinkPad:19789 → VPS:18789)
- Tunnel tested and confirmed working — VPS gateway reachable at `http://127.0.0.1:19789/`
- `openclaw.json5`: removed global `tools.deny: ["browser"]` — Orchestrator and Researcher now have active browser tool access
- ThinkPad node host restored to local gateway (paired + connected)

**Blocked (requires 2 manual steps on VPS — see "What Needs To Happen Next"):**
- ThinkPad node host cannot pair with VPS gateway until auth tokens are synchronized
- Security hooks correctly prevent automated credential operations via SSH

---

## What Was Completed Last Session (2026-02-28)

### Browser Automation — ThinkPad Setup (DONE)

Full browser automation stack deployed on local ThinkPad workstation:

- **OpenClaw gateway** configured on ThinkPad (mode: local, auth token set, systemd)
- **Node host** `ThinkPad-Chrome` installed as systemd service, permanently paired
- **Chrome extension** installed at `~/.openclaw/browser/chrome-extension`, loaded in Chrome v145
- **Managed browser profile** (`openclaw`) tested — headless, snapshot, screenshot, navigation all working
- **Chrome relay profile** (`chrome`) relay reachable at `http://127.0.0.1:18792/` — requires clicking extension icon on a tab to attach

**New docs added**:
- `reference/13-BROWSER-AUTOMATION.md` — complete reference for all browser automation
- `operations/DEPLOYMENT-STATE.md` — ThinkPad services section added

**Commit**: `feat: add browser automation stack (ThinkPad) with reference doc`

---

## What Was Completed Last Session (2026-02-27)

### Telegram Removal (DONE)
Complete removal of all Telegram references from the codebase. Discord-only architecture now.

**Commit**: `5e16445` — "refactor: complete Telegram removal — Discord-only architecture"

**Changes made (17 files modified, 3 deleted)**:
- `openclaw.json5` — Removed 6 Telegram agents, telegram channel config, telegram bindings
- `config/permission-tiers.yaml` — Tier 2 changed from "Telegram Approval" to "Discord Approval"
- `config/capability-timeline.yaml` — All telegram approval/notification references → discord
- `config/cost-registry.yaml` — Removed Telegram cost entries
- `config/model-routing.yaml` — Removed Telegram routing entries
- `docker/docker-compose.yml` — Removed telegram-bot.env mounts, removed openclaw-voice service
- `deployment/discord-agents/.env.template` — Removed TELEGRAM section
- `reference/01-OPENCLAW-OVERVIEW.md`, `03-*.md`, `04-*.md` — Removed "telegram" from channel enums
- `README.md` — Changed "5 Discord + 1 Telegram" to "5 Discord"
- `PROJECT-REFRESHER.md` — Removed Telegram debug bot mentions
- `TODO.md` — Cleaned Telegram references
- **DELETED**: `config/profiles/telegram/settings.yaml`, `config/profiles/telegram/voiceprint.yaml`, `config/secrets/telegram-bot.env.template`

**Verification**: `grep -ri "telegram\|clawbot\|bot_token_telegram" --include="*.md" --include="*.yaml" --include="*.yml" --include="*.json" --include="*.json5" --include="*.sh" --include="*.env*"` returns zero results outside `docs/archive/`.

### Discord Bot Token Storage (DONE)
All 5 bot tokens stored at `/opt/openclaw/secrets/discord-bots.env`:
- Variable naming aligned to match `openclaw.json5`: `DISCORD_ORCHESTRATOR_TOKEN` (not COORDINATOR)
- Includes app IDs and permission integers for each bot
- OpenRouter API key stored at `/opt/openclaw/secrets/openrouter-api.env`
- OpenRouter also configured in n8n UI

### Local/Remote Repo Sync (DONE)
- Local was 30+ commits behind origin/main at start of session
- Pulled to sync, re-applied all changes on fresh state
- Pushed final commit to origin/main

---

## What Needs To Happen Next

### IMMEDIATE — VPS Browser Integration (2 Manual Steps)

The SSH tunnel is running and openclaw.json5 is updated. To complete browser tool activation for Discord agents, run these two commands on the VPS:

**Step 1 — Sync auth token** (SSH to VPS, run as root):
```bash
# Get the VPS gateway token:
cat /opt/openclaw/secrets/gateway-token.txt
```
Take that token value, then on ThinkPad run:
```bash
openclaw config set gateway.auth.token <VPS-TOKEN-VALUE>
openclaw node install --host 127.0.0.1 --port 19789 --display-name "ThinkPad-Chrome" --force
systemctl --user restart openclaw-node.service
```

**Step 2 — Approve the node pairing** (SSH to VPS, run as root):
```bash
# After node host connects (wait ~5s), approve the pending request:
openclaw nodes pending    # shows the pending ThinkPad-Chrome node
openclaw nodes approve <node-id>
```

**Step 3 — Deploy updated openclaw.json5 to VPS** (SSH to VPS):
```bash
cd /root/claws-and-pincers && git pull origin main
cp openclaw.json5 /opt/openclaw/config/openclaw.json5  # if this is how it's deployed
cd /opt/openclaw/gateway && docker compose restart
```
(Exact deploy path depends on how the container reads the config — check `/opt/openclaw/gateway/docker-compose.yml` for mount path)

**SSH tunnel** (`openclaw-vps-tunnel.service`) is already running on ThinkPad and survives reboots.
VPS gateway accessible at `http://127.0.0.1:19789/` from ThinkPad while tunnel is active.

---

### Immediate — Completed (2026-02-27)

1. **Charter-compliant directory scaffolding** — DONE. Added `workspace/`, `sessions/`, `skills/` subdirs to all 5 agent directories. Identity docs (SOUL.md, AGENTS.md, HEARTBEAT.md) remain at agent root.

2. **Discord channel setup** — DONE. 27 channels across 8 categories created via `deployment/setup-discord-channels.py` using Orchestrator bot token. Permissions match CORE-CHARTER access control matrix. Added `#project-registry` channel to Logging & Reporting category.

3. **Remove legacy Discord bots** — Still pending. Old bot accounts from the Telegram era need cleanup in the Discord server (manual action)

### Phase 2 — n8n Core Systems (HIGH Priority)

n8n becomes the universal control plane. Currently has 2 workflows (RAG Health Check, Knowledge Curator). Phase 2 adds governance enforcement.

**n8n access**: Port 5678, accessible via Tailscale at `http://100.113.138.27:5678`

#### Phase 2A — Laws Enforcement via n8n
- [x] Project ID validator (polls `#task-dispatch` every 30s, validates PROJ-XXX against registry)
- [x] Charter approval gate check (validates charter approval status before allowing work)
- [x] Severity routing automation (routes WARN/BLOCKED/CRITICAL from `#review-verdicts` to correct channels)
- [ ] Conflict registry watchdog
- [ ] Token cost monitor with kill switch
- [ ] Anti-pattern repeat detection
- [ ] Heartbeat dead man's switch

#### Phase 2B — Memory Orchestration via n8n
- [ ] Integrate OpenClaw Memory API (`localhost:8002`) into n8n workflows
- [ ] Design per-agent namespaced memory contexts
- [ ] Memory lifecycle workflow (create, prune, archive)
- [ ] Cross-agent knowledge sharing rules

#### Phase 2C — Agent File Structure Management via n8n
- [ ] Workflow for agent workspace directory management
- [ ] Automated project folder creation on PROJ-XXX registration
- [ ] Lock file management and collision prevention

#### Phase 2D — Config Evolution via n8n
- [ ] Config change workflows (model swaps, tool grants, scope changes)
- [ ] Config drift detection (live state vs declared state)
- [ ] Role evolution tracking

#### Phase 2E — Discord Channel & Category Redesign
- [ ] Map channel structure to n8n-managed routing rules
- [ ] Set up Discord channel permissions matching access control matrix
- [ ] Category redesign informed by 2A-2D decisions

### Later Phases

- **Phase 3** — Context & token optimization (audit cache settings, skills inventory, context budgets)
- **Phase 4** — Research LangChain/LangFlow/LangGraph integration
- **Phase 5+** — Additional specialists, on-demand spawning, self-optimizing governance

---

## Infrastructure Reference

### Docker Service Map (23 Containers)

| Service | Port | Compose File |
|---------|------|-------------|
| openclaw-orchestrator | 127.0.0.1:8081 | `/opt/openclaw/discord-agents/docker-compose.agents.yml` |
| openclaw-researcher | 127.0.0.1:8082 | same |
| openclaw-developer | 127.0.0.1:8083 | same |
| openclaw-sysadmin | 127.0.0.1:8084 | same |
| openclaw-reviewer | 127.0.0.1:8085 | same |
| rag-api | 127.0.0.1:8000 | `/root/rag-stack/docker-compose.yml` |
| rugs-mcp | 127.0.0.1:8001 | same |
| n8n | 127.0.0.1:5678 | `/docker/n8n/docker-compose.yml` |
| openclaw-memory | 127.0.0.1:8002 | `/root/openclaw-memory/docker-compose.yml` |
| qdrant | 127.0.0.1:6333 | `/root/rag-stack/docker-compose.yml` |
| timescaledb | 127.0.0.1:5433 | `/root/rag-stack/docker-compose.yml` |
| rabbitmq | 127.0.0.1:5672 | varies |
| grafana | 127.0.0.1:3000 | `/docker/grafana/docker-compose.yml` |
| uptime-kuma | 127.0.0.1:3001 | `/docker/uptime-kuma/docker-compose.yml` |
| metabase | 127.0.0.1:3002 | `/docker/metabase/docker-compose.yml` |
| dozzle | 127.0.0.1:8080 | `/docker/dozzle/docker-compose.yml` |
| ollama | 127.0.0.1:11434 | varies |

### Secrets Map

| What | Where | Notes |
|------|-------|-------|
| Discord bot tokens (5) | `/opt/openclaw/secrets/discord-bots.env` | ORCHESTRATOR, RESEARCHER, DEVELOPER, SYSADMIN, REVIEWER |
| OpenRouter API key | `/opt/openclaw/secrets/openrouter-api.env` | Also configured in n8n UI |
| Deployed agent env | `/opt/openclaw/discord-agents/.env` | Combined tokens + config for docker-compose |
| n8n encryption + postgres | `/docker/n8n/.env` | |
| OpenClaw Memory API key | `/root/openclaw-memory/.env` | Also in docker-compose.yml env |

### Network

- All services on `n8n_default` Docker bridge network
- All ports bound to `127.0.0.1` (not publicly accessible)
- External access via Tailscale VPN only (100.113.138.27)
- UFW active: default deny incoming, SSH (22) + Cockpit (9090) only
- Fail2ban protecting SSH

---

## Known Issues

| Issue | Severity | Notes |
|-------|----------|-------|
| 3 n8n credentials need re-entry | LOW | Encrypted with old key, re-enter via UI |
| Legacy OpenRouter API keys | LOW | Need manual revocation on OpenRouter dashboard |
| Network segmentation deferred | MEDIUM | Agents share n8n_default bridge with all services (H-13 from audit) |
| Agent directories lack subdirs | DONE | Added workspace/, sessions/, skills/ per CORE-CHARTER Section 9 |
| Discord channels not yet created | DONE | 27 channels, 8 categories created via setup script |
| Legacy Discord bots | LOW | Old Telegram-era bot accounts need manual cleanup |

---

## Key Documents (Read Priority Order)

| Priority | Document | Path | Purpose |
|----------|----------|------|---------|
| 1 | CLAUDE.md | `./CLAUDE.md` | Project instructions (auto-loaded by Claude Code) |
| 2 | CORE-CHARTER | `governance/operations/CORE-CHARTER.md` | Supreme governance doc — 4 laws, 12 sections |
| 3 | This document | `docs/plans/SESSION-CONTINUITY.md` | Current state and pending work |
| 4 | TODO.md | `./TODO.md` | Phased roadmap with priorities |
| 5 | DEPLOYMENT-STATE | `operations/DEPLOYMENT-STATE.md` | Live infrastructure snapshot |
| 6 | Agent SOULs | `agents/*/SOUL.md` | Agent identities and boundaries |
| 7 | PROJECT-REFRESHER | `./PROJECT-REFRESHER.md` | Quick context summary |

---

## Lessons Learned (For Future Sessions)

1. **Always verify local repo is synced with remote before making claims.** Session 2026-02-27 had a critical incident where the local repo was 30+ commits behind, leading to incorrect reports that agent files were empty stubs.

2. **User demands verified facts.** Never report on file contents without reading them first. "I haven't checked yet" is always better than a wrong answer presented as fact.

3. **Use OpenRouter, not direct Anthropic API.** All LLM routing goes through OpenRouter.

4. **Telegram is dead.** If you find any Telegram references outside `docs/archive/`, they are artifacts that need removal.

5. **Commit attribution is disabled.** Don't add Co-Authored-By lines.

6. **Docker port binding matters.** Always use `127.0.0.1:PORT:PORT` format for localhost-only services. Plain `PORT:PORT` exposes to internet even with UFW.

---

## Updating This Document

When completing significant work:
1. Update the "Quick Status" table at the top
2. Move completed items from "What Needs To Happen Next" to a new "Completed" section or remove
3. Add any new known issues
4. Update the "Last Updated" date
5. Commit and push changes

This document is the bridge between sessions. Keep it accurate and current.
