# OpenClaw Setup Plan

> **Decisions Finalized**: 2026-01-31
> **Status**: ✅ INSTALLED & OPERATIONAL (2026-02-01)

---

## 🎉 Installation Complete

OpenClaw gateway is **live and operational** on the VPS as of 2026-02-01.

| Component | Status | Details |
|-----------|--------|---------|
| OpenClaw Runtime | ✅ | v2026.1.30 @ `/opt/openclaw/runtime` |
| pnpm | ✅ | v10.28.2 globally installed |
| systemd Service | ✅ | `openclaw.service` (auto-restart) |
| Telegram Bot | ✅ | @dutch_claws_bot (ID: 8503309726) |
| Gateway API | ✅ | `127.0.0.1:18789` (loopback only) |
| Anthropic API | ✅ | New key deployed |

### Critical IPv6 Fix

The VPS had 100% packet loss on IPv6. Telegram API was failing until we forced IPv4:

```bash
# Added to /etc/hosts on VPS
149.154.166.110 api.telegram.org
```

**Symptom**: `TypeError: fetch failed`, `Network request for 'getUpdates' failed!`
**Root cause**: VPS resolved to IPv6 (2001:67c:4e8:f004::9) with no connectivity
**Fix**: Force IPv4 via hosts file entry

---

## Configuration Summary

| Component | Choice |
|-----------|--------|
| **Telegram** | New bot on existing account via @BotFather |
| **2FA Method** | Voice message + voiceprint analysis |
| **Crypto Wallet** | USDC on Base network |
| **Spending Card** | Privacy.com (Free tier) |
| **RunPod LLMs** | Ablated models for maximum truthfulness |
| **Deployment** | Docker sandbox with tiered authorization |

---

## Phase 1: Prerequisites

### 1.1 Security Hardening (CRITICAL - Do First)

```bash
# Disable root password login, allow key-only
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
sudo systemctl restart sshd

# Verify change
grep PermitRootLogin /etc/ssh/sshd_config
```

### 1.2 System Updates

```bash
sudo apt update && sudo apt upgrade -y
# Note: Kernel update requires reboot - schedule maintenance window
```

### 1.3 Create Directory Structure

```bash
sudo mkdir -p /opt/openclaw/{config/{profiles/telegram,agents,tools/tool-configs,tools/custom-tools},runtime,workspace/{shared,sessions,artifacts},skills/{custom,imported},data/{memory,conversations,metrics,audit,authorization-queue/pending,authorization-queue/completed},secrets,docker,scripts}

sudo chown -R $USER:$USER /opt/openclaw
chmod 700 /opt/openclaw/secrets
```

---

## Phase 2: Telegram Bot Setup

### 2.1 Create Bot via @BotFather

1. Open Telegram, search for `@BotFather`
2. Send `/newbot`
3. Choose a name: `OpenClaw Assistant` (display name)
4. Choose a username: `your_openclaw_bot` (must end in `bot`)
5. **Save the token** - looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2.2 Configure Bot Settings (in @BotFather)

```
/setdescription - "Personal AI assistant with autonomous capabilities"
/setabouttext - "Powered by Claude. Owned by @yourusername"
/setuserpic - Upload an avatar
/setcommands - Set these commands:
```

Paste this command list:
```
status - Show pending authorization requests
approve - Approve a pending request
deny - Deny a request
authorize - Start 2FA for sensitive actions
limits - Show spending limits
pause - Pause autonomous operation
resume - Resume autonomous operation
audit - Show recent actions
emergency - Kill all agent processes
help - Show available commands
```

### 2.3 Get Your Chat ID

1. Send a message to your new bot
2. Visit: `https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates`
3. Find `"chat":{"id":123456789}` - that's your chat ID
4. This ensures only YOU can control the bot

### 2.4 Store Credentials

