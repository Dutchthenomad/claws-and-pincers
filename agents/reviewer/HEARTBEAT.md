# HEARTBEAT.md — Reviewer / QA

**Interval:** Every 30 minutes
**Purpose:** Monitor review pipeline and maintain governance oversight

---

## Every Heartbeat Check

### 1. Review Queue
- Check `sessions_list` for sessions awaiting review (spawned by Orchestrator).
- **If found:** Pick up the highest-priority item. Begin with the governance compliance check before assessing technical quality.

### 2. Overdue Reviews
- Do you have any reviews in progress that have been open for more than 2 heartbeat cycles?
- **If yes:** Complete and submit the review. If the deliverable is complex enough to require more time, notify Orchestrator via `sessions_send` with an estimated completion time.

### 3. Governance Spot Check
- Check `sessions_list` for active sessions; verify governance compliance via `sessions_history`.
- For each active task, verify: Does the task have a valid Project ID? Is the project charter approved? Was conflict detection run?
- **If any governance gap found:** Notify Orchestrator immediately via `sessions_send`. Do not wait for the deliverable to reach review — governance violations should be caught early.

### 4. Anti-Pattern Registry
- Review anti-patterns in workspace `memory/`. Are there any recent additions that should inform your current or upcoming reviews?
- Have you identified any new recurring failure patterns from recent reviews that should be logged?
- **If new pattern identified:** Log it to workspace `memory/` using the standard format (AP-XXX) and notify Orchestrator to update the shared file.

### 5. Severity Routing Verification
- Check #severity-alerts and #review-verdicts. Are there any verdicts you've issued that haven't been acted on?
- **If found:** Notify Orchestrator via `sessions_send` that a review verdict is pending action.

---

## If Nothing Needs Attention

Reply with `HEARTBEAT_OK`.
