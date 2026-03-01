# TODO — OpenClaw Agent Team Framework

**Updated:** 2026-03-01
**Priority Key:** BLOCKER | HIGH | NORMAL | NICE | DONE

---

## Phase 1 — Foundation (DONE)

All Phase 1 work is complete. Agents defined, configured, deployed, and online.

### Phase 1A — Agent Definitions (DONE)
- [x] SOUL.md, AGENTS.md, HEARTBEAT.md for all 5 agents
- **Location:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/`

### Phase 1B — Configuration (DONE)
- [x] openclaw.json5 multi-agent config (5 Discord agents)
- [x] Discord bot tokens mapped to agent IDs
- [x] OpenRouter model routing with frontier models
- [x] Environment variable secret management (.env)
- [x] OpenClaw runtime updated to v2026.2.26

### Phase 1C — Deployment (DONE)
- [x] All 5 Discord agents deployed and online on VPS
- [x] Merged config: single openclaw.json serving Discord

### Phase 1D — Repo Housekeeping (DONE)
- [x] README.md rewritten for multi-agent framework
- [x] Outdated single-agent docs archived
- [x] .gitignore updated
- [x] Config files aligned with live deployment

### Phase 1E — Foundation Completion (DONE)
- [x] Agent directory scaffolding (workspace/, sessions/, skills/ per agent)
- [x] Discord channel setup script (`deployment/setup-discord-channels.py`)
- [x] 27 channels across 8 categories with CORE-CHARTER permissions
- [x] `#project-registry` channel added to Logging & Reporting
- [ ] Legacy Discord bot cleanup (manual — Telegram-era bots)

### Phase 1F — Deployment Architecture Fix (DONE)
- [x] Replaced 5 OOM crash-looping containers with single gateway architecture
- [x] Updated OpenClaw from v2026.2.9 to v2026.2.26
- [x] Built local Docker image from official OpenClaw source
- [x] Fixed config: expanded bindings, guild locked, sandbox off, no Telegram
- [x] Gateway token generated and stored
- [x] Single `openclaw-gateway` container on port 18789 (was 5 containers on 8081-8085)

---

## Phase 2 — Native OpenClaw Integration (HIGH)

Core agent coordination uses native OpenClaw features (sessions, heartbeats, `/usage`, cron). n8n retains a reduced scope for external integrations only (Discord polling, webhooks, RAG health).

