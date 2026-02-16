# Claws and Pincers

> **OpenClaw Personal AI Agent - Central Command Repository**
> *30-Day Autonomous Agent Experiment*

**Status**: OPERATIONAL | **Bot**: @dutch_claws_bot | **Phase**: 0 ✅ → 1 | **Day**: 2 | **Mode**: UNSANDBOXED

---

## For Claude Code Sessions: START HERE

If you're a Claude Code session working on this project:

1. **Read this README first** - it's the source of truth
2. **Check [TODO.md](TODO.md)** - current task priorities
3. **Check [Refactored Priorities](research/openclaw-refactored-priorities-2026-02-01.md)** - full 30-day plan
4. **Use the rugs-expert MCP** - it has RAG access to all project knowledge
5. **Don't reinvent wheels** - query the RAG before building anything new

**Key Infrastructure:**
- VPS: `ssh vps` (72.62.160.2)
- Bot: @dutch_claws_bot on Telegram
- Wallet: `0x491245D10A16552A7f6317b9d437dA8A37d35799` (Base network, FUNDED)
- MCP: rugs-expert server at http://72.62.160.2:8001/sse

---

## What Is This?

An experiment in building a fully autonomous AI assistant with:
- **Multi-model LLM routing** (Claude, GPT, Gemini, ablated models)
- **Tiered authorization** (5 levels from autonomous to 2FA-required)
- **Cost-aware operation** (tracks and optimizes API spend)
- **Gradual capability expansion** (sandbox safety enables fast rollout)
- **Higher intelligence layers** (RunPod GPU, local models, TTS, image gen)

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

### Phase 0 Complete (Ahead of Schedule)

