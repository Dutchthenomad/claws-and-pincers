# OpenClaw Due Diligence Report

> **Repository**: https://github.com/openclaw/openclaw
> **Website**: https://openclaw.ai
> **Analyzed**: 2026-01-31
> **Status**: UNDER REVIEW

---

## Executive Summary

OpenClaw is a highly active, open-source personal AI assistant platform with **131,933 stars** and **19,073 forks**. It enables AI interactions through multiple messaging channels (WhatsApp, Telegram, Discord, Slack, Signal, iMessage, etc.) while running on user-controlled infrastructure.

| Metric | Value | Assessment |
|--------|-------|------------|
| Stars | 131,933 | Extremely High |
| Forks | 19,073 | Very Active |
| Contributors | 30 | Moderate team |
| Open Issues | 1,123 | Active development |
| Open PRs | 1,037 | High velocity |
| Last Commit | Today (2026-01-31) | Very Active |
| Latest Release | v2026.1.30 (Yesterday) | Current |
| License | MIT | Permissive |

---

## Technical Requirements

### System Requirements

| Requirement | OpenClaw Needs | This VPS Has | Compatible |
|-------------|----------------|--------------|------------|
| Node.js | >= 22.12.0 | v22.22.0 | YES |
| RAM | Not specified (est. 2-4GB) | 15GB (12GB free) | YES |
| Disk | Not specified | 122GB free | YES |
| CPU | Not specified | 4 cores | YES |
| Docker | Required (sandbox mode) | Installed | YES |

### Port Requirements

| Port | Service | Conflict Check |
|------|---------|----------------|
| 18789 | Gateway WebSocket | AVAILABLE |
| 18790 | Bridge | AVAILABLE |

### Dependencies

