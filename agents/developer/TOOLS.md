# TOOLS.md — Developer Tool Notes

## Available Tools

- `exec` — Run shell commands on the gateway host
- `read` / `write` / `edit` / `apply_patch` — Full file operations
- `sessions_list` / `sessions_history` / `sessions_send` — View sessions and send messages to other agents
- `discord` — Send messages, read channels, react, manage threads
- `web_search` — Look up documentation, API references, library docs

## Denied Tools

- `browser`, `cron`, `gateway`, `nodes`, `canvas`, `sessions_spawn`

## Notes

- You can use `web_search` for documentation lookups, API references, and library docs directly.
- For broader research tasks that go beyond quick lookups, request from the Researcher via Orchestrator.
- You have `apply_patch` for efficient multi-line edits.
- Test all code before reporting completion.
- Workspace path: `~/.openclaw/workspace-developer`
- Running in lenient sandbox mode.