| Component | Status | Date |
|-----------|--------|------|
| Telegram 2FA (Inline Buttons) | ✅ WORKING | 2026-02-02 |
| Base Wallet Funding | ✅ FUNDED | 2026-02-02 |
| PR to upstream | ✅ [#6892](https://github.com/openclaw/openclaw/pull/6892) | 2026-02-02 |
| Multi-Model LLM Routing | ✅ 4 PROVIDERS | 2026-02-02 |
| Cost Tracking Infrastructure | ✅ READY | 2026-02-02 |
| Debug Cleanup | ✅ CLEAN | 2026-02-02 |

### Active LLM Providers

| Provider | Models | Status |
|----------|--------|--------|
| Anthropic | Claude Opus/Sonnet/Haiku | ✅ Primary |
| Groq | llama-3.3-70b (FREE) | ✅ Cost fallback |
| Google | Gemini 2.0 Flash | ✅ Active |
| OpenRouter | Kimi K2.5, GPT-4o | ✅ Active |

### Pending (30-Day Experiment)

| Component | Phase | Target Day | Status |
|-----------|-------|------------|--------|
| RAG Integration for Bot | 1 | Day 4-7 | 🔜 Next |
| RunPod + Intelligence Layers | 2 | Day 8-14 | ❌ Pending |
| Claude Code Bridge | 4 | Day 22-26 | ❌ Pending |
| Full Sandbox Autonomy | 5 | Day 27-30 | ❌ Pending |

---

## 30-Day Experiment Timeline

```
Phase 0 (D1-3)   Foundation    ✅ COMPLETE (Day 2)
Phase 1 (D4-7)   Knowledge     🔜 Full RAG access (read + write)
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
│  │              OPENCLAW GATEWAY (systemd)                  │    │
│  │  ├── Telegram Bot (@dutch_claws_bot)                    │    │
│  │  ├── Multi-model LLM Router                             │    │
│  │  ├── Authorization Engine (Telegram approvals)          │    │
│  │  ├── Cost Tracker                                       │    │
│  │  └── MCP Tool Access                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│  ┌───────────────────────────┴───────────────────────────────┐  │
│  │              AGENT-MAIN (Native Host User)                │  │
│  │  ├── Home: /home/agent-main                              │  │
│  │  ├── Full host filesystem access (as agent-main user)    │  │
│  │  ├── Docker group membership                             │  │
│  │  ├── Skills: 52+ tools in ~/skills                       │  │
│  │  └── Symlinks to /opt/openclaw/workspace                 │  │
│  └───────────────────────────────────────────────────────────┘  │
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
| [Exec Fix Analysis](docs/diagnostics/EXEC-FIX-PLAN.md) | Exec output troubleshooting |
| [Phase 0 Foundation](docs/plans/2026-02-01-phase0-foundation.md) | Phase 0 implementation plan |
| [Change Repo Visibility on Mobile](docs/CHANGE-REPO-VISIBILITY-MOBILE.md) | How to make repository public using mobile devices |

---

## Quick Reference

### Bot Access
```
Telegram: @dutch_claws_bot
Owner Chat ID: 6490779444
```

### VPS Access (Prefer MCP over SSH)

**Use rugs-expert MCP tools when possible:**
```
mcp__rugs-expert__get_system_info()        # System resources
mcp__rugs-expert__get_docker_status()      # Container health
mcp__rugs-expert__get_service_logs()       # Read container logs
mcp__rugs-expert__run_health_checks()      # Full health check
mcp__rugs-expert__search_rugs_knowledge()  # Query RAG
mcp__rugs-expert__ingest_knowledge()       # Add to RAG
```

**SSH only when MCP insufficient:**
```bash
ssh vps                              # Direct VPS access
systemctl status openclaw            # Gateway status
journalctl -u openclaw -f            # Live logs
```

### Wallet (Base Network)
```
Address: 0x491245D10A16552A7f6317b9d437dA8A37d35799
Status: FUNDED (via Coinbase)
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
| **Primary Channel** | Telegram | ✅ Active |
| **2FA Method** | Inline buttons (Telegram native) | ✅ Working |
| **LLM Strategy** | Multi-model routing (cost-optimized) | ⏳ Pending APIs |
| **Crypto Wallet** | USDC on Base | ✅ Funded |
| **Spending Card** | Privacy.com | ❌ Deferred |
| **Ablated Models** | RunPod serverless (scale-to-zero) | ❌ Not deployed |
| **Execution Mode** | Native host user (agent-main) | ✅ Active |

---

## Intelligence Layers (Phase 2+)

OpenClaw will have admin access to RunPod for higher-level capabilities:

| Layer | Purpose | Technology | Status |
|-------|---------|------------|--------|
| **Ablated LLM** | Uncensored reasoning | dolphin-llama3.1-70b on RunPod | ❌ Pending |
| **Code Specialist** | Deep code analysis | deepseek-coder-v2 on RunPod | ❌ Pending |
| **Local Models** | Fast inference, privacy | Ollama / LM Studio | ❌ Pending |
| **Image Generation** | Visual content | ComfyUI on RunPod | ❌ Pending |
| **Voice/TTS** | Verbal capabilities | Chatterbox TTS | ❌ Pending |

**Scaling model:** All RunPod workloads use scale-to-zero (no idle cost)

---

## Safety Model

> **UPDATE 2026-02-02**: Migrated from Docker sandbox to native host user execution

The bot now operates as a **dedicated Linux user** (`agent-main`) with:
- Non-root user isolation (uid 1002)
- Home directory: `/home/agent-main`
- Docker group membership (can manage containers)
- Full audit logging via OpenClaw gateway
- Telegram exec approvals still required for sensitive operations

**Blast radius if compromised**:
- Everything accessible by `agent-main` user
- Docker containers (via group membership)
- API credits (still protected by Telegram approvals)
- Host system files remain protected (not root)

**Why unsandboxed?**
- Enables true autonomous operation
- Removes friction for legitimate tasks
- Owner explicitly authorized this elevation
- Still maintains Telegram approval workflow for exec operations

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

*Project initiated: 2026-01-31 | Gateway live: 2026-02-01 | 30-day experiment: Day 2 of 30*

---

## Changelog

- **2026-02-02 (EVE)**: SANDBOX REMOVED - Migrated to native host user `agent-main` at `/home/agent-main`. Full host access granted.
- **2026-02-02 (PM)**: Phase 0 COMPLETE - Multi-model routing (4 providers), cost tracking, Groq free tier configured
- **2026-02-02 (AM)**: Telegram 2FA inline buttons working, wallet funded, PR #6892 submitted
- **2026-02-01**: Gateway deployed, Docker infrastructure healthy, RAG indexed
