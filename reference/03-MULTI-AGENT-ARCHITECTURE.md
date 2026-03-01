# 03 — Multi-Agent Architecture

## Overview

OpenClaw runs multiple isolated agents within a single Gateway process using a **hub-and-spoke** coordination model. The Orchestrator agent sits at the hub; all specialist agents (Researcher, Developer, Sysadmin, Reviewer) are spokes. Coordination flows exclusively through session tools — there are no file-based coordination mechanisms (no task-board.json, active-locks.json, or conflict-registry.json).

Each agent maintains:
- **Separate workspace** directory (AGENTS.md, SOUL.md, skills, files)
- **Isolated agentDir** for auth profiles, model registry, per-agent config
- **Independent session store** (chat history + routing state) under `~/.openclaw/agents/<agentId>/sessions`
- **Per-agent model configuration** with independent fallback chains
- **Per-agent tool restrictions** and sandbox settings
- **Per-agent `agentToAgent` allow lists** enforcing hub-and-spoke topology
- **Distinct identity** (name, theme, emoji) for multi-agent mentions

## Hub-and-Spoke Model

The architecture enforces a strict hub-and-spoke topology through two mechanisms:

### 1. `sessions_spawn` restricted to Orchestrator

Only the Orchestrator has `sessions_spawn` in its tool allow list. Specialists explicitly deny it:

```json5
// Orchestrator — hub
tools: {
  allow: ["sessions_spawn", "sessions_send", "sessions_list", "sessions_history", ...],
}

// Every specialist — spoke
tools: {
  allow: ["sessions_send", "sessions_list", "sessions_history", ...],
  deny: ["sessions_spawn"],  // Cannot spawn sub-sessions
}
```

This means only the Orchestrator can delegate work by spawning isolated sessions on other agents.

### 2. `agentToAgent` per-agent allow lists

Each specialist's `agentToAgent.allow` is restricted to `["orchestrator"]`, while the Orchestrator allows `["*"]`:

```json5
// Orchestrator — can message any agent
tools: {
  agentToAgent: { enabled: true, allow: ["*"] },
}

// Researcher — can only message Orchestrator
tools: {
  agentToAgent: { enabled: true, allow: ["orchestrator"] },
}

// Developer — can only message Orchestrator
tools: {
  agentToAgent: { enabled: true, allow: ["orchestrator"] },
}
```

This prevents specialists from directly coordinating with each other. All cross-specialist communication must flow through the Orchestrator, which maintains full situational awareness.

### Session-Based Delegation Flow

```
Human/Heartbeat/Cron triggers Orchestrator
       |
       v
Orchestrator decomposes task
       |
       +--sessions_spawn--> Researcher (isolated session)
       |                         |
       |                    sessions_send back to Orchestrator
       |                         |
       +--sessions_spawn--> Developer (isolated session)
       |                         |
       |                    sessions_send back to Orchestrator
       |                         |
       +--sessions_spawn--> Reviewer (isolated session)
       |                         |
       |                    sessions_send back to Orchestrator
       |
       v
Orchestrator synthesizes results, reports to Discord
```

Specialists never contact each other directly. If the Developer needs research context, the Orchestrator retrieves it from the Researcher's session history and includes it in the Developer's spawn prompt.

## Agent Definition

Agents are defined in `agents.list[]` in `openclaw.json5`:

