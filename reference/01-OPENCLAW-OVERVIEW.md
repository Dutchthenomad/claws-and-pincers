# 01 — OpenClaw Overview

## What Is OpenClaw

OpenClaw (formerly Clawdbot, then Moltbot) is an open-source, MIT-licensed personal AI assistant framework created by Peter Steinberger. It runs as a local-first Node.js daemon (the "Gateway") that connects AI models to messaging platforms, tools, and the local filesystem. Unlike cloud chatbots, OpenClaw is a persistent agent runtime — it maintains state, executes shell commands, controls browsers, manages files, and operates autonomously via heartbeat schedules.

**Key differentiator:** OpenClaw is a *gateway and control plane*, not an AI model. It orchestrates communication between messaging channels (Discord, Slack, WhatsApp, Signal, iMessage, etc.), AI model providers (Anthropic, OpenAI, Google, local via Ollama), and local/remote tools.

## Current State (Mar 2026)

- **GitHub Stars:** 157,000+ (one of the fastest-growing OSS repos in history)
- **ClawHub Skills:** 5,700+ community-built skills
- **Version:** 2026.2.26 (releases are date-versioned, shipping daily)
- **Supported Models:** Claude Opus 4.6, Claude Sonnet 4.5, GPT-5.2 Codex, GLM-5, KIMI K2.5, Gemini 3 Pro, plus any OpenAI-compatible endpoint including Ollama local models
- **Supported Channels:** WhatsApp, Slack, Discord, Google Chat, Signal, iMessage, BlueBubbles, Microsoft Teams, Matrix, Zalo, WebChat, macOS app, iOS/Android nodes
- **Native Features Used in This Project:** Cron scheduling, session tools (sessions_spawn/send/list/history), memory-core, heartbeats, exec approvals — all built into the Gateway, no external orchestration (n8n) needed for control plane functions

## Core Architecture

```
Messaging Channels (Discord/Slack/WhatsApp/etc.)
    │
    ▼
┌─────────────────────────────┐
│         Gateway              │
│    (Node.js control plane)   │
│    ws://127.0.0.1:18789      │
│                              │
│  - Session management        │
│  - Channel routing           │
│  - Tool orchestration        │
│  - Multi-agent bindings      │
│  - Heartbeat scheduler       │
│  - Cron engine               │
│  - Exec approvals            │
└──────────┬──────────────────┘
           │
    ┌──────┼──────┐
    │      │      │
  Pi Agent CLI   WebChat UI
  (RPC)         macOS/iOS/Android
```

## Key Concepts

### Gateway
The long-running background daemon. Manages all connections, sessions, routing, and tool invocation. Runs as systemd service on Linux, LaunchAgent on macOS.

### Workspace
A directory containing the agent's personality files (`SOUL.md`, `AGENTS.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `MEMORY.md`, `HEARTBEAT.md`), local notes, and skills. Default: `~/.openclaw/workspace`.

### Sessions
Each conversation context is a session with its own transcript (stored as JSONL). Session keys follow the pattern `agent:<agentId>:<channel>:<type>:<id>`. Discord guild channels get isolated sessions: `agent:<agentId>:discord:channel:<channelId>`.

### Skills
Modular capability packages — a folder with a `SKILL.md` file plus supporting files. Skills add tools, inject domain knowledge, wire in external services, or define workflows. Installed to `<workspace>/skills/` and loaded at session start.

### Bindings
Routing rules that map inbound messages to specific agents based on channel type, guild ID, account ID, peer ID, or Discord role IDs. First match wins; more specific bindings should come first.

### Heartbeat
A periodic check-in (default every 30 minutes) where the agent reads `HEARTBEAT.md` and decides whether any action is needed. This enables proactive, unprompted behavior.

### Cron
Native scheduled task engine built into the Gateway. Uses standard crontab syntax for precise timing. Cron jobs fire messages to specific agents at exact times — used for governance audits, cost reports, and scheduled maintenance.

### Memory-Core
Built-in persistent memory system. Agents can store and retrieve observations, decisions, and context across sessions. Replaces external memory solutions for most use cases.

### Context Compaction
When conversation history exceeds the model's context window, OpenClaw automatically compacts older messages while preserving key context. This is critical for long-running autonomous sessions.

## File System Layout

```
~/.openclaw/
├── openclaw.json5          # Main configuration
├── workspace/              # Default agent workspace
│   ├── AGENTS.md           # Agent instructions
│   ├── SOUL.md             # Agent personality/philosophy
│   ├── TOOLS.md            # Tool usage instructions
│   ├── IDENTITY.md         # Presentation metadata
│   ├── USER.md             # User context
│   ├── MEMORY.md           # Persistent memory
│   ├── HEARTBEAT.md        # Heartbeat checklist
│   └── skills/             # Installed skills
│       └── <skill>/SKILL.md
├── agents/                 # Per-agent state
│   ├── main/
│   │   ├── agent/
│   │   │   └── auth-profiles.json
│   │   └── sessions/
│   │       ├── main.jsonl
│   │       └── discord_channel_123.jsonl
│   └── <agentId>/
│       ├── agent/
│       └── sessions/
├── credentials/            # Channel auth (Discord tokens, etc.)
├── skills/                 # Shared skills (available to all agents)
└── cron/                   # Cron job definitions
```

## Model Strategy

OpenClaw assembles large prompts: system instructions + conversation history + tool schemas + skills + memory. Frontier models work best as primary orchestrators due to the context load. Common pattern:
- **Opus 4.6** for orchestrator/deep-work agents
- **Sonnet 4.5** for specialist/everyday agents
- **Cheaper models** (or local via Ollama) for heartbeats and sub-agent tasks

Per-agent model configuration is supported, including fallback chains with exponential backoff.

## Ecosystem Components

| Component | Purpose | URL |
|---|---|---|
| OpenClaw Core | Gateway + agent runtime | github.com/openclaw/openclaw |
| ClawHub | Skill registry (5,700+ skills) | clawhub.ai |
| OnlyCrabs | SOUL.md persona registry | onlycrabs.ai |
| Moltbook | Agent-only social network (study reference) | moltbook.com |
| Friends of the Crustacean | Official Discord community | Discord server |
| DeepWiki | Auto-generated deep documentation | deepwiki.com/openclaw/openclaw |

## Installation (Quick Reference)

```bash
# Global install (requires Node.js 22+)
npm install -g openclaw@latest

# Verify
openclaw --version

# Run onboarding wizard
openclaw onboard

# Or Docker
docker pull openclaw/openclaw:latest
docker run -it -v ~/.openclaw:/root/.openclaw openclaw/openclaw
```
