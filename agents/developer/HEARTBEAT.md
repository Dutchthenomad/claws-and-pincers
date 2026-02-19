# HEARTBEAT.md — Developer

**Interval:** Every 30 minutes  
**Purpose:** Monitor for pending development tasks and maintain work quality

---

## Every Heartbeat Check

### 1. Pending Tasks
- Check #task-dispatch for any tasks mentioning @developer that haven't been picked up.
- **If found:** Acknowledge the task and begin work on the highest-priority item. Verify Project ID, charter approval, and conflict status before starting.

### 2. In-Progress Work
- Do you have any tasks currently in progress?
- **If yes:** Check if the task has been active for more than 2 heartbeat cycles without delivering output. If so, send a progress update to Orchestrator via `sessions_send` with current status, what's remaining, and any blockers.

### 3. Review Feedback
- Has Reviewer returned any of your deliverables with NEEDS_REVISION?
- **If yes:** Pick up the revision. Review the Reviewer's findings, address blocking issues, and resubmit. Revision work takes priority over new tasks.

### 4. Test Verification
- For any recently submitted deliverables, did you include test results?
- **If uncertain:** Review your last submission. If tests were omitted, flag this to Orchestrator proactively rather than waiting for Reviewer to catch it.

### 5. Anti-Patterns
- Read `anti-patterns.md` if you haven't consulted it since your last task started. Confirm you're not exhibiting any known patterns (especially AP-001, AP-003, and AP-005).

---

## If Nothing Needs Attention

Reply with `HEARTBEAT_OK`.
