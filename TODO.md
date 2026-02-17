# TODO — OpenClaw Agent Team Framework

**Updated:** 2026-02-16  
**Priority Key:** 🔴 Blocker | 🟡 High | 🟢 Normal | ⚪ Nice-to-have

---

## Phase 1A — Agent Definitions (Must complete before agents can run)

- [ ] 🔴 Write SOUL.md for Orchestrator (personality, rules, governance enforcement)
- [ ] 🔴 Write SOUL.md for Researcher
- [ ] 🔴 Write SOUL.md for Developer
- [ ] 🔴 Write SOUL.md for Sysadmin
- [ ] 🔴 Write SOUL.md for Reviewer/QA
- [ ] 🔴 Write AGENTS.md for each agent (operational instructions)
- [ ] 🔴 Write HEARTBEAT.md for each agent (proactive check-in checklists)

## Phase 1B — Configuration (Must complete before agents can run)

- [ ] 🔴 Write openclaw.json5 multi-agent config (5 agents, Discord bindings, tool restrictions, model assignments)
- [ ] 🔴 Map Discord bot tokens to agent IDs in config
- [ ] 🔴 Set up Discord channel permissions matching access control matrix in CORE-CHARTER
- [ ] 🟡 Write GOVERNANCE-RULES.md (detailed enforcement procedures, companion to CORE-CHARTER)

## Phase 1C — n8n Enforcement Layer

- [ ] 🟡 Build n8n workflow: Project ID validator (webhook on #task-dispatch)
- [ ] 🟡 Build n8n workflow: Charter approval gate
- [ ] 🟡 Build n8n workflow: Conflict registry watchdog
- [ ] 🟡 Build n8n workflow: Severity routing automation
- [ ] 🟡 Build n8n workflow: Token cost monitor with kill switch
- [ ] 🟡 Build n8n workflow: Anti-pattern repeat detection
- [ ] 🟡 Build n8n workflow: Heartbeat dead man's switch

## Phase 1D — Repo Housekeeping

- [ ] 🟡 Rewrite README.md for multi-agent framework focus
- [ ] 🟡 Archive outdated single-agent docs to docs/archive/
- [ ] 🟡 Review discord-design-docs/ and merge or archive
- [ ] 🟢 Update .gitignore for new paths
- [ ] ⚪ Update HTML dashboard with full file structure detail

## Phase 2 — Deployment & Testing

- [ ] 🟡 Deploy all 5 agents on VPS
- [ ] 🟡 Verify Discord channel bindings and routing
- [ ] 🟡 Test full project lifecycle: charter → ID → dispatch → work → review → complete
- [ ] 🟡 Test conflict detection on overlapping scope
- [ ] 🟡 Test severity escalation chain (INFO → WARN → BLOCKED → CRITICAL)
- [ ] 🟡 Test n8n enforcement catches violations
- [ ] 🟢 Run first real project through the system end-to-end

## Phase 3+ — Expansion

- [ ] ⚪ Evaluate need for additional specialists (Creative, Data, Security, Writer)
- [ ] ⚪ Implement on-demand specialist spawning via sessions_spawn
- [ ] ⚪ Cross-project knowledge transfer system
- [ ] ⚪ Automated charter generation for recurring project types
