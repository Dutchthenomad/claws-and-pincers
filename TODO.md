# TODO — OpenClaw Agent Team Framework

**Updated:** 2026-02-27
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
- [x] OpenClaw runtime updated to 2026.2.25

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

## Phase 2 — n8n Core Systems Architecture (HIGH)

n8n becomes the universal control plane. Static YAML/JSON configs are state snapshots; n8n workflows are the living, enforceable, debuggable truth.

### Phase 2A — Laws Enforcement via n8n
- [x] HIGH: Project ID validator (polls #task-dispatch, validates PROJ-XXX)
- [x] HIGH: Charter approval gate check (validates charter in PROJECT-REGISTRY.md)
- [x] HIGH: Severity routing automation (routes from #review-verdicts per notification matrix)
- [ ] HIGH: Conflict registry watchdog
- [ ] HIGH: Token cost monitor with kill switch
- [ ] NORMAL: Anti-pattern repeat detection
- [ ] NORMAL: Heartbeat dead man's switch

### Phase 2B — Memory Orchestration via n8n
- [ ] HIGH: Integrate existing OpenClaw Memory API (localhost:8002) into n8n workflows
- [ ] HIGH: Design per-agent namespaced memory contexts
- [ ] NORMAL: n8n workflow for memory lifecycle (create, prune, archive)
- [ ] NORMAL: Cross-agent knowledge sharing rules (what's shared vs private)

### Phase 2C — Agent File Structure Management via n8n
- [ ] HIGH: n8n workflow to manage agent workspace directories
- [ ] NORMAL: Automated project folder creation on PROJ-XXX registration
- [ ] NORMAL: Lock file management and collision prevention
- [ ] NICE: File structure health checks and cleanup automation

### Phase 2D — Responsibility & Config Evolution via n8n
- [ ] HIGH: n8n workflow for agent config changes (model swaps, tool grants, scope changes)
- [ ] NORMAL: Config drift detection (live state vs declared state)
- [ ] NORMAL: Role evolution tracking (when agents gain/lose responsibilities)
- [ ] NICE: Automated changelog generation from config diffs

### Phase 2E — Discord Channel & Category Redesign
- [ ] HIGH: Map channel structure to n8n-managed routing rules
- [ ] HIGH: Set up Discord channel permissions matching access control matrix
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
- [ ] NORMAL: Implement context window health metrics in n8n

### Phase 3D — Research Proposal
- [ ] NORMAL: Write formal research proposal for token/context optimization
- [ ] NORMAL: Benchmark current token spend per agent per task type
- [ ] NICE: Propose optimization targets with measurable KPIs

---

## Phase 4 — Research: LangChain / LangFlow / LangGraph (NICE)

Evaluate whether LangChain, LangFlow, or LangGraph adds meaningful scalability and capability to the n8n-based orchestration pipeline. This is exploratory, not committed.

- [ ] NICE: Research LangChain integration points with n8n
- [ ] NICE: Evaluate LangFlow as visual workflow layer alongside n8n
- [ ] NICE: Assess LangGraph for multi-agent state machine orchestration
- [ ] NICE: Pros/cons analysis with recommendation (augment n8n, replace, or skip)
- [ ] NICE: Decision criteria: does it optimize end-use goals more effectively than n8n alone?

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
**Phase 2:** HIGH — Next up
**Phase 3:** NORMAL — After Phase 2 foundations
**Phase 4:** NICE — Research track

**Blockers:** None

**Next Milestone:** Build Phase 2A Laws enforcement workflows in n8n
