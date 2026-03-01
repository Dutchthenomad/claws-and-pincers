# Implementation Plan — Native OpenClaw Alignment

**Date:** 2026-03-01
**Author:** Claude Opus 4.6 (VPS session)
**Source:** OPENCLAW-COMPLIANCE-AUDIT.md (9 compliance issues, 10 optimization opportunities)
**Scope:** Full project update — config, governance, agent workspaces, reference docs, operations docs, README

---

## Overview

This plan brings Claws & Pincers into full compliance with the OpenClaw platform by replacing external/custom systems with native OpenClaw features. It is organized into 7 phases executed sequentially. Each phase lists every file affected, what changes, and why.

**Guiding principle:** Use OpenClaw native features first. Only use external tools (n8n, custom APIs) for things OpenClaw genuinely cannot do.

---

## Phase 1: Config Hardening (openclaw.json5)

**Addresses:** C-05, C-07, C-08, C-09, O-01, O-06, O-08, O-09, O-10

### 1.1 Fix agentToAgent hub-and-spoke routing (C-05)

**File:** `openclaw.json5`

Remove the global `agentToAgent.allow` list. Add per-agent overrides so only the Orchestrator can contact all agents, and specialists can only contact the Orchestrator:

```jsonc
// Remove from agents.defaults:
//   agentToAgent: { enabled: true, allow: [...all 5...] }

// Add per-agent:
orchestrator: { tools: { agentToAgent: { enabled: true, allow: ["*"] } } }
researcher:   { tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } }
developer:    { tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } }
sysadmin:     { tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } }
reviewer:     { tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } }
```

### 1.2 Per-agent heartbeat intervals (C-07, O-10)

**File:** `openclaw.json5`

Replace the global `heartbeat.every: "30m"` with per-agent settings:

| Agent | Interval | Model Override | Rationale |
|-------|----------|---------------|-----------|
| Orchestrator | 15m | (primary) | Active coordinator, needs frequent check-ins |
| Sysadmin | 30m | `groq/llama-3.3-70b-versatile` | Infrastructure monitoring, cheaper model sufficient |
| Researcher | 2h | `groq/llama-3.3-70b-versatile` | Low-frequency check-in only |
| Developer | 2h | `groq/llama-3.3-70b-versatile` | Only active during project work |
| Reviewer | 4h | `groq/llama-3.3-70b-versatile` | Checks for pending reviews |

Add heartbeat visibility config per agent (`showOk: false` for infrequent agents, `showAlerts: true` for all).

### 1.3 Tool permission tightening (C-09)

**File:** `openclaw.json5`

| Agent | Change | Reason |
|-------|--------|--------|
| Orchestrator | Remove `exec` from allow, add to deny | Charter says "does not write code" |
| Orchestrator | Add `sessions_spawn`, `sessions_send`, `sessions_list`, `sessions_history`, `cron` to allow | Core delegation tools |
| Researcher | Remove `exec` from allow, add to deny | Charter says "cannot execute code" |
| Developer | Add `web_search` to allow | Needs documentation lookup |
| All specialists | Add `sessions_send` to allow | Need to communicate back to Orchestrator |

### 1.4 Enable native platform features (O-01, O-06, O-08, O-09)

**File:** `openclaw.json5`

Add/enable:
```jsonc
hooks: { enabled: true }
cron: { enabled: true }
gateway: { openaiApi: { enabled: true } }
plugins: { slots: { memory: "memory-core" } }
channels: {
  discord: {
    execApprovals: {
      enabled: true,
      approvers: ["<devin-discord-id>"]
    }
  }
}
```

### 1.5 Sandbox evaluation (C-08)

**File:** `openclaw.json5`

Set sandbox mode per agent based on risk profile:

| Agent | Sandbox Mode | Rationale |
|-------|-------------|-----------|
| Orchestrator | off | Coordinator only, no code execution |
| Researcher | off | Read-only research, exec denied via tools |
| Developer | `lenient` | Executes code, needs some containment |
| Sysadmin | off | Needs full host access for infrastructure |
| Reviewer | off | Read-only by tool policy |

Add `tools.elevated` restrictions where appropriate.

---

