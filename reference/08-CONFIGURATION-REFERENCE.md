# 08 — Configuration Reference

## Overview

This is the complete annotated `openclaw.json5` configuration for the Claws & Pincers multi-agent Discord team. Copy this as your starting template and replace placeholder values.

## Complete Config Template

```json5
// ~/.openclaw/openclaw.json5
// Claws & Pincers — Production Multi-Agent Configuration
// Last updated: 2026-03-01
{
  // =============================================
  // ENVIRONMENT VARIABLES
  // =============================================
  env: {
    vars: {
      OPENROUTER_API_KEY: "${OPENROUTER_API_KEY}",
    },
  },

  // =============================================
  // LOGGING
  // =============================================
  logging: {
    level: "info",
    file: "/home/node/.openclaw/logs/openclaw.log",
    consoleLevel: "info",
    consoleStyle: "pretty",
    redactSensitive: "tools",  // Redact sensitive data in tool outputs
  },

  // =============================================
  // AGENT DEFINITIONS
  // =============================================
  agents: {
    // Shared defaults (applied to all agents unless overridden)
    defaults: {
      model: {
        primary: "openrouter/moonshotai/kimi-k2.5",
        fallbacks: ["openrouter/google/gemini-3-flash-preview"],
      },
      // Global model aliases — available to all agents
      models: {
        "openrouter/anthropic/claude-opus-4.6": { alias: "opus" },
        "openrouter/minimax/minimax-m2.5": { alias: "minimax" },
        "openrouter/x-ai/grok-4.1-fast": { alias: "grok" },
        "openrouter/moonshotai/kimi-k2.5": { alias: "kimi" },
        "openrouter/google/gemini-3-flash-preview": { alias: "gemini" },
        "anthropic/claude-sonnet-4-5": { alias: "sonnet", params: { cacheControlTtl: "1h" } },
        "groq/llama-3.3-70b-versatile": { alias: "groq" },
        "groq/llama-3.1-8b-instant": { alias: "groq-fast" },
      },
      workspace: "/home/agent-main",
      userTimezone: "America/New_York",
      contextPruning: { mode: "cache-ttl", ttl: "1h" },
      compaction: { mode: "safeguard" },
      thinkingDefault: "low",
      timeoutSeconds: 600,
      maxConcurrent: 2,
      subagents: { maxConcurrent: 8 },
      sandbox: { mode: "off" },
    },

    // Agent roster
    list: [
      // === ORCHESTRATOR (Hub) ===
      // Coordinator only — delegates via sessions_spawn, does not exec.
      {
        id: "orchestrator",
        default: true,
        workspace: "~/.openclaw/workspace-orchestrator",
        agentDir: "~/.openclaw/agents/orchestrator/agent",
        model: {
          primary: "openrouter/anthropic/claude-opus-4.6",
          fallbacks: ["openrouter/moonshotai/kimi-k2.5"],
        },
        identity: { name: "Orchestrator", emoji: "🎯" },
        groupChat: { mentionPatterns: ["@orchestrator", "@orch", "@Orchestrator"] },
        subagents: { allowAgents: ["*"] },  // Can spawn any agent
        sandbox: { mode: "off" },
        heartbeat: { every: "15m" },        // Frequent autonomous check-ins
        tools: {
          profile: "full",
          allow: [
            "read", "write", "edit",
            "sessions_list", "sessions_history", "sessions_send", "sessions_spawn",
            "discord", "web_search", "browser", "cron",
          ],
          deny: ["exec", "apply_patch"],
          // Hub: can message any agent
          agentToAgent: { enabled: true, allow: ["*"] },
        },
      },

      // === RESEARCHER (Spoke) ===
      // Knowledge engine. Read-only research, no exec.
      {
        id: "researcher",
        workspace: "~/.openclaw/workspace-researcher",
        agentDir: "~/.openclaw/agents/researcher/agent",
        model: {
          primary: "openrouter/x-ai/grok-4.1-fast",
          fallbacks: ["openrouter/moonshotai/kimi-k2.5"],
        },
        identity: { name: "Researcher", emoji: "🔬" },
        groupChat: { mentionPatterns: ["@researcher", "@research", "@Researcher"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "2h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: [
            "read", "write",
            "sessions_list", "sessions_history", "sessions_send",
            "web_search", "browser", "discord",
          ],
          deny: ["exec", "edit", "apply_patch", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          // Spoke: can only message Orchestrator
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // === DEVELOPER (Spoke) ===
      // Builder. Code execution with lenient sandbox.
      {
        id: "developer",
        workspace: "~/.openclaw/workspace-developer",
        agentDir: "~/.openclaw/agents/developer/agent",
        model: {
          primary: "openrouter/minimax/minimax-m2.5",
          fallbacks: ["openrouter/moonshotai/kimi-k2.5"],
        },
        identity: { name: "Developer", emoji: "💻" },
        groupChat: { mentionPatterns: ["@developer", "@dev", "@Developer"] },
        sandbox: { mode: "lenient" },       // Sandboxed but relaxed
        heartbeat: { every: "2h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: [
            "exec", "read", "write", "edit", "apply_patch",
            "sessions_list", "sessions_history", "sessions_send",
            "web_search", "discord",
          ],
          deny: ["browser", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // === SYSADMIN (Spoke) ===
      // Infrastructure guardian. Full host access needed.
      {
        id: "sysadmin",
        workspace: "~/.openclaw/workspace-sysadmin",
        agentDir: "~/.openclaw/agents/sysadmin/agent",
        model: {
          primary: "openrouter/moonshotai/kimi-k2.5",
          fallbacks: ["openrouter/google/gemini-3-flash-preview"],
        },
        identity: { name: "Sysadmin", emoji: "🖥️" },
        groupChat: { mentionPatterns: ["@sysadmin", "@sys", "@Sysadmin"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "30m", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: [
            "exec", "read", "write", "edit",
            "sessions_list", "sessions_history", "sessions_send",
            "discord",
          ],
          deny: ["browser", "web_search", "cron", "gateway", "nodes", "canvas", "sessions_spawn"],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },

      // === REVIEWER (Spoke) ===
      // Quality gate. Read-only by tool policy.
      {
        id: "reviewer",
        workspace: "~/.openclaw/workspace-reviewer",
        agentDir: "~/.openclaw/agents/reviewer/agent",
        model: {
          primary: "openrouter/google/gemini-3-flash-preview",
          fallbacks: ["openrouter/moonshotai/kimi-k2.5"],
        },
        identity: { name: "Reviewer", emoji: "🔍" },
        groupChat: { mentionPatterns: ["@reviewer", "@review", "@Reviewer"] },
        sandbox: { mode: "off" },
        heartbeat: { every: "4h", model: "groq/llama-3.3-70b-versatile" },
        tools: {
          allow: [
            "read",
            "sessions_list", "sessions_history", "sessions_send",
            "discord",
          ],
          deny: [
            "exec", "write", "edit", "apply_patch",
            "browser", "web_search", "cron", "gateway", "nodes", "canvas",
            "sessions_spawn",
          ],
          agentToAgent: { enabled: true, allow: ["orchestrator"] },
        },
      },
    ],
  },

  // =============================================
  // GLOBAL TOOL CONFIGURATION
  // =============================================
  tools: {
    allow: ["exec", "process", "read", "write", "edit"],
    // Global agentToAgent — per-agent allow lists enforce hub-and-spoke
    agentToAgent: { enabled: true },
    // Elevated tool permissions — only specific Discord users
    elevated: {
      enabled: true,
      allowFrom: { discord: ["YOUR_DISCORD_USER_ID"] },
    },
    exec: {
      host: "gateway",
      security: "full",
      ask: "off",
      backgroundMs: 10000,
      timeoutSec: 1800,
    },
  },

  // =============================================
  // BINDINGS (Message Routing)
  // =============================================
  // Per-account bindings: each Discord bot routes to its agent.
  // First match wins — most specific first.
  bindings: [
    { agentId: "orchestrator", match: { channel: "discord", accountId: "orchestrator" } },
    { agentId: "researcher", match: { channel: "discord", accountId: "researcher" } },
    { agentId: "developer", match: { channel: "discord", accountId: "developer" } },
    { agentId: "sysadmin", match: { channel: "discord", accountId: "sysadmin" } },
    { agentId: "reviewer", match: { channel: "discord", accountId: "reviewer" } },
    // Fallback: unmatched Discord traffic goes to orchestrator
    { agentId: "orchestrator", match: { channel: "discord" } },
  ],

  // =============================================
  // MESSAGE HANDLING
  // =============================================
  messages: {
    ackReaction: "👍",
    ackReactionScope: "all",
  },
  commands: {
    native: "auto",
    nativeSkills: "auto",
  },

  // =============================================
  // APPROVALS
  // =============================================
  approvals: {
    exec: {
      enabled: true,
      mode: "targets",
      targets: [{ channel: "discord", to: "YOUR_DISCORD_USER_ID" }],
    },
  },

  // =============================================
  // SESSION CONFIGURATION
  // =============================================
  session: {
    scope: "per-sender",
    resetTriggers: ["/new", "/reset", "/clear"],
    reset: { mode: "idle", idleMinutes: 60 },
    typingIntervalSeconds: 5,
    // Send policy — control where agents can send messages
    // sendPolicy: {
    //   rules: [
    //     { match: { channel: "discord", chatType: "group" }, action: "deny" }
    //   ],
    //   default: "allow"
    // },
  },

  // =============================================
  // DISCORD CHANNEL CONFIGURATION
  // =============================================
  channels: {
    discord: {
      enabled: true,
      allowBots: true,           // Required for agent-to-agent on Discord
      groupPolicy: "allowlist",
      dmPolicy: "pairing",
      allowFrom: ["YOUR_DISCORD_USER_ID"],
      streaming: "off",
      execApprovals: {
        enabled: true,
        approvers: ["YOUR_DISCORD_USER_ID"],
      },

      // Guild config
      guilds: {
        "YOUR_GUILD_ID": {
          requireMention: true,  // Prevents infinite agent loops
        },
      },

      // Multi-account setup — one Discord bot per agent
      accounts: {
        orchestrator: { token: "${DISCORD_ORCHESTRATOR_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        researcher:   { token: "${DISCORD_RESEARCHER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        developer:    { token: "${DISCORD_DEVELOPER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        sysadmin:     { token: "${DISCORD_SYSADMIN_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        reviewer:     { token: "${DISCORD_REVIEWER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
      },

      // Discord actions
      actions: {
        reactions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        channelInfo: true,
        channels: true,       // Allow creating/editing/deleting channels
        voiceStatus: true,
      },
    },
  },

  // =============================================
  // GATEWAY
  // =============================================
  gateway: {
    port: 18789,
    mode: "local",
    bind: "lan",  // Container needs LAN binding; host-side port bound to 127.0.0.1
    // OpenAI-compatible API endpoint
    openaiApi: { enabled: true },
    // Control UI (web dashboard)
    controlUi: {
      enabled: true,
      basePath: "/",
      allowedOrigins: ["http://127.0.0.1:18789", "http://YOUR_TAILSCALE_IP:18789"],
    },
    // Gateway authentication
    auth: {
      mode: "token",
      token: "${OPENCLAW_GATEWAY_TOKEN}",
    },
  },

  // =============================================
  // HOOKS AND WEBHOOKS
  // =============================================
  hooks: {
    enabled: true,
    webhooks: {
      "governance-alert": {
        url: "http://127.0.0.1:5678/webhook/openclaw-governance",
        events: ["cron.complete", "session.error", "heartbeat.alert"],
      },
    },
  },

  // =============================================
  // CRON JOBS
  // =============================================
  cron: {
    enabled: true,
    // Governance cron jobs — added via `openclaw cron add` CLI.
    // Examples:
    //   law1-audit: */5 * * * * — Check #task-dispatch for untagged messages
    //   law2-audit: */15 * * * * — Check for unapproved charters
    //   cost-daily: 0 0 * * * — Daily cost summary via /usage
  },

  // =============================================
  // PLUGINS
  // =============================================
  plugins: {
    entries: {
      discord: { enabled: true },
      "cli-offload": { enabled: true },
    },
    slots: {
      memory: "memory-core",  // Native memory plugin
    },
  },
}
```

