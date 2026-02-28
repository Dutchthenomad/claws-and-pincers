# Claws & Pincers — OpenClaw Agent Team Framework

> **Owner**: Dutchthenomad (Devin)
> **Repo**: https://github.com/Dutchthenomad/claws-and-pincers
> **VPS**: srv1216617 (Hostinger) — 4 vCPU, 16GB RAM, 200GB NVMe
> **Last Updated**: 2026-02-27

---

## What This Project Is

An autonomous multi-agent team using OpenClaw on Discord. 5 specialized AI agents (Orchestrator, Researcher, Developer, Sysadmin, Reviewer) operate under strict governance rules defined in CORE-CHARTER.md. Think of it as a small company: Devin is the CEO, the Orchestrator is the VP, and the specialists are department heads.

Inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes). This version adds persistent agents, governance enforcement, project-based isolation, and a 4-law operating system.

---

## Session Start Protocol

**Before doing ANY work in this repo, read these files IN ORDER:**

1. `governance/operations/CORE-CHARTER.md` — Supreme governing document (4 Absolute Laws, 12 sections)
2. `docs/plans/SESSION-CONTINUITY.md` — Current project state, pending work, infrastructure details
3. `TODO.md` — Phased roadmap with priorities
4. `operations/DEPLOYMENT-STATE.md` — Live infrastructure state (23 containers)

**Then verify the local repo is current:**
```bash
cd /root/claws-and-pincers && git fetch origin && git status
```
If behind origin/main, pull before making any changes. **Never audit or report on stale local state.**

---

## The 4 Absolute Laws

These are NON-NEGOTIABLE and govern all agent behavior:

1. **No Project ID, No Work Allowed** — Every task requires PROJ-XXX registration
2. **No Charter, No Code** — Charter approved by Devin before implementation
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks until resolved
4. **Quality Over Speed** — "Fast but wrong" is a governance violation

---

## Architecture Overview

### 5 Discord Agents (All Deployed)

| Agent | Model (OpenRouter) | Role |
|-------|-------------------|------|
| Orchestrator | claude-opus-4-6 | VP coordinator — delegates, enforces laws, synthesizes |
| Researcher | grok-4.1-fast | Knowledge engine — investigates, verifies, reports |
| Developer | minimax-m2.5 | Builder — implements specs, tests, delivers code |
| Sysadmin | kimi-k2.5 | Infrastructure guardian — deploys, configures, monitors |
| Reviewer | gemini-3-flash-preview | Quality gate — reviews, enforces governance, catches defects |

### Infrastructure (19 Docker Containers)

All ports bound to `127.0.0.1`, accessible via Tailscale VPN only.

- **OpenClaw gateway** (18789) — single container, 5 agents via routing bindings (v2026.2.26)
- **RAG/Knowledge**: rag-api (8000), rugs-mcp (8001), qdrant (6333), timescaledb (5433)
- **Orchestration**: n8n (5678), n8n-postgres, openclaw-memory (8002), rabbitmq (5672)
- **Monitoring**: grafana (3000), uptime-kuma (3001), metabase (3002), dozzle (8080)
- **Other**: ollama (11434), apprise-api (8003)

### Secrets (chmod 600, never committed)

| Secret | Location |
|--------|----------|
| Discord bot tokens | `/opt/openclaw/secrets/discord-bots.env` |
| OpenRouter API key | `/opt/openclaw/secrets/openrouter-api.env` |
| Gateway .env | `/opt/openclaw/config/.env` |
| Gateway auth token | `/opt/openclaw/secrets/gateway-token.txt` |
| n8n encryption key | `/docker/n8n/.env` |
| Memory API key | `/root/openclaw-memory/.env` |

---

## Repository Structure

