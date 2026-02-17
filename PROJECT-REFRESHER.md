# OpenClaw Agent Team — Project Refresher

## What This Is

You're building an autonomous multi-agent team using OpenClaw on Discord. Think of it like a small company: you're the CEO, an Orchestrator bot is your VP, and specialist bots (Researcher, Developer, Sysadmin, Reviewer/QA) are your department heads. They each have their own Discord workspace, share a coordination channel, and operate under strict governance rules you defined.

The model is inspired by Anthropic's Agent Teams framework (Carlini's C compiler project — 16 parallel Claudes, 2,000 sessions, $20K, zero human interaction for weeks). Your version adds persistent agents, a governance layer, and project-based isolation that their system doesn't have.

---

## What's Been Built (Two Doc Packages)

### Package 1: OpenClaw Reference Docs (13 files, 102KB)
Technical reference for how OpenClaw works — Discord integration, multi-agent routing, bindings, session tools, skills, security, deployment. This is the "how does the platform work" knowledge base.

**Download:** `openclaw-discord-agents.zip`

### Package 2: Governance & Operations Docs (11 files, ~35KB)
The actual operating system for your agent team. This is what matters for building.

**operations/**
- `CORE-CHARTER.md` — The master document. Org hierarchy, 4 absolute laws, full project lifecycle, severity levels, conflict detection, self-learning anti-pattern system, Discord channel map, file system structure, access control matrix.
- `PROJECT-REGISTRY.md` — Where all projects are tracked. PROJ-XXX format.
- `EXPANSION-ROADMAP.md` — Phase 1-4 plans.

**templates/**
- `charter-template.md` — Every project needs one before code starts.
- `task-template.md` — Per-task template with governance pre-checks.
- `conflict-report-template.md` — Structured conflict logging.
- `severity-definitions.md` — INFO/WARN/BLOCKED/CRITICAL + auto-escalation rules.

**shared/**
- `anti-patterns.md` — Pre-loaded with 7 patterns (AP-001 through AP-007).
- `task-board.json`, `active-locks.json`, `conflict-registry.json` — Initialized, empty.

**Download:** `agent-team-governance-docs.zip`

### Interactive Dashboard
`agent-team-dashboard.html` — Tabbed visual showing org structure, Discord layout, file system, and governance flow. Opens in browser.

---

## Your 4 Absolute Laws
1. **No Project ID, No Work Allowed** — Every task needs a PROJ-XXX tag.
2. **No Charter, No Code** — Charter approved by you before implementation starts.
3. **Conflict = No Pass** — Scope/resource/dependency overlap blocks work until resolved.
4. **Quality Over Speed** — "Fast but wrong" is a governance violation.

---

## What's NOT Built Yet

### Must-Have (Before Agents Can Run)
- [ ] **SOUL.md files** for each agent (personality, rules, boundaries)
- [ ] **AGENTS.md files** for each agent (operational instructions)
- [ ] **HEARTBEAT.md files** for each agent (proactive check-in checklists)
- [ ] **openclaw.json5** — The actual OpenClaw configuration tying everything together
- [ ] **GOVERNANCE-RULES.md** — Detailed enforcement procedures (companion to CORE-CHARTER)

### Should-Have (Discussed, Not Specced)
- [ ] **n8n enforcement layer** — Programmatic compliance enforcement sitting between Discord and OpenClaw. Catches violations in real-time without relying on agent self-policing. Key workflows:
  - Project ID validation on every dispatch
  - Charter approval gate check
  - Conflict registry watchdog
  - Severity routing automation
  - Token cost monitoring with kill switch
  - Anti-pattern repeat detection
  - Dead man's switch / heartbeat monitor
- [ ] **Setup script** — Automated creation of the full file structure and Discord server

### Nice-to-Have (Mentioned)
- [ ] Updated HTML dashboard with full file structure detail
- [ ] Mermaid diagram files (created but rendering was problematic on mobile)

---

## Your Existing Setup
- Discord server: built
- Bot applications: multiple (one per agent)
- Some bots already working in server
- Missing: the comprehensive framework connecting everything

---

## Where to Start at Lunch

**If you have Claude Code available:**
1. Download both zip packages to your project directory
2. The governance docs (Package 2) are the ones Claude Code needs first
3. CORE-CHARTER.md is the single most important file — it defines everything
4. Next priority: get the SOUL.md and openclaw.json5 written (we haven't done these yet)

**If you're continuing here with me:**
1. SOUL.md files for all 5 agents — these define who each agent IS
2. openclaw.json5 config — this wires everything together in OpenClaw
3. n8n workflow specs — the enforcement layer

**If you just want to read and think:**
1. Open CORE-CHARTER.md and read Sections 3 (Absolute Laws) and 4 (Project Lifecycle)
2. Look at the charter-template.md to see what every project requires
3. Think about whether the 4 specialist roles feel right or need adjusting

---

## Key Design Decisions Already Made
- Orchestrator is coordination-only (no code, no research)
- File-based coordination (task-board.json, locks, conflict registry) keeps agent context clean
- Discord #status-updates is lightweight observation channel for you, not the coordination mechanism
- Specialists don't message each other directly — everything flows through Orchestrator
- You can direct-chat any specialist for simple stuff
- Phase 2+ specialists added through the standard project process (charter, PROJ-ID, approval)
- n8n sits outside agent context as the enforcement cop they can't override