- **Runtime**: Node.js 22+ with pnpm
- **Primary Language**: TypeScript (16.4 MB)
- **AI Providers**: Anthropic (Claude), OpenAI
- **Required**: Docker for sandbox execution (autonomous mode)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenClaw Gateway                          │
│                   (ws://127.0.0.1:18789)                    │
├──────────────────┬──────────────────┬───────────────────────┤
│   Channels       │   Agent Runtime  │   Tool Ecosystem      │
│                  │                  │                       │
│ - WhatsApp       │ - Pi Agent       │ - Browser Automation  │
│ - Telegram       │ - RPC Mode       │ - Cron Jobs          │
│ - Discord        │ - Streaming      │ - Webhooks           │
│ - Slack          │                  │ - Skills Platform    │
│ - Signal         │                  │                       │
│ - iMessage       │                  │                       │
│ - Matrix         │                  │                       │
│ - Teams          │                  │                       │
└──────────────────┴──────────────────┴───────────────────────┘
```

---

## CRITICAL: Autonomous Operation Requirements

### Docker Sandbox Architecture for Full Autonomy

Since this deployment will experiment with **complete agent autonomy**, strict containerization is mandatory:

```
┌────────────────────────────────────────────────────────────────┐
│                     HOST (srv1216617)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Docker Network: openclaw-net                 │  │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐   │  │
│  │  │ openclaw-gateway│  │    Per-Session Sandboxes    │   │  │
│  │  │   (orchestrator)│  │  ┌───────┐ ┌───────┐       │   │  │
│  │  │                 │──│  │sandbox│ │sandbox│ ...   │   │  │
│  │  │ - State mgmt    │  │  │  -01  │ │  -02  │       │   │  │
│  │  │ - Channel routing│  │  └───────┘ └───────┘       │   │  │
│  │  │ - Tool dispatch │  │  (ephemeral, isolated)      │   │  │
│  │  └─────────────────┘  └─────────────────────────────┘   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                  │
│  ┌───────────────────────────┴──────────────────────────────┐  │
│  │              Shared Services (read-only access)           │  │
│  │   qdrant │ timescaledb │ rabbitmq │ rag-api │ n8n        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────┘
```

### Sandbox Security Controls

| Control | Configuration | Purpose |
|---------|--------------|---------|
| `--read-only` | Filesystem | Prevent persistent malicious writes |
| `--cap-drop=ALL` | Capabilities | Minimal Linux capabilities |
| `--network=openclaw-net` | Network | Isolated Docker network |
| `--memory=2g` | Resources | Prevent runaway memory |
| `--cpus=1` | Resources | Limit CPU consumption |
| `--pids-limit=100` | Processes | Prevent fork bombs |
| `--security-opt=no-new-privileges` | Security | Prevent privilege escalation |
| Volume mounts | Workspace | Only `/workspace` writable |

---

## Dedicated Profile Configuration Strategy

### Centralized Configuration Repository

Create a dedicated local configuration structure for all OpenClaw profiles, dependencies, and channel setups:

```
/opt/openclaw/
├── config/
│   ├── profiles/
│   │   ├── telegram/
│   │   │   ├── .env                    # Bot token, API credentials
│   │   │   ├── settings.yaml           # Channel-specific settings
│   │   │   └── allowed-users.txt       # Authorized user list
│   │   ├── whatsapp/
│   │   │   ├── .env                    # Twilio/native credentials
│   │   │   ├── settings.yaml
│   │   │   └── session-data/           # WhatsApp session persistence
│   │   ├── discord/
│   │   │   ├── .env                    # Bot token, guild IDs
│   │   │   ├── settings.yaml
│   │   │   └── slash-commands.yaml     # Custom commands
│   │   └── slack/
│   │       ├── .env                    # OAuth tokens
│   │       └── settings.yaml
│   │
│   ├── agents/
│   │   ├── default-agent.yaml          # Base agent configuration
│   │   ├── autonomous-agent.yaml       # Full autonomy settings
│   │   └── restricted-agent.yaml       # Limited permissions
│   │
│   ├── tools/
│   │   ├── enabled-tools.yaml          # Tool whitelist per profile
│   │   ├── tool-configs/
│   │   │   ├── browser.yaml            # Playwright/Puppeteer settings
│   │   │   ├── shell.yaml              # Allowed commands
│   │   │   └── filesystem.yaml         # Allowed paths
│   │   └── custom-tools/               # User-defined MCP tools
│   │
│   └── gateway.yaml                    # Main gateway configuration
│
├── runtime/
│   ├── node_modules/                   # Pinned dependencies
│   ├── package.json                    # Dependency manifest
│   ├── pnpm-lock.yaml                  # Lock file
│   └── .nvmrc                          # Node version lock
│
├── workspace/
│   ├── shared/                         # Cross-session shared data
│   ├── sessions/                       # Per-session workspaces
│   └── artifacts/                      # Generated outputs
│
├── skills/
│   ├── custom/                         # Custom skill definitions
│   ├── imported/                       # Skills from ClawHub
│   └── registry.yaml                   # Skill manifest
│
├── data/
│   ├── memory/                         # Persistent memory store
│   ├── conversations/                  # Conversation logs
│   └── metrics/                        # Usage analytics
│
├── secrets/
│   ├── .gitignore                      # Never commit secrets
│   ├── anthropic.env                   # Claude API keys
│   ├── openai.env                      # OpenAI keys (if used)
│   └── channel-secrets.env             # All channel credentials
│
├── docker/
│   ├── docker-compose.yml              # Main compose file
│   ├── docker-compose.sandbox.yml      # Sandbox overrides
│   ├── Dockerfile.gateway              # Custom gateway image
│   └── Dockerfile.sandbox              # Sandbox base image
│
├── scripts/
│   ├── setup.sh                        # Initial setup
│   ├── backup.sh                       # Backup script
│   ├── restore.sh                      # Restore script
│   └── health-check.sh                 # Health monitoring
│
└── README.md                           # Local documentation
```

### Profile Requirements by Channel

#### Telegram Profile
| Requirement | Details | Status |
|-------------|---------|--------|
| Bot Token | Create via @BotFather | NEEDED |
| API ID | From my.telegram.org | NEEDED |
| API Hash | From my.telegram.org | NEEDED |
| Webhook URL | Via Tailscale Funnel | CONFIGURE |
| Allowed Users | Whitelist Telegram IDs | DEFINE |

#### WhatsApp Profile
| Requirement | Details | Status |
|-------------|---------|--------|
| Twilio Account | For business API | OPTIONAL |
| Native Session | WhatsApp Web pairing | ALTERNATIVE |
| Phone Number | Dedicated number recommended | NEEDED |
| Session Backup | Persist auth state | CONFIGURE |

#### Discord Profile
| Requirement | Details | Status |
|-------------|---------|--------|
| Bot Token | Discord Developer Portal | NEEDED |
| Application ID | From developer portal | NEEDED |
| Guild IDs | Servers to join | DEFINE |
| Intents | Message content, etc. | CONFIGURE |
| Slash Commands | Optional custom commands | OPTIONAL |

#### Slack Profile
| Requirement | Details | Status |
|-------------|---------|--------|
| App Manifest | Slack app configuration | NEEDED |
| Bot Token | xoxb-* token | NEEDED |
| App Token | xapp-* for socket mode | NEEDED |
| Signing Secret | Request verification | NEEDED |

---

## Pre-Installation Checklist

### Phase 1: Security Hardening (Before OpenClaw)

- [ ] **CRITICAL**: Disable root SSH login or set to key-only
- [ ] Update kernel (6.8.0-90 → 6.8.0-94)
- [ ] Apply pending package updates (25 packages)
- [ ] Verify Tailscale is only access method for OpenClaw

### Phase 2: Infrastructure Setup

- [ ] Create `/opt/openclaw/` directory structure
- [ ] Initialize Git repository for config version control
- [ ] Create Docker network `openclaw-net`
- [ ] Configure Docker resource limits

### Phase 3: Dependency Installation

- [ ] Verify Node.js 22.22.0 compatibility
- [ ] Install pnpm globally
- [ ] Clone OpenClaw to `/opt/openclaw/runtime/`
- [ ] Pin to version v2026.1.30
- [ ] Run `pnpm install`

### Phase 4: Channel Profile Setup

- [ ] Create Telegram bot and obtain credentials
- [ ] Set up WhatsApp session method (Twilio or native)
- [ ] Create Discord bot application
- [ ] Configure Slack app (if needed)
- [ ] Populate secrets in `/opt/openclaw/secrets/`

### Phase 5: Gateway Configuration

- [ ] Configure gateway.yaml with sandbox mode enabled
- [ ] Set up tool restrictions for autonomous mode
- [ ] Configure memory and conversation logging
- [ ] Set up health check endpoints

### Phase 6: Integration Testing

- [ ] Test each channel individually
- [ ] Verify sandbox isolation
- [ ] Test tool execution limits
- [ ] Validate resource constraints
- [ ] Run autonomous behavior tests in isolated mode

---

## Security Assessment

### Strengths

1. **Active Security Focus**: Recent security fix (GHSA-4mhr-g7xj-cg8j) for arbitrary exec vulnerability
2. **Secret Detection**: Uses `detect-secrets` in CI/CD pipeline
3. **Sandbox Support**: Docker isolation for non-main sessions
4. **Access Control**: Approval codes required for unknown senders in DM mode
5. **Local-First Design**: Designed for loopback access, not public exposure

### Concerns for Autonomous Operation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Agent escapes sandbox | Low | Critical | Multi-layer isolation, seccomp profiles |
| Credential exfiltration | Medium | Critical | Secrets in read-only env vars only |
| Resource exhaustion | Medium | High | Hard container limits |
| Malicious tool execution | Medium | High | Tool whitelist, command filtering |
| Data leakage via channels | Low | Medium | Audit logging, rate limits |
| Prompt injection | Medium | Medium | Input sanitization, context isolation |

### Required Mitigations for Autonomous Mode

| Control | Implementation |
|---------|---------------|
| Network egress filtering | Docker network policies |
| Command allowlist | Shell tool configuration |
| Filesystem isolation | Read-only mounts + temp workspace |
| API rate limiting | Gateway-level throttling |
| Audit logging | All actions to TimescaleDB |
| Kill switch | Manual gateway shutdown endpoint |
| Session timeouts | Auto-terminate long-running sandboxes |

---

## Integration with Existing Services

### RAG Agent Integration

OpenClaw can leverage the local RAG system for knowledge retrieval:

```yaml
# Example tool configuration for RAG integration
tools:
  rag-query:
    endpoint: http://rag-api:8000/query
    description: "Query local knowledge base"
    parameters:
      query: string
      collection: string
      top_k: number
```

### Synergy Matrix

| Existing Service | OpenClaw Integration | Priority |
|------------------|---------------------|----------|
| RAG API (8000) | Knowledge retrieval tool | HIGH |
| n8n (5678) | Webhook automation | HIGH |
| Qdrant (6333) | Memory embeddings | MEDIUM |
| RabbitMQ (5672) | Async task queue | MEDIUM |
| TimescaleDB (5433) | Conversation/metrics logging | HIGH |

---

## Cost Analysis

| Component | Cost |
|-----------|------|
| OpenClaw Software | FREE (MIT License) |
| Claude API | Pay-per-use via Anthropic |
| Claude Pro/Max | $20-$200/month (recommended for autonomy) |
| Telegram Bot | FREE |
| WhatsApp (Twilio) | ~$0.005-0.05/message |
| WhatsApp (Native) | FREE (personal use) |
| Discord Bot | FREE |
| Slack App | FREE (under limits) |
| VPS Resources | Already provisioned |

---

## Knowledge Base Collections to Ingest

The following resources should be scraped and ingested into the local RAG system:

### Priority 1: Core Documentation
| Source | Type | Purpose |
|--------|------|---------|
| https://docs.openclaw.ai | Documentation | Full usage reference |
| https://github.com/openclaw/openclaw/tree/main/docs | Markdown | Technical deep-dive |
| https://openclaw.ai/blog | Blog | Updates, patterns, announcements |

### Priority 2: Security & Sandbox
| Source | Type | Purpose |
|--------|------|---------|
| OpenClaw security docs | Security | Sandbox configuration |
| Docker security best practices | Security | Container hardening |
| Seccomp/AppArmor profiles | Security | Process isolation |

### Priority 3: Channel APIs
| Source | Type | Purpose |
|--------|------|---------|
| Telegram Bot API | API Docs | Bot development |
| WhatsApp Business API | API Docs | Message handling |
| Discord Developer Docs | API Docs | Bot integration |
| Slack API | API Docs | App development |

### Priority 4: AI/Agent Development
| Source | Type | Purpose |
|--------|------|---------|
| Anthropic Claude Docs | API Docs | Model usage |
| Claude Code documentation | Tool Docs | Agent patterns |
| MCP Protocol Spec | Protocol | Tool development |
| https://clawhub.com | Skills | Pre-built capabilities |

### Priority 5: Supporting Technologies
| Source | Type | Purpose |
|--------|------|---------|
| Node.js 22 documentation | Runtime | Platform reference |
| pnpm documentation | Package Mgr | Dependency management |
| Tailscale documentation | VPN | Secure access |

---

## Next Steps

### Immediate Actions
1. Discuss and finalize channel priorities (which to set up first)
2. Decide on WhatsApp method (Twilio vs native)
3. Create required bot accounts (Telegram, Discord, Slack)
4. Address critical SSH security issue

### Discussion Points
- [ ] Which channels to enable initially?
- [ ] Autonomy guardrails - what actions should be blocked?
- [ ] Budget for Claude API usage?
- [ ] Backup strategy for conversation/memory data?
- [ ] Monitoring and alerting preferences?

---

*Report generated: 2026-01-31 | Next review: Before installation*
