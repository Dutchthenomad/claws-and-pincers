# Quick Start Guide - Testing Your Discord Agents

**Status:** Agents deployed and connected to Discord ✅  
**Next:** Invite bots to your server and test

---

## 🚀 Step 1: Invite Bots to Discord

### Option A: Use Pre-Generated URLs (Easiest)

Open these links in your browser and invite each bot:

| Bot | Invite Link |
|-----|-------------|
| 🎯 Orchestrator | https://discord.com/oauth2/authorize?client_id=1472379948915228965&permissions=274877910016&scope=bot+applications.commands |
| 🔬 Researcher | https://discord.com/oauth2/authorize?client_id=1472638515958386790&permissions=274877910016&scope=bot+applications.commands |
| 💻 Developer | https://discord.com/oauth2/authorize?client_id=1472383272402026548&permissions=274877910016&scope=bot+applications.commands |
| 🖥️ Sysadmin | https://discord.com/oauth2/authorize?client_id=1472384348115304509&permissions=274877910016&scope=bot+applications.commands |
| 🔍 Reviewer | https://discord.com/oauth2/authorize?client_id=1468111419911311446&permissions=274877910016&scope=bot+applications.commands |

**For each link:**
1. Click the link
2. Select your Discord server
3. Click "Authorize"
4. Complete CAPTCHA if prompted

---

## 🧪 Step 2: Test the Bots

### Basic Ping Test

In any channel where bots have access, try:

```
@Orchestrator hello
```

Expected response: Bot should acknowledge you

### Agent-Specific Tests

| Agent | Test Message | Expected Capability |
|-------|--------------|---------------------|
| 🎯 **Orchestrator** | "@Orchestrator what can you do?" | Should describe capabilities, offer to spawn other agents |
| 🔬 **Researcher** | "@Researcher search for OpenClaw documentation" | Should search web and return results |
| 💻 **Developer** | "@Developer show me the git status" | Should run git commands, show file status |
| 🖥️ **Sysadmin** | "@Sysadmin check docker status" | Should check container status |
| 🔍 **Reviewer** | "@Reviewer read the README" | Should read files and summarize |

---

## 🏗️ Step 3: Set Up Discord Channels

Create these channels in your Discord server for organized workflow:

### Required Channels:

**#general-coordination** - Main chat with all agents
- All bots should have access
- Used for general discussion and task dispatch

**#orchestrator** - Direct line to coordinator
- Only Orchestrator bot
- For governance and project management

**#research** - Research workspace
- Researcher bot primary
- For web searches, data gathering

**#development** - Code workspace
- Developer bot primary
- For code editing, PRs, file operations

**#infrastructure** - System workspace
- Sysadmin bot primary
- For Docker, VPS, monitoring tasks

**#review** - Quality workspace
- Reviewer bot primary
- For code review, audits, read-only tasks

### Channel Permissions:

| Channel | Orchestrator | Researcher | Developer | Sysadmin | Reviewer |
|---------|--------------|------------|-----------|----------|----------|
| #general-coordination | ✅ | ✅ | ✅ | ✅ | ✅ |
| #orchestrator | ✅ | ❌ | ❌ | ❌ | ❌ |
| #research | ✅ | ✅ | ❌ | ❌ | ❌ |
| #development | ✅ | ❌ | ✅ | ❌ | ✅ (read) |
| #infrastructure | ✅ | ❌ | ❌ | ✅ | ❌ |
| #review | ✅ | ❌ | ❌ | ❌ | ✅ |

---

## 📝 Step 4: Run Your First Project

### Project: "Test Agent Capabilities" (PROJ-TEST-001)

**Charter:**
```markdown
# Project Charter: PROJ-TEST-001

## Objective
Test all 5 agents' capabilities and document what works

## Scope
- Test each agent's primary function
- Document response times
- Identify any issues

## Deliverables
- Test results for each agent
- List of working capabilities
- Any bugs or limitations found

## Assigned Agents
- Orchestrator: Project coordination
- Researcher: Web search test
- Developer: Git/file operation test
- Sysadmin: Docker test
- Reviewer: File reading test

## Success Criteria
- All 5 agents respond to mentions
- Each agent performs its specialty task
- No critical errors
```

### How to Dispatch:

In #general-coordination:
```
@Orchestrator I want to start project PROJ-TEST-001: Test Agent Capabilities. 

The charter is in governance/templates/charter-template.md. 

Please coordinate with all agents to test their capabilities.
```

---

## 🔍 Troubleshooting

### Bot shows as offline:
```bash
# Check if container is running
docker ps | grep openclaw-orchestrator

# Check logs
docker logs openclaw-orchestrator

# Restart if needed
cd /opt/openclaw/discord-agents && docker compose restart
```

### Bot doesn't respond:
- ✅ Verify bot is online (green dot in Discord)
- ✅ Check bot has permission to read/send in channel
- ✅ Try @ mentioning with exact username
- ✅ Check logs: `docker logs openclaw-orchestrator`

### Can't invite bot:
- ✅ You need "Manage Server" permission
- ✅ Or ask server owner to invite
- ✅ Check bot isn't already in server

---

## 📊 Monitoring

### Run Health Check:
```bash
cd /opt/openclaw/discord-agents
./health-check.sh
```

### Watch Logs:
```bash
# All agents
docker compose logs -f

# Specific agent
docker logs -f openclaw-orchestrator
```

### Resource Usage:
```bash
docker stats
```

---

## 🎯 Next Steps After Testing

1. **Document what works** - Update TODO.md
2. **Build n8n workflows** - Add enforcement layer
3. **Run real project** - Use actual task
4. **Expand team** - Add more specialists if needed

---

## 📚 Reference

- **Agent configs:** `agents/{orchestrator,researcher,developer,sysadmin,reviewer}/`
- **Core charter:** `governance/operations/CORE-CHARTER.md`
- **OAuth2 URLs:** `deployment/discord-agents/OAUTH2_URLS.md`
- **Health check:** `deployment/discord-agents/health-check.sh`

---

**Status:** Ready to invite and test! 🚀