## Phase 2: CORE-CHARTER v2.0 Rewrite

**Addresses:** C-01, C-02, C-03, C-04, C-05, C-06

### 2.1 Rewrite CORE-CHARTER.md

**File:** `governance/operations/CORE-CHARTER.md`

This is the most impactful change. The CORE-CHARTER must be updated from v1.1 to v2.0 with the following section-by-section changes:

| Section | Current State | Required Change |
|---------|--------------|-----------------|
| Section 4.4 (Task Dispatch) | `task-board.json` as source of truth | Replace with `sessions_spawn` as primary dispatch mechanism. Orchestrator spawns specialist sessions. Discord channels remain as human-visible layer |
| Section 4.5 (Execution) | `active-locks.json` for collision prevention | Replace with OpenClaw session isolation (each spawned session is inherently isolated) |
| Section 5 (Communication) | Text-based rules about hub-and-spoke | Add explicit reference to `agentToAgent` config enforcement. Note that platform enforces this, not just policy |
| Section 7 (Self-Learning) | `anti-patterns.md` in shared directory | Move anti-patterns into each agent's workspace `memory/` as evergreen files |
| Section 8.2 (File Coordination) | "Actual coordination state lives in JSON files" | Coordination state lives in sessions (`sessions_list`, `sessions_history`). Persistent records in workspace `memory/` and Discord threads |
| Section 8.3 (Communication Pathways) | "Specialists do NOT message each other directly" | Add: "This is enforced at platform level via `agentToAgent` config" |
| Section 9 (File Structure) | Custom `~/.openclaw/` layout | Align with OpenClaw native workspace layout (SOUL.md, AGENTS.md, USER.md, IDENTITY.md, HEARTBEAT.md, BOOTSTRAP.md, TOOLS.md, BOOT.md, memory/, notes/) |
| NEW Section | — | Add section on OpenClaw native features used: cron, heartbeats, sessions, memory-core, Discord threads, webhooks |
| NEW Section | — | Add section on n8n scope: external integrations only, not governance enforcement |

### 2.2 Remove file-based coordination references

All references to these files as "source of truth" must be removed or redirected:
- `task-board.json` → `sessions_list` / `sessions_history` + Discord thread per project
- `active-locks.json` → Session isolation (no locks needed)
- `conflict-registry.json` → Conflicts tracked in dedicated Discord channel + agent memory

### 2.3 Update the 4 Laws enforcement mechanism

The 4 Laws remain unchanged in substance. What changes is HOW they're enforced:

| Law | Old Enforcement | New Enforcement |
|-----|----------------|-----------------|
| 1: No Project ID, No Work | n8n polls Discord every 30s | Orchestrator's AGENTS.md enforces on every message + cron job audit |
| 2: No Charter, No Code | n8n polls every 30s | Orchestrator's AGENTS.md enforces + cron job audit |
| 3: Conflict = No Pass | Manual file checks | Session isolation prevents overlap; Orchestrator checks via `sessions_list` |
| 4: Quality Over Speed | Reviewer checks task-board | Reviewer checks via `sessions_history` on spawned reviews |

---

## Phase 3: Agent Workspace Files Update (30 files)

**Addresses:** C-01, C-02, C-03, C-06, C-07, O-02, O-03, O-05

### 3.1 All Agents — AGENTS.md (5 files)

**Files:**
- `agents/orchestrator/AGENTS.md`
- `agents/researcher/AGENTS.md`
- `agents/developer/AGENTS.md`
- `agents/sysadmin/AGENTS.md`
- `agents/reviewer/AGENTS.md`

**Common changes for ALL agents:**
1. Remove ALL references to `task-board.json`, `active-locks.json`, `conflict-registry.json`
2. Replace file-based coordination SOPs with session-based equivalents
3. Add `sessions_send` instructions for communicating with Orchestrator
4. Add reference to workspace `memory/` for persistent notes
5. Embed relevant 4 Laws summary (agents see AGENTS.md every session)
6. Add anti-patterns summary (from `governance/shared/anti-patterns.md`)