## Per-Agent Heartbeat Configuration

Each agent's heartbeat frequency is set in the agent definition. When any agent has a `heartbeat` block, only agents with explicit heartbeat config will run heartbeats.

| Agent | Interval | Model Override | Purpose |
|-------|----------|----------------|---------|
| Orchestrator | 15m | (default: opus) | Task queue monitoring, governance checks |
| Sysadmin | 30m | groq/llama-3.3-70b-versatile | Infrastructure health checks |
| Researcher | 2h | groq/llama-3.3-70b-versatile | Knowledge base freshness |
| Developer | 2h | groq/llama-3.3-70b-versatile | Build status, dependency checks |
| Reviewer | 4h | groq/llama-3.3-70b-versatile | Review queue monitoring |

The heartbeat checklist is defined in each agent's `HEARTBEAT.md` workspace file, not in openclaw.json5.

## Hub-and-Spoke agentToAgent Pattern

The `agentToAgent` config enforces hub-and-spoke at two levels:

```json5
// Level 1: Global — enable the feature
tools: {
  agentToAgent: { enabled: true },
},

// Level 2: Per-agent — restrict who each agent can contact
// Orchestrator (hub): allow: ["*"]
// All specialists (spokes): allow: ["orchestrator"]
```

This is the key enforcement mechanism. Even though `agentToAgent` is globally enabled, each specialist's per-agent allow list restricts them to only messaging the Orchestrator.