```
claws-and-pincers/
├── agents/{orchestrator,researcher,developer,sysadmin,reviewer}/
│   ├── SOUL.md           # Identity and personality
│   ├── AGENTS.md          # Operations, SOPs, tools
│   └── HEARTBEAT.md       # Proactive monitoring config
├── governance/
│   ├── operations/        # CORE-CHARTER, PROJECT-REGISTRY, EXPANSION-ROADMAP
│   ├── templates/         # Charter, task, conflict, severity templates
│   └── shared/            # task-board.json, active-locks.json, conflict-registry.json
├── config/
│   ├── model-routing.yaml
│   ├── cost-registry.yaml
│   ├── capability-timeline.yaml
│   └── permission-tiers.yaml
├── deployment/discord-agents/
│   ├── docker-compose.agents.yml
│   ├── deploy-agents.sh, health-check.sh, Makefile
│   └── QUICKSTART.md, OAUTH2_URLS.md
├── operations/            # DEPLOYMENT-STATE.md, AUDIT-2026-02-26.md
├── reference/             # 12 OpenClaw platform reference docs
├── docs/plans/            # Design docs, SESSION-CONTINUITY.md
├── visuals/               # Mermaid diagrams, dashboard HTML
├── n8n/                   # Workflow exports (Phase 2)
├── openclaw.json5         # Master OpenClaw config
├── TODO.md                # Phased roadmap
├── PROJECT-REFRESHER.md   # Quick context summary
└── README.md              # Project overview
```

---

## Current Phase Status

| Phase | Status | Priority |
|-------|--------|----------|
| Phase 1 — Foundation | DONE | — |
| Phase 2 — n8n Core Systems | NEXT | HIGH |
| Phase 3 — Context Optimization | Queued | NORMAL |
| Phase 4 — LangChain Research | Queued | NICE |
| Phase 5+ — Expansion | Planned | — |

**Next milestone**: Phase 2A — Laws enforcement workflows in n8n

---

## Working Rules for Claude Code Sessions

### Verification Standards

- **NEVER report on file contents without reading them first.** If unsure whether local matches remote, check with `git fetch origin && git status`.
- **ALL claims must be personally validated.** Do not assume files exist, have content, or are complete based on memory or previous sessions.
- **When auditing, always check remote state.** The local repo can be behind origin/main. This has caused false reports before (Session 2026-02-27: 30+ commits behind, agent files incorrectly reported as stubs).

### Code and Config Standards

- **OpenRouter is the LLM provider.** Not direct Anthropic API. All model routing goes through OpenRouter.
- **Environment variables for all secrets.** Never hardcode tokens, keys, or passwords. Store in `.env` files under `/opt/openclaw/secrets/`.
- **Discord-only architecture.** Telegram was fully removed (2026-02-27). Zero Telegram references should exist outside `docs/archive/`.
- Follow the coding style rules in `~/.claude/rules/coding-style.md` (immutability, small files, error handling, input validation).

### User Preferences

- Devin values **verified facts over assumptions**. When something seems off, investigate before reporting.
- Devin wants **minimal system management overhead**. Prefer automation, avoid manual steps.
- Devin uses **OpenRouter** for all LLM access.
- Devin wants **single-source-of-truth documentation**. Don't create redundant docs.
- Attribution is **disabled** globally via `~/.claude/settings.json`.

---

## Key Commands

```bash
# Check gateway health
openclaw health
docker stats openclaw-gateway --no-stream

# View gateway logs
docker logs openclaw-gateway --tail 50

# Gateway status
openclaw gateway status

# Restart gateway
cd /opt/openclaw/gateway && docker compose restart

# Access Control UI (from Tailscale)
# http://100.113.138.27:18789/

# Access n8n UI (from Tailscale)
# http://100.113.138.27:5678

# Quick VPS health
uptime; free -h | grep Mem; df -h / | tail -1; docker ps -q | wc -l
```

---

## Related Systems

| System | Location | Purpose |
|--------|----------|---------|
| SysAdmin Knowledge Base | `/opt/sysadmin-ai/` | VPS health monitoring, runbooks |
| OpenClaw Memory API | `127.0.0.1:8002` | Persistent agent memory (MCP-integrated) |
| Knowledge Curator | `/root/curator-mcp/` | RAG ingestion pipeline |
| RAG Stack | `/root/rag-stack/` | Vector search infrastructure |