**Orchestrator-specific AGENTS.md changes:**
- SOPs 4-8 currently reference file reads/writes → replace with `sessions_spawn`, `sessions_send`, `sessions_list`, `sessions_history`
- Add SOP for creating Discord threads per project (`sessions_spawn(thread=true)`)
- Add SOP for cron-based governance audits
- Add SOP for checking `sessions_list` during heartbeats instead of reading JSON files
- Document the Orchestrator as the ONLY agent that can `sessions_spawn` specialists

**Researcher AGENTS.md changes:**
- Remove `exec`-based SOPs (tool is denied)
- Update communication SOPs to use `sessions_send` to Orchestrator
- Add SOP for workspace memory usage (write findings to `memory/`)

**Developer AGENTS.md changes:**
- Update project pickup SOP: receive work via spawned session, not channel monitoring
- Add `web_search` usage for documentation lookups
- Update delivery SOP: announce completion via session (auto-announces back to spawner)

**Sysadmin AGENTS.md changes:**
- Remove `active-locks.json` check (SOP-2)
- Add cron-based monitoring SOPs
- Update infrastructure check procedures to use heartbeat context

**Reviewer AGENTS.md changes:**
- Update review trigger: receive spawned review sessions from Orchestrator
- Remove task-board polling
- Add `sessions_history` for reviewing specialist work
- Update verdict delivery: announce back via session

### 3.2 All Agents — HEARTBEAT.md (5 files)

**Files:**
- `agents/orchestrator/HEARTBEAT.md`
- `agents/researcher/HEARTBEAT.md`
- `agents/developer/HEARTBEAT.md`
- `agents/sysadmin/HEARTBEAT.md`
- `agents/reviewer/HEARTBEAT.md`

**Common changes:**
- Remove ALL references to reading `task-board.json`, `conflict-registry.json`
- Replace with `sessions_list` checks and workspace memory review

**Per-agent heartbeat task updates:**

| Agent | Old Heartbeat Tasks | New Heartbeat Tasks |
|-------|-------------------|-------------------|
| Orchestrator | Read task-board.json, check conflicts, check deployments | `sessions_list` for stuck sessions, check for unresolved conflicts in #conflict-resolution, review cost via `/usage` |
| Researcher | Check for pending research requests | Check for spawned sessions awaiting response |
| Developer | Check for assigned tasks in task-board | Check for spawned sessions awaiting implementation |
| Sysadmin | Check infrastructure, read active-locks | Infrastructure health check (existing), check for spawned sessions |
| Reviewer | Governance spot check via task-board | Check `sessions_list` for completed work needing review |

### 3.3 All Agents — SOUL.md (5 files)

**Files:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/SOUL.md`

**Changes:** Minor updates only:
- Update any references to file-based coordination
- Keep R&M character identities intact
- Add brief note about native OpenClaw tool usage philosophy

### 3.4 All Agents — IDENTITY.md (5 files)

**Files:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/IDENTITY.md`

**Changes:** No content changes needed. These contain R&M character identities. Verify they match SOUL.md.

### 3.5 All Agents — USER.md (5 files)

**Files:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/USER.md`

**Changes:** Review for any stale references. Update if they mention n8n as "control plane" or reference file-based coordination.

### 3.6 All Agents — TOOLS.md (5 files)

**Files:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/TOOLS.md`

**Changes:**
- Add documentation for session tools (`sessions_spawn`, `sessions_send`, etc.) where appropriate
- Orchestrator: Add cron tool documentation
- Remove references to tools that are now denied per C-09

### 3.7 BOOTSTRAP.md Cleanup (C-06)

**Decision point:** Either:
- **Option A (Recommended):** Pre-populate IDENTITY.md with finalized identities, remove BOOTSTRAP.md from all agent dirs, add BOOT.md with startup governance checks
- **Option B:** Run each agent through BOOTSTRAP.md flow, then delete

**BOOT.md (NEW, 5 files):**
Create `agents/{each}/BOOT.md` with startup checklist:
1. Read anti-patterns from workspace memory
2. Check `sessions_list` for any orphaned sessions
3. Verify model provider (OpenRouter) is responding
4. Report ready status to #agent-status channel

---

## Phase 4: Governance & Template Docs Update

**Addresses:** C-03, C-04 residual references

### 4.1 Governance Templates (4 files)

