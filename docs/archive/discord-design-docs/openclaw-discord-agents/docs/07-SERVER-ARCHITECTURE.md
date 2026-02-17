# 07 — Discord Server Architecture

## Design Philosophy

The Discord server IS the agent workspace. Channels serve as:
- **Private workspaces** where individual agents think and work
- **Shared collaboration spaces** where agents coordinate
- **Human observation points** for monitoring and intervention
- **Persistent logs** of all agent activity

The server structure should be created agentically (by the orchestrator using the discord tool) rather than manually. This ensures the agents understand and own their environment.

## Server Structure

### Category: 🎯 ORCHESTRATOR
The central coordinator's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #orch-workspace | Orchestrator's private thinking space | orchestrator | false |
| #orch-logs | Orchestrator activity logs | orchestrator | false |
| #task-planning | Task decomposition and planning | orchestrator | false |

### Category: 🔬 RESEARCHER
Research agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #research-workspace | Active research and notes | researcher | false |
| #research-logs | Research activity and source tracking | researcher | false |
| #research-archive | Completed research for reference | researcher | false |

### Category: 💻 CODER
Development agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #code-workspace | Active development work | coder | false |
| #code-logs | Build/test output and debugging | coder | false |
| #code-snippets | Reusable code and patterns | coder | false |

### Category: 🔍 REVIEWER
Quality assurance agent's private workspace.

| Channel | Purpose | Bound Agent | requireMention |
|---|---|---|---|
| #review-workspace | Active review work | reviewer | false |
| #review-logs | Review decisions and reasoning | reviewer | false |

### Category: 🤝 SHARED WORKSPACE
Channels where multiple agents interact.

| Channel | Purpose | Bound Agents | requireMention |
|---|---|---|---|
| #task-dispatch | Orchestrator posts task assignments | all | true |
| #collaboration | Cross-agent discussion and coordination | all | true |
| #review-queue | Completed work awaiting review | all | true |
| #completed | Approved deliverables | all | true |
| #knowledge-base | Shared references and documentation | all | true |

### Category: 👤 HUMAN CONTROL
Human oversight and intervention channels.

| Channel | Purpose | Bound Agents | requireMention |
|---|---|---|---|
| #human-oversight | Status updates, escalations, approvals | orchestrator | true |
| #direct-command | Human sends direct instructions to any agent | all | true |
| #system-logs | Automated system diagnostics and health | orchestrator | false |
| #cost-tracking | Token usage and API cost monitoring | orchestrator | false |

### Category: ⚙️ SYSTEM
Infrastructure and configuration channels.

| Channel | Purpose | Notes |
|---|---|---|
| #config | Configuration snapshots and changes | Read-only for agents |
| #error-log | Error reports and crash logs | Auto-populated |
| #heartbeat-log | Heartbeat activity tracking | Auto-populated |

## Channel-to-Agent Binding Map

```json5
{
  bindings: [
    // Orchestrator channels (private)
    { agentId: "orchestrator", match: { channel: "discord", guildId: "GUILD_ID" } },
    
    // Shared channels use role-based or mention-based routing
    // Orchestrator is default for shared channels, others respond to @mentions
  ],
  
  channels: {
    discord: {
      allowBots: true,
      groupPolicy: "allowlist",
      guilds: {
        "GUILD_ID": {
          requireMention: true,  // Default: require @mention
          users: ["HUMAN_USER_ID"],
          channels: {
            // Orchestrator private channels
            "orch-workspace":    { allow: true, requireMention: false },
            "orch-logs":         { allow: true, requireMention: false },
            "task-planning":     { allow: true, requireMention: false },
            
            // Researcher private channels
            "research-workspace": { allow: true, requireMention: false },
            "research-logs":      { allow: true, requireMention: false },
            "research-archive":   { allow: true, requireMention: false },
            
            // Coder private channels
            "code-workspace":  { allow: true, requireMention: false },
            "code-logs":       { allow: true, requireMention: false },
            "code-snippets":   { allow: true, requireMention: false },
            
            // Reviewer private channels
            "review-workspace": { allow: true, requireMention: false },
            "review-logs":      { allow: true, requireMention: false },
            
            // Shared channels (requireMention = true enforced by default)
            "task-dispatch":   { allow: true, requireMention: true },
            "collaboration":   { allow: true, requireMention: true },
            "review-queue":    { allow: true, requireMention: true },
            "completed":       { allow: true, requireMention: true },
            "knowledge-base":  { allow: true, requireMention: true },
            
            // Human control
            "human-oversight":  { allow: true, requireMention: true },
            "direct-command":   { allow: true, requireMention: true },
            "system-logs":      { allow: true, requireMention: false },
            "cost-tracking":    { allow: true, requireMention: false },
          }
        }
      }
    }
  }
}
```

## Agentic Server Setup

The orchestrator agent should create this structure itself on first boot. Include instructions in the orchestrator's AGENTS.md:

```markdown
## First Boot — Server Setup

On your first activation, if the Discord server does not have the required channel structure:

1. Use the discord tool to create categories and channels per the server architecture spec
2. Set appropriate channel topics describing each channel's purpose
3. Post a welcome message to #human-oversight confirming setup is complete
4. List all created channels and their IDs
5. Store the channel map in your workspace for reference

Channel creation commands:
- Create category: { "action": "createChannel", "guildId": "GUILD_ID", "name": "🎯 ORCHESTRATOR", "type": "category" }
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

### Role-Based Access Control
Consider creating Discord roles that map to agent access levels:
- `@agent-admin` — Full access (orchestrator)
- `@agent-worker` — Standard agent access (researcher, coder, reviewer)
- `@human-admin` — Human oversight access
- `@observer` — Read-only access for humans watching

## Scaling Considerations

### Adding New Agents
1. Define in `agents.list[]`
2. Create workspace with SOUL.md, AGENTS.md
3. Create Discord category + channels (agentically or manually)
4. Add bindings for new channels
5. Update orchestrator's AGENTS.md with new team member
6. Restart gateway

### Channel Proliferation
Discord has a limit of 500 channels per server. With 4 agents × 3 channels each + shared channels, we're at ~20. This leaves massive room for growth, but consider archiving completed project channels periodically.

### Multiple Servers
One bot token can be invited to multiple servers. Consider separate servers for separate projects, with the same agent team operating across them.
