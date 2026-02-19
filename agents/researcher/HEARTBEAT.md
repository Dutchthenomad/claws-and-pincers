# HEARTBEAT.md — Researcher

**Interval:** Every 30 minutes  
**Purpose:** Monitor for pending research tasks and maintain research quality

---

## Every Heartbeat Check

### 1. Pending Tasks
- Check #task-dispatch for any tasks mentioning @researcher that haven't been picked up.
- **If found:** Acknowledge the task and begin work on the highest-priority item.

### 2. In-Progress Research
- Do you have any research tasks currently in progress?
- **If yes:** Check if any interim findings should be reported to Orchestrator (especially if you've hit the 10-search threshold on a subtopic). Post progress update via `sessions_send` to Orchestrator if the task has been active for more than one heartbeat cycle.

### 3. Stale Findings
- Review any recently delivered research in your workspace. Are there findings you flagged as time-sensitive that may now be stale?
- **If yes:** Notify Orchestrator via `sessions_send` that the findings may need re-verification before being acted on.

### 4. Anti-Patterns
- Read `anti-patterns.md` if you haven't consulted it since your last task started. Confirm you're not exhibiting any known patterns (especially AP-001 and AP-005).

---

## If Nothing Needs Attention

Reply with `HEARTBEAT_OK`.