**Files:**
- `governance/templates/charter-template.md` — Remove references to `task-board.json` registration. Project registration now happens via Orchestrator's `sessions_spawn` with thread creation
- `governance/templates/task-template.md` — Update to reflect session-based task tracking instead of JSON files
- `governance/templates/conflict-report-template.md` — Update resolution pathway to use `sessions_send` to Orchestrator + #conflict-resolution channel
- `governance/templates/severity-definitions.md` — No changes needed (severity levels are abstract)

### 4.2 Governance Shared Files

**File:** `governance/shared/anti-patterns.md`
- No content changes (the 7 anti-patterns are valid)
- Add note: "This file is replicated into each agent's workspace `memory/` directory as an evergreen file"

**Files to evaluate for removal:**
- `governance/shared/task-board.json` — Archive or remove (replaced by session tools)
- `governance/shared/active-locks.json` — Archive or remove (replaced by session isolation)
- `governance/shared/conflict-registry.json` — Archive or remove (replaced by Discord channel + memory)

### 4.3 Other Governance Docs

**File:** `governance/operations/PROJECT-REGISTRY.md`
- Update project lifecycle to reference Discord threads and session-based tracking
- Keep project ID scheme (PROJ-XXX)

**File:** `governance/operations/EXPANSION-ROADMAP.md`
- Update Phase 2 description to match new native-OpenClaw approach
- Mark items that are now handled by native features

---

## Phase 5: Reference Docs, Operations & Planning Docs Update

### 5.1 Reference Docs (14 files)

**File: `reference/01-OPENCLAW-OVERVIEW.md`**
- MINOR: Update to reflect native feature usage (cron, sessions, memory-core)

**File: `reference/02-DISCORD-INTEGRATION.md`**
- MINOR: Add Discord threads for project isolation, Discord components v2 mention

**File: `reference/03-MULTI-AGENT-ARCHITECTURE.md`**
- CRITICAL REWRITE: Clarify hub-and-spoke model, document `agentToAgent` config enforcement, add session-based delegation model diagram

**File: `reference/04-AGENT-COMMUNICATION.md`**
- CRITICAL REWRITE: Replace direct-agent-to-agent model with session-based hub-and-spoke. Document `sessions_spawn`, `sessions_send`, `sessions_list`, `sessions_history` as the communication primitives

**File: `reference/05-IDENTITY-AND-PERSONAS.md`**
- MINOR: Verify R&M identities match deployed workspace files

**File: `reference/06-SKILLS-AND-CLAWHUB.md`**
- MINOR: Add section on workspace-level skills for governance SOPs (O-05)

**File: `reference/07-SERVER-ARCHITECTURE.md`**
- MAJOR REWRITE: Remove assumption that n8n is the control plane. Update to show OpenClaw gateway as primary orchestration with n8n for external integrations only. Update container list, port mappings, service descriptions

**File: `reference/08-CONFIGURATION-REFERENCE.md`**
- MAJOR REWRITE: Update all config examples to use OpenRouter model refs. Add `agentToAgent`, cron, heartbeat, hooks, memory plugin, openaiApi config examples. Remove direct model references

**File: `reference/09-AUTONOMOUS-LOOPS.md`**
- MODERATE: Add cron job examples, clarify heartbeat vs cron use cases, add `sessions_spawn` for delegation loops

**File: `reference/10-SECURITY-AND-SAFETY.md`**
- MINOR: Add sandbox mode documentation, exec approval buttons, tool policy enforcement

**File: `reference/11-DEPLOYMENT-GUIDE.md`**
- MAJOR: Update VPS deployment guide to include config hardening steps, workspace setup procedures, cron job setup, webhook configuration

**File: `reference/12-RESOURCE-LINKS.md`**
- MINOR: Verify all links are current

**File: `reference/13-BROWSER-AUTOMATION.md`**
- NONE: No changes needed

**File: `reference/README.md`**
- MINOR: Update any references to removed/restructured docs

### 5.2 Operations Docs (2 files)

**File: `operations/DEPLOYMENT-STATE.md`**
- Update container list (verify current count)
- Remove "Token cost monitoring planned as n8n workflow" → replace with "Native OpenClaw `/usage` + cron job"
- Update n8n workflow section to reflect reduced scope (external integrations only)

