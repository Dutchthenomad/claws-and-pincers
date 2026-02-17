# 09 — Autonomous Loops

## Overview

OpenClaw provides two mechanisms for unprompted autonomous behavior: **heartbeats** (periodic check-ins) and **cron jobs** (scheduled tasks). Combined with session tools, these enable recursive feedback loops where agents work continuously without human prompting.

## Heartbeat System

### How It Works
1. Gateway runs the heartbeat daemon (systemd on Linux, LaunchAgent on macOS)
2. Every interval (default 30 min, 60 min with Anthropic OAuth), the agent is woken up
3. Agent reads `HEARTBEAT.md` from its workspace
4. Agent evaluates each checklist item and decides whether action is needed
5. If no action needed: agent replies `HEARTBEAT_OK` (Gateway silently drops this)
6. If action needed: agent executes the task and messages accordingly

### Configuration
Heartbeat interval is set globally. Per-agent behavior is controlled via each workspace's `HEARTBEAT.md`.

### HEARTBEAT.md Templates

**Orchestrator:**
```markdown
# Heartbeat — Orchestrator

## Every Check (30 min)
- Are there unresolved items in #task-dispatch?
- Are any subagent runs stalled (>30 min without progress)?
- Are there new messages in #human-oversight requiring response?
- Check sessions_list for any errored or timed-out sessions

## If issues found:
- For stalled subagents: send a follow-up via sessions_send
- For unresolved tasks: assess priority and delegate or escalate
- For human messages: respond promptly
- Post status update to #system-logs

## If nothing needs attention:
HEARTBEAT_OK
```

**Researcher:**
```markdown
# Heartbeat — Researcher

## Every Check
- Are there pending research requests in #task-dispatch mentioning @researcher?
- Are there ongoing research tasks that need follow-up searches?

## If work is pending:
- Pick up the highest priority unassigned research task
- Begin research and post progress to #research-workspace

## If nothing needs attention:
HEARTBEAT_OK
```

## Cron Jobs

For precise scheduling (vs. heartbeat's periodic check-in).

### Cron Configuration
```json5
// In openclaw.json5 or via workspace cron files
{
  cron: {
    jobs: [
      {
        id: "morning-briefing",
        schedule: "0 9 * * 1-5",  // 9 AM weekdays
        agent: "orchestrator",
        message: "Generate a morning briefing: check all agent session statuses, pending tasks, and completed work from the last 24 hours. Post to #human-oversight.",
      },
      {
        id: "health-check",
        schedule: "*/15 * * * *",  // Every 15 minutes
        agent: "orchestrator",
        message: "Quick health check: verify all agents are responsive. If any are unresponsive, report to #system-logs.",
      },
      {
        id: "cost-report",
        schedule: "0 18 * * *",  // 6 PM daily
        agent: "orchestrator",
        message: "Generate daily cost report: token usage across all agents. Post to #cost-tracking.",
      },
    ]
  }
}
```

### Cron via CLI
```bash
# Send a message to a channel on schedule
0 9 * * 1-5 openclaw message send "channel:CHANNEL_ID" "Good morning team! Daily standup time."
```

### Cron Session Keys
Cron jobs use session key format: `cron:<job.id>`

## Recursive Feedback Loop Implementation

### The Core Pattern

```
Trigger (Human message / Heartbeat / Cron)
    │
    ▼
Orchestrator: Analyze & Decompose
    │
    ├─ sessions_spawn → Researcher (isolated session)
    │       │
    │       ▼
    │   Research completes → Result announced back
    │       │
    │       ▼
    ├─ Orchestrator evaluates quality
    │       │
    │       ├─ PASS → sessions_send → Coder
    │       │           │
    │       │           ▼
    │       │       Implementation completes
    │       │           │
    │       │           ▼
    │       │       sessions_send → Reviewer
    │       │           │
    │       │           ▼
    │       │       Review result
    │       │           │
    │       │           ├─ APPROVED → Post to #completed
    │       │           │
    │       │           └─ NEEDS_REVISION → Loop back to Coder
    │       │                   (max 3 iterations)
    │       │
    │       └─ FAIL → sessions_spawn → Researcher (with feedback)
    │               (max 5 iterations)
    │
    └─ Post final result to #completed + notify #human-oversight
```

### Implementation in Orchestrator's AGENTS.md

```markdown
## Recursive Task Workflow

### Phase 1: Research
1. Use sessions_spawn to create isolated research task
2. Set timeoutSeconds to 300 (5 min max)
3. Evaluate response against quality criteria
4. If insufficient: spawn again with specific feedback (include what was missing)
5. Max 5 research iterations — then escalate to human

### Phase 2: Implementation
1. Use sessions_send to Coder's session with research output + task spec
2. Set timeoutSeconds to 600 (10 min max)
3. Forward output to Reviewer

### Phase 3: Review
1. Use sessions_send to Reviewer's session with implementation + original spec
2. Parse Reviewer's verdict: APPROVED | NEEDS_REVISION | BLOCKED
3. If NEEDS_REVISION: send back to Coder with reviewer feedback
4. If BLOCKED: escalate to human via #human-oversight
5. Max 3 review cycles

### Phase 4: Completion
1. Post approved deliverable to #completed
2. Post summary to #human-oversight
3. Archive relevant session history

### Safety Rails
- Track iteration count in session state
- Hard limit: 5 research + 3 code + 3 review = 11 max total iterations
- If any single loop exceeds its limit, STOP and escalate
- Monitor cumulative token cost — pause at $5 threshold per task
```

## Loop Safety Mechanisms

### 1. Iteration Limits (in SOUL.md/AGENTS.md)
Always set explicit hard limits on how many times a loop can iterate.

### 2. Cost Tracking
Monitor token usage and set budget caps per task and per day.

### 3. Timeout on sessions_spawn/sessions_send
Always set `timeoutSeconds`. A runaway agent without a timeout will consume tokens indefinitely.

### 4. Discord requireMention
Prevents agents from responding to every message in shared channels, which is the most common source of infinite loops.

### 5. Bot Message Filtering
Even with `allowBots: true`, agents' own messages are filtered (they don't respond to themselves). But Agent A can respond to Agent B, who responds to Agent A — this IS the loop risk.

### 6. AGENTS.md Communication Rules
```markdown
## Anti-Loop Rules
- When responding to another agent's @mention, respond ONCE
- Do NOT @mention them back unless you explicitly need their input
- If you detect the same topic being discussed for the 3rd time, STOP and post to #human-oversight
- Never respond to a message that is a response to your own previous message (detect via message history)
```

### 7. Gateway-Level Controls
```json5
{
  // Block high-risk tools from HTTP invocation
  gateway: {
    tools: {
      deny: ["sessions_spawn", "sessions_send"],  // Only allow from agent sessions, not HTTP
    }
  }
}
```

## Monitoring Autonomous Activity

```bash
# Watch active sessions in real-time
openclaw sessions list --watch

# Check subagent status
# (In Discord, send to bot): /subagents list

# View session history
openclaw sessions history <sessionKey>

# Check gateway health
openclaw status

# View logs
openclaw gateway logs --tail
```
