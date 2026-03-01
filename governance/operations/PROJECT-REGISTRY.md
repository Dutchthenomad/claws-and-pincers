# PROJECT REGISTRY

**Authority:** Orchestrator (maintained) · Devin (oversight)
**Rule:** NO PROJECT ID = NO WORK ALLOWED

---

## Active Projects

| PROJ-ID | Title | Status | Charter Approved | Specialists | Created | Updated |
|---------|-------|--------|-----------------|-------------|---------|---------|
| — | — | — | — | — | — | — |

## Completed Projects

| PROJ-ID | Title | Completed | Charter |
|---------|-------|-----------|---------|
| PROJ-AUDIT-001 | Full Ecosystem Audit & Remediation | 2026-02-26 | Devin-directed (no formal charter) |

### PROJ-AUDIT-001 — Full Ecosystem Audit & Remediation

- **Scope:** Docker infrastructure, configs, security, runtime health, dead code, governance
- **Method:** 6 parallel audit agents + 4-phase remediation
- **Findings:** 6 CRITICAL, 14 HIGH, 18 MEDIUM, 16 LOW
- **Result:** 23 containers (down from 27), 52% disk (down from 57%), all agents healthy and governance-aware
- **Remaining:** C-3 key revocation (user action), n8n credential re-entry, H-13 network segmentation
- **Report:** `/tmp/claws-and-pincers/operations/AUDIT-2026-02-26.md`

## Cancelled / Archived Projects

| PROJ-ID | Title | Cancelled | Reason |
|---------|-------|-----------|--------|
| — | — | — | — |

---

## ID Assignment Rules
- Format: `PROJ-XXX` (zero-padded three digits, starting at PROJ-001)
- IDs are never reused, even for cancelled projects
- Task IDs: `PROJ-XXX-T-YYY` (sequential per project)
- Charter prep tasks: `PROJ-XXX-CHARTER-PREP` (exempt from "no code" rule, research only)
- Conflict IDs: `CONF-XXX` (sequential, global)
- Anti-pattern IDs: `AP-XXX` (sequential, global)

## Project Lifecycle

Projects are tracked through Discord threads and OpenClaw native session tools:

1. **Registration**: Orchestrator creates project entry here, spawns a Discord thread via `sessions_spawn`
2. **Task dispatch**: Individual tasks dispatched to specialists via `sessions_spawn` with project context
3. **Tracking**: Active sessions monitored via `sessions_list`; history via `sessions_history`
4. **Completion**: All tasks reviewed, project marked COMPLETED, thread archived

## Status Definitions
- **ACTIVE** — Charter approved, work in progress (tracked via `sessions_list`)
- **PAUSED** — Work temporarily halted (by Devin or due to BLOCKED issue)
- **COMPLETED** — All tasks done, reviewed, and delivered
- **CANCELLED** — Project terminated before completion
- **BLOCKED** — Cannot proceed due to unresolved conflict or CRITICAL issue
