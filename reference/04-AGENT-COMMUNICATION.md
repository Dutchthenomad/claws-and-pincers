# 04 — Agent Communication

## Overview

OpenClaw provides session-based communication primitives that enforce a **hub-and-spoke** topology. By design, agents are isolated — no cross-talk unless explicitly enabled through `agentToAgent` per-agent allow lists. The Orchestrator is the hub; all specialists are spokes that can only communicate with the Orchestrator.

There are no file-based coordination mechanisms. All inter-agent communication flows through session tools.

## Hub-and-Spoke Enforcement

Two config-level mechanisms enforce the topology:

### 1. Per-Agent `agentToAgent` Allow Lists

Each agent declares which other agents it can contact. Specialists are restricted to `["orchestrator"]`:

```json5
// Global: enable the feature
tools: {
  agentToAgent: { enabled: true },
},

// Per-agent: Orchestrator can reach anyone
{ id: "orchestrator", tools: { agentToAgent: { enabled: true, allow: ["*"] } } },

// Per-agent: Specialists can only reach Orchestrator
{ id: "researcher", tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } },
{ id: "developer",  tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } },
{ id: "sysadmin",   tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } },
{ id: "reviewer",   tools: { agentToAgent: { enabled: true, allow: ["orchestrator"] } } },
```

### 2. `sessions_spawn` Denied for Specialists

Only the Orchestrator has `sessions_spawn` in its tool allow list. Every specialist explicitly denies it:

```json5
// Orchestrator
tools: { allow: ["sessions_spawn", ...] }

// All specialists
tools: { deny: ["sessions_spawn"] }
```

This prevents specialists from creating sub-sessions on other agents. All delegation flows through the Orchestrator.

## Session Tools (Communication Primitives)

These are the runtime tools available to agents for inter-agent communication.

### sessions_list

Lists all active sessions across the system. Available to all agents.

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
  discord:channel:456 (agent: developer) — Last activity: 5h ago — 78 messages (compacted)
```

### sessions_history

Fetches transcript for a specific session. Available to all agents.

**Parameters:**
- `sessionKey` (required) — accepts session key or sessionId
- `limit` — max messages (server clamps)
- `includeTools` — include tool call/result messages (default false)

Use case: The Orchestrator reads a specialist's session history to extract results without requiring the specialist to explicitly report back.

### sessions_send

**The primary inter-agent communication tool.** Sends a message into another agent's session and optionally waits for the response. Governed by `agentToAgent` allow lists.

**Parameters:**
- `sessionKey` (required) — target session
- `message` — the content to send
- `timeoutSeconds` — if > 0, waits for completion then returns `{ runId, status, reply }`

**Behavior:**
- `timeoutSeconds > 0`: Wait up to N seconds. Returns `{ runId, status: "ok", reply }` on success, `{ runId, status: "timeout" }` if waiting expires (run continues in background), or `{ runId, status: "error" }` on failure.
- After completion, OpenClaw runs an **agent-to-agent announce step**: the target agent can reply `ANNOUNCE_SKIP` to stay silent, or any other reply is sent to the target channel.

**Hub-and-spoke constraint:** A specialist calling `sessions_send` to another specialist's session will be rejected by the `agentToAgent` allow list. The specialist can only `sessions_send` to the Orchestrator's session.

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

**Spawns a sub-agent run in an isolated session.** The result is announced back to the requester's chat channel. **Only available to the Orchestrator.**

This is the primary delegation mechanism. The Orchestrator spawns a task on a specialist, the specialist runs it in isolation, and the result flows back to the Orchestrator.

**Configuration for spawn permissions:**
```json5
{
  agents: {
    list: [
      {
        id: "orchestrator",
        subagents: { allowAgents: ["*"] },  // Can spawn any agent
        // Or: subagents: { allowAgents: ["researcher", "developer"] }
      }
    ]
  }
}
```

## Subagents System

Subagents are long-running background processes spawned by the Orchestrator. Managed via the `/subagents` command.

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
Subagents (current session)
Active: 2 / Done: 1
1) running  Process logs     5m  run 12ab34cd  agent:main:subagent:abc
2) running  Analyze data     3m  run 56ef78gh  agent:main:subagent:def
3) done     Generate report  2m  run 90ij12kl  agent:main:subagent:xyz
```

