# OpenClaw Agent Team — Project Refresher

**Last Updated:** 2026-02-20

## What This Is

You're building an autonomous multi-agent team using OpenClaw on Discord. Think of it like a small company: you're the CEO, an Orchestrator bot is your VP, and specialist bots (Researcher, Developer, Sysadmin, Reviewer/QA) are your department heads. They each have their own Discord workspace, share a coordination channel, and operate under strict governance rules you defined.

The model is inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes, 2,000 sessions, $20K, zero human interaction for weeks). Your version adds persistent agents, a governance layer, and project-based isolation that their system doesn't have.

---

## ✅ What's Been Built

### 1. Agent Definitions (Complete)
All 5 agents have their identity and operational docs:

| Agent | SOUL.md | AGENTS.md | HEARTBEAT.md |
|-------|---------|-----------|--------------|
| 🎯 Orchestrator | ✅ | ✅ | ✅ |
| 🔬 Researcher | ✅ | ✅ | ✅ |
| 💻 Developer | ✅ | ✅ | ✅ |
| 🖥️ Sysadmin | ✅ | ✅ | ✅ |
| 🔍 Reviewer | ✅ | ✅ | ✅ |

**Location:** `agents/{agent-name}/`

### 2. Governance Framework (Complete)
The operating system for your agent team:

- **CORE-CHARTER.md** — Master document with 4 laws, project lifecycle, severity levels
- **PROJECT-REGISTRY.md** — Project tracking (PROJ-XXX format)
- **EXPANSION-ROADMAP.md** — Phase 1-4 plans
- **Templates** — Charter, task, conflict report, severity definitions
- **Shared State** — Task board, locks, conflict registry, anti-patterns

**Location:** `governance/`

### 3. Configuration (Complete)
- **openclaw.json5** — Multi-agent config with Discord bindings, tool restrictions, models
- **Environment variables** — Secure token management (.env, not committed)
- **Reference docs** — 13 technical files covering Discord integration, architecture, deployment

**Location:** `openclaw.json5`, `reference/`

### 4. Deployment Infrastructure (Complete)
Production-ready Docker deployment:

- **docker-compose.agents.yml** — 5 agent containers + Redis + Watchtower
- **deploy-agents.sh** — Management script (start/stop/health/logs)
- **Makefile** — Quick commands (`make start`, `make logs`)
- **Health checks** — Automatic restart, monitoring endpoints

**Location:** `deployment/discord-agents/`

### 5. Documentation (Complete)
- **README.md** — Multi-agent framework overview
- **TODO.md** — Phased priorities with status
- **Interactive dashboard** — HTML visualization of org structure
- **Mermaid diagrams** — Filesystem, governance, structure

**Location:** `README.md`, `TODO.md`, `visuals/`

---

## Your 4 Absolute Laws
1. **No Project ID, No Work Allowed** — Every task needs a PROJ-XXX tag.
2. **No Charter, No Code** — Charter approved by you before implementation starts.
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks work until resolved.
4. **Quality Over Speed** — "Fast but wrong" is a governance violation.

---

## 🟡 What's In Progress / Next

### Phase 1C — n8n Enforcement Layer (In Progress)
Programmatic compliance enforcement between Discord and OpenClaw:

- [ ] Project ID validator webhook
- [ ] Charter approval gate check
- [ ] Conflict registry watchdog
- [ ] Severity routing automation
- [ ] Token cost monitor with kill switch
- [ ] Anti-pattern repeat detection
- [ ] Heartbeat dead man's switch

### Phase 2 — Deployment & Testing (Ready to Start)
- [ ] Start the agent swarm on VPS
- [ ] Invite bots to Discord server
- [ ] Test Discord channel bindings
- [ ] Run first project through full lifecycle

---

## Quick Links

| Resource | Location | Status |
|----------|----------|--------|
| **Core Charter** | `governance/operations/CORE-CHARTER.md` | ✅ Complete |
| **Agent Configs** | `agents/{agent-name}/` | ✅ Complete |
| **OpenClaw Config** | `openclaw.json5` | ✅ Complete |
| **Deployment** | `deployment/discord-agents/` | ✅ Ready |
| **Task Board** | `governance/shared/task-board.json` | ✅ Initialized |
| **TODO** | `TODO.md` | ✅ Updated |

---

## Where to Start Now

### Immediate Actions:
1. **Start the swarm:** `cd /opt/openclaw/discord-agents && ./deploy-agents.sh start`
2. **Invite bots to Discord:** Use Discord Developer Portal → OAuth2 → URL Generator
3. **Test connectivity:** `make health`
4. **Create first project:** Use `governance/templates/charter-template.md`

### For New Claude Code Sessions:
1. Read **CORE-CHARTER.md** — source of truth for the entire framework
2. Read **agents/{agent}/SOUL.md** — understand who each agent is
3. Check **TODO.md** — current priorities
4. Use the **rugs-expert MCP** — it has RAG access to all project knowledge

---

## Repository Structure

```
claws-and-pincers/
├── agents/                  # Per-agent SOUL, AGENTS, HEARTBEAT
├── governance/              # Operating system
│   ├── operations/          # CORE-CHARTER, PROJECT-REGISTRY
│   ├── templates/           # Charter, task, conflict templates
│   └── shared/              # Task board, locks, registry (JSON)
├── reference/               # 13 OpenClaw reference docs
├── deployment/              # Docker deployment
│   └── discord-agents/      # docker-compose, scripts
├── visuals/                 # Dashboard HTML + diagrams
├── openclaw.json5           # Main OpenClaw config
├── TODO.md                  # Current priorities
└── README.md                # Project overview
```

---

## Status Summary

**Phase 1A (Agent Definitions):** ✅ Complete  
**Phase 1B (Configuration):** ✅ Complete  
**Phase 1C (n8n Enforcement):** 🟡 In Progress  
**Phase 1D (Housekeeping):** ✅ Complete  
**Phase 2 (Deployment):** 🟡 Ready to Start  

**Blockers:** None

**Next Milestone:** Start agent swarm and complete first project lifecycle
