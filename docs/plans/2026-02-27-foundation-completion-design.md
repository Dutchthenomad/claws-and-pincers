# Design: Foundation Completion — Directory Scaffolding & Discord Channels

> **Date**: 2026-02-27
> **Author**: Claude Opus 4.6 + Devin
> **Status**: APPROVED
> **Scope**: Agent directory restructuring, Discord channel provisioning, project doc updates

---

## Deliverables

### 1. Agent Directory Scaffolding

Restructure each agent directory to CORE-CHARTER Section 9 compliance.

**Current state** (flat):
```
agents/{agent}/
├── SOUL.md
├── AGENTS.md
└── HEARTBEAT.md
```

**Target state**:
```
agents/{agent}/
├── SOUL.md              # Identity (stays at root, not in workspace/)
├── AGENTS.md            # Operations (stays at root)
├── HEARTBEAT.md         # Monitoring config (stays at root)
├── workspace/           # Per-agent working area
│   └── .gitkeep
├── sessions/            # Session history
│   └── .gitkeep
└── skills/              # Agent-specific skills
    └── .gitkeep
```

**Design decision**: SOUL.md, AGENTS.md, HEARTBEAT.md stay at agent root — they're identity docs, not workspace artifacts. The CORE-CHARTER shows them nested in workspace/ but that conflates identity with working state.

### 2. Discord Channel Setup Script

Python script at `deployment/setup-discord-channels.py`.

**27 channels across 8 categories:**

| Category | Channels |
|----------|----------|
| HUMAN CONTROL | #direct-command, #human-oversight, #cost-tracking |
| SHARED WORKSPACE | #task-dispatch, #status-updates, #completed |
| ORCHESTRATOR | #orch-workspace, #orch-logs |
| RESEARCHER | #research-workspace, #research-sources, #research-logs |
| DEVELOPER | #dev-workspace, #dev-testing, #dev-logs |
| SYSADMIN | #sys-workspace, #sys-monitoring, #sys-logs |
| REVIEWER | #review-workspace, #review-verdicts, #review-logs |
| LOGGING & REPORTING | #conflict-log, #error-log, #severity-alerts, #anti-patterns, #project-registry |

**Permission model:**
- Human Control: All bots read, Orchestrator writes
- Shared: All bots read/write
- Agent workspaces: Owning bot + Orchestrator (read-only) only
- Logging: All bots read, Orchestrator + Reviewer write

**Script properties:**
- Uses Orchestrator bot token from `/opt/openclaw/secrets/discord-bots.env`
- Guild ID: `1472374974340665477`
- Idempotent (checks before creating)
- Uses raw `requests` (no async dependency)
- Logs actions taken

### 3. Governance Files

Already properly structured — no changes needed. task-board.json, active-locks.json, conflict-registry.json, anti-patterns.md all in good shape.

### 4. Project Status Doc Updates

After completing deliverables 1-2, update:
- `docs/plans/SESSION-CONTINUITY.md` — mark directory scaffolding and Discord channels as DONE
- `TODO.md` — reflect completed work
- `operations/DEPLOYMENT-STATE.md` — update if relevant

---

## Approach

- **Agent directories**: Direct file operations (mkdir + .gitkeep)
- **Discord channels**: Python script using Discord REST API via `requests`
- **Not used**: n8n (premature for bootstrapping), discord.py (overkill for one-time setup)

## Rejected Alternatives

- **n8n workflow**: Phase 2 control plane isn't ready yet
- **Shell + curl**: Too verbose for permission overwrites
- **discord.py**: Async framework unnecessary for a synchronous setup script
