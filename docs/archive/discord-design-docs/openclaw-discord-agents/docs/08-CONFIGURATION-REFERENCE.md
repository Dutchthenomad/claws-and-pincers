# 08 — Configuration Reference

## Overview

This is the complete annotated `openclaw.json5` configuration for the multi-agent Discord team. Copy this as your starting template and replace placeholder values.

## Complete Config Template

```json5
// ~/.openclaw/openclaw.json5
// OpenClaw Multi-Agent Discord Team Configuration
// Last updated: 2026-02-16
{
  // ═══════════════════════════════════════════
  // AGENT DEFINITIONS
  // ═══════════════════════════════════════════
  agents: {
    // Shared defaults (applied to all agents unless overridden)
    defaults: {
      model: {
        primary: "anthropic/claude-sonnet-4-5",
        fallbacks: ["openai/gpt-5.2"],
      },
      sandbox: {
        mode: "non-main",  // Sandbox group/channel sessions, not main DM
      },
    },

    // Agent roster
    list: [
      // ── ORCHESTRATOR ──
      {
        id: "orchestrator",
        default: true,
        name: "Orchestrator",
        workspace: "~/.openclaw/workspace-orchestrator",
        agentDir: "~/.openclaw/agents/orchestrator/agent",
        model: "anthropic/claude-opus-4-6",
        identity: { name: "Orchestrator", emoji: "🎯" },
        groupChat: {
          mentionPatterns: ["@orchestrator", "@orch", "@Orchestrator"],
        },
        allowAgents: ["*"],  // Can spawn any agent
        tools: {
          profile: "full",
          allow: [
            "exec", "read", "write", "edit",
            "sessions_list", "sessions_history", "sessions_send", "sessions_spawn",
            "discord", "web_search", "browser", "cron",
          ],
        },
        sandbox: { mode: "off" },  // Full host access
      },

      // ── RESEARCHER ──
      {
        id: "researcher",
        name: "Researcher",
        workspace: "~/.openclaw/workspace-researcher",
        agentDir: "~/.openclaw/agents/researcher/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Researcher", emoji: "🔬" },
        groupChat: {
          mentionPatterns: ["@researcher", "@research", "@Researcher"],
        },
        tools: {
          allow: [
            "exec", "read", "write",
            "sessions_list", "sessions_history", "sessions_send",
            "web_search", "browser", "discord",
          ],
          deny: ["cron", "gateway", "nodes", "canvas"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },

      // ── CODER ──
      {
        id: "coder",
        name: "Coder",
        workspace: "~/.openclaw/workspace-coder",
        agentDir: "~/.openclaw/agents/coder/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Coder", emoji: "💻" },
        groupChat: {
          mentionPatterns: ["@coder", "@dev", "@Coder"],
        },
        tools: {
          allow: [
            "exec", "read", "write", "edit", "apply_patch",
            "sessions_list", "sessions_history", "sessions_send",
            "discord",
          ],
          deny: ["browser", "cron", "gateway", "nodes", "canvas"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },

      // ── REVIEWER ──
      {
        id: "reviewer",
        name: "Reviewer",
        workspace: "~/.openclaw/workspace-reviewer",
        agentDir: "~/.openclaw/agents/reviewer/agent",
        model: "anthropic/claude-sonnet-4-5",
        identity: { name: "Reviewer", emoji: "🔍" },
        groupChat: {
          mentionPatterns: ["@reviewer", "@review", "@Reviewer"],
        },
        tools: {
          allow: [
            "read",
            "sessions_list", "sessions_history", "sessions_send",
            "discord",
          ],
          deny: ["exec", "write", "edit", "browser", "cron", "gateway", "nodes", "canvas"],
        },
        sandbox: { mode: "all", scope: "agent" },
      },
    ],
  },

  // ═══════════════════════════════════════════
  // AGENT-TO-AGENT COMMUNICATION
  // ═══════════════════════════════════════════
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["orchestrator", "researcher", "coder", "reviewer"],
    },
  },

  // ═══════════════════════════════════════════
  // BINDINGS (Message Routing)
  // ═══════════════════════════════════════════
  // First match wins — most specific first
  bindings: [
    // Human DMs go to orchestrator
    {
      agentId: "orchestrator",
      match: {
        channel: "discord",
        peer: { kind: "direct" },
      },
    },

    // Guild fallback — orchestrator handles all guild messages by default
    // Other agents respond via @mentions in shared channels
    {
      agentId: "orchestrator",
      match: {
        channel: "discord",
        guildId: "REPLACE_WITH_GUILD_ID",
      },
    },
  ],

  // ═══════════════════════════════════════════
  // DISCORD CHANNEL CONFIGURATION
  // ═══════════════════════════════════════════
  channels: {
    discord: {
      enabled: true,
      // Use env var: DISCORD_BOT_TOKEN
      // Or set directly: token: "YOUR_TOKEN_HERE",

      // CRITICAL for multi-agent Discord communication
      allowBots: true,

      // Access control
      groupPolicy: "allowlist",

      // DM policy
      dm: {
        enabled: true,
        policy: "pairing",
        allowFrom: ["REPLACE_WITH_YOUR_USER_ID"],
        groupEnabled: false,
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
        events: true,
        polls: true,
        stickers: true,
        emojiUploads: true,
        permissions: true,
        roles: false,          // Keep disabled unless needed
        moderation: false,     // Keep disabled unless needed
      },

      // Message formatting
      textChunkLimit: 2000,
      maxLinesPerMessage: 17,
      replyToMode: "off",

      // Media
      mediaMaxMb: 8,

      // Guild config
      guilds: {
        "REPLACE_WITH_GUILD_ID": {
          slug: "agent-team",
          requireMention: true,  // Default: require @mention in guild
          users: ["REPLACE_WITH_YOUR_USER_ID"],
          reactionNotifications: "own",

          // Channel-specific overrides
          // NOTE: After agentic setup, update this with actual channel IDs
          channels: {
            // Wildcard — allow all channels with default settings
            "*": { allow: true },
          },
        },
      },
    },
  },

  // ═══════════════════════════════════════════
  // SESSION CONFIGURATION
  // ═══════════════════════════════════════════
  session: {
    // Send policy — control where agents can send messages
    sendPolicy: {
      rules: [],
      default: "allow",
    },
  },

  // ═══════════════════════════════════════════
  // HEARTBEAT
  // ═══════════════════════════════════════════
  // Default: every 30 minutes
  // Configured per-agent via HEARTBEAT.md in workspace

  // ═══════════════════════════════════════════
  // MODEL PROVIDERS (example)
  // ═══════════════════════════════════════════
  // API keys via environment variables:
  //   ANTHROPIC_API_KEY=sk-ant-...
  //   OPENAI_API_KEY=sk-...
  // Or configure inline (not recommended for security)
}
```

