# OpenClaw Agent Team — Project Refresher

**Last Updated:** 2026-03-01

## What This Is

An autonomous multi-agent team using OpenClaw on Discord. Think of it like a small company: Devin is the CEO, an Orchestrator bot is the VP, and specialist bots (Researcher, Developer, Sysadmin, Reviewer/QA) are department heads. They each have their own Discord workspace, share a coordination channel, and operate under strict governance rules.

The model is inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes, 2,000 sessions, $20K, zero human interaction for weeks). This version adds persistent agents, a governance layer, and project-based isolation.

---

## Current State: DEPLOYED

All 5 Discord agents are online and running on the VPS.

### Model Stack (via OpenRouter)

| Agent | Primary Model | Fallback |
|-------|--------------|----------|
| Orchestrator | anthropic/claude-opus-4-6 | moonshotai/kimi-k2.5 |
| Researcher | x-ai/grok-4.1-fast | moonshotai/kimi-k2.5 |
| Developer | minimax/minimax-m2.5 | moonshotai/kimi-k2.5 |
| Sysadmin | moonshotai/kimi-k2.5 | google/gemini-3-flash-preview |
| Reviewer/QA | google/gemini-3-flash-preview | moonshotai/kimi-k2.5 |

### Key Infrastructure

- **OpenClaw Runtime:** v2026.2.26
- **LLM Provider:** OpenRouter (primary), Anthropic (fallback), Groq (fallback)
- **Memory:** OpenClaw Memory API at localhost:8002 (SQLite + FTS5, MCP-integrated)
- **Orchestration:** Native OpenClaw sessions + heartbeats (primary); n8n at port 5678 (external integrations only)
- **Vector DB:** Qdrant at port 6333
- **Secrets:** All in `.env` file (not hardcoded in config)

---

## What's Been Built (Phase 1 — DONE)

### Agent Definitions
All 5 agents have SOUL.md, AGENTS.md, and HEARTBEAT.md in `agents/{agent-name}/`.

### Governance Framework
- CORE-CHARTER.md with 4 Absolute Laws
- PROJECT-REGISTRY.md for PROJ-XXX tracking
- Templates for charters, tasks, conflicts, severity
- Anti-patterns knowledge base (AP-001 through AP-005)

### Configuration
- Merged openclaw.json serving Discord (5 agents)
- OpenRouter-first model routing with per-agent frontier models
- Environment variable secret management

### Deployment
- All 5 Discord bots logged in and running
- Unified gateway process on VPS

---

## The 4 Absolute Laws

1. **No Project ID, No Work Allowed** — Every task needs a PROJ-XXX tag.
2. **No Charter, No Code** — Charter approved by Devin before implementation starts.
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks work until resolved.
4. **Quality Over Speed** — "Fast but wrong" is a governance violation.

---

## What's Next

### Phase 2 — Native OpenClaw Integration (HIGH)

Core agent coordination uses native OpenClaw features (sessions, heartbeats, `/usage`, cron jobs). n8n retains a reduced scope for external integrations only (Discord polling, webhooks, RAG health).

- **2A:** Laws enforcement (hybrid n8n + native) — conflict detection via sessions, cost tracking via `/usage` + cron, heartbeat dead man's switch
- **2B:** Native session & memory integration — docs/config aligned to session tools; runtime testing and Memory API integration remain
- **2C:** Agent workspace management — native workspace mounts, lock management via sessions
- **2D:** Config evolution & drift detection — live gateway state vs declared config
- **2E:** Discord channel optimization — permissions audit, category redesign

### Phase 3 — Context & Token Optimization (NORMAL)

- Audit token caching (contextPruning, compaction safeguards)
- Inventory and refine skills across agents
- Define per-agent context budgets
- Write formal research proposal for optimization

### Phase 4 — Research: LangChain / LangFlow / LangGraph (NICE)

Evaluate whether these frameworks add meaningful capability beyond native OpenClaw features. Exploratory only.

### Phase 5+ — Expansion

Additional specialists, on-demand spawning, cross-project knowledge transfer, self-optimizing governance.

---

## Quick Links

| Resource | Location | Status |
|----------|----------|--------|
| Core Charter | `governance/operations/CORE-CHARTER.md` | v2.0 |
| Agent Configs | `agents/{agent-name}/` | DONE |
| OpenClaw Config | `openclaw.json5` | DONE |
| Model Routing | `config/model-routing.yaml` | DONE |
| Cost Registry | `config/cost-registry.yaml` | DONE |
| TODO | `TODO.md` | Updated 2026-03-01 |
| Design Docs | `docs/plans/` | Active |

---

## For New Claude Code Sessions

1. Read **CLAUDE.md** (project root) — auto-loaded by Claude Code, contains session start protocol
2. Read **docs/plans/SESSION-CONTINUITY.md** — single source of truth for current state and pending work
3. Read **CORE-CHARTER.md** — supreme governance document
4. Read **agents/{agent}/SOUL.md** — understand who each agent is
5. Check **TODO.md** — current priorities
6. Check `docs/plans/` for design decisions and architectural context

---

## Repository Structure

```
claws-and-pincers/
+-- agents/                  # Per-agent SOUL, AGENTS, HEARTBEAT
+-- governance/              # Operating system
|   +-- operations/          # CORE-CHARTER v2.0, PROJECT-REGISTRY
|   +-- templates/           # Charter, task, conflict templates
|   +-- shared/              # Anti-patterns knowledge base (JSON files archived to docs/archive/)
+-- reference/               # OpenClaw platform reference docs
+-- config/                  # Model routing, cost registry
+-- visuals/                 # Dashboard HTML + diagrams
+-- docs/plans/              # Design documents
+-- n8n/                     # Workflow exports (Phase 2)
+-- openclaw.json5           # Main OpenClaw config
+-- TODO.md                  # Current priorities
+-- README.md                # Project overview
```

---

## Status Summary

**Phase 1 (Foundation):** DONE
**Phase 2 (Native OpenClaw Integration):** HIGH — In progress
**Phase 3 (Context Optimization):** NORMAL — After Phase 2
**Phase 4 (LangChain Research):** NICE — Exploratory

**Blockers:** None

**Next Milestone:** Phase 2A/2B — Native session migration and cost tracking via `/usage` + cron
