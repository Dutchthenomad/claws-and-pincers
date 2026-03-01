# Startup Governance Checklist

On every boot/session start, complete these checks:

1. **Read anti-patterns** from workspace `memory/` — consult known failure patterns (especially AP-001, AP-003)
2. **Check for pending sessions** via `sessions_list` — identify any spawned sessions awaiting implementation
3. **Check for revision requests** — review sessions that returned NEEDS_REVISION from Reviewer
4. **Verify exec environment** — confirm code execution tools are operational
5. **Report ready status** to Orchestrator via `sessions_send` if in an active session
