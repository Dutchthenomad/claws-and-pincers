# TODO — OpenClaw Agent Team Framework

**Updated:** 2026-02-20  
**Priority Key:** 🔴 Blocker | 🟡 High | 🟢 Normal | ⚪ Nice-to-have | ✅ Complete

---

## Phase 1A — Agent Definitions ✅ COMPLETE

- [x] ✅ Write SOUL.md for Orchestrator (personality, rules, governance enforcement)
- [x] ✅ Write SOUL.md for Researcher
- [x] ✅ Write SOUL.md for Developer
- [x] ✅ Write SOUL.md for Sysadmin
- [x] ✅ Write SOUL.md for Reviewer/QA
- [x] ✅ Write AGENTS.md for each agent (operational instructions)
- [x] ✅ Write HEARTBEAT.md for each agent (proactive check-in checklists)

**Location:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/`

---

## Phase 1B — Configuration ✅ COMPLETE

- [x] ✅ Write openclaw.json5 multi-agent config (5 agents, Discord bindings, tool restrictions, model assignments)
- [x] ✅ Map Discord bot tokens to agent IDs in config
- [x] ✅ Set up deployment infrastructure with Docker Compose (container isolation, health checks, auto-restart)
- [ ] 🟡 Set up Discord channel permissions matching access control matrix in CORE-CHARTER
- [x] ✅ Write GOVERNANCE-RULES.md reference (detailed procedures in CORE-CHARTER)

**Location:**
- Config: `openclaw.json5`
- Deployment: `deployment/discord-agents/`
- Reference: `reference/08-CONFIGURATION-REFERENCE.md`

---

## Phase 1C — n8n Enforcement Layer 🟡 IN PROGRESS

- [ ] 🟡 Build n8n workflow: Project ID validator (webhook on #task-dispatch)
- [ ] 🟡 Build n8n workflow: Charter approval gate
- [ ] 🟡 Build n8n workflow: Conflict registry watchdog
- [ ] 🟡 Build n8n workflow: Severity routing automation
- [ ] 🟡 Build n8n workflow: Token cost monitor with kill switch
- [ ] 🟡 Build n8n workflow: Anti-pattern repeat detection
- [ ] 🟡 Build n8n workflow: Heartbeat dead man's switch

**Location:** `n8n/` (pending creation)

---

## Phase 1D — Repo Housekeeping ✅ COMPLETE

- [x] ✅ Rewrite README.md for multi-agent framework focus
- [x] ✅ Archive outdated single-agent docs to docs/archive/
- [x] ✅ Review discord-design-docs/ and merge or archive (moved to docs/archive/)
- [x] ✅ Update .gitignore for new paths
- [ ] ⚪ Update HTML dashboard with full file structure detail

**Location:** `README.md`, `docs/archive/`, `visuals/`

---

## Phase 2 — Deployment & Testing 🟡 READY TO START

- [x] ✅ Deploy all 5 agents on VPS (containers defined, ready to start)
- [ ] 🟡 Verify Discord channel bindings and routing
- [ ] 🟡 Test full project lifecycle: charter → ID → dispatch → work → review → complete
- [ ] 🟡 Test conflict detection on overlapping scope
- [ ] 🟡 Test severity escalation chain (INFO → WARN → BLOCKED → CRITICAL)
- [ ] 🟡 Test n8n enforcement catches violations
- [ ] 🟢 Run first real project through the system end-to-end

**Next Action:** Start the agent swarm: `./deploy-agents.sh start`

---

## Phase 3+ — Expansion ⚪ PLANNED

- [ ] ⚪ Evaluate need for additional specialists (Creative, Data, Security, Writer)
- [ ] ⚪ Implement on-demand specialist spawning via sessions_spawn
- [ ] ⚪ Cross-project knowledge transfer system
- [ ] ⚪ Automated charter generation for recurring project types

---

## Quick Links

| Resource | Location |
|----------|----------|
| **Core Charter** | `governance/operations/CORE-CHARTER.md` |
| **Agent Configs** | `agents/{agent-name}/{SOUL,AGENTS,HEARTBEAT}.md` |
| **Deployment** | `deployment/discord-agents/` |
| **Reference Docs** | `reference/` (13 files) |
| **Project Registry** | `governance/operations/PROJECT-REGISTRY.md` |
| **Task Board** | `governance/shared/task-board.json` |

---

## Current Blockers

**None** — All Phase 1A/1B/1D complete. Phase 2 ready to begin.

## Immediate Next Steps

1. **Start the agent swarm:** `cd /opt/openclaw/discord-agents && ./deploy-agents.sh start`
2. **Invite bots to Discord server** with proper permissions
3. **Test basic connectivity:** `make health`
4. **Create first project charter** and run through lifecycle
5. **Build n8n enforcement workflows** (Phase 1C)
