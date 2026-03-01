# Startup Governance Checklist

On every boot/session start, complete these checks:

1. **Read anti-patterns** from workspace `memory/` — consult known failure patterns before any reviews
2. **Check for pending review sessions** via `sessions_list` — identify any spawned sessions awaiting your review
3. **Review CORE-CHARTER governance rules** — refresh on the 4 Absolute Laws
4. **Check `#severity-alerts`** for any unresolved BLOCKED/CRITICAL items
5. **Report ready status** to Orchestrator via `sessions_send` if in an active session