```json5
{
  agents: {
    // Shared defaults for all agents
    defaults: {
      model: {
        primary: "openrouter/moonshotai/kimi-k2.5",
        fallbacks: ["openrouter/google/gemini-3-flash-preview"],
      },
      sandbox: { mode: "off" },
      userTimezone: "America/New_York",
      contextPruning: { mode: "cache-ttl", ttl: "1h" },
      compaction: { mode: "safeguard" },
      thinkingDefault: "low",
      timeoutSeconds: 600,
      maxConcurrent: 2,
      subagents: { maxConcurrent: 8 },
    },

    // Agent roster
    list: [
      // --- ORCHESTRATOR (Hub) ---
      {
        id: "orchestrator",
        default: true,                // Default agent for unrouted messages
        workspace: "~/.openclaw/workspace-orchestrator",
        agentDir: "~/.openclaw/agents/orchestrator/agent",
        model: { primary: "openrouter/anthropic/claude-opus-4.6", fallbacks: ["openrouter/moonshotai/kimi-k2.5"] },
        identity: { name: "Orchestrator", emoji: "🎯" },
        groupChat: { mentionPatterns: ["@orchestrator", "@orch", "@Orchestrator"] },
        subagents: { allowAgents: ["*"] },  // Can spawn any agent
        sandbox: { mode: "off" },           // Full host access
        heartbeat: { every: "15m" },
        tools: {
          profile: "full",
          allow: ["read", "write", "edit", "sessions_list", "sessions_history",
                  "sessions_send", "sessions_spawn", "discord", "web_search", "browser", "cron"],
          deny: ["exec", "apply_patch"],
          agentToAgent: { enabled: true, allow: ["*"] },
        },
      },

      // --- RESEARCHER (Spoke) ---
      {
        id: "researcher",
        workspace: "~/.openclaw/workspace-researcher",
        agentDir: "~/.openclaw/agents/researcher/agent",
        model: { primary: "openrouter/x-ai/grok-4.1-fast", fallbacks: ["openrouter/moonshotai/kimi-k2.5"] },
        identity: { name: "Researcher", emoji: "🔬" },
        groupChat: { mentionPatterns: ["@researcher", "@research", "@Researcher"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "2h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: ["read", "write", "sessions_list", "sessions_history", "sessions_send",
                  "web_search", "browser", "discord"],
          deny: ["exec", "edit", "apply_patch", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // --- DEVELOPER (Spoke) ---
      {
        id: "developer",
        workspace: "~/.openclaw/workspace-developer",
        agentDir: "~/.openclaw/agents/developer/agent",
        model: { primary: "openrouter/minimax/minimax-m2.5", fallbacks: ["openrouter/moonshotai/kimi-k2.5"] },
        identity: { name: "Developer", emoji: "💻" },
        groupChat: { mentionPatterns: ["@developer", "@dev", "@Developer"] },
        sandbox: { mode: "lenient" },
        heartbeat: { every: "2h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: ["exec", "read", "write", "edit", "apply_patch", "sessions_list",
                  "sessions_history", "sessions_send", "web_search", "discord"],
          deny: ["browser", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // --- SYSADMIN (Spoke) ---
      {
        id: "sysadmin",
        workspace: "~/.openclaw/workspace-sysadmin",
        agentDir: "~/.openclaw/agents/sysadmin/agent",
        model: { primary: "openrouter/moonshotai/kimi-k2.5", fallbacks: ["openrouter/google/gemini-3-flash-preview"] },
        identity: { name: "Sysadmin", emoji: "🖥️" },
        groupChat: { mentionPatterns: ["@sysadmin", "@sys", "@Sysadmin"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "30m", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: ["exec", "read", "write", "edit", "sessions_list", "sessions_history",
                  "sessions_send", "discord"],
          deny: ["browser", "web_search", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // --- REVIEWER (Spoke) ---
      {
        id: "reviewer",
        workspace: "~/.openclaw/workspace-reviewer",
        agentDir: "~/.openclaw/agents/reviewer/agent",
        model: { primary: "openrouter/google/gemini-3-flash-preview", fallbacks: ["openrouter/moonshotai/kimi-k2.5"] },
        identity: { name: "Reviewer", emoji: "🔍" },
        groupChat: { mentionPatterns: ["@reviewer", "@review", "@Reviewer"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "4h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: ["read", "sessions_list", "sessions_history", "sessions_send", "discord"],
          deny: ["exec", "write", "edit", "apply_patch", "browser", "web_search", "cron",
                 "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },
    ],
  },
}
```

## Bindings (Message Routing)

Bindings map inbound messages to agents. **First match wins** — put specific bindings before general ones.

This deployment uses per-account bindings: each Discord bot token maps to its agent via `accountId`:

```json5
{
  bindings: [
    // Per-account bindings — each Discord bot routes to its agent
    { agentId: "orchestrator", match: { channel: "discord", accountId: "orchestrator" } },
    { agentId: "researcher", match: { channel: "discord", accountId: "researcher" } },
    { agentId: "developer", match: { channel: "discord", accountId: "developer" } },
    { agentId: "sysadmin", match: { channel: "discord", accountId: "sysadmin" } },
    { agentId: "reviewer", match: { channel: "discord", accountId: "reviewer" } },

    // Fallback: unmatched Discord traffic goes to orchestrator
    { agentId: "orchestrator", match: { channel: "discord" } },
  ],
}
```

### Binding Match Fields
- `channel`: "discord", "whatsapp", etc.
- `accountId`: Maps to a Discord account key in `channels.discord.accounts`
- `guildId`: Discord guild (server) ID
- `peer.kind`: "direct" | "group"
- `peer.id`: User ID or group ID
- `roles`: Array of Discord role IDs