```bash
# Create telegram profile config
cat > /opt/openclaw/config/profiles/telegram/settings.yaml << 'EOF'
channel: telegram
enabled: true
mode: private  # Only owner can interact

bot:
  username: "your_openclaw_bot"  # Replace with actual

access:
  owner_chat_id: 0  # Replace with your chat ID
  allowed_users: []  # Add additional trusted user IDs if needed

notifications:
  tier1_actions: false  # Don't notify for routine actions
  tier2_requests: true  # Notify for approval requests
  tier3_requests: true  # Notify for 2FA requests
  daily_digest: true
  digest_time: "09:00"  # UTC

authorization:
  timeout_hours: 4  # Auto-deny after 4 hours
  max_pending: 10   # Max queued requests
EOF

# Store token securely
cat > /opt/openclaw/secrets/telegram-bot.env << 'EOF'
TELEGRAM_BOT_TOKEN=your_token_here
TELEGRAM_OWNER_CHAT_ID=your_chat_id_here
EOF

chmod 600 /opt/openclaw/secrets/telegram-bot.env
```

---

## Phase 3: Voice Authentication Setup

### 3.1 Voiceprint Enrollment

The bot will need voice samples to create your voiceprint:

```yaml
# /opt/openclaw/config/profiles/telegram/voiceprint.yaml
voiceprint:
  enabled: true
  enrollment_status: pending  # Will change to 'enrolled' after setup

  enrollment:
    required_samples: 3
    phrases:
      - "authorize this action"
      - "confirm the request"
      - "approve the transaction"

  verification:
    confidence_threshold: 0.85  # 85% match required
    max_duration_seconds: 10
    fallback_to_pin: true  # If voice fails, allow PIN

  anti_spoofing:
    liveness_detection: true
    reject_recordings: true
```

### 3.2 Fallback PIN Setup

```bash
# Generate a random 6-digit PIN (you'll change this)
PIN=$(shuf -i 100000-999999 -n 1)
echo "Your fallback PIN: $PIN"
echo "OPENCLAW_FALLBACK_PIN_HASH=$(echo -n $PIN | sha256sum | cut -d' ' -f1)" >> /opt/openclaw/secrets/telegram-bot.env
```

---

## Phase 4: Crypto Wallet Setup (USDC on Base)

### 4.1 Create Hot Wallet

**Option A: Use existing wallet software**
- Rabby, MetaMask, or Rainbow
- Create a NEW wallet specifically for the agent
- Add Base network if not present
- Fund with small amount of ETH (for gas) + USDC

**Option B: Generate via command line**
```bash
# Install ethers for wallet generation (one-time)
npm install -g ethers

# Generate wallet (SAVE THIS SECURELY)
node -e "const w = require('ethers').Wallet.createRandom(); console.log('Address:', w.address); console.log('Private Key:', w.privateKey); console.log('Mnemonic:', w.mnemonic.phrase)"
```

### 4.2 Wallet Configuration

```yaml
# /opt/openclaw/config/tools/wallet.yaml
wallet:
  network: base
  chain_id: 8453
  rpc_url: "https://mainnet.base.org"

  hot_wallet:
    address: "0x..."  # Your hot wallet address
    # Private key stored separately in secrets

  tokens:
    usdc:
      address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"  # USDC on Base
      decimals: 6

  limits:
    per_transaction_usdc: 50
    daily_usdc: 200
    max_balance_usdc: 500

  gas:
    max_gas_price_gwei: 1  # Base is cheap
    eth_reserve: 0.01  # Keep for gas
```

### 4.3 Store Wallet Key Securely

```bash
# This should ideally be in an encrypted vault
cat > /opt/openclaw/secrets/wallet.env << 'EOF'
OPENCLAW_WALLET_PRIVATE_KEY=0x...your_private_key...
EOF

chmod 600 /opt/openclaw/secrets/wallet.env
```

**CRITICAL**: The private key should eventually be moved to an encrypted vault that requires 2FA to access. For initial setup, this works but isn't the final security posture.