**File: `operations/AUDIT-2026-02-26.md`**
- No changes (historical record)

### 5.3 Planning Docs (5 active files)

**File: `docs/plans/SESSION-CONTINUITY.md`**
- MAJOR REWRITE: Update Phase 2 plan from n8n-centric to native-OpenClaw. Update infrastructure state. Remove references to n8n as "universal control plane"

**File: `docs/plans/2026-02-26-repo-update-design.md`**
- No changes (historical design doc for completed work)

**File: `docs/plans/2026-02-27-foundation-completion-design.md`**
- No changes (historical design doc for completed work)

**File: `docs/plans/2026-02-27-phase2a-laws-enforcement-design.md`**
- Add addendum noting that the 3 n8n workflows (Law 1, Law 2, Severity Routing) are being replaced by native OpenClaw cron + AGENTS.md enforcement. The n8n workflows remain deployed but are deprecated

**File: `docs/plans/OPENCLAW-COMPLIANCE-AUDIT.md`**
- No changes (reference document for this plan)

### 5.4 Config Files (4 files)

**File: `config/model-routing.yaml`**
- Add heartbeat model override entries
- Add cron model override entries
- Verify OpenRouter routing is complete

**File: `config/cost-registry.yaml`**
- Line 53: Replace "n8n workflow (Phase 2A)" reference with "Native OpenClaw `/usage` + cron job"
- Add heartbeat cost estimates with new per-agent intervals

**File: `config/capability-timeline.yaml`**
- ARCHIVE: This is a 906-line legacy 30-day experiment config (Feb 1 - Mar 2, 2026) that has expired. Move to `docs/archive/config/capability-timeline.yaml`

**File: `config/permission-tiers.yaml`**
- ARCHIVE OR RECONCILE: This 633-line custom tier system conflicts with OpenClaw's native `sandbox` + `tools.allow/deny` + `tools.elevated`. Two options:
  - **Option A (Recommended):** Archive to `docs/archive/config/permission-tiers.yaml`. The native OpenClaw tool policy (configured in openclaw.json5) replaces this
  - **Option B:** Reconcile by mapping tiers to OpenClaw native equivalents and keeping as documentation reference

### 5.5 Top-Level Docs (2 files)

**File: `TODO.md`**
- MAJOR REWRITE: Update Phase 2 from "n8n Core Systems" to "Native OpenClaw Integration". Remove n8n-as-control-plane language. Add new sub-phases matching this plan. Update Phase 3+ to reflect reduced n8n scope

**File: `PROJECT-REFRESHER.md`**
- Update "What's Next" section
- Update Phase 2 description
- Remove references to n8n as control plane

### 5.6 Deployment Docs (3 files)

**File: `deployment/discord-agents/README.md`**
- Already marked DEPRECATED — no changes needed

**File: `deployment/discord-agents/QUICKSTART.md`**
- Update channel section if referenced channels have changed
- Add note about native OpenClaw features available

**File: `deployment/discord-agents/OAUTH2_URLS.md`**
- No changes (OAuth URLs are independent of architecture)

---

## Phase 6: n8n Workflow Scope Reduction

**Addresses:** C-04, O-01, O-06

### 6.1 Deprecate governance n8n workflows

The 3 deployed n8n workflows are being replaced by native OpenClaw enforcement:

| n8n Workflow | Replacement | Action |
|---|---|---|
| Law 1: Project ID Validator | Orchestrator AGENTS.md + cron audit | Disable in n8n, keep JSON export as archive |
| Law 2: Charter Approval Gate | Orchestrator AGENTS.md + cron audit | Disable in n8n, keep JSON export as archive |
| Severity Routing | Orchestrator `sessions_send` + Discord tools | Disable in n8n, keep JSON export as archive |

### 6.2 Define n8n's new scope

n8n retains value for:
1. **External notifications** — Email alerts, Slack webhooks (if added), SMS via Apprise
2. **Cost dashboard** — Aggregate `/usage` data into Metabase/Grafana
3. **External API integrations** — Services that agents can't reach natively
4. **Webhook receivers** — Accept POSTs from OpenClaw cron/hooks for external processing