### Binding Precedence (most to least specific)
1. Peer + channel + guild + roles
2. AccountId + channel
3. Peer + channel
4. Guild + roles
5. Guild only
6. Channel only

## Per-Agent Configuration Details

### Workspaces
Each agent's workspace is its default `cwd`. Relative paths resolve inside the workspace. **Absolute paths can reach other host locations unless sandboxing is enabled.**

```
~/.openclaw/workspace-orchestrator/
├── AGENTS.md       # Instructions for this specific agent
├── SOUL.md         # Personality/philosophy
├── TOOLS.md        # Tool usage guidance
├── IDENTITY.md     # Presentation metadata
├── HEARTBEAT.md    # Autonomous checklist
├── MEMORY.md       # Persistent notes
└── skills/         # Per-agent skills
    └── discord/SKILL.md
```

### Auth Profiles
Per-agent auth at `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`. **Never reuse agentDir across agents** — causes auth/session collisions. If agents need shared credentials, explicitly copy `auth-profiles.json`.

### Model Configuration
Two forms supported:
```json5
// String form (overrides primary only)
model: "openrouter/anthropic/claude-opus-4.6"

// Object form (overrides primary + fallbacks)
model: {
  primary: "openrouter/anthropic/claude-opus-4.6",
  fallbacks: ["openrouter/moonshotai/kimi-k2.5"]
}
// Set fallbacks: [] to disable global fallbacks for this agent
```

### Tool Restrictions
```json5
tools: {
  // Base profile: "minimal" | "coding" | "messaging" | "full"
  profile: "coding",

  allow: ["exec", "read", "write"],     // Explicit allowlist
  deny: ["browser", "cron", "gateway"],  // Explicit denylist

  // Per-agent agentToAgent (enforces hub-and-spoke)
  agentToAgent: { enabled: true, allow: ["orchestrator"] },

  // Deny always wins at any level
}
```

### Sandbox Configuration
```json5
sandbox: {
  mode: "off",       // "off" | "all" | "non-main" | "lenient"
  scope: "agent",    // "agent" (one container per agent) | "session" | "shared"
  docker: {
    setupCommand: "apt-get update && apt-get install -y git curl",
  }
}
```

- `mode: "off"` — no sandboxing (Orchestrator, Sysadmin)
- `mode: "lenient"` — sandbox with relaxed restrictions (Developer)
- `mode: "non-main"` — sandbox group/channel sessions, not the main DM session
- `mode: "all"` — sandbox everything
- `scope: "agent"` — one Docker container per agent (recommended for isolation)

### Heartbeat Configuration
Per-agent heartbeats enable autonomous proactive behavior:
```json5
heartbeat: {
  every: "15m",                              // Orchestrator: frequent check-ins
  model: "groq/llama-3.3-70b-versatile",     // Optional: cheaper model for heartbeats
}
```

When any agent in the roster has a `heartbeat` block, only those agents with explicit heartbeat config will run heartbeats. The heartbeat checklist is defined in each agent's `HEARTBEAT.md` workspace file.

## CLI Commands

```bash
# List all agents
openclaw agents list

# Add a new agent (interactive wizard)
openclaw agents add

# Show agent details
openclaw agents show <agentId>

# List sessions across agents
openclaw sessions list

# Send message as specific agent
openclaw agent --agent <agentId> "Your message here"

# Check configuration
openclaw doctor
```

## Critical Constraints

1. **Hub-and-spoke is mandatory** — Only the Orchestrator can `sessions_spawn`. Specialists contact only the Orchestrator via `agentToAgent.allow`.
2. **Each inbound message routes to exactly ONE agent** (unless broadcast groups are used)
3. **Never reuse agentDir** across agents — causes auth and session collisions
4. **`tools.elevated` is global and sender-based** — not configurable per agent. Use `agents.list[].tools` deny lists for per-agent boundaries.
5. **When multiple agents have `default: true`**, the first wins (with a warning logged)
6. **Agent ID "main"** falls back to `agents.defaults.workspace` instead of `~/.openclaw/workspace-main`
7. **Bindings match in strict order** — a broad binding before a specific one will shadow it
8. **Session tools are the coordination layer** — No file-based coordination (task-board.json, active-locks.json, conflict-registry.json) is used. All task delegation, status tracking, and result collection happens through `sessions_spawn`, `sessions_send`, `sessions_list`, and `sessions_history`.
