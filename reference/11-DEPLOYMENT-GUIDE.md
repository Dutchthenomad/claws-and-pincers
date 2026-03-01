# 11 — Deployment Guide

## Prerequisites

- **Node.js 22+** (required)
- **Docker** (recommended for agent sandboxing)
- **Git** (for version control of workspaces)
- **API Keys:** OpenRouter (primary), optionally direct Anthropic, Groq
- **Discord Bots:** One bot per agent, created via Developer Portal with proper intents

## Installation

### Option A: Global npm Install (Recommended)
```bash
npm install -g openclaw@latest
openclaw --version
openclaw onboard
```

### Option B: Docker
```bash
docker pull openclaw/openclaw:latest
docker run -it \
  -v ~/.openclaw:/root/.openclaw \
  -e OPENROUTER_API_KEY="sk-or-v1-..." \
  -e DISCORD_ORCHESTRATOR_TOKEN="..." \
  openclaw/openclaw
```

### Option C: From Source
```bash
git clone https://github.com/openclaw/openclaw.git
cd openclaw
pnpm install
pnpm ui:build
pnpm build
```

## VPS Deployment (Linux)

### 1. Server Setup
```bash
# Ubuntu 24 on VPS
sudo apt update && sudo apt upgrade -y
sudo apt install -y curl git docker.io docker-compose

# Install Node.js 22
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs

# Create dedicated user
sudo useradd -m -s /bin/bash openclaw
sudo usermod -aG docker openclaw
sudo su - openclaw
```

### 2. Install OpenClaw
```bash
npm install -g openclaw@latest
openclaw --version
```

### 3. Configure Environment
```bash
# Create secrets directory
mkdir -p /opt/openclaw/secrets /opt/openclaw/config
chmod 700 /opt/openclaw/secrets

# Store secrets (chmod 600 each)
cat > /opt/openclaw/config/.env << 'EOF'
OPENROUTER_API_KEY=sk-or-v1-your_key_here
DISCORD_ORCHESTRATOR_TOKEN=your_orchestrator_token
DISCORD_RESEARCHER_TOKEN=your_researcher_token
DISCORD_DEVELOPER_TOKEN=your_developer_token
DISCORD_SYSADMIN_TOKEN=your_sysadmin_token
DISCORD_REVIEWER_TOKEN=your_reviewer_token
OPENCLAW_GATEWAY_TOKEN=your_gateway_auth_token
EOF

chmod 600 /opt/openclaw/config/.env
```

### 4. Create Workspace Structure
```bash
# Create agent workspaces
mkdir -p ~/.openclaw/workspace-{orchestrator,researcher,developer,sysadmin,reviewer}

# Copy identity files to each workspace
# (Use the templates from 05-IDENTITY-AND-PERSONAS.md)
for agent in orchestrator researcher developer sysadmin reviewer; do
  touch ~/.openclaw/workspace-$agent/SOUL.md
  touch ~/.openclaw/workspace-$agent/AGENTS.md
  touch ~/.openclaw/workspace-$agent/HEARTBEAT.md
  touch ~/.openclaw/workspace-$agent/TOOLS.md
  mkdir -p ~/.openclaw/workspace-$agent/skills
done

# Create agent state directories
mkdir -p ~/.openclaw/agents/{orchestrator,researcher,developer,sysadmin,reviewer}/agent
```

### 5. Apply Configuration
```bash
# Copy your openclaw.json5 (from 08-CONFIGURATION-REFERENCE.md)
cp openclaw.json5 ~/.openclaw/openclaw.json5

# Validate
openclaw doctor
```

### 6. Config Hardening

Before going live, verify these security and compliance settings:

```bash
# Verify hub-and-spoke enforcement
# Check that only orchestrator has sessions_spawn in allow list
grep -A5 "sessions_spawn" ~/.openclaw/openclaw.json5

# Verify agentToAgent restrictions
# Specialists should have: allow: ["orchestrator"]
# Orchestrator should have: allow: ["*"]
grep -B2 -A2 "agentToAgent" ~/.openclaw/openclaw.json5

# Verify sandbox modes
# Developer should be "lenient", not "off"
grep -B1 "sandbox" ~/.openclaw/openclaw.json5

# Verify gateway is not exposed to public internet
# Port 18789 should be bound to 127.0.0.1 on the host
ss -tlnp | grep 18789

# Verify gateway auth is enabled
grep -A2 "auth:" ~/.openclaw/openclaw.json5

# Verify Discord requireMention is set
grep "requireMention" ~/.openclaw/openclaw.json5
```

### 7. Install as Systemd Service
```bash
# Using OpenClaw's built-in daemon installer
openclaw gateway --install-daemon

# Or manually create systemd unit:
sudo cat > /etc/systemd/system/openclaw.service << 'EOF'
[Unit]
Description=OpenClaw Gateway
After=network.target docker.service
Wants=docker.service

[Service]
Type=simple
User=openclaw
Group=openclaw
WorkingDirectory=/home/openclaw
EnvironmentFile=/opt/openclaw/config/.env
ExecStart=/usr/bin/openclaw gateway
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/openclaw/.openclaw /opt/openclaw

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

### 8. Enable Native Features

After the gateway is running, enable these native features:

```bash
# Enable cron jobs for governance automation
openclaw cron add --name "law1-audit" --schedule "*/5 * * * *" \
  --agent orchestrator --prompt "Check #task-dispatch for messages without PROJ-XXX tags"