### 6.3 Set up OpenClaw cron jobs

Create initial cron jobs to replace n8n governance:

```bash
# Law 1 audit: Check for untagged messages every 5 minutes
openclaw cron add --name "law1-audit" --cron "*/5 * * * *" \
  --agent orchestrator --session isolated \
  --message "Scan #task-dispatch for any messages in the last 5 minutes without PROJ-XXX tags. Report violations to #severity-alerts."

# Law 2 audit: Check for unapproved charters every 15 minutes
openclaw cron add --name "law2-audit" --cron "*/15 * * * *" \
  --agent orchestrator --session isolated \
  --message "Check if any active projects lack an approved charter. Report violations to #severity-alerts."

# Cost check: Daily cost summary
openclaw cron add --name "cost-daily" --cron "0 0 * * *" \
  --agent orchestrator --session isolated --model "groq/llama-3.3-70b-versatile" \
  --message "Generate a daily cost summary using /usage data. Report to #cost-tracking."
```

### 6.4 Set up OpenClaw webhooks

Configure webhook integration so OpenClaw pushes events to n8n (replacing n8n polling Discord):

```jsonc
// In openclaw.json5
hooks: {
  enabled: true,
  webhooks: {
    "governance-alert": {
      url: "http://127.0.0.1:5678/webhook/openclaw-governance",
      events: ["cron.complete", "session.error", "heartbeat.alert"]
    }
  }
}
```

---

## Phase 7: README.md Marketing Landing Page

**Addresses:** User request for marketing-optimized README

**File:** `README.md`

### 7.1 Target audience

The README serves as the GitHub landing page for anyone discovering the project. Target audiences:
- **AI/ML engineers** interested in multi-agent architectures
- **OpenClaw community members** looking for real-world implementations
- **Potential collaborators** evaluating project quality
- **Devin's portfolio visitors** assessing technical depth

### 7.2 Structure

```markdown
# Claws & Pincers

> [One-line tagline about autonomous AI agent team on Discord]

[Hero section: What it does in 2-3 sentences]

## Architecture

[Clean Mermaid diagram showing 5 agents, gateway, Discord, infrastructure]

## The Team

[Table of 5 agents with roles, models, personalities]

## Governance

[Brief explanation of 4 Laws, severity system, anti-patterns]
[Why this matters — quality over speed, structured autonomy]

## Tech Stack

[Clean list: OpenClaw, OpenRouter, Docker, Qdrant, TimescaleDB, etc.]

## Project Structure

[Condensed tree view of repo]

## Getting Started

[Quick setup guide — clone, configure, deploy]

## Status

[Current phase, what's deployed, what's next]

## License / Author

[Devin/Dutchthenomad credit, contact]
```

### 7.3 Quality standards

- Professional tone, no jargon overload
- Mermaid architecture diagram (rendered natively by GitHub)
- Clean badges (build status, license, etc.) if applicable
- Mobile-friendly formatting
- No internal implementation details — focus on WHAT, not HOW
- Link to reference docs for deep dives

---

## Phase 8: Verification & Cleanup

### 8.1 Full doc scan

After all changes, scan every active markdown file (excluding `docs/archive/` and `.venv/`) for stale references:

**Search terms to verify are removed from all active docs:**
- `task-board.json` (replaced by session tools)
- `active-locks.json` (replaced by session isolation)
- `conflict-registry.json` (replaced by Discord channel + memory)
- `n8n.*universal control plane` (n8n scope reduced)
- `n8n.*governance` (moved to native OpenClaw)
- `Phase 2A.*n8n` (redesigned)
- `Phase 2B.*n8n` (redesigned)

### 8.2 Config validation

```bash
# Verify openclaw.json5 is valid
openclaw config validate

# Verify gateway accepts the new config
openclaw gateway restart
openclaw health
```

### 8.3 Workspace deployment

Sync updated workspace files to the live deployment:
```bash
# For each agent, sync workspace files
for agent in orchestrator researcher developer sysadmin reviewer; do
  rsync -av agents/$agent/ /opt/openclaw/config/workspace-$agent/
done

# Restart gateway to pick up config changes
cd /opt/openclaw/gateway && docker compose restart
```