---

## Phase 5: Docker Sandbox Setup

### 5.1 Create Docker Network

```bash
docker network create openclaw-net
```

### 5.2 Docker Compose Configuration

```yaml
# /opt/openclaw/docker/docker-compose.yml
version: '3.8'

services:
  openclaw-gateway:
    image: openclaw:v2026.1.30
    container_name: openclaw-gateway
    restart: unless-stopped
    networks:
      - openclaw-net
      - default  # Access to existing services
    ports:
      - "127.0.0.1:18789:18789"  # Loopback only
    volumes:
      - /opt/openclaw/config:/home/node/.openclaw/config:ro
      - /opt/openclaw/workspace:/home/node/.openclaw/workspace
      - /opt/openclaw/data:/home/node/.openclaw/data
      - /opt/openclaw/skills:/home/node/.openclaw/skills:ro
      - /opt/openclaw/secrets:/run/secrets:ro
    environment:
      - NODE_ENV=production
      - OPENCLAW_SANDBOX_MODE=true
      - OPENCLAW_GATEWAY_BIND=0.0.0.0
      - OPENCLAW_GATEWAY_PORT=18789
    env_file:
      - /opt/openclaw/secrets/telegram-bot.env
      - /opt/openclaw/secrets/anthropic-api.env
    deploy:
      resources:
        limits:
          memory: 4G
          cpus: '2'
    security_opt:
      - no-new-privileges:true
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

  openclaw-sandbox:
    image: openclaw:v2026.1.30-sandbox
    container_name: openclaw-sandbox-template
    profiles: ["sandbox"]  # Not started by default
    networks:
      - openclaw-net
    read_only: true
    tmpfs:
      - /tmp:size=512M
      - /home/node/.openclaw/workspace:size=1G
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1'
          pids: 100
    security_opt:
      - no-new-privileges:true
      - seccomp:unconfined  # Will add custom profile later
    cap_drop:
      - ALL

networks:
  openclaw-net:
    external: true
  default:
    external: true
    name: bridge
```

### 5.3 Anthropic API Key

```bash
cat > /opt/openclaw/secrets/anthropic-api.env << 'EOF'
ANTHROPIC_API_KEY=sk-ant-...your_key_here...
EOF

chmod 600 /opt/openclaw/secrets/anthropic-api.env
```

---

## Phase 6: Authorization System

### 6.1 Tier Configuration

```yaml
# /opt/openclaw/config/agents/autonomous-agent.yaml
agent:
  name: "OpenClaw Autonomous"
  model: "claude-opus-4-5-20251101"

authorization:
  default_tier: 0

  tier_0:  # Unrestricted
    - "research"
    - "web_browse"
    - "file_read"
    - "file_write:/workspace/**"
    - "code_execute:sandbox"
    - "rag_query"
    - "memory_*"
    - "message_respond"

  tier_1:  # Notify only
    - "api_call:read_only"
    - "email_draft"
    - "git_local"
    - "schedule_create"
    - "webhook_register"

  tier_2:  # Telegram approval
    - "email_send"
    - "social_post"
    - "account_create"
    - "git_push"
    - "package_install"
    - "secret_access"
    - "wallet_transaction:<50"
    - "card_transaction:<100"

  tier_3:  # 2FA required
    - "wallet_transaction:>=50"
    - "card_transaction:>=100"
    - "root_command"
    - "secret_rotate"
    - "backup_restore"
    - "container_*"
    - "firewall_*"
    - "user_permission"

  tier_4:  # Hardcoded deny
    - "rm:/etc/**"
    - "rm:/opt/**"
    - "rm:/var/**"
    - "systemctl:stop:fail2ban"
    - "systemctl:stop:ufw"
    - "ufw:disable"
    - "secret_expose_public"
    - "config_modify:authorization"
    - "logging_disable"
    - "ssh_key_*"
```

### 6.2 Integration with Existing Services

