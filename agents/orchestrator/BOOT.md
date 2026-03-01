# Startup Governance Checklist

On every boot/session start, complete these checks before accepting new work:

1. **Read anti-patterns** from workspace `memory/` — consult known failure patterns
2. **Check active sessions** via `sessions_list` — identify any orphaned or stuck sessions from previous runs
3. **Check #direct-command** for any pending Devin directives
4. **Verify model provider** — confirm OpenRouter is responding (attempt a simple operation)
5. **Report ready status** to `#orch-workspace` — post a brief status message confirming operational
6. **Review governance cron jobs** — verify `law1-audit` and `law2-audit` crons are active via `cron` tool
