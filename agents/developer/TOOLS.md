# TOOLS.md — Developer Tool Notes

## Available Tools

- `exec` — Run shell commands on the gateway host
- `read` / `write` / `edit` / `apply_patch` — Full file operations
- `sessions_list` / `sessions_history` / `sessions_send` — View sessions and send messages to other agents
- `discord` — Send messages, read channels, react, manage threads

## Denied Tools

- `browser`, `web_search`, `cron`, `gateway`, `nodes`, `canvas`, `sessions_spawn`

## Notes

- You cannot do web research. If you need external information, request it from the Researcher via `sessions_send` or Discord.
- You have `apply_patch` for efficient multi-line edits.
- Test all code before reporting completion.
- Workspace path: `~/.openclaw/workspace-developer`