```yaml
# /opt/openclaw/config/tools/integrations.yaml
integrations:
  rag_api:
    enabled: true
    endpoint: "http://rag-api:8000"
    tier: 0

  n8n:
    enabled: true
    endpoint: "http://n8n:5678"
    webhook_path: "/webhook/openclaw"
    tier: 1  # Notify when creating workflows

  qdrant:
    enabled: true
    endpoint: "http://qdrant:6333"
    collection: "openclaw_memory"
    tier: 0

  timescaledb:
    enabled: true
    host: "timescaledb"
    port: 5432
    database: "openclaw"
    tier: 0  # For logging only

  rabbitmq:
    enabled: true
    endpoint: "amqp://rabbitmq:5672"
    tier: 1
```

---

## Phase 7: RunPod LLM Integration

### 7.1 Purpose

Deploy ablated/uncensored LLM models on RunPod to complement Claude:
- **Maximize epistemic access** - Remove overly cautious guardrails that obscure truth
- **Research integrity** - Ensure scientific method isn't compromised by model censorship
- **Proactive identification** - Discover potential fraud/abuse vectors before bad actors
- **Cost optimization** - Use cheaper models for routine tasks, reserve Claude for complex work

### 7.2 Model Selection Strategy

```yaml
# /opt/openclaw/config/tools/runpod-models.yaml
runpod:
  enabled: true
  api_key_env: "RUNPOD_API_KEY"

  endpoints:
    primary_uncensored:
      name: "dolphin-llama3.1-70b"
      endpoint_id: "to_be_configured"
      purpose: "Deep research, uncensored analysis"
      vram_required: "80GB (A100/H100)"

    fast_uncensored:
      name: "dolphin-llama3.1-8b"
      endpoint_id: "to_be_configured"
      purpose: "Quick queries, drafts"
      vram_required: "24GB (A10/L4)"

    code_specialist:
      name: "deepseek-coder-v2-lite"
      endpoint_id: "to_be_configured"
      purpose: "Code generation, debugging"
      vram_required: "48GB (A40/A100)"

  routing:
    default: "claude-opus-4-5"  # Primary model
    uncensored_research: "dolphin-llama3.1-70b"
    fast_draft: "dolphin-llama3.1-8b"
    code_tasks: "deepseek-coder-v2-lite"

  fallback_chain:
    - "claude-opus-4-5"      # Best quality
    - "dolphin-llama3.1-70b" # Uncensored fallback
    - "dolphin-llama3.1-8b"  # Fast fallback
```

### 7.3 RunPod Setup Steps

1. **Create RunPod Account**: https://runpod.io
2. **Add API Key**:
   ```bash
   cat >> /opt/openclaw/secrets/runpod.env << 'EOF'
   RUNPOD_API_KEY=your_api_key_here
   EOF
   chmod 600 /opt/openclaw/secrets/runpod.env
   ```

3. **Deploy Serverless Endpoints**:
   - Go to Serverless → New Endpoint
   - Select vLLM worker template
   - Configure model (e.g., `cognitivecomputations/dolphin-2.9.2-llama3.1-70b`)
   - Set min/max workers (0/3 for cost optimization)
   - Note endpoint ID

4. **Configure Auto-Scaling**:
   ```yaml
   scaling:
     min_workers: 0          # Scale to zero when idle
     max_workers: 3          # Handle bursts
     idle_timeout: 300       # 5 min before scale down
     queue_delay: 30         # Max queue time before scale up
   ```

### 7.4 Model Router Configuration

