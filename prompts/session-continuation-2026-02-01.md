# OpenClaw Continuation Session Prompt

> **Created**: 2026-02-01
> **Purpose**: Continue OpenClaw setup - remaining tasks after initial installation

---

## Context

OpenClaw gateway is **live and operational** on the VPS. The Telegram bot (@dutch_claws_bot) is responding to messages. This session should complete the remaining setup tasks.

### What's Already Done

| Component | Status | Location |
|-----------|--------|----------|
| OpenClaw Runtime | ✅ v2026.1.30 | `/opt/openclaw/runtime/` |
| Gateway Service | ✅ systemd | `systemctl status openclaw` |
| Telegram Bot | ✅ Active | @dutch_claws_bot (ID: 8503309726) |
| Main Config | ✅ | `/root/.openclaw/openclaw.json` |
| Environment | ✅ | `/root/.openclaw/.env` |
| Secrets | ✅ | `/opt/openclaw/secrets/` |
| Docker Network | ✅ | `openclaw-net` |
| IPv6 Fix | ✅ | `/etc/hosts` (149.154.166.110 api.telegram.org) |
| RAG System | ✅ | 3,623 vectors indexed |

### Key Files & Access

```bash
# VPS Access
ssh vps

# Local Repository
cd /home/devops/Desktop/CLAWED/claws-and-pincers

# Local Telegram CLI (for debugging)
/snap/bin/telegram-cli

# Key Documentation
research/openclaw-setup-plan.md
research/openclaw-authorization-architecture.md
config/profiles/telegram/settings.yaml
```

---

## Remaining Tasks

### Task 1: Voice 2FA Enrollment (Priority: HIGH)

**Goal**: Enroll voiceprint for Tier 3 authorization (financial transactions, root commands)

**Current State**:
- Voice 2FA configured in settings but enrollment_status: pending
- SpeechBrain ECAPA-TDNN model specified (0.25 threshold)
- Fallback PIN already generated and stored

**Steps**:
1. Check if OpenClaw has voice enrollment command/flow
2. Send 3 voice messages to bot saying enrollment phrases:
   - "authorize this action"
   - "confirm the request"
   - "approve the transaction"
3. Verify enrollment completes and status changes to 'enrolled'
4. Test voice verification with a Tier 3 action

**Reference**: `research/openclaw-authorization-architecture.md` (2FA Implementation section)

---

### Task 2: RunPod Endpoint Deployment (Priority: MEDIUM)

**Goal**: Deploy ablated/uncensored LLM models for research tasks

**Current State**:
- RunPod account: NOT CREATED
- RunPod API key: NOT STORED
- Endpoints: NOT DEPLOYED

**Planned Models**:
| Model | Purpose | GPU |
|-------|---------|-----|
| dolphin-llama3.1-70b | Deep research, uncensored | A100 80GB |
| dolphin-llama3.1-8b | Quick queries, drafts | A10 24GB |
| deepseek-coder-v2-lite | Code generation | A40 48GB |

**Steps**:
1. Create RunPod account at https://runpod.io
2. Add payment method
3. Generate API key
4. Store key: `/opt/openclaw/secrets/runpod.env`
5. Deploy serverless endpoints (vLLM worker template)
6. Configure model router in OpenClaw
7. Test routing with sample queries

**Reference**: `research/openclaw-setup-plan.md` (Phase 7: RunPod LLM Integration)

---

### Task 3: Privacy.com Card Setup (Priority: LOW)

**Goal**: Virtual card for agent-controlled online purchases

**Current State**:
- Account: NOT CREATED
- Card limits: $100/transaction, $500/monthly (planned)

**Steps**:
1. Create Privacy.com account (free tier)
2. Generate virtual card
3. Set merchant locks (digital_goods, software only)
4. Block categories (gambling, crypto_exchange, wire_transfer)
5. Store card details securely (Tier 2 access)
6. Configure transaction notifications → Telegram

**Reference**: `research/openclaw-burner-card-comparison.md`

---

### Task 4: Base Wallet Funding (Priority: LOW)

**Goal**: Fund hot wallet for small autonomous transactions

**Current State**:
- Wallet CREATED (address exists)
- Private key stored in `/opt/openclaw/secrets/wallet.env`
- Balance: $0 (FUNDING PENDING)

**Planned Limits**:
- Max balance: $500 USDC
- Per transaction: $50
- Daily limit: $200

**Steps**:
1. Get wallet address from VPS secrets
2. Fund with small amount of ETH (gas) + USDC on Base network
3. Verify balance via RPC
4. Test small transaction (Tier 2 approval flow)

**Reference**: `research/openclaw-setup-plan.md` (Phase 4: Crypto Wallet Setup)

---

### Task 5: System Packages Update (Priority: LOW)

**Goal**: Update 25 pending packages on VPS

**Current State**:
- 25 packages pending update
- Kernel update requires reboot
- OpenClaw service set to auto-restart

**Steps**:
1. Check current pending updates: `ssh vps "apt list --upgradable"`
2. Schedule maintenance window
3. Run update: `ssh vps "apt update && apt upgrade -y"`
4. Reboot if kernel updated: `ssh vps "reboot"`
5. Verify all services come back online
6. Check OpenClaw gateway status

**Caution**: Reboot will cause brief downtime. Telegram bot will be offline during restart.

---

## MCP Tools Available

Use the rugs-expert MCP server for VPS operations:
- `mcp__rugs-expert__get_system_info` - VPS health
- `mcp__rugs-expert__get_docker_status` - Container status
- `mcp__rugs-expert__search_rugs_knowledge` - Query RAG knowledge base
- `mcp__rugs-expert__ingest_knowledge` - Add new knowledge

---

## Verification Commands

```bash
# Check OpenClaw status
ssh vps "systemctl status openclaw --no-pager"

# View live gateway logs
ssh vps "journalctl -u openclaw -f"

# Check Docker containers
ssh vps "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Test Telegram API connectivity
ssh vps "source /root/.openclaw/.env && curl -s 'https://api.telegram.org/bot\${TELEGRAM_BOT_TOKEN}/getMe' | jq .ok"

# Check wallet address
ssh vps "grep ADDRESS /opt/openclaw/secrets/wallet.env"
```

---

## Session Goals

By the end of this session:
1. [ ] Voice 2FA enrolled and tested
2. [ ] RunPod account created with at least one endpoint
3. [ ] (Optional) Privacy.com card configured
4. [ ] (Optional) Wallet funded with small amount
5. [ ] (Optional) System packages updated

**Priority Order**: Voice 2FA → RunPod → Others (as time permits)

---

## Notes

- The user has Telegram open on mobile for testing
- Local telegram-cli available at `/snap/bin/telegram-cli`
- VPS has IPv6 issues - always use `-4` flag or rely on hosts file fix
- OpenClaw config uses JSON5 format (comments allowed)
- Gateway binds to loopback only (127.0.0.1:18789) for security

---

*Continuation prompt created: 2026-02-01*
