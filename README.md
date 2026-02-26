# Claws and Pincers

> **OpenClaw Multi-Agent Discord Framework — Central Command Repository**

**Status**: DEPLOYED | **Platform**: Discord + Telegram | **Agents**: 5 Discord + 1 Telegram Debug | **Governance**: CORE-CHARTER v1.1

---

## For Claude Code Sessions: START HERE

1. **Read [CORE-CHARTER.md](governance/operations/CORE-CHARTER.md)** — source of truth for the entire framework
2. **Check [TODO.md](TODO.md)** — current task priorities (phased, with priority tags)
3. **Read [PROJECT-REFRESHER.md](PROJECT-REFRESHER.md)** — quick context on what's been built and what's next
4. **Use the rugs-expert MCP** — it has RAG access to all project knowledge
5. **Don't reinvent wheels** — query the RAG before building anything new

---

## What Is This?

An autonomous multi-agent team built on OpenClaw, operating through Discord. Inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes), this adds persistent agents, a governance layer, and project-based isolation.

### The Team

| Agent | Role | Model (via OpenRouter) | Fallback |
|-------|------|------------------------|----------|
| **Orchestrator** | Coordination, task dispatch, governance | anthropic/claude-opus-4-6 | moonshotai/kimi-k2.5 |
| **Researcher** | Knowledge gathering, RAG, analysis | x-ai/grok-4.1-fast | moonshotai/kimi-k2.5 |
| **Developer** | Code implementation, PRs, technical | minimax/minimax-m2.5 | moonshotai/kimi-k2.5 |
| **Sysadmin** | Infrastructure, Docker, VPS, monitoring | moonshotai/kimi-k2.5 | google/gemini-3-flash-preview |
| **Reviewer/QA** | Code review, quality gates, testing | google/gemini-3-flash-preview | moonshotai/kimi-k2.5 |

**Telegram Debug Bot** (Clawbot): anthropic/claude-sonnet-4-5 (direct Anthropic API)

### The 4 Absolute Laws

1. **No Project ID, No Work Allowed** — Every task needs a PROJ-XXX tag
2. **No Charter, No Code** — Charter approved before implementation starts
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks work until resolved
4. **Quality Over Speed** — "Fast but wrong" is a governance violation

---

## Architecture

```
+-----------------------------------------------------------------+
|                      VPS (srv1216617)                            |
|-----------------------------------------------------------------|
|                                                                  |
|  +----------------------------------------------------------+   |
|  |             DISCORD AGENT TEAM (OpenRouter)               |   |
|  |  +-- Orchestrator  [Opus 4.6]                             |   |
|  |  +-- Researcher    [Grok 4.1 Fast]                        |   |
|  |  +-- Developer     [MiniMax M2.5]                         |   |
|  |  +-- Sysadmin      [Kimi K2.5]                            |   |
|  |  +-- Reviewer/QA   [Gemini 3 Flash Preview]               |   |
|  +----------------------------------------------------------+   |
|                              |                                   |
|  +----------------------------------------------------------+   |
|  |             GOVERNANCE & CONTROL PLANE                    |   |
|  |  +-- CORE-CHARTER.md (4 laws, lifecycle, severity)        |   |
|  |  +-- n8n (workflow enforcement - Phase 2)                 |   |
|  |  +-- File coordination (task-board, locks, conflicts)     |   |
|  +----------------------------------------------------------+   |
|                              |                                   |
|  +----------------------------------------------------------+   |
|  |                  SHARED SERVICES                          |   |
|  |  qdrant (vectors) | timescaledb (metrics) | rag-api       |   |
|  |  rabbitmq (queues) | n8n (workflows) | rugs-mcp (RAG)     |   |
|  |  openclaw-memory (persistent memory API, localhost:8002)   |   |
|  +----------------------------------------------------------+   |
|                              |                                   |
|  +----------------------------------------------------------+   |
|  |           TELEGRAM DEBUG BOT (Clawbot)                    |   |
|  |  Direct Anthropic API | Sonnet 4.5 | Debug interface      |   |
|  +----------------------------------------------------------+   |
|                                                                  |
+-----------------------------------------------------------------+
```

