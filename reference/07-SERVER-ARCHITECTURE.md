# 07 — Server Architecture

## Design Philosophy

The architecture has two layers:

1. **OpenClaw Gateway** — The primary orchestration and coordination layer. Runs all 5 agents, handles session management, inter-agent communication, heartbeats, cron jobs, Discord integration, and tool execution.
2. **n8n** — External integration layer only. Handles webhook-triggered workflows (governance alerts, cost reporting) that bridge OpenClaw events to external services. n8n is NOT the control plane.

The Discord server serves as the **visibility and interaction layer**:
- **Private workspaces** where individual agents think and work
- **Shared collaboration spaces** where agents post results
- **Human observation points** for monitoring and intervention
- **Persistent logs** of all agent activity via project threads

The server structure should be created agentically (by the Orchestrator using the discord tool) rather than manually.

## Infrastructure Overview

The deployment runs **19 Docker containers** on a single VPS (4 vCPU, 16GB RAM, 200GB NVMe):

| Service | Port | Purpose |
|---------|------|---------|
| **openclaw-gateway** | 18789 | Primary orchestration — 5 agents, session tools, cron, hooks |
| rag-api | 8000 | RAG API service |
| rugs-mcp | 8001 | RUGS MCP server |
| openclaw-memory | 127.0.0.1:8002 | Persistent agent memory API (localhost only) |
| n8n | 5678 | External integration workflows (webhook-triggered only) |
| n8n-postgres | internal | PostgreSQL for n8n |
| qdrant | 6333 | Vector database |
| timescaledb | 5433 | Time-series database |
| rabbitmq | 5672, 15672 | Message broker |
| ollama | 11434 | Local LLM inference |
| grafana | 3000 | Monitoring dashboards |
| uptime-kuma | 3001 | Uptime monitoring |
| metabase | 3002 | Analytics |
| dozzle | 8080 | Container log viewer |
| apprise-api | 8003 | Notification service |

All ports bound to `127.0.0.1`, accessible via Tailscale VPN only.

## OpenClaw Gateway (Primary Orchestration)

The OpenClaw Gateway is a single container running all 5 agents. It provides:

- **Session management** — per-agent, per-sender session isolation
- **Hub-and-spoke coordination** — `sessions_spawn`, `sessions_send`, `sessions_list`, `sessions_history`
- **Discord integration** — 5 bot accounts via `channels.discord.accounts`
- **Heartbeats** — per-agent autonomous check-ins (Orchestrator: 15m, Sysadmin: 30m, others: 2-4h)
- **Cron jobs** — scheduled governance audits and cost reporting
- **Hooks/Webhooks** — event-driven integration with n8n for governance alerts
- **OpenAI-compatible API** — `gateway.openaiApi.enabled: true`
- **Control UI** — web dashboard at port 18789

### Gateway Config Location

```
/opt/openclaw/config/openclaw.json5   # Mounted into container
/opt/openclaw/config/.env             # Environment variables (secrets)
/opt/openclaw/secrets/                 # Tokens and keys (chmod 600)
```

## n8n (External Integrations Only)

n8n handles webhook-triggered workflows that bridge OpenClaw events to external systems. It is NOT the control plane — the Gateway handles all agent orchestration natively.

**Current n8n role:**
- Receive OpenClaw webhook events (cron.complete, session.error, heartbeat.alert)
- Trigger external notifications (Apprise, email)
- Run cost reporting workflows
- Bridge to external APIs that agents cannot reach directly

**Webhook configuration in openclaw.json5:**
```json5
hooks: {
  enabled: true,
  webhooks: {
    "governance-alert": {
      url: "http://127.0.0.1:5678/webhook/openclaw-governance",
      events: ["cron.complete", "session.error", "heartbeat.alert"],
    },
  },
},
```

## Discord Server Structure

### Category: ORCHESTRATOR
The central coordinator's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #orch-workspace | Orchestrator's private thinking space | orchestrator | false |
| #orch-logs | Orchestrator activity logs | orchestrator | false |
| #task-planning | Task decomposition and planning | orchestrator | false |

### Category: RESEARCHER
Research agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #research-workspace | Active research and notes | researcher | false |
| #research-logs | Research activity and source tracking | researcher | false |
| #research-archive | Completed research for reference | researcher | false |

### Category: DEVELOPER
Development agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #code-workspace | Active development work | developer | false |
| #code-logs | Build/test output and debugging | developer | false |
| #code-snippets | Reusable code and patterns | developer | false |

### Category: SYSADMIN
Infrastructure agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #sys-workspace | Infrastructure operations | sysadmin | false |
| #sys-logs | System health and alerts | sysadmin | false |

### Category: REVIEWER
Quality assurance agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #review-workspace | Active review work | reviewer | false |
| #review-logs | Review decisions and reasoning | reviewer | false |

