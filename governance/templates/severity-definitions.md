# SEVERITY DEFINITIONS & NOTIFICATION STANDARDS

**Reference document — all agents must know these definitions.**

---

## Severity Levels

### ℹ️ INFO
**Minor suggestions, style preferences, non-blocking observations.**
- Work continues uninterrupted
- Logged to `#review-verdicts` only
- Specialist may address now or note for later
- No escalation required

### ⚠️ WARN
**Issues that should be fixed but don't block functionality.**
- Work continues but rework expected
- Posted to `#review-verdicts` AND `#status-updates`
- Specialist must address before task marked DONE
- If unresolved after 2 rework cycles → auto-escalate to BLOCKED

### 🛑 BLOCKED
**Issues that prevent the task from completing correctly.**
- Task CANNOT proceed
- Posted to `#severity-alerts` AND `#status-updates`
- Orchestrator reviews: reassign, re-scope, or request Devin input
- If Orchestrator cannot resolve → escalate to CRITICAL

### 🔴 CRITICAL
**Issues that threaten project integrity or violate governance rules.**
- ALL work on affected project HALTED immediately
- Posted to `#severity-alerts` AND `#human-oversight` AND `#status-updates`
- Devin must review and resolve before ANY work resumes
- This is the highest severity — no further escalation exists

**CRITICAL triggers include:**
- Work performed without Project ID
- Charter violated
- Conflict detected on active work
- Agent bypassed governance rules
- Runaway token spend
- Security breach or credential exposure
- Repeat violation of known anti-pattern

---

## Notification Routing Matrix

| Severity | #review-verdicts | #status-updates | #severity-alerts | #human-oversight |
|----------|:---:|:---:|:---:|:---:|
| INFO     | ✅ | — | — | — |
| WARN     | ✅ | ✅ | — | — |
| BLOCKED  | ✅ | ✅ | ✅ | — |
| CRITICAL | ✅ | ✅ | ✅ | ✅ |

---

## Auto-Escalation Rules

1. WARN unresolved after 2 rework cycles → BLOCKED
2. Known anti-pattern violation → severity +1 level from its defined severity
3. Repeat anti-pattern violation (same pattern, same agent, within 7 days) → CRITICAL
4. Any governance law violation → CRITICAL (no intermediate steps)