---

## Repository Structure

```
claws-and-pincers/
+-- governance/              # Operating system for the agent team
|   +-- operations/          # CORE-CHARTER, project registry, roadmap
|   +-- templates/           # Charter, task, conflict, severity templates
|   +-- shared/              # Task board, locks, conflict registry (JSON)
+-- reference/               # OpenClaw platform reference docs (13 files)
+-- agents/                  # Per-agent directories
|   +-- orchestrator/        # SOUL.md, AGENTS.md, HEARTBEAT.md
|   +-- researcher/
|   +-- developer/
|   +-- sysadmin/
|   +-- reviewer/
+-- visuals/                 # Dashboard HTML + Mermaid diagrams
+-- config/                  # Model routing, permissions, cost registry
+-- docker/                  # Docker compose + security profiles
+-- scripts/                 # Operational scripts
+-- docs/
|   +-- plans/               # Design documents and decisions
|   +-- archive/             # Historical docs from 30-day experiment
+-- n8n/                     # Workflow exports (Phase 2)
+-- TODO.md                  # Phased priorities with priority tags
+-- PROJECT-REFRESHER.md     # Quick context doc for new sessions
+-- openclaw.json5           # OpenClaw config (repo version)
+-- README.md                # You are here
```

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [CORE-CHARTER.md](governance/operations/CORE-CHARTER.md) | **Source of truth** — Laws, lifecycle, severity, coordination |
| [TODO.md](TODO.md) | Current priorities (phased, priority-tagged) |
| [PROJECT-REFRESHER.md](PROJECT-REFRESHER.md) | Quick context for continuing sessions |
| [PROJECT-REGISTRY.md](governance/operations/PROJECT-REGISTRY.md) | Active project tracking (PROJ-XXX) |
| [EXPANSION-ROADMAP.md](governance/operations/EXPANSION-ROADMAP.md) | Growth plan |
| [Anti-Patterns](governance/shared/anti-patterns.md) | Self-learning pattern avoidance |
| [Model Routing](config/model-routing.yaml) | LLM provider and model assignments |
| [Cost Registry](config/cost-registry.yaml) | Budget tracking per provider |
| [Reference Docs](reference/README.md) | OpenClaw platform reference (13 files) |

---

## Infrastructure

| Resource | Value |
|----------|-------|
| **Host** | srv1216617 (Hostinger VPS) |
| **OS** | Ubuntu 24.04 LTS |
| **Resources** | 4 vCPU, 16GB RAM, 200GB NVMe |
| **VPN** | Tailscale (100.113.138.27) |
| **LLM Provider** | OpenRouter (primary), Anthropic (Telegram), Groq (fallback) |
| **OpenClaw Runtime** | 2026.2.25 |
| **Docker Services** | qdrant, timescaledb, rag-api, rugs-mcp, n8n, rabbitmq, openclaw-memory |

### MCP Tools (Prefer over SSH)

```
mcp__rugs-expert__search_rugs_knowledge()  # Query RAG
mcp__rugs-expert__ingest_knowledge()       # Add to RAG
mcp__rugs-expert__get_system_info()        # System resources
mcp__rugs-expert__get_docker_status()      # Container health
mcp__rugs-expert__get_service_logs()       # Read container logs
mcp__rugs-expert__run_health_checks()      # Full health check
```

---

## Historical Context

This project evolved from a 30-day autonomous agent experiment using a single Telegram bot (@dutch_claws_bot). Phase 0 of that experiment was completed ahead of schedule (multi-model LLM routing, 5-tier authorization, cost tracking). The project then pivoted to a multi-agent Discord framework with formal governance.

Historical docs from the Telegram experiment are preserved in [docs/archive/](docs/archive/).

---

## Owner

- **User**: Dutchthenomad (Devin)
- **Access**: Via Tailscale VPN or direct IP

---

*Framework initiated: 2026-02-16 | Deployed: 2026-02-26 | Evolved from 30-day experiment (2026-01-31)*