### Category: SHARED WORKSPACE
Channels where multiple agents post results (via the Orchestrator's coordination).

| Channel | Purpose | Bound Agents | requireMention |
|---|---|---|---|
| #task-dispatch | Orchestrator posts task assignments; project threads created here | all | true |
| #collaboration | Cross-agent discussion and coordination | all | true |
| #review-queue | Completed work awaiting review | all | true |
| #completed | Approved deliverables | all | true |
| #knowledge-base | Shared references and documentation | all | true |

### Category: HUMAN CONTROL
Human oversight and intervention channels.

| Channel | Purpose | Bound Agents | requireMention |
|---|---|---|---|
| #human-oversight | Status updates, escalations, approvals | orchestrator | true |
| #direct-command | Human sends direct instructions to any agent | all | true |
| #system-logs | Automated system diagnostics and health | orchestrator | false |
| #cost-tracking | Token usage and API cost monitoring | orchestrator | false |

### Category: SYSTEM
Infrastructure and configuration channels.

| Channel | Purpose | Notes |
|---|---|---|
| #config | Configuration snapshots and changes | Read-only for agents |
| #error-log | Error reports and crash logs | Auto-populated |
| #heartbeat-log | Heartbeat activity tracking | Auto-populated |

## Channel-to-Agent Binding Map

With per-account bindings, each Discord bot account routes to its agent automatically. Channel-specific bindings are not required — the `accountId` in bindings handles routing:

```json5
{
  bindings: [
    { agentId: "orchestrator", match: { channel: "discord", accountId: "orchestrator" } },
    { agentId: "researcher", match: { channel: "discord", accountId: "researcher" } },
    { agentId: "developer", match: { channel: "discord", accountId: "developer" } },
    { agentId: "sysadmin", match: { channel: "discord", accountId: "sysadmin" } },
    { agentId: "reviewer", match: { channel: "discord", accountId: "reviewer" } },
    { agentId: "orchestrator", match: { channel: "discord" } },  // Fallback
  ],

  channels: {
    discord: {
      allowBots: true,
      groupPolicy: "allowlist",
      guilds: {
        "GUILD_ID": {
          requireMention: true,
        },
      },
      accounts: {
        orchestrator: { token: "${DISCORD_ORCHESTRATOR_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        researcher:   { token: "${DISCORD_RESEARCHER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        developer:    { token: "${DISCORD_DEVELOPER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        sysadmin:     { token: "${DISCORD_SYSADMIN_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
        reviewer:     { token: "${DISCORD_REVIEWER_TOKEN}", groupPolicy: "allowlist", streaming: "off" },
      },
    },
  },
}
```

## Agentic Server Setup

The Orchestrator agent should create the channel structure itself on first boot. Include instructions in the Orchestrator's AGENTS.md:

```markdown
## First Boot — Server Setup

On your first activation, if the Discord server does not have the required channel structure:

1. Use the discord tool to create categories and channels per the server architecture spec
2. Set appropriate channel topics describing each channel's purpose
3. Post a welcome message to #human-oversight confirming setup is complete
4. List all created channels and their IDs
5. Store the channel map in your workspace for reference

Channel creation commands:
- Create category: { "action": "createChannel", "guildId": "GUILD_ID", "name": "ORCHESTRATOR", "type": "category" }
- Create channel: { "action": "createChannel", "guildId": "GUILD_ID", "name": "orch-workspace", "type": "text", "parentId": "CATEGORY_ID" }
```

## Discord Permission Strategy

### Bot Permissions Required
- Send Messages
- Read Message History
- Embed Links
- Attach Files
- Add Reactions
- Manage Channels (for agentic server building)
- Manage Roles (optional — only if agents need to manage access)
- Use External Emojis
- Create Public Threads / Create Private Threads
- Send Messages in Threads

### Role-Based Access Control
Consider creating Discord roles that map to agent access levels:
- `@agent-admin` — Full access (Orchestrator)
- `@agent-worker` — Standard agent access (Researcher, Developer, Sysadmin, Reviewer)
- `@human-admin` — Human oversight access
- `@observer` — Read-only access for humans watching

## Scaling Considerations

### Adding New Agents
1. Define in `agents.list[]` with appropriate `agentToAgent.allow: ["orchestrator"]`
2. Create workspace with SOUL.md, AGENTS.md
3. Add Discord bot account in `channels.discord.accounts`
4. Add per-account binding
5. Create Discord category + channels (agentically or manually)
6. Update Orchestrator's AGENTS.md with new team member
7. Restart gateway

### Channel Proliferation
Discord has a limit of 500 channels per server. With 5 agents x 2-3 channels each + shared channels, we're at ~25. This leaves room for growth, but consider archiving completed project channels periodically.

### Multiple Servers
One bot token can be invited to multiple servers. Consider separate servers for separate projects, with the same agent team operating across them.
