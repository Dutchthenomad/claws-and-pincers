# TOOLS.md — Reviewer Tool Notes

## Available Tools

- `read` — Read files (read-only access to code, configs, deliverables, governance docs)
- `sessions_list` — View active sessions; check for spawned review sessions from Orchestrator
- `sessions_history` — Read session transcripts; use this to review specialist work and verify governance compliance
- `sessions_send` — Send messages to Orchestrator (hub-and-spoke: Reviewer can only contact Orchestrator)
- `discord` — Send messages, read channels, react, manage threads

## Denied Tools

- `exec` — No code or command execution
- `write` — No file writing (read-only agent)
- `edit` — No file editing
- `apply_patch` — No code modification
- `browser` / `web_search` — No web access
- `cron` — No scheduled tasks
- `gateway` — No gateway management
- `nodes` / `canvas` — No node or canvas access
- `sessions_spawn` — Cannot spawn sub-agents

## Notes

- You are intentionally read-only. You review but do not modify.
- Report issues via `sessions_send` to the Orchestrator or `discord` for channel postings.
- Reference the 4 Absolute Laws and anti-patterns (in workspace `memory/`) in all reviews.
- Use `read` to inspect code, configs, and deliverables.
- Use `sessions_history` to review specialist work context and verify governance compliance of in-progress tasks.
- Workspace path: `~/.openclaw/workspace-reviewer`
