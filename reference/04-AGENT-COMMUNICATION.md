# 04 — Agent Communication

## Overview

OpenClaw provides several mechanisms for agents to communicate with each other. By design, agents are isolated — no cross-talk unless explicitly enabled. This document covers all available communication primitives.

## Agent-to-Agent Messaging (Direct)

**Off by default.** Must be explicitly enabled and allowlisted.

```json5
{
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["orchestrator", "researcher", "coder", "reviewer"],  // Agent IDs that can communicate
    }
  }
}
```

When enabled, agents can use `sessions_send` to message other agents directly through the Gateway's internal routing — not through Discord.

## Session Tools

The core primitives for inter-agent communication. These are tools available to agents at runtime.

### sessions_list

Lists all active sessions across the system.

**Returns per session:**
- `key`: Session key string
- `kind`: main | group | cron | hook | node | other
- `channel`: whatsapp | discord | internal | unknown
- `displayName`: Group display label if available
- `updatedAt`: Timestamp (ms)
- `model`, `contextTokens`, `totalTokens`
- `sendPolicy`: Session override if set

```
# Example output:
Sessions:
  main (agent: orchestrator) — Last activity: 2m ago — 45 messages
  discord:channel:123 (agent: researcher) — Last activity: 1h ago — 23 messages
  discord:channel:456 (agent: coder) — Last activity: 5h ago — 78 messages (compacted)
```

### sessions_history

Fetches transcript for a specific session.

**Parameters:**
- `sessionKey` (required) — accepts session key or sessionId
- `limit` — max messages (server clamps)
- `includeTools` — include tool call/result messages (default false)

### sessions_send

**The primary inter-agent communication tool.** Sends a message into another agent's session and optionally waits for the response.

**Parameters:**
- `sessionKey` (required) — target session
- `message` — the content to send
- `timeoutSeconds` — if > 0, waits for completion then returns `{ runId, status, reply }`

**Behavior:**
- `timeoutSeconds > 0`: Wait up to N seconds. Returns `{ runId, status: "ok", reply }` on success, `{ runId, status: "timeout" }` if waiting expires (run continues in background), or `{ runId, status: "error" }` on failure.
- After completion, OpenClaw runs an **agent-to-agent announce step**: the target agent can reply `ANNOUNCE_SKIP` to stay silent, or any other reply is sent to the target channel.

**Send Policy** can restrict which channels/types can be messaged:
```json5
{
  session: {
    sendPolicy: {
      rules: [
        { match: { channel: "discord", chatType: "group" }, action: "deny" }
      ],
      default: "allow"
    }
  }
}
```

### sessions_spawn

**Spawns a sub-agent run in an isolated session.** The result is announced back to the requester's chat channel.

**Key for recursive feedback loops** — the orchestrator spawns a task, the specialist runs it in isolation, and the result flows back.

**Configuration for spawn permissions:**
```json5
{
  agents: {
    list: [
      {
        id: "orchestrator",
        // Controls which agents can be spawned from this agent
        allowAgents: ["*"],  // Allow spawning any agent
        // Or: allowAgents: ["researcher", "coder"]
      }
    ]
  }
}
```

## Subagents System

Subagents are long-running background processes spawned by a main agent. Managed via the `/subagents` command.

### Commands
```
/subagents list       — Show active and completed subagent runs
/subagents stop <id>  — Stop a running subagent
/subagents logs <id>  — View conversation history of a subagent
/subagents info <id>  — Detailed metadata about a run
/subagents send <id> <message> — Send a message to a subagent and wait
```

### Example Output
```
🧭 Subagents (current session)
Active: 2 · Done: 1
1) running · Process logs     · 5m · run 12ab34cd · agent:main:subagent:abc
2) running · Analyze data     · 3m · run 56ef78gh · agent:main:subagent:def
3) done    · Generate report  · 2m · run 90ij12kl · agent:main:subagent:xyz
```

Subagent counts appear in `/status` when verbose mode is enabled or subagents are active.

## Discord as Communication Bus

The most natural pattern for multi-agent collaboration on Discord: agents communicate through shared Discord channels rather than (or in addition to) internal session tools.

### How It Works
1. Multiple agents are bound to overlapping Discord channels
2. Agents use `@mentionPatterns` to address each other
3. `allowBots: true` allows agents to see each other's messages
4. `requireMention: true` prevents agents from responding to everything (only their @mentions)

### Critical Safety: Loop Prevention
```json5
{
  channels: {
    discord: {
      allowBots: true,  // REQUIRED for agent-to-agent on Discord
      guilds: {
        "GUILD_ID": {
          requireMention: true,  // CRITICAL: prevents infinite loops
          channels: {
            "shared-workspace": {
              allow: true,
              requireMention: true,
              // Per-agent allowlists can further restrict
              users: ["ORCHESTRATOR_BOT_ID", "RESEARCHER_BOT_ID", "CODER_BOT_ID"],
            }
          }
        }
      }
    }
  }
}
```

**Without `requireMention: true` and proper guardrails, agents WILL enter infinite response loops, burning through API tokens.**

Additional loop prevention in AGENTS.md / SOUL.md:
```markdown
## Communication Rules
- NEVER respond to a message unless you are explicitly @mentioned
- When another agent @mentions you, respond ONCE and do not @mention them back unless you need input
- If you detect a potential loop (same topic being discussed repeatedly), stop and report to #human-oversight
- Limit yourself to a maximum of 3 back-and-forth exchanges per task before escalating
```

## Recursive Feedback Loop Pattern

The core workflow for autonomous agent collaboration:

```
1. Human or Heartbeat triggers Orchestrator
       │
       ▼
2. Orchestrator analyzes task, decomposes into subtasks
       │
       ▼
3. Orchestrator uses sessions_spawn to delegate to Researcher
       │
       ▼
4. Researcher completes research, result announced back to Orchestrator
       │
       ▼
5. Orchestrator evaluates result quality
       │
       ├─ Quality OK → Forward to Coder via sessions_send
       │
       └─ Quality insufficient → Spawn another Researcher round with feedback
              │
              ▼
6. Coder produces implementation, announces back
       │
       ▼
7. Orchestrator sends to Reviewer via sessions_send
       │
       ▼
8. Reviewer evaluates, returns assessment
       │
       ├─ Approved → Orchestrator posts to #completed
       │
       └─ Issues found → Orchestrator spawns Coder with reviewer feedback
              │
              ▼
9. Loop continues until quality threshold met or max iterations reached
       │
       ▼
10. All activity visible in Discord channels for human observation
```

### Max Iteration Safety
Always set a hard limit on recursive loops in the orchestrator's SOUL.md:
```markdown
## Iteration Limits
- Maximum 5 research iterations per task before requiring human input
- Maximum 3 code review cycles before escalating to #human-oversight
- If total token spend on a single task exceeds $2, pause and report
```

## Communication Summary

| Method | Scope | Use Case |
|---|---|---|
| `sessions_send` | Internal (Gateway) | Direct agent-to-agent, with optional wait |
| `sessions_spawn` | Internal (Gateway) | Delegate subtask to isolated session |
| `/subagents` | Internal (Gateway) | Monitor/manage background agent runs |
| Discord @mentions | External (Discord) | Visible collaboration in shared channels |
| `agentToAgent` | Internal config | Enable/disable and allowlist inter-agent comms |
| Heartbeat/Cron | Internal (Gateway) | Trigger autonomous check-ins and workflows |