```yaml
# /opt/openclaw/config/agents/model-router.yaml
model_router:
  enabled: true

  rules:
    # Use uncensored for specific research topics
    - pattern: "research|investigate|analyze|deep dive"
      context_keywords: ["security", "vulnerability", "exploit", "fraud", "abuse"]
      route_to: "dolphin-llama3.1-70b"
      reason: "Uncensored analysis for security research"

    # Use Claude for general assistant tasks
    - pattern: "*"
      context_keywords: []
      route_to: "claude-opus-4-5"
      reason: "Default high-quality responses"

    # Use fast model for drafts and iteration
    - pattern: "draft|quick|outline|summarize"
      route_to: "dolphin-llama3.1-8b"
      reason: "Fast iteration, not final output"

    # Use code model for programming
    - pattern: "code|implement|debug|refactor"
      route_to: "deepseek-coder-v2-lite"
      reason: "Specialized code model"

  cost_tracking:
    enabled: true
    log_to: "timescaledb"
    alert_threshold_daily: 50  # USD
```

### 7.5 Authorization for Model Selection

```yaml
# Model selection permissions
model_authorization:
  tier_0:  # Agent can freely choose
    - "claude-*"
    - "dolphin-*-8b"
    - "deepseek-coder-*"

  tier_1:  # Notify when using (cost tracking)
    - "dolphin-*-70b"
    - "*-120b"

  tier_3:  # Require approval (expensive models)
    - "*-405b"
    - "claude-opus-*"  # If on pay-per-use
```

### 7.6 RunPod Cost Optimization

| Model | GPU | $/hr (active) | $/hr (idle) | Strategy |
|-------|-----|---------------|-------------|----------|
| dolphin-70b | A100 80GB | ~$1.50 | $0 | Scale to zero |
| dolphin-8b | A10 24GB | ~$0.30 | $0 | Scale to zero |
| deepseek-coder | A40 48GB | ~$0.70 | $0 | Scale to zero |

**Estimated Monthly Cost** (moderate use):
- 20 hrs/month active: ~$30-50
- All idle otherwise: $0

---

## Phase 8: Final Checklist

### Pre-Launch

- [x] SSH security hardened (root login key-only) ✅ DONE 2026-01-31
- [ ] System packages updated (25 pending - requires reboot)
- [x] Directory structure created ✅ DONE 2026-02-01
- [x] Telegram bot created and configured ✅ DONE 2026-02-01 (@dutch_claws_bot)
- [x] Bot token and chat ID stored ✅ DONE 2026-02-01 (/opt/openclaw/secrets/)
- [x] Voiceprint enrollment phrases prepared ✅ DONE 2026-02-01
- [x] Fallback PIN generated and stored ✅ DONE 2026-02-01
- [ ] Base wallet created and funded (small amount) - CREATED, FUNDING PENDING
- [x] Wallet private key secured ✅ DONE 2026-02-01
- [x] Anthropic API key stored ✅ DONE 2026-02-01 (new key)
- [ ] Privacy.com account created (free tier)
- [ ] RunPod account created
- [ ] RunPod API key stored
- [ ] At least one RunPod endpoint deployed
- [x] Docker network created ✅ DONE 2026-01-31 (openclaw-net)
- [x] Docker compose file configured ✅ Running via systemd instead
- [x] Authorization tiers configured ✅ DONE 2026-02-01 (5-tier in config)
- [x] Integration configs set up ✅ DONE 2026-02-01
- [ ] Model router configured (pending RunPod)

### Post-Launch Testing

- [x] Bot responds to messages ✅ CONFIRMED 2026-02-01 (mobile Telegram chat working)
- [ ] Tier 0 actions work without approval
- [ ] Tier 2 actions trigger Telegram approval
- [ ] Tier 3 actions require voice message
- [ ] Voiceprint enrollment completes
- [ ] Wallet can send small test transaction
- [ ] Privacy.com card works for test transaction
- [ ] RAG API integration works
- [ ] RunPod model routing works
- [ ] Fallback chain functions correctly
- [ ] Audit logs being written
- [ ] Emergency stop works

---

## Knowledge Base Ingestion Priority

Based on this setup, prioritize these for RAG ingestion:

