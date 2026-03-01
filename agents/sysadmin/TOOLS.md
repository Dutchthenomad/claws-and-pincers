# TOOLS.md — Sysadmin Tool Notes

## Available Tools

- `exec` — Run shell commands on the gateway host
- `read` / `write` / `edit` — File operations
- `sessions_list` / `sessions_history` / `sessions_send` — View sessions and send messages to other agents
- `discord` — Send messages, read channels, react, manage threads

## Denied Tools

- `browser`, `web_search`, `cron`, `gateway`, `nodes`, `canvas`, `sessions_spawn`

## Notes

- You cannot do web research. If you need external docs, request from the Researcher.
- Docker, systemd, UFW, and infrastructure tools are available via `exec`.
- Always bind new ports to 127.0.0.1, never 0.0.0.0.
- Check `/opt/sysadmin-ai/CRITICAL.md` before any infrastructure work.
- Workspace path: `~/.openclaw/workspace-sysadmin`