### Phase 2A — Laws Enforcement (Hybrid: n8n + Native)
- [x] HIGH: Project ID validator (n8n polls #task-dispatch, validates PROJ-XXX)
- [x] HIGH: Charter approval gate check (n8n validates charter in PROJECT-REGISTRY.md)
- [x] HIGH: Severity routing automation (n8n routes from #review-verdicts per notification matrix)
- [ ] HIGH: Conflict detection via native OpenClaw session tools (config aligned; runtime testing remains)
- [ ] HIGH: Token cost monitoring via native `/usage` endpoint + cron job
- [ ] NORMAL: Anti-pattern repeat detection
- [ ] NORMAL: Heartbeat dead man's switch via native heartbeat system + per-agent cron intervals

### Phase 2B — Native Session & Memory Integration
- [x] HIGH: Docs/config aligned to native session tools (JSON files archived to `docs/archive/governance/`)
- [ ] HIGH: Runtime testing of session-based coordination (sessions_spawn, sessions_send)
- [ ] HIGH: Integrate OpenClaw Memory API (localhost:8002) with native session lifecycle
- [ ] NORMAL: Per-agent namespaced memory contexts using native session scoping
- [ ] NORMAL: Cross-agent knowledge sharing rules (what's shared vs private)

### Phase 2C — Agent Workspace Management
- [ ] HIGH: Agent workspace directory management via native OpenClaw workspace mounts
- [ ] NORMAL: Automated project folder creation on PROJ-XXX registration
- [ ] NORMAL: Lock management via native session tools (config aligned; runtime testing remains)
- [ ] NICE: Workspace health checks and cleanup automation

### Phase 2D — Config Evolution & Drift Detection
- [ ] HIGH: Config change tracking (model swaps, tool grants, scope changes)
- [ ] NORMAL: Config drift detection (live gateway state vs declared openclaw.json5)
- [ ] NORMAL: Role evolution tracking (when agents gain/lose responsibilities)
- [ ] NICE: Automated changelog generation from config diffs

### Phase 2E — Discord Channel Optimization
- [ ] HIGH: Channel permissions audit against CORE-CHARTER access control matrix
- [ ] NORMAL: Category redesign informed by 2A-2D decisions
- [ ] NORMAL: Channel archival and lifecycle management

---

## Phase 3 — Context & Token Optimization (NORMAL)

Context window bloat is a first-class architectural concern. This phase audits, refines, and proposes optimizations.

### Phase 3A — Token Caching Audit
- [ ] NORMAL: Audit current contextPruning cache-ttl settings
- [ ] NORMAL: Measure actual cache hit rates per agent
- [ ] NORMAL: Evaluate compaction safeguard mode effectiveness

### Phase 3B — Skills Inventory & Refinement
- [ ] NORMAL: Catalog all active skills across agents
- [ ] NORMAL: Identify redundant, conflicting, or bloated skills
- [ ] NORMAL: Decide: system-wide skill model vs per-agent skill model

### Phase 3C — Context Window Strategy
- [ ] NORMAL: Define per-agent context budget (what goes in, what stays out)
- [ ] NORMAL: Design progressive disclosure for agent system prompts
- [ ] NORMAL: Implement context window health metrics via native OpenClaw tooling

### Phase 3D — Research Proposal
- [ ] NORMAL: Write formal research proposal for token/context optimization
- [ ] NORMAL: Benchmark current token spend per agent per task type
- [ ] NICE: Propose optimization targets with measurable KPIs

---

## Phase 4 — Research: LangChain / LangFlow / LangGraph (NICE)

Evaluate whether LangChain, LangFlow, or LangGraph adds meaningful capability beyond native OpenClaw features. n8n remains for external integrations; this evaluates whether additional frameworks are needed. Exploratory, not committed.

- [ ] NICE: Research LangChain integration points with native OpenClaw and n8n
- [ ] NICE: Evaluate LangFlow as visual workflow layer for external integrations
- [ ] NICE: Assess LangGraph for multi-agent state machine orchestration vs native OpenClaw sessions
- [ ] NICE: Pros/cons analysis with recommendation (augment, replace, or skip)
- [ ] NICE: Decision criteria: does it optimize end-use goals more effectively than native OpenClaw?

---

## Phase 5+ — Expansion (PLANNED)

- [ ] Evaluate additional specialists (Creative, Data, Security, Writer)
- [ ] On-demand specialist spawning via sessions_spawn
- [ ] Cross-project knowledge transfer system
- [ ] Automated charter generation for recurring project types
- [ ] Self-optimization of governance rules based on retrospectives

---

## Quick Links

| Resource | Location |
|----------|----------|
| Core Charter | `governance/operations/CORE-CHARTER.md` |
| Agent Configs | `agents/{agent-name}/{SOUL,AGENTS,HEARTBEAT}.md` |
| OpenClaw Config | `openclaw.json5` |
| Model Routing | `config/model-routing.yaml` |
| Cost Registry | `config/cost-registry.yaml` |
| Design Docs | `docs/plans/` |
| Reference Docs | `reference/` |

---

## Current Status

**Phase 1:** DONE
**Phase 2:** HIGH — Native OpenClaw integration in progress
**Phase 3:** NORMAL — After Phase 2 foundations
**Phase 4:** NICE — Research track (evaluate against native OpenClaw capabilities)

**Blockers:** None

**Next Milestone:** Phase 2A/2B — Native session migration and cost tracking via `/usage` + cron