openclaw cron add --name "law2-audit" --schedule "*/15 * * * *" \
  --agent orchestrator --prompt "Check for projects with unapproved charters"

openclaw cron add --name "cost-daily" --schedule "0 0 * * *" \
  --agent orchestrator --prompt "Run /usage and post daily cost summary to #cost-tracking"

# Verify cron jobs
openclaw cron list

# Verify hooks/webhooks are active
openclaw hooks list

# Test heartbeat
openclaw heartbeat trigger --agent orchestrator
```

### 9. Set Up Webhooks

Configure n8n to receive OpenClaw webhook events:

```bash
# In n8n, create a Webhook node at:
#   http://127.0.0.1:5678/webhook/openclaw-governance
#
# The webhook receives events configured in openclaw.json5:
#   - cron.complete: Governance audit results
#   - session.error: Agent session failures
#   - heartbeat.alert: Heartbeat check failures
#
# n8n workflow should:
#   1. Parse the event type
#   2. Route to appropriate handler
#   3. Send notifications via Apprise if critical
```

### 10. Verify
```bash
# Check service status
sudo systemctl status openclaw

# Check gateway status
openclaw status

# Check Discord connection
openclaw channels status --probe

# Verify all agents are registered
openclaw agents list

# Verify sessions are working
openclaw sessions list

# View logs
journalctl -u openclaw -f
# or
openclaw gateway logs --tail
```

## Podman Alternative (Rootless Containers)

OpenClaw includes Podman support for rootless container deployment:

```bash
# One-time host setup
./setup-podman.sh

# Launch
./run-openclaw-podman.sh

# Or use systemd Quadlet for auto-start
# See docs/platforms/podman for full instructions
```

## Remote Access

### Tailscale (Recommended)
Use Tailscale Serve/Funnel for secure remote access to the Gateway dashboard and WebSocket:

```bash
# Install Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Expose Gateway dashboard
tailscale serve https://127.0.0.1:18789
```

### SSH Tunnel (Alternative)
```bash
# From your local machine
ssh -L 18789:localhost:18789 openclaw@your-vps-ip
# Then access Gateway UI at http://localhost:18789
```

## Git Version Control for Workspaces

Track workspace changes (SOUL.md, AGENTS.md, skills, etc.) in Git:

```bash
cd ~/.openclaw
git init
cat > .gitignore << 'EOF'
# Credentials and secrets
.env
credentials/
agents/*/agent/auth-profiles.json

# Session data (large, binary-ish)
agents/*/sessions/

# Node modules
node_modules/

# Temp files
*.tmp
*.log
EOF

git add .
git commit -m "Initial workspace setup"

# Push to private GitHub repo
git remote add origin git@github.com:YOUR_USER/openclaw-workspaces.git
git push -u origin main
```

## Build-Out Sequence

Recommended order for bringing the system online:

### Phase 1: Single Agent Baseline
1. Deploy OpenClaw with just the Orchestrator agent
2. Connect to Discord — verify bot responds in a test channel
3. Test basic Discord tool actions (create channel, send message)
4. Verify heartbeat is working (check HEARTBEAT.md triggers)
5. Confirm DM communication works

### Phase 2: Add Specialist Agents
1. Add Researcher agent to config with `agentToAgent: { allow: ["orchestrator"] }`
2. Create workspace with SOUL.md and AGENTS.md
3. Test `sessions_spawn` from Orchestrator to Researcher
4. Verify isolated sessions and workspace separation
5. Repeat for Developer, Sysadmin, and Reviewer

### Phase 3: Discord Server Structure
1. Have Orchestrator create the full channel/category structure agentically
2. Test per-account routing (each bot token routes to its agent)
3. Verify `requireMention` works correctly in shared channels
4. Set up project thread workflow in #task-dispatch

### Phase 4: Native Features
1. Enable cron jobs for governance audits
2. Configure webhooks to n8n for external notifications
3. Test the full delegation loop (Orchestrator spawns Researcher, Developer, Reviewer)
4. Verify hub-and-spoke enforcement (specialists cannot spawn or message each other)
5. Test heartbeat model overrides (groq for cheap check-ins)

### Phase 5: Autonomous Operation
1. Configure heartbeat checklists for each agent
2. Monitor for 24 hours with close oversight
3. Tune iteration limits and cost thresholds in SOUL.md files
4. Gradually reduce oversight as confidence builds
5. Set up Grafana dashboards for token usage and session metrics

## Updating

```bash
# Update OpenClaw
sudo npm install -g openclaw@latest

# Update skills
clawhub sync

# Restart gateway
sudo systemctl restart openclaw
```

OpenClaw is shipping daily. Pin to specific versions if stability matters more than features:
```bash
npm install -g openclaw@2026.3.1
```

## Monitoring Checklist

After deployment, regularly check:

- [ ] `openclaw status` — Gateway health
- [ ] `openclaw channels status --probe` — Discord connection
- [ ] `openclaw sessions list` — Active sessions (any stuck/errored?)
- [ ] `openclaw agents list` — All 5 agents configured correctly
- [ ] `openclaw cron list` — Cron jobs running on schedule
- [ ] `openclaw heartbeat status` — Heartbeats firing
- [ ] Provider dashboards — API token usage and spend (OpenRouter, Groq)
- [ ] Discord #system-logs — Any errors or warnings
- [ ] `journalctl -u openclaw --since "1 hour ago"` — System logs
- [ ] `docker stats openclaw-gateway --no-stream` — Container resource usage
