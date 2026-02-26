# OpenClaw Agent Team — Project Refresher

**Last Updated:** 2026-02-26

## What This Is

An autonomous multi-agent team using OpenClaw on Discord. Think of it like a small company: Devin is the CEO, an Orchestrator bot is the VP, and specialist bots (Researcher, Developer, Sysadmin, Reviewer/QA) are department heads. They each have their own Discord workspace, share a coordination channel, and operate under strict governance rules.

The model is inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes, 2,000 sessions, $20K, zero human interaction for weeks). This version adds persistent agents, a governance layer, and project-based isolation.

---

## Current State: DEPLOYED

All 5 Discord agents are online and running on the VPS. A Telegram debug bot (Clawbot) runs alongside for development diagnostics.

### Model Stack (via OpenRouter)

| Agent | Primary Model | Fallback |
|-------|--------------|----------|
| Orchestrator | anthropic/claude-opus-4-6 | moonshotai/kimi-k2.5 |
| Researcher | x-ai/grok-4.1-fast | moonshotai/kimi-k2.5 |
| Developer | minimax/minimax-m2.5 | moonshotai/kimi-k2.5 |
| Sysadmin | moonshotai/kimi-k2.5 | google/gemini-3-flash-preview |
| Reviewer/QA | google/gemini-3-flash-preview | moonshotai/kimi-k2.5 |

Telegram debug bot: anthropic/claude-sonnet-4-5 (direct Anthropic API)

### Key Infrastructure

- **OpenClaw Runtime:** 2026.2.25
- **LLM Provider:** OpenRouter (primary), Anthropic (Telegram), Groq (fallback)
- **Memory:** OpenClaw Memory API at localhost:8002 (SQLite + FTS5, MCP-integrated)
- **Orchestration:** n8n at port 5678 (Phase 2 will expand this significantly)
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
- Merged openclaw.json serving both Discord (5 agents) and Telegram (debug bot)
- OpenRouter-first model routing with per-agent frontier models
- Environment variable secret management

### Deployment
- All 5 Discord bots logged in and running
- Telegram debug bot preserved
- Unified gateway process on VPS

---

## The 4 Absolute Laws

1. **No Project ID, No Work Allowed** — Every task needs a PROJ-XXX tag.
2. **No Charter, No Code** — Charter approved by Devin before implementation starts.
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks work until resolved.
4. **Quality Over Speed** — "Fast but wrong" is a governance violation.

---

## What's Next

### Phase 2 — n8n Core Systems Architecture (HIGH)

n8n becomes the universal control plane. Static configs are state snapshots; n8n workflows are the living, enforceable truth.

- **2A:** Laws enforcement workflows (Project ID validation, charter gates, conflict watchdog, cost kill switch)
- **2B:** Memory orchestration (integrate OpenClaw Memory, per-agent namespaces, lifecycle management)
- **2C:** Agent file structure management (workspace creation, lock management, cleanup)
- **2D:** Responsibility and config evolution (drift detection, role tracking, changelog)
- **2E:** Discord channel/category redesign (informed by 2A-2D)

### Phase 3 — Context & Token Optimization (NORMAL)

- Audit token caching (contextPruning, compaction safeguards)
- Inventory and refine skills across agents
- Define per-agent context budgets
- Write formal research proposal for optimization

### Phase 4 — Research: LangChain / LangFlow / LangGraph (NICE)

Evaluate whether these frameworks add meaningful capability to n8n-based orchestration. Exploratory only.

### Phase 5+ — Expansion

Additional specialists, on-demand spawning, cross-project knowledge transfer, self-optimizing governance.

---

## Quick Links

| Resource | Location | Status |
|----------|----------|--------|
| Core Charter | `governance/operations/CORE-CHARTER.md` | v1.1 |
| Agent Configs | `agents/{agent-name}/` | DONE |
| OpenClaw Config | `openclaw.json5` | DONE |
| Model Routing | `config/model-routing.yaml` | DONE |
| Cost Registry | `config/cost-registry.yaml` | DONE |
| TODO | `TODO.md` | Updated 2026-02-26 |
| Design Docs | `docs/plans/` | Active |

---

## For New Claude Code Sessions

1. Read **CORE-CHARTER.md** — source of truth
2. Read **agents/{agent}/SOUL.md** — understand who each agent is
3. Check **TODO.md** — current priorities
4. Use the **rugs-expert MCP** — RAG access to all project knowledge
5. Check `docs/plans/` for design decisions and architectural context

---

## Repository Structure

```
claws-and-pincers/
+-- agents/                  # Per-agent SOUL, AGENTS, HEARTBEAT
+-- governance/              # Operating system
|   +-- operations/          # CORE-CHARTER, PROJECT-REGISTRY
|   +-- templates/           # Charter, task, conflict templates
|   +-- shared/              # Task board, locks, registry (JSON)
+-- reference/               # 13 OpenClaw reference docs
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
**Phase 2 (n8n Core Systems):** HIGH — Next up
**Phase 3 (Context Optimization):** NORMAL — After Phase 2
**Phase 4 (LangChain Research):** NICE — Exploratory

**Blockers:** None

**Next Milestone:** Build Phase 2A Laws enforcement workflows in n8n