### 8.4 Archive moved files

Ensure all archived files are properly moved:
- `config/capability-timeline.yaml` → `docs/archive/config/capability-timeline.yaml`
- `config/permission-tiers.yaml` → `docs/archive/config/permission-tiers.yaml` (if archiving)
- `n8n/*.json` → remain in place as reference but add deprecation headers

### 8.5 Git commit sequence

```
1. chore: archive legacy config files (capability-timeline, permission-tiers)
2. feat: harden openclaw.json5 (hub-and-spoke, heartbeats, tool policy, native features)
3. docs: rewrite CORE-CHARTER v2.0 (session-based coordination)
4. docs: update all 30 agent workspace files for native OpenClaw alignment
5. docs: update governance templates and shared files
6. docs: update reference docs (03, 04, 07, 08, 09, 11 rewrites; others minor)
7. docs: update operations, planning, and top-level docs
8. feat: add cron jobs and webhook config for native governance
9. docs: rewrite README.md as marketing landing page
```

---

## File Impact Summary

### Files with MAJOR changes (full rewrite or significant restructuring)

| File | Phase | Change Type |
|------|-------|------------|
| `openclaw.json5` | 1 | Config hardening — hub-and-spoke, heartbeats, tools, features |
| `governance/operations/CORE-CHARTER.md` | 2 | v2.0 rewrite — session-based coordination |
| `agents/orchestrator/AGENTS.md` | 3 | SOPs rewritten for session tools |
| `agents/researcher/AGENTS.md` | 3 | Remove exec SOPs, add session communication |
| `agents/developer/AGENTS.md` | 3 | Session-based project pickup and delivery |
| `agents/sysadmin/AGENTS.md` | 3 | Remove lock file checks, add cron monitoring |
| `agents/reviewer/AGENTS.md` | 3 | Session-based review trigger and delivery |
| `agents/*/HEARTBEAT.md` (5 files) | 3 | Replace file polling with session checks |
| `reference/03-MULTI-AGENT-ARCHITECTURE.md` | 5 | Hub-and-spoke documentation rewrite |
| `reference/04-AGENT-COMMUNICATION.md` | 5 | Session-based communication rewrite |
| `reference/07-SERVER-ARCHITECTURE.md` | 5 | Remove n8n-as-control-plane assumption |
| `reference/08-CONFIGURATION-REFERENCE.md` | 5 | Full config examples update |
| `reference/11-DEPLOYMENT-GUIDE.md` | 5 | Deployment procedure update |
| `docs/plans/SESSION-CONTINUITY.md` | 5 | Phase 2 plan rewrite |
| `TODO.md` | 5 | Phase 2+ roadmap rewrite |
| `README.md` | 7 | Marketing landing page rewrite |

### Files with MODERATE changes (targeted updates)

| File | Phase | Change Type |
|------|-------|------------|
| `agents/*/SOUL.md` (5 files) | 3 | Remove stale coordination references |
| `agents/*/TOOLS.md` (5 files) | 3 | Add session tool documentation |
| `agents/*/USER.md` (5 files) | 3 | Remove n8n control plane references |
| `governance/templates/charter-template.md` | 4 | Session-based registration |
| `governance/templates/task-template.md` | 4 | Session-based tracking |
| `governance/templates/conflict-report-template.md` | 4 | Session-based resolution |
| `governance/operations/PROJECT-REGISTRY.md` | 4 | Thread-based project lifecycle |
| `governance/operations/EXPANSION-ROADMAP.md` | 4 | Update Phase 2 description |
| `reference/09-AUTONOMOUS-LOOPS.md` | 5 | Add cron examples |
| `operations/DEPLOYMENT-STATE.md` | 5 | Update service descriptions |
| `config/model-routing.yaml` | 5 | Add heartbeat/cron model overrides |
| `config/cost-registry.yaml` | 5 | Remove n8n reference |
| `PROJECT-REFRESHER.md` | 5 | Update Phase 2 description |

### Files with MINOR changes (small fixes or verification only)

