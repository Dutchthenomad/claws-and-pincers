# HEARTBEAT.md — Orchestrator

**Interval:** Every 30 minutes  
**Purpose:** Proactive team oversight and governance enforcement

---

## Every Heartbeat Check

### 1. Human Messages
- Are there unread messages from Devin in #direct-command or #human-oversight?
- **If yes:** Acknowledge and act immediately. Devin's directives take priority over all other heartbeat items.

### 2. Stalled Sessions
- Run `sessions_list` and check for specialist sessions with no activity in the last 30 minutes that have open tasks.
- **If found:** Send a follow-up via `sessions_send` asking for status. If no response after a second heartbeat cycle (60 min total), escalate to #human-oversight as a potential issue.

### 3. Task Board Health
- Read `task-board.json` and check for:
  - Tasks stuck in IN_PROGRESS for more than 2 heartbeat cycles without a status update
  - Tasks in BLOCKED status that haven't been addressed
  - Tasks in REVIEW status with no reviewer pickup
- **If found:** Take appropriate action — reassign, escalate, or send a nudge to the assigned specialist.

### 4. Review Queue
- Are there completed deliverables in #review-queue that haven't been picked up by Reviewer?
- **If yes:** Notify Reviewer via `sessions_send` to pick up the review.

### 5. Conflict Registry
- Read `conflict-registry.json` for any OPEN conflicts.
- **If found:** Check if resolution is pending from Devin. If the conflict has been open for more than 2 heartbeat cycles without progress, escalate to #human-oversight.

### 6. Severity Alerts
- Check #severity-alerts for any unresolved BLOCKED or CRITICAL items.
- **If found:** Ensure they've been properly escalated. CRITICAL items must have a corresponding post in #human-oversight.

### 7. Anti-Pattern Check
- Have any anti-pattern violations been logged since last heartbeat?
- **If yes:** Verify the violation was properly categorized and routed per severity definitions.

---

## Weekly (Monday)

- Post a weekly summary to #human-oversight covering: projects completed, projects in progress, blockers, total tasks completed/failed, any new anti-patterns logged, and upcoming priorities.
- Review long-running sessions and trigger context compaction if needed.

---

## If Nothing Needs Attention

Reply with `HEARTBEAT_OK`.
