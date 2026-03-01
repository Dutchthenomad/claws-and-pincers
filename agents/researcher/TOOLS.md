# TOOLS.md — Researcher Tool Notes

## Available Tools

- `exec` — Run shell commands on the gateway host
- `read` / `write` — File operations (no `edit`)
- `sessions_list` / `sessions_history` / `sessions_send` — View sessions and send messages to other agents
- `discord` — Send messages, read channels, react, manage threads
- `web_search` / `browser` — Web research capabilities

## Denied Tools

- `cron`, `gateway`, `nodes`, `canvas`, `sessions_spawn`

## Notes

- You cannot spawn sub-agents. Report findings back via `sessions_send` to the Orchestrator.
- Your primary value is web research — use `web_search` and `browser` extensively.
- Cite sources in all research output.
- Workspace path: `~/.openclaw/workspace-researcher`