| File | Phase | Change Type |
|------|-------|------------|
| `agents/*/IDENTITY.md` (5 files) | 3 | Verify consistency with SOUL.md |
| `governance/shared/anti-patterns.md` | 4 | Add replication note |
| `governance/templates/severity-definitions.md` | 4 | No changes |
| `reference/01-OPENCLAW-OVERVIEW.md` | 5 | Minor native feature mention |
| `reference/02-DISCORD-INTEGRATION.md` | 5 | Add threads and components v2 |
| `reference/05-IDENTITY-AND-PERSONAS.md` | 5 | Verify identities |
| `reference/06-SKILLS-AND-CLAWHUB.md` | 5 | Add workspace skills section |
| `reference/10-SECURITY-AND-SAFETY.md` | 5 | Add sandbox docs |
| `reference/12-RESOURCE-LINKS.md` | 5 | Verify links |
| `reference/13-BROWSER-AUTOMATION.md` | 5 | No changes |
| `reference/README.md` | 5 | Minor update |
| `docs/plans/2026-02-27-phase2a-laws-enforcement-design.md` | 5 | Add deprecation addendum |
| `deployment/discord-agents/QUICKSTART.md` | 5 | Minor channel update |
| `operations/AUDIT-2026-02-26.md` | — | No changes (historical) |

### Files to ARCHIVE (move to `docs/archive/`)

| File | Destination |
|------|------------|
| `config/capability-timeline.yaml` | `docs/archive/config/capability-timeline.yaml` |
| `config/permission-tiers.yaml` | `docs/archive/config/permission-tiers.yaml` |

### Files to CREATE

| File | Phase | Purpose |
|------|-------|---------|
| `agents/*/BOOT.md` (5 files) | 3 | Startup governance checks |

### Files UNCHANGED (no action needed)

- `CLAUDE.md` (project instructions — separate from repo docs)
- `docs/archive/*` (all 18 archived files — historical, not updated)
- `docs/plans/2026-02-26-repo-update-design.md` (completed historical design)
- `docs/plans/2026-02-27-foundation-completion-design.md` (completed historical design)
- `docs/plans/OPENCLAW-COMPLIANCE-AUDIT.md` (audit source document)
- `deployment/discord-agents/README.md` (already marked DEPRECATED)
- `deployment/discord-agents/OAUTH2_URLS.md` (OAuth URLs unchanged)
- `visuals/*` (diagrams — update separately if needed)
- `n8n/*.json` (workflow exports — kept as reference)
- `scripts/*` (tooling — unchanged)

---

## Estimated Scope

| Phase | Files Affected | Complexity |
|-------|---------------|-----------|
| Phase 1: Config Hardening | 1 | MEDIUM |
| Phase 2: CORE-CHARTER v2.0 | 1 | HIGH |
| Phase 3: Agent Workspaces | 30 (+5 new BOOT.md) | HIGH |
| Phase 4: Governance Docs | 7 | MEDIUM |
| Phase 5: Reference & Ops Docs | ~20 | HIGH |
| Phase 6: n8n Scope Reduction | 3 workflows + config | MEDIUM |
| Phase 7: README Landing Page | 1 | MEDIUM |
| Phase 8: Verification | 0 (scan only) | LOW |
| **Total** | **~65 files** | — |

---

## Dependencies & Risks

### Dependencies
- Phase 2 (CORE-CHARTER) must be completed before Phase 3 (agent workspaces) — agents reference the charter
- Phase 1 (config) should be completed before Phase 6 (cron setup) — cron needs to be enabled first
- Phase 8 (verification) runs last

### Risks
1. **OpenClaw cron feature may require specific gateway version** — verify `openclaw cron` is available in v2026.2.26
2. **Webhook config syntax may differ from documented examples** — test with `openclaw config validate`
3. **Agent workspace sync requires gateway restart** — brief downtime during Phase 8.3
4. **Some OpenClaw features (Lobster, ClawHub) are lower priority** — deferred to future phases

### Out of Scope (Future Work)
- O-04: Discord Components v2 (buttons for governance) — requires frontend implementation
- O-05: ClawHub skill publishing — requires account setup and skill packaging
- O-07: Lobster workflow engine investigation — requires testing and evaluation
- Mermaid diagrams in `visuals/` — update after architecture changes settle
