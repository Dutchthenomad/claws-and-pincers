# 11 — Deployment Guide

## Prerequisites

- **Node.js 22+** (required)
- **Docker** (recommended for agent sandboxing)
- **Git** (for version control of workspaces)
- **API Keys:** Anthropic (primary), optionally OpenAI, Google
- **Discord Bot:** Created via Developer Portal with proper intents

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
  -e DISCORD_BOT_TOKEN="your_token" \
  -e ANTHROPIC_API_KEY="sk-ant-..." \
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
cat > ~/.openclaw/.env << 'EOF'
DISCORD_BOT_TOKEN=your_discord_bot_token_here
ANTHROPIC_API_KEY=sk-ant-api03-your_key_here
EOF

chmod 600 ~/.openclaw/.env
```

### 4. Create Workspace Structure
```bash
# Create agent workspaces
mkdir -p ~/.openclaw/workspace-{orchestrator,researcher,coder,reviewer}

# Copy identity files to each workspace
# (Use the templates from 05-IDENTITY-AND-PERSONAS.md)
for agent in orchestrator researcher coder reviewer; do
  touch ~/.openclaw/workspace-$agent/SOUL.md
  touch ~/.openclaw/workspace-$agent/AGENTS.md
  touch ~/.openclaw/workspace-$agent/HEARTBEAT.md
  touch ~/.openclaw/workspace-$agent/TOOLS.md
  mkdir -p ~/.openclaw/workspace-$agent/skills
done

# Create agent state directories
mkdir -p ~/.openclaw/agents/{orchestrator,researcher,coder,reviewer}/agent
mkdir -p ~/.openclaw/agents/{orchestrator,researcher,coder,reviewer}/sessions
```

### 5. Apply Configuration
```bash
# Copy your openclaw.json5 (from 08-CONFIGURATION-REFERENCE.md)
cp openclaw.json5 ~/.openclaw/openclaw.json5

# Validate
openclaw doctor
```

### 6. Install as Systemd Service
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
EnvironmentFile=/home/openclaw/.openclaw/.env
ExecStart=/usr/bin/openclaw gateway
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security hardening
NoNewPrivileges=true
ProtectSystem=strict
ReadWritePaths=/home/openclaw/.openclaw

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable openclaw
sudo systemctl start openclaw
```

### 7. Verify
```bash
# Check service status
sudo systemctl status openclaw

# Check gateway status
openclaw status

# Check Discord connection
openclaw channels status --probe

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
1. Deploy OpenClaw with just the orchestrator agent
2. Connect to Discord — verify bot responds in a test channel
3. Test basic Discord tool actions (create channel, send message)
4. Verify heartbeat is working
5. Confirm DM communication works

### Phase 2: Add Specialist Agents
1. Add researcher agent to config
2. Create workspace with SOUL.md and AGENTS.md
3. Test `sessions_spawn` from orchestrator → researcher
4. Verify isolated sessions and workspace separation
5. Repeat for coder and reviewer

### Phase 3: Discord Server Structure
1. Have orchestrator create the full channel/category structure agentically
2. Update config with actual channel IDs
3. Test per-channel routing and skill filtering
4. Verify `requireMention` works correctly in shared channels

### Phase 4: Agent-to-Agent Communication
1. Enable `agentToAgent` in config
2. Set `allowBots: true` in Discord config
3. Test orchestrator delegating to researcher in shared Discord channel
4. Verify loop prevention (requireMention + SOUL.md rules)
5. Test the full recursive feedback loop (research → code → review)

### Phase 5: Autonomous Operation
1. Configure heartbeat checklists for each agent
2. Set up cron jobs for scheduled tasks
3. Monitor for 24 hours with close oversight
4. Tune iteration limits and cost thresholds
5. Gradually reduce oversight as confidence builds

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
npm install -g openclaw@2026.2.16
```

## Monitoring Checklist

After deployment, regularly check:

- [ ] `openclaw status` — Gateway health
- [ ] `openclaw channels status --probe` — Discord connection
- [ ] `openclaw sessions list` — Active sessions (any stuck/errored?)
- [ ] `openclaw agents list` — All agents configured correctly
- [ ] Provider dashboards — API token usage and spend
- [ ] Discord #system-logs — Any errors or warnings
- [ ] `journalctl -u openclaw --since "1 hour ago"` — System logs
