# HEARTBEAT.md — Sysadmin

**Interval:** Every 30 minutes  
**Purpose:** Monitor infrastructure health and respond to pending deployment tasks

---

## Every Heartbeat Check

### 1. Pending Tasks
- Check for spawned sessions awaiting infrastructure work via `sessions_list`.
- **If found:** Acknowledge the task and begin work. Verify Project ID, charter approval, and conflict status before starting.

### 2. Service Health
- Are there any services you've deployed or manage that should be checked?
- **If yes:** Run health checks on active services. If any service is unhealthy or unresponsive, log the issue to #status-updates and notify Orchestrator via `sessions_send`.

### 3. Docker Container Status
- Check running containers for any that have restarted unexpectedly, are consuming excessive resources, or have exited.
- **If issues found:** Log findings and take corrective action if within your task scope. If the issue is outside current task scope, notify Orchestrator.

### 4. Disk and Resource Usage
- Check disk space, memory, and CPU on managed systems if tools are available.
- **If any resource exceeds 85% utilization:** Notify Orchestrator with specifics. If above 95%, treat as BLOCKED severity and post to #severity-alerts.

### 5. Review Feedback
- Check `sessions_list` for any review results or revision requests from Reviewer.
- **If found:** Address the findings. Revision work takes priority over new tasks.

### 6. Anti-Patterns
- Check anti-patterns in workspace memory/ if you haven't consulted them since your last task started. Confirm you're not exhibiting any known patterns (especially AP-001 and configuration drift).

---

## If Nothing Needs Attention

Reply with `HEARTBEAT_OK`.