## Environment Variables

```bash
# Required
export DISCORD_BOT_TOKEN="your_discord_bot_token"
export ANTHROPIC_API_KEY="sk-ant-api03-..."

# Optional (for fallback models)
export OPENAI_API_KEY="sk-..."
export GOOGLE_API_KEY="..."

# Optional (for specific features)
export CLAWHUB_CONFIG_PATH="~/.config/clawhub"
```

## Post-Setup Steps

After applying this config:

```bash
# 1. Create workspace directories
mkdir -p ~/.openclaw/workspace-{orchestrator,researcher,coder,reviewer}

# 2. Copy SOUL.md, AGENTS.md, HEARTBEAT.md to each workspace
# (See 05-IDENTITY-AND-PERSONAS.md for templates)

# 3. Validate configuration
openclaw doctor

# 4. List agents
openclaw agents list

# 5. Start gateway
openclaw gateway

# 6. Check Discord connection
openclaw channels status --probe

# 7. Monitor logs
openclaw gateway logs
```

## Configuration Gotchas

1. **Config token > env var.** If you set `token` in config AND `DISCORD_BOT_TOKEN`, config wins.
2. **Channel keys can be slugs or numeric IDs.** Slugs are easier to read, but `--probe` only works with numeric IDs.
3. **`allowBots: true` is dangerous.** Always pair with `requireMention: true` and agent allowlists.
4. **Bindings order matters.** First match wins. Put specific before general.
5. **`agents.defaults.sandbox.mode: "non-main"`** is based on session.mainKey, not agent ID. Group/channel sessions always count as non-main.
6. **Restarting gateway** is required after config changes. Use `openclaw gateway --force` if the old process won't die.