## Sandbox Mode Examples

```json5
// Off — full host access (Orchestrator, Sysadmin)
sandbox: { mode: "off" }

// Lenient — sandboxed with relaxed restrictions (Developer)
sandbox: { mode: "lenient" }

// All — fully sandboxed, one container per agent
sandbox: { mode: "all", scope: "agent" }

// Non-main — sandbox group/channel sessions only
sandbox: { mode: "non-main" }

// With Docker setup command
sandbox: {
  mode: "all",
  scope: "agent",
  docker: {
    setupCommand: "apt-get update && apt-get install -y git curl nodejs",
  },
}
```

## Environment Variables

```bash
# Required — LLM provider
export OPENROUTER_API_KEY="sk-or-v1-..."

# Required — Discord bot tokens (one per agent)
export DISCORD_ORCHESTRATOR_TOKEN="..."
export DISCORD_RESEARCHER_TOKEN="..."
export DISCORD_DEVELOPER_TOKEN="..."
export DISCORD_SYSADMIN_TOKEN="..."
export DISCORD_REVIEWER_TOKEN="..."

# Required — Gateway authentication
export OPENCLAW_GATEWAY_TOKEN="..."

# Optional — Direct provider keys (for specific model aliases)
export ANTHROPIC_API_KEY="sk-ant-..."
export GROQ_API_KEY="gsk_..."
```

