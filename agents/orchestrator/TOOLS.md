# TOOLS.md — Orchestrator Tool Notes

## Available Tools

- `sessions_spawn` — Spawn isolated specialist sessions for task delegation (**Orchestrator-exclusive** — no other agent has this tool)
- `sessions_send` — Send messages to existing agent sessions (follow-ups, nudges, clarifications)
- `sessions_list` — View all active sessions across the system (monitor activity, detect conflicts, check capacity)
- `sessions_history` — Read another session's transcript (review work without interrupting)
- `discord` — Send messages, read channels, react, manage threads
- `read` / `write` / `edit` — File operations in workspace
- `web_search` / `browser` — Web research capabilities (governance/coordination context only)
- `cron` — Schedule recurring tasks (governance audits: law1-audit, law2-audit; health checks; weekly reports)

## Denied Tools

- `exec` — Shell execution denied per gateway config. Delegate system commands to Sysadmin.

## Notes

- You are the **only agent** with `sessions_spawn` — use it to delegate sub-tasks to specialists.
- You are the **only agent** with `cron` — use it for scheduled governance checks (law1-audit, law2-audit).
- All elevated commands require Devin's approval via Discord exec approvals.
- Workspace path: `~/.openclaw/workspace-orchestrator`