| Priority | Source | Reason |
|----------|--------|--------|
| 1 | OpenClaw docs (gateway, telegram, tools) | Core functionality |
| 2 | RunPod serverless documentation | LLM deployment |
| 3 | vLLM documentation | Model inference |
| 4 | Ablated model information | Uncensored capabilities |
| 5 | Base network documentation | Crypto transactions |
| 6 | Telegram Bot API | Channel operations |
| 7 | Anthropic Claude API | Model interactions |
| 8 | Privacy.com documentation | Card management |
| 9 | Docker security best practices | Sandbox hardening |

See `/opt/sysadmin-ai/research/openclaw-rag-knowledge-plan.md` for comprehensive RAG collection plan.

---

## Estimated Resource Usage

### VPS Resources (Local)

| Service | Memory | CPU | Disk |
|---------|--------|-----|------|
| openclaw-gateway | 2-4 GB | 1-2 cores | 2 GB |
| openclaw-sandbox (per) | 1-2 GB | 0.5-1 core | 1 GB |
| Voice processing | 512 MB | 0.5 core | 100 MB |
| **Total New** | ~4-6 GB | ~2-3 cores | ~3 GB |
| **Currently Used** | 3.4 GB | - | 72 GB |
| **Available** | 12 GB | 4 cores | 122 GB |
| **Status** | ✅ OK | ✅ OK | ✅ OK |

### External Costs (Monthly Estimates)

| Service | Cost | Notes |
|---------|------|-------|
| Claude API | Variable | Depends on usage, ~$20-100/mo |
| RunPod (serverless) | ~$30-50 | Scale to zero when idle |
| Privacy.com | $0-5 | Free tier or Plus |
| Base gas fees | <$1 | Very cheap L2 |
| **Total External** | ~$50-150/mo | Conservative estimate |

---

## Related Documents

| Document | Purpose |
|----------|---------|
| `openclaw-due-diligence.md` | Project evaluation and risk assessment |
| `openclaw-authorization-architecture.md` | Tiered autonomy and 2FA design |
| `openclaw-rag-knowledge-plan.md` | RAG ingestion strategy and sources |
| `openclaw-burner-card-comparison.md` | Virtual card provider analysis |

---

*Setup plan finalized: 2026-01-31 | SSH hardened: 2026-01-31 23:38 UTC*
*Phase 1-4 completed: 2026-02-01 | Wallet funding pending*
*Phase 5 completed: 2026-02-01 | Docker infrastructure ready*

---

## Appendix: Production Configuration (2026-02-01)

### VPS File Locations

| Purpose | Path |
|---------|------|
| OpenClaw Runtime | `/opt/openclaw/runtime/` |
| Main Config | `/root/.openclaw/openclaw.json` |
| Environment | `/root/.openclaw/.env` |
| Secrets | `/opt/openclaw/secrets/` |
| Logs | `/opt/openclaw/data/logs/gateway.log` |
| systemd Service | `/etc/systemd/system/openclaw.service` |
| IPv6 Fix | `/etc/hosts` (api.telegram.org → 149.154.166.110) |

### Key Commands

```bash
# Check gateway status
systemctl status openclaw

# View live logs
journalctl -u openclaw -f

# Restart gateway
systemctl restart openclaw

# Test Telegram connectivity
curl -4 "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getMe"
```

### Local Development Tools

| Tool | Path |
|------|------|
| Telegram CLI | `/snap/bin/telegram-cli` |
| VPS SSH | `ssh vps` (via ~/.ssh/config) |

### Configuration JSON5 Structure

```json5
// /root/.openclaw/openclaw.json (simplified)
{
  anthropicApiKey: "${ANTHROPIC_API_KEY}",
  telegram: { botToken: "${TELEGRAM_BOT_TOKEN}", ... },
  agents: { list: [{ identity: {...}, ... }] },
  gateway: { bind: "127.0.0.1", port: 18789 },
  sandbox: { enabled: true, docker: {...} }
}
```

*Installation completed: 2026-02-01 | Gateway operational | Telegram bot active*
