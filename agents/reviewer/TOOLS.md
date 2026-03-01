# TOOLS.md — Reviewer Tool Notes

## Available Tools

- `read` — Read files (read-only access)
- `sessions_list` / `sessions_history` / `sessions_send` — View sessions and send messages to other agents
- `discord` — Send messages, read channels, react, manage threads

## Denied Tools

- `exec`, `write`, `edit`, `apply_patch`, `browser`, `web_search`, `cron`, `gateway`, `nodes`, `canvas`, `sessions_spawn`

## Notes

- You are intentionally read-only. You review but do not modify.
- Report issues via `discord` or `sessions_send` to the relevant agent.
- Reference the 4 Absolute Laws and anti-patterns registry in all reviews.
- Use `read` to inspect code, configs, and deliverables.
- Workspace path: `~/.openclaw/workspace-reviewer`
