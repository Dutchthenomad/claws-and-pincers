# Startup Governance Checklist

On every boot/session start, complete these checks:

1. **Read anti-patterns** from workspace `memory/` — consult known failure patterns before any research
2. **Check for pending sessions** via `sessions_list` — identify any spawned sessions awaiting your response
3. **Verify web search** — confirm web_search tool is operational with a simple test query
4. **Report ready status** to Orchestrator via `sessions_send` if in an active session
