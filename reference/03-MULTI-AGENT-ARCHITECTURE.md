# 03 — Multi-Agent Architecture

## Overview

OpenClaw supports running multiple isolated agents within a single Gateway process. Each agent maintains:
- **Separate workspace** directory (AGENTS.md, SOUL.md, skills, files)
- **Isolated agentDir** for auth profiles, model registry, per-agent config
- **Independent session store** (chat history + routing state) under `~/.openclaw/agents/<agentId>/sessions`
- **Per-agent model configuration** with independent fallback chains
- **Per-agent tool restrictions** and sandbox settings
- **Distinct identity** (name, theme, emoji) for multi-agent mentions

## Agent Definition

Agents are defined in `agents.list[]` in `openclaw.json5`:

```json5
{
  agents: {
    // Shared defaults for all agents
    defaults: {
      model: { primary: "anthropic/claude-sonnet-4-5" },
      sandbox: { mode: "non-main" },  // Sandbox non-main sessions by default
    },
    
    // Agent definitions
    list: [
      {
        id: "orchestrator",           // Stable ID used in session keys
        default: true,                // Default agent for unrouted messages
        name: "Orchestrator",         // Display name
        workspace: "~/.openclaw/workspace-orchestrator",
        agentDir: "~/.openclaw/agents/orchestrator/agent",
        model: "anthropic/claude-opus-4-6",  // Override default model
        identity: {
          name: "Orchestrator",
          emoji: "🎯",
        },
        groupChat: {
          mentionPatterns: ["@orchestrator", "@orch"],  // How to @mention this agent
        },
        // Tool restrictions
        tools: {
          allow: ["exec", "read", "write", "edit", "sessions_list", "sessions_history",
                  "sessions_send", "sessions_spawn", "discord", "web_search", "browser"],
        },
        // Sandbox config
        sandbox: { mode: "off" },  // Full access for orchestrator
      },
      {
        id: "researcher",
        name: "Researcher",
        workspace: "~/.openclaw/workspace-researcher",
        agentDir: "~/.openclaw/agents/researcher/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Researcher", emoji: "🔬" },
        groupChat: { mentionPatterns: ["@researcher", "@research"] },
        tools: {
          allow: ["exec", "read", "write", "web_search", "browser",
                  "sessions_list", "sessions_history", "sessions_send"],
          deny: ["cron", "gateway", "nodes"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },
      {
        id: "coder",
        name: "Coder",
        workspace: "~/.openclaw/workspace-coder",
        agentDir: "~/.openclaw/agents/coder/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Coder", emoji: "💻" },
        groupChat: { mentionPatterns: ["@coder", "@dev"] },
        tools: {
          allow: ["exec", "read", "write", "edit", "apply_patch",
                  "sessions_list", "sessions_history", "sessions_send"],
          deny: ["browser", "cron", "gateway", "nodes"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },
      {
        id: "reviewer",
        name: "Reviewer",
        workspace: "~/.openclaw/workspace-reviewer",
        agentDir: "~/.openclaw/agents/reviewer/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Reviewer", emoji: "🔍" },
        groupChat: { mentionPatterns: ["@reviewer", "@review"] },
        tools: {
          allow: ["read", "sessions_list", "sessions_history", "sessions_send"],
          deny: ["exec", "write", "edit", "browser", "cron", "gateway", "nodes"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },
    ],
  },
}
```

## Bindings (Message Routing)

Bindings map inbound messages to agents. **First match wins** — put specific bindings before general ones.

```json5
{
  bindings: [
    // Per-channel bindings (most specific)
    {
      agentId: "orchestrator",
      match: {
        channel: "discord",
        guildId: "GUILD_ID",
        // Match specific channels by ID or pattern
      }
    },
    
    // Role-based routing (route Discord members by role)
    {
      agentId: "coder",
      match: {
        channel: "discord",
        guildId: "GUILD_ID",
        roles: ["CODER_ROLE_ID"],  // Role IDs only (not names)
      }
    },
    
    // Peer-based routing (route specific users)
    {
      agentId: "orchestrator",
      match: {
        channel: "discord",
        peer: { kind: "direct", id: "YOUR_USER_ID" },
      }
    },
    
    // Channel-wide fallback (least specific — put last)
    {
      agentId: "orchestrator",
      match: { channel: "discord" }
    },
  ],
}
```

### Binding Match Fields
- `channel`: "discord", "telegram", "whatsapp", etc.
- `guildId`: Discord guild (server) ID
- `accountId`: For multi-account channels
- `peer.kind`: "direct" | "group"
- `peer.id`: User ID or group ID
- `roles`: Array of Discord role IDs

### Binding Precedence (most to least specific)
1. Peer + channel + guild + roles
2. Peer + channel
3. Guild + roles
4. Guild only
5. Channel only

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
model: "anthropic/claude-opus-4-6"

// Object form (overrides primary + fallbacks)
model: {
  primary: "anthropic/claude-opus-4-6",
  fallbacks: ["anthropic/claude-sonnet-4-5", "openai/gpt-5.2"]
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
  
  // Deny always wins at any level
}
```

### Sandbox Configuration
```json5
sandbox: {
  mode: "off",       // "off" | "all" | "non-main"
  scope: "agent",    // "agent" (one container per agent) | "session" | "shared"
  docker: {
    setupCommand: "apt-get update && apt-get install -y git curl",  // Runs once on container creation
  }
}
```

- `mode: "non-main"` — sandbox group/channel sessions, not the main DM session
- `mode: "all"` — sandbox everything
- `scope: "agent"` — one Docker container per agent (recommended for isolation)

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

1. **Each inbound message routes to exactly ONE agent** (unless broadcast groups are used)
2. **Never reuse agentDir** across agents — causes auth and session collisions
3. **`tools.elevated` is global and sender-based** — not configurable per agent. Use `agents.list[].tools` deny lists for per-agent boundaries.
4. **When multiple agents have `default: true`**, the first wins (with a warning logged)
5. **Agent ID "main"** falls back to `agents.defaults.workspace` instead of `~/.openclaw/workspace-main`
6. **Bindings match in strict order** — a broad binding before a specific one will shadow it
