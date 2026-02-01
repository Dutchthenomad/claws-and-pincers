# Claws and Pincers

> OpenClaw Personal AI Agent - Central Command Repository
> *30-Day Autonomous Agent Experiment*

**Status**: OPERATIONAL | **Bot**: @dutch_claws_bot | **Phase**: 0 (Foundation)

---

## What Is This?

An experiment in building a fully autonomous AI assistant with:
- **Multi-model LLM routing** (Claude, GPT, Gemini, ablated models)
- **Tiered authorization** (5 levels from autonomous to 2FA-required)
- **Cost-aware operation** (tracks and optimizes API spend)
- **Gradual capability expansion** (sandbox safety enables fast rollout)

The bot operates in a VPS sandbox - if anything goes wrong, blast radius is contained.

---

## Current State (2026-02-01)

### Operational

| Component | Status | Details |
|-----------|--------|---------|
| OpenClaw Gateway | **LIVE** | v2026.1.30 via systemd |
| Telegram Bot | **ACTIVE** | @dutch_claws_bot responding |
| Docker Infrastructure | **HEALTHY** | 8 containers on `openclaw-net` |
| RAG Knowledge Base | **INDEXED** | 3,623 vectors |
| 5-Tier Authorization | **CONFIGURED** | In gateway config |

### Pending (30-Day Experiment)

| Component | Phase | Target Day |
|-----------|-------|------------|
| Samsung Fingerprint 2FA | 0 | Day 1-3 |
| Multi-model API keys (OpenAI, Google) | 0 | Day 1-3 |
| RAG Integration for Bot | 1 | Day 4-7 |
| RunPod Ablated Models | 2 | Day 8-14 |
| Claude Code Bridge | 4 | Day 22-26 |
| Full Sandbox Autonomy | 5 | Day 27-30 |

---

## 30-Day Experiment Timeline

```
Phase 0 (D1-3)   Foundation    2FA + cost tracking + multi-model APIs
Phase 1 (D4-7)   Knowledge     Full RAG access (read + write)
Phase 2 (D8-14)  External      GitHub + web research + RunPod
Phase 3 (D15-21) Execution     Bash + file ops in sandbox
Phase 4 (D22-26) Bridge        Claude Code integration
Phase 5 (D27-30) Autonomy      Maximum sandbox capabilities
```

See [Refactored Priorities](research/openclaw-refactored-priorities-2026-02-01.md) for full details.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         VPS (srv1216617)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │              SANDBOX (openclaw-gateway)                  │    │
│  │  ├── Telegram Bot (@dutch_claws_bot)                    │    │
│  │  ├── Multi-model LLM Router                             │    │
│  │  ├── Authorization Engine (5-tier)                      │    │
│  │  ├── Cost Tracker                                       │    │
│  │  └── MCP Tool Access (phased)                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │                    SHARED SERVICES                         │  │
│  │  qdrant (vectors) │ timescaledb (metrics) │ rag-api       │  │
│  │  rabbitmq (queues) │ n8n (workflows) │ rugs-mcp (RAG)     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Documents

| Document | Purpose |
|----------|---------|
| [Refactored Priorities](research/openclaw-refactored-priorities-2026-02-01.md) | **START HERE** - Current plan and 30-day timeline |
| [Setup Plan](research/openclaw-setup-plan.md) | Original installation guide (completed) |
| [Authorization Architecture](research/openclaw-authorization-architecture.md) | 5-tier autonomy design |
| [RAG Knowledge Plan](research/openclaw-rag-knowledge-plan.md) | Knowledge ingestion strategy |
| [Due Diligence](research/openclaw-due-diligence.md) | Initial project evaluation |
| [Burner Card Comparison](research/openclaw-burner-card-comparison.md) | Virtual card analysis |

---

## Quick Reference

### Bot Access
```
Telegram: @dutch_claws_bot
Owner Chat ID: 6490779444
```

### VPS Access
```bash
ssh vps                              # Connect to VPS
systemctl status openclaw            # Check gateway
journalctl -u openclaw -f            # Live logs
docker ps                            # Container status
```

### Wallet (Base Network)
```
Address: 0x491245D10A16552A7f6317b9d437dA8A37d35799
Status: UNFUNDED (pending)
```

### Secrets Location
```
/opt/openclaw/secrets/
├── anthropic-api.env    # Claude API key
├── telegram-bot.env     # Bot token + PIN hash
├── wallet.env           # Private key
├── openai-api.env       # (pending)
├── google-ai.env        # (pending)
└── runpod.env           # (pending)
```

---

## Configuration Summary

| Component | Choice | Status |
|-----------|--------|--------|
| **Primary Channel** | Telegram | Active |
| **2FA Method** | Samsung fingerprint (simplified from voice) | Pending |
| **LLM Strategy** | Multi-model routing (cost-optimized) | Pending |
| **Crypto Wallet** | USDC on Base | Created, unfunded |
| **Spending Card** | Privacy.com | Not created |
| **Ablated Models** | RunPod serverless (scale-to-zero) | Not deployed |
| **Sandbox** | Docker with full isolation | Active |

---

## Safety Model

The bot operates in a **sandboxed Docker container** with:
- `--cap-drop=ALL` (minimal capabilities)
- `--read-only` filesystem (except /workspace)
- Memory/CPU/PID limits
- Network egress allowlist
- Full audit logging

**Blast radius if compromised**:
- /workspace contents (wipeable)
- API credits (protected by 2FA)
- Nothing else - host is isolated

---

## For the Bot

If you're the OpenClaw bot reading this:

1. **Your current phase**: Check `/phase status`
2. **Your capabilities**: See tool access matrix in [Refactored Priorities](research/openclaw-refactored-priorities-2026-02-01.md)
3. **Cost awareness**: All LLM calls should consider cost tier
4. **Authorization**: Check tier before external actions
5. **Knowledge**: Query RAG for project context (Phase 1+)

**Core principles**:
- Trust is earned, not assumed
- ALL financial actions require 2FA
- Sandbox is your playground - experiment freely within it
- Log everything for audit

---

## Infrastructure

| Resource | Value |
|----------|-------|
| **Host** | srv1216617 (Hostinger VPS) |
| **OS** | Ubuntu 24.04 LTS |
| **Resources** | 4 vCPU, 16GB RAM, 200GB NVMe |
| **VPN** | Tailscale (100.113.138.27) |
| **Docker Network** | openclaw-net |

---

*Project initiated: 2026-01-31 | Gateway live: 2026-02-01 | 30-day experiment: In progress*
