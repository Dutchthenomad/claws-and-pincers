# Design: Phase 2A — Laws Enforcement via n8n

> **Date**: 2026-02-27
> **Author**: Claude Opus 4.6 + Devin
> **Status**: IMPLEMENTED (core trio)

---

## Architecture

n8n polls Discord channels every 30 seconds, validates messages against governance files, and posts violations back to Discord. Token read from file at `/governance/.discord-token` (never passed through JSON pipeline).

### Infrastructure Changes

1. **n8n volume mount**: `/opt/openclaw/discord-agents/shared-governance:/governance:rw`
2. **n8n env vars**: `NODE_FUNCTION_ALLOW_BUILTIN=fs,https,path,crypto` (Code node sandbox allowlist)
3. **Discord token file**: `/governance/.discord-token` (readable by n8n's node user)

### Workflow Pattern

Each workflow follows the same pattern:
- Schedule Trigger (30s interval)
- Single Code node that: reads token from file, fetches Discord messages, validates against governance files, sends alerts, tracks state via `.n8n-*-state.json`

### Workflows Deployed

#### Law 1 — Project ID Validator
- **Watches**: `#task-dispatch`
- **Validates**: Every message must contain `PROJ-XXX` pattern registered in `PROJECT-REGISTRY.md`
- **On violation**: Posts CRITICAL to `#severity-alerts` + `#human-oversight`

#### Law 2 — Charter Approval Gate
- **Watches**: `#task-dispatch`
- **Validates**: Referenced PROJ-XXX must have charter approval date in registry
- **Exemption**: `CHARTER-PREP` tagged tasks are exempt
- **On violation**: Posts CRITICAL to `#severity-alerts` + `#human-oversight`

#### Severity Routing — Review Verdicts
- **Watches**: `#review-verdicts`
- **Classifies**: CRITICAL / BLOCKED / WARN / INFO based on message content
- **Routes per CORE-CHARTER notification matrix**:
  - INFO: stays in `#review-verdicts` only
  - WARN: + `#status-updates`
  - BLOCKED: + `#status-updates` + `#severity-alerts`
  - CRITICAL: + `#status-updates` + `#severity-alerts` + `#human-oversight`

### Remaining Phase 2A Items
- Conflict registry watchdog
- Token cost monitor with kill switch
- Anti-pattern repeat detection
- Heartbeat dead man's switch
