# TOOLS.md — Orchestrator Tool Notes

## Available Tools

- `exec` — Run shell commands on the gateway host
- `read` / `write` / `edit` — File operations in workspace
- `sessions_list` / `sessions_history` / `sessions_send` / `sessions_spawn` — Full session management (can spawn sub-agents)
- `discord` — Send messages, read channels, react, manage threads
- `web_search` / `browser` — Web research capabilities
- `cron` — Schedule recurring tasks

## Denied Tools

None — Orchestrator has full tool profile.

## Notes

- You are the only agent with `sessions_spawn` — use it to delegate sub-tasks to specialists.
- You are the only agent with `cron` — use it for scheduled governance checks.
- All elevated commands require Devin's approval via Discord exec approvals.
- Workspace path: `~/.openclaw/workspace-orchestrator`
