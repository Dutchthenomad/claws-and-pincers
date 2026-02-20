# OpenClaw Discord Multi-Agent Swarm

Production-ready deployment of 5 specialized AI agents for Discord, following best practices for containerization, security, and monitoring.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Discord Server                                │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐              │
│  │Orchestrator │ │ Researcher  │ │  Developer  │              │
│  │    🎯       │ │    🔬       │ │    💻       │              │
│  └─────────────┘ └─────────────┘ └─────────────┘              │
│  ┌─────────────┐ ┌─────────────┐                               │
│  │  Sysadmin   │ │  Reviewer   │                               │
│  │    🖥️       │ │    🔍       │                               │
│  └─────────────┘ └─────────────┘                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   Docker Network   │
                    │  openclaw-agents   │
                    └─────────┬─────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────▼────┐         ┌────▼────┐         ┌────▼────┐
    │  Redis  │         │Watchtower│        │  Logs   │
    │  Cache  │         │Auto-update│        │Central  │
    └─────────┘         └─────────┘         └─────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Discord bot tokens (5 bots)

### 1. Setup Environment

```bash
cd /opt/openclaw/discord-agents

# Copy template and fill in your tokens
cp .env.template .env

# Edit .env with your actual Discord bot tokens
nano .env
```

### 2. Deploy

```bash
# Using the deploy script
./deploy-agents.sh start

# Or using Make
make start

# Or using docker-compose directly
docker-compose -f docker-compose.agents.yml --env-file .env up -d
```

### 3. Verify

```bash
# Check status
./deploy-agents.sh status
make status

# Health check
./deploy-agents.sh health
make health

# View logs
./deploy-agents.sh logs
make logs
```

## 🎭 Agent Capabilities

| Agent | Emoji | Model | Sandbox | Key Capabilities |
|-------|-------|-------|---------|------------------|
| **Orchestrator** | 🎯 | Claude Opus | Off | Full access, coordination, spawning |
| **Researcher** | 🔬 | Claude Sonnet | On | Web search, browser, read-only exec |
| **Developer** | 💻 | Claude Sonnet | On | Code editing, patching, file ops |
| **Sysadmin** | 🖥️ | Claude Sonnet | On | System monitoring, Docker, infra |
| **Reviewer** | 🔍 | Claude Sonnet | On | Read-only, audit, code review |

## 📁 File Structure

```
/opt/openclaw/discord-agents/
├── docker-compose.agents.yml    # Main compose file
├── deploy-agents.sh             # Deployment script
├── .env                         # Secrets (gitignored)
├── .env.template                # Template for .env
├── Makefile                     # Quick commands
└── README.md                    # This file
```

## 🔒 Security

- **Token isolation**: Each bot has its own token, no sharing
- **Container isolation**: Each agent runs in its own container
- **Read-only mounts**: Secrets mounted read-only
- **Resource limits**: CPU/memory limits per agent
- **Sandbox modes**: Appropriate sandboxing per agent role
- **Network isolation**: Dedicated Docker network
- **Health checks**: Automatic restart on failure
- **Auto-updates**: Watchtower keeps images current

## 📝 Commands

### Deploy Script
```bash
./deploy-agents.sh start      # Start all agents
./deploy-agents.sh stop       # Stop all agents
./deploy-agents.sh restart    # Restart all agents
./deploy-agents.sh status     # Show container status
./deploy-agents.sh logs       # Follow logs
./deploy-agents.sh health     # Health check
```

### Make Commands
```bash
make start       # Start all agents
make stop        # Stop all agents
make restart     # Restart all agents
make status      # Show status
make logs        # View logs
make health      # Health check
make clean       # Remove all containers and volumes
```

### Docker Compose
```bash
docker-compose -f docker-compose.agents.yml up -d      # Start
docker-compose -f docker-compose.agents.yml down       # Stop
docker-compose -f docker-compose.agents.yml ps         # Status
docker-compose -f docker-compose.agents.yml logs -f    # Logs
```

## 🌐 Access Points

Each agent exposes its API on a different port:

| Agent | Port | Health Endpoint |
|-------|------|-----------------|
| Orchestrator | 8081 | http://localhost:8081/health |
| Researcher | 8082 | http://localhost:8082/health |
| Developer | 8083 | http://localhost:8083/health |
| Sysadmin | 8084 | http://localhost:8084/health |
| Reviewer | 8085 | http://localhost:8085/health |

## 🔧 Troubleshooting

### Agents won't start
```bash
# Check logs
docker-compose -f docker-compose.agents.yml logs orchestrator

# Verify tokens are set
grep DISCORD .env | head -1

# Check Docker is running
docker ps
```

### Discord connection issues
- Verify bot tokens are valid
- Ensure bots are invited to your Discord server
- Check bot permissions (should have Send Messages, Read History, etc.)

### High memory usage
```bash
# Check resource usage
docker stats

# Restart specific agent
docker-compose -f docker-compose.agents.yml restart researcher
```

## 📊 Monitoring

### Health Dashboard
Access agent health at:
- http://your-server:8081/health (Orchestrator)
- http://your-server:8082/health (Researcher)
- etc.

### Logs
```bash
# All agents
docker-compose -f docker-compose.agents.yml logs -f

# Specific agent
docker-compose -f docker-compose.agents.yml logs -f researcher
```

### Resource Usage
```bash
docker stats
```

## 🔄 Updates

Watchtower automatically checks for updates every hour. To manually update:

```bash
docker-compose -f docker-compose.agents.yml pull
docker-compose -f docker-compose.agents.yml up -d
```

## 🗑️ Cleanup

```bash
# Stop and remove containers
make clean

# Or manually
docker-compose -f docker-compose.agents.yml down -v
```

## 📚 References

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [Discord Developer Portal](https://discord.com/developers/applications)
- [Docker Compose Docs](https://docs.docker.com/compose/)

## 🤝 Agent Communication

Agents can communicate with each other via:
1. **Discord channels** - Mention @AgentName
2. **Shared Redis** - State synchronization
3. **API calls** - Direct HTTP to other agents' ports

## ⚠️ Important Notes

- **Never commit `.env`** - It contains secrets
- **Backup your data volumes** - Agent data persists in Docker volumes
- **Monitor costs** - Each agent makes API calls that incur costs
- **Resource limits** are set but adjust based on your workload
