# Startup Governance Checklist

On every boot/session start, complete these checks:

1. **Read anti-patterns** from workspace `memory/` — consult known failure patterns
2. **Check `/opt/sysadmin-ai/CRITICAL.md`** — review any active critical infrastructure issues
3. **Check for pending sessions** via `sessions_list` — identify any spawned sessions awaiting infrastructure work
4. **Quick infrastructure health check:**
   - `uptime; free -h | grep Mem; df -h / | tail -1`
   - `docker ps -q | wc -l` (verify expected container count)
   - Check for containers in restart loops
5. **Report ready status** to Orchestrator via `sessions_send` if in an active session