Subagent counts appear in `/status` when verbose mode is enabled or subagents are active.

## Discord as Communication Bus

Discord serves as the **visibility layer** for agent activity. Agents post results to Discord channels, but inter-agent coordination uses session tools, not Discord @mentions.

### Discord Threads for Project Isolation

Each project gets its own Discord thread. The Orchestrator creates a thread in the appropriate channel when a new project starts, and all agents post their results to that thread. This keeps project context contained and browsable.

```
#task-dispatch
  └── Thread: "PROJ-042 — API Rate Limiter"
        ├── Orchestrator: Task decomposition and assignments
        ├── Researcher: Research findings (posted via sessions_spawn result)
        ├── Developer: Implementation status (posted via sessions_spawn result)
        └── Reviewer: Review verdict (posted via sessions_spawn result)
```

### Safety: Loop Prevention

When multiple agents share Discord channels, use `requireMention: true` and bot allowlists:

```json5
{
  channels: {
    discord: {
      allowBots: true,
      guilds: {
        "GUILD_ID": {
          requireMention: true,  // Prevents infinite response loops
        }
      }
    }
  }
}
```

**Without `requireMention: true`, agents WILL enter infinite response loops, burning through API tokens.**

Additional loop prevention in AGENTS.md / SOUL.md:
```markdown
## Communication Rules
- NEVER respond to a message unless you are explicitly @mentioned
- When another agent @mentions you, respond ONCE and do not @mention them back unless you need input
- If you detect a potential loop (same topic being discussed repeatedly), stop and report to #human-oversight
- Limit yourself to a maximum of 3 back-and-forth exchanges per task before escalating
```

## Delegation Workflow (Hub-and-Spoke)

The core workflow for autonomous agent collaboration:

```
1. Human or Heartbeat or Cron triggers Orchestrator
       |
       v
2. Orchestrator analyzes task, decomposes into subtasks
       |
       v
3. Orchestrator uses sessions_spawn to delegate to Researcher
       |
       v
4. Researcher completes research in isolated session
       |  (result announced back to Orchestrator automatically)
       v
5. Orchestrator evaluates result quality via sessions_history
       |
       +-- Quality OK --> sessions_spawn Developer with research context
       |
       +-- Insufficient --> sessions_spawn Researcher again with feedback
              |
              v
6. Developer produces implementation in isolated session
       |  (result announced back to Orchestrator)
       v
7. Orchestrator sends to Reviewer via sessions_spawn
       |
       v
8. Reviewer evaluates, returns assessment
       |
       +-- Approved --> Orchestrator posts to Discord project thread
       |
       +-- Issues found --> Orchestrator spawns Developer with reviewer feedback
              |
              v
9. Loop continues until quality threshold met or max iterations reached
       |
       v
10. All results posted to Discord project thread for human visibility
```

### Max Iteration Safety
Always set a hard limit on recursive loops in the Orchestrator's SOUL.md:
```markdown
## Iteration Limits
- Maximum 5 research iterations per task before requiring human input
- Maximum 3 code review cycles before escalating to #human-oversight
- If total token spend on a single task exceeds $2, pause and report
```

## Communication Summary

| Method | Scope | Who Can Use | Use Case |
|---|---|---|---|
| `sessions_spawn` | Internal (Gateway) | Orchestrator only | Delegate subtask to specialist in isolated session |
| `sessions_send` | Internal (Gateway) | All (governed by allow list) | Send message to another agent's session |
| `sessions_list` | Internal (Gateway) | All | View all active sessions |
| `sessions_history` | Internal (Gateway) | All | Read transcript of any session |
| `/subagents` | Internal (Gateway) | Orchestrator | Monitor/manage background agent runs |
| Discord threads | External (Discord) | All | Project-isolated visibility for humans |
| `agentToAgent` config | Config-level | N/A | Enable/disable and restrict inter-agent messaging per agent |
| Heartbeat/Cron | Internal (Gateway) | Per-agent config | Trigger autonomous check-ins and workflows |