## Post-Setup Steps

After applying this config:

```bash
# 1. Create workspace directories
mkdir -p ~/.openclaw/workspace-{orchestrator,researcher,developer,sysadmin,reviewer}

# 2. Copy SOUL.md, AGENTS.md, HEARTBEAT.md to each workspace
# (See 05-IDENTITY-AND-PERSONAS.md for templates)

# 3. Create agent state directories
mkdir -p ~/.openclaw/agents/{orchestrator,researcher,developer,sysadmin,reviewer}/agent

# 4. Validate configuration
openclaw doctor

# 5. List agents
openclaw agents list

# 6. Start gateway
openclaw gateway

# 7. Check Discord connection
openclaw channels status --probe

# 8. Monitor logs
openclaw gateway logs
```

## Configuration Gotchas

1. **Config token > env var.** If you set `token` in config AND `DISCORD_BOT_TOKEN`, config wins.
2. **Channel keys can be slugs or numeric IDs.** Slugs are easier to read, but `--probe` only works with numeric IDs.
3. **`allowBots: true` is dangerous.** Always pair with `requireMention: true` in guild config.
4. **Bindings order matters.** First match wins. Put specific (accountId) before general (channel-only).
5. **`agents.defaults.sandbox.mode: "non-main"`** is based on session.mainKey, not agent ID.
6. **Restarting gateway** is required after config changes. Use `openclaw gateway --force` if the old process won't die.
7. **Per-agent `agentToAgent.allow`** overrides the global `tools.agentToAgent` — the global setting enables the feature, per-agent settings restrict it.
8. **Heartbeat model overrides** use cheaper models (groq) for frequent check-ins to control costs.
9. **`sessions_spawn` must be in both `tools.allow` AND `subagents.allowAgents`** for spawning to work. Missing either one blocks delegation.
