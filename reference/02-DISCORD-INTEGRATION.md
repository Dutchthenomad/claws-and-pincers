# 02 — Discord Integration

## Overview

Discord is a first-class channel in OpenClaw. The integration supports guild (server) channels, DMs, threads, slash commands, reactions, components v2 UI, voice messages, and rich media. Each guild channel gets its own isolated session key.

## Bot Setup (Discord Developer Portal)

1. Go to https://discord.com/developers/applications
2. Click **New Application** → name it (e.g., "Orchestrator Bot")
3. Go to **Bot** tab → **Reset Token** → copy and store securely
4. Enable **Privileged Gateway Intents:**
   - **Message Content Intent** (REQUIRED — without this, bot connects but can't read messages)
   - **Server Members Intent** (recommended — needed for role allowlists, member lookups)
   - Presence Intent is optional (only for presence updates, not required for setPresence)
5. Go to **OAuth2 → URL Generator:**
   - Scopes: `bot`, `applications.commands`
   - Permissions: Send Messages, Read Message History, Embed Links, Attach Files, Add Reactions, Manage Channels (if agents will create channels), Manage Roles (if agents will manage roles)
   - **Avoid Administrator** unless debugging
6. Copy generated URL → open in browser → invite to your server

**IMPORTANT: For multi-agent setups, you need ONE Discord bot application PER agent** (each needs its own token), OR you use a single bot with role-based routing via bindings.

## Configuration

### Minimal Config
```json5
{
  channels: {
    discord: {
      enabled: true,
      token: "YOUR_BOT_TOKEN",  // or use DISCORD_BOT_TOKEN env var
    }
  }
}
```

### Production Config (Annotated)
```json5
{
  channels: {
    discord: {
      enabled: true,
      // Token resolution: config > env var. DISCORD_BOT_TOKEN is fallback for default account only.
      token: "abc.123",
      
      // Access control for guilds
      groupPolicy: "allowlist",  // "open" | "allowlist" — use allowlist for production
      
      // Per-guild configuration
      guilds: {
        // Wildcard — applies to all guilds unless overridden
        "*": {
          requireMention: true,  // Bot only responds when @mentioned
        },
        
        // Specific guild override
        "GUILD_ID_HERE": {
          slug: "my-agent-server",
          requireMention: false,  // Override: respond to all messages in this guild
          
          // Authorized users (IDs or usernames)
          users: ["YOUR_USER_ID"],
          
          // Authorized roles (role IDs only)
          roles: ["ROLE_ID"],
          
          // Reaction handling
          reactionNotifications: "own",  // "off" | "own" | "all" | "allowlist"
          
          // Per-channel config
          channels: {
            "general": {
              allow: true,
              requireMention: true,
              // Per-channel skill filter (omit = all skills, empty array = no skills)
              skills: ["discord", "web_search"],
              // Extra system prompt for this channel
              systemPrompt: "You are operating in the general discussion channel. Keep responses concise.",
            },
            "agent-workspace": {
              allow: true,
              requireMention: false,  // Agent responds to everything here
              systemPrompt: "This is your private workspace. You can think out loud and use all tools.",
            },
          },
        },
      },
      
      // DM configuration
      dm: {
        enabled: true,
        policy: "pairing",  // "pairing" | "allowlist" | "open" | "disabled"
        allowFrom: ["YOUR_USER_ID"],
        groupEnabled: false,  // Group DMs off by default
      },
      
      // Discord actions the agent can perform
      actions: {
        reactions: true,
        stickers: true,
        emojiUploads: true,
        polls: true,
        permissions: true,
        messages: true,
        threads: true,
        pins: true,
        search: true,
        memberInfo: true,
        roleInfo: true,
        channelInfo: true,
        channels: true,        // CREATE/EDIT/DELETE channels and categories
        voiceStatus: true,
        events: true,
        roles: false,          // Disabled by default — enable carefully
        moderation: false,     // Disabled by default — enable carefully
      },
      
      // Message formatting
      textChunkLimit: 2000,    // Discord's message limit
      chunkMode: "length",     // "length" | "newline"
      maxLinesPerMessage: 17,
      
      // Reply threading
      replyToMode: "off",      // "off" | "all" — "off" disables implicit reply threading
      
      // Media
      mediaMaxMb: 8,
      
      // History context for mentions
      historyLimit: 20,        // Recent guild messages included as context
    }
  }
}
```

## Session Keys

Discord sessions follow deterministic patterns:
- **Guild channels:** `agent:<agentId>:discord:channel:<channelId>`
- **Threads:** `agent:<agentId>:discord:thread:<guildId>:<threadId>`
- **DMs:** Collapse to agent's main session (`agent:<agentId>:main`)
- **Slash commands:** `agent:<agentId>:discord:slash:<userId>`

Display names use `discord:<guildSlug>#<channelSlug>`.

## The Discord Tool (Built-in Skill)

The `discord` tool is exposed automatically when the current channel is Discord. It provides full server management capabilities:

### Message Actions
```json5
// Send a message
{ "action": "sendMessage", "to": "channel:123456", "content": "Hello from the agent" }

// Send with media
{ "action": "sendMessage", "to": "channel:123456", "content": "Check this out", "mediaUrl": "file:///tmp/output.png" }

// Read messages from a channel
{ "action": "readMessages", "channelId": "123456", "limit": 50 }

// Edit a message
{ "action": "editMessage", "channelId": "123456", "messageId": "789", "content": "Updated" }

// Delete a message
{ "action": "deleteMessage", "channelId": "123456", "messageId": "789" }

// Reply in thread
{ "action": "threadReply", "channelId": "123456", "messageId": "789", "content": "Thread reply" }
```

### Channel/Category Management (Key for Agentic Server Building)
```json5
// Create a category
{ "action": "createChannel", "guildId": "GUILD_ID", "name": "Researcher Agent", "type": "category" }

// Create a text channel under a category
{ "action": "createChannel", "guildId": "GUILD_ID", "name": "workspace", "type": "text", "parentId": "CATEGORY_ID" }

// Edit channel
{ "action": "editChannel", "channelId": "123456", "name": "renamed-channel", "topic": "New topic" }

// Delete channel
{ "action": "deleteChannel", "channelId": "123456" }
```

### Reactions, Polls, Stickers
```json5
// React to a message
{ "action": "react", "channelId": "123", "messageId": "456", "emoji": "✅" }

// Create a poll
{ "action": "poll", "to": "channel:123", "question": "Approach A or B?", "answers": ["Approach A", "Approach B"], "durationHours": 24 }
```

### Components v2 (Interactive UI)
```json5
{
  "action": "send",
  "channel": "discord",
  "to": "channel:123",
  "components": {
    "text": "Choose a path",
    "blocks": [
      {
        "type": "actions",
        "buttons": [
          { "label": "Approve", "style": "success" },
          { "label": "Decline", "style": "danger" }
        ]
      }
    ]
  }
}
```

Interaction results route back to the agent as normal inbound messages.

## Discord Threads for Project Isolation

Use `sessions_spawn` with `thread: true` to create isolated Discord threads per project or task. This keeps the main channel clean while giving each project its own conversation context.

```json5
// Orchestrator spawning a task in an isolated Discord thread
{
  tool: "sessions_spawn",
  args: {
    agent: "developer",
    message: "Implement PROJ-042: WebSocket reconnection handler per charter spec.",
    thread: true,  // Creates a Discord thread for this session
    timeoutSeconds: 600,
  }
}
```

### Thread Benefits
- Each PROJ-XXX gets its own thread — clean audit trail
- Thread sessions are isolated from the parent channel session
- Agents can be spawned into threads without polluting shared channels
- Human can follow along in the thread without interfering with the agent's work

### Thread Session Keys
Thread sessions use the format: `agent:<agentId>:discord:thread:<guildId>:<threadId>`

## Discord Components v2

OpenClaw supports Discord Components v2 for interactive UI elements (buttons, select menus, action rows). These are used for:
- **Exec approval buttons** (Approve/Decline for dangerous commands)
- **Task status polls** (agents can create polls for human decision-making)
- **Interactive reports** (agents can post reports with action buttons)

Components v2 is an evolving Discord feature. Current support covers buttons and basic action rows. Select menus and modals are potential future additions as Discord expands the API.

## Key Behaviors

- **Routing is deterministic:** replies always go back to the channel they arrived on
- **Channel topics** are injected as untrusted context (not system prompt)
- **Threads** inherit parent channel config unless explicitly overridden
- **Bot-authored messages** are ignored by default — set `allowBots: true` to allow (critical for agent-to-agent on Discord)
- **Message IDs** are surfaced in context/history so agents can target specific messages
- **PluralKit** proxied senders are resolved correctly for allowlists

## Troubleshooting

```bash
# Run diagnostics
openclaw doctor
openclaw channels status --probe

# Common issues:
# "Used disallowed intents" → Enable Message Content Intent in Developer Portal
# "not authorized" → This is from OpenClaw, not Discord. User not on allowlist.
# Bot online but not responding → Check requireMention setting
# Duplicate messages → Multiple gateway instances running. Stop old ones.
# "Unknown Channel" → Bot lacks permissions or channel ID is wrong
```
