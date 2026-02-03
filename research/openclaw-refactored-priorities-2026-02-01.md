# OpenClaw Refactored Priorities

> **Created**: 2026-02-01
> **Status**: ACTIVE - Supersedes original setup-plan for remaining tasks
> **Principle**: Trust is earned, not assumed. Cost awareness is mandatory.
> **Timeline**: 30-day rapid capability rollout (VPS sandbox = safety net)

---

## Core Philosophy Changes

### From → To

| Original Approach | Refactored Approach |
|-------------------|---------------------|
| Voice 2FA as primary | Samsung fingerprint via Telegram (simpler, faster) |
| Claude Opus as default | Multi-model routing (cost-optimized by context) |
| RunPod for uncensored only | RunPod as part of broader LLM cost strategy |
| Agent can spend < $50 autonomously | **ALL charges require 2FA** until trust earned |
| Cost tracking as nice-to-have | **Cost management as core capability** |

---

## Priority 1: Simplified 2FA (Samsung Biometric)

### Goal
Replace complex voice enrollment with Telegram + Samsung fingerprint authentication.

### How It Works

```
Agent requests Tier 2/3 action
        │
        ▼
┌───────────────────────────────┐
│  Telegram Bot sends request   │
│  with deep link button:       │
│                               │
│  "🔐 APPROVAL REQUIRED        │
│   Action: Purchase API credit │
│   Amount: $25                 │
│   Provider: RunPod            │
│                               │
│  [🔓 Authenticate to Approve] │
│  [❌ Deny]                    │
└───────────────────────────────┘
        │
        ▼
  Deep link opens browser/app
  with biometric prompt
        │
        ▼
  Samsung fingerprint scans
        │
        ▼
  Webhook confirms to bot
        │
        ▼
  Action proceeds or denied
```

### Implementation Options

| Method | Complexity | Security | Notes |
|--------|------------|----------|-------|
| **Telegram WebApp + WebAuthn** | Medium | High | Native fingerprint in Telegram mini-app |
| **n8n webhook + Tailscale** | Low | Medium | Simple URL with one-time token |
| **Pushover/Ntfy with action** | Low | Medium | Push notification with confirm action |

### Recommended: Telegram WebApp with WebAuthn

1. Create minimal web page hosted on VPS (Tailscale-only access)
2. Page uses WebAuthn API to request fingerprint
3. Samsung device handles biometric natively
4. Success triggers webhook to OpenClaw gateway
5. Token-based to prevent replay attacks

### Fallback
- PIN code (410416) if biometric unavailable
- Rate-limited: 3 attempts per hour

---

## Priority 2: Multi-Model LLM Strategy

### Goal
Optimize for cost AND capability by routing to appropriate model based on context.

### Model Tiers

```yaml
model_tiers:
  flagship_development:
    # Use when actively developing, debugging, complex reasoning
    models:
      - claude-opus-4-5      # Primary for code, architecture
      - claude-sonnet-4      # Faster iteration
    triggers:
      - "coding session active"
      - "debugging"
      - "architecture design"
    cost: $$$

  flagship_general:
    # General assistant tasks when not developing
    models:
      - gpt-5.2-turbo        # ChatGPT for general tasks
      - gemini-3.5-pro       # Google for research, search
    triggers:
      - "default mode"
      - "general queries"
      - "summarization"
    cost: $$

  fast_cheap:
    # Quick tasks, drafts, simple queries
    models:
      - gpt-4o-mini          # Very cheap, fast
      - gemini-3.5-flash     # Google fast tier
      - claude-haiku-3.5     # Anthropic fast tier
    triggers:
      - "draft"
      - "quick question"
      - "simple task"
    cost: $

  truth_seeking:
    # Deep epistemological analysis, uncensored research
    models:
      - dolphin-llama3.1-70b # RunPod serverless
      - local-ablated        # If local GPU available
    triggers:
      - "uncensored analysis"
      - "security research"
      - "controversial topic"
      - "maximum truthfulness"
    cost: $$ (only when invoked)
    scaling: zero-to-one (no idle cost)

  code_specialist:
    # Code generation, debugging
    models:
      - deepseek-coder-v2    # RunPod or API
      - claude-opus-4-5      # Fallback
    triggers:
      - "code generation"
      - "debugging code"
    cost: $$
```

### Routing Logic

```
User Query
    │
    ▼
┌─────────────────────────────────┐
│  Context Analyzer               │
│  - Is coding session active?    │
│  - Keywords: research, truth,   │
│    uncensored, controversial?   │
│  - Task complexity?             │
│  - User override flag?          │
└─────────────────────────────────┘
    │
    ├─── Development mode ──→ Claude Opus
    ├─── General query ─────→ GPT-5.2 / Gemini
    ├─── Quick task ────────→ GPT-4o-mini
    ├─── Truth-seeking ─────→ Dolphin (RunPod)
    └─── Code task ─────────→ DeepSeek / Opus
```

### User Override Commands

```
/model opus     → Force Claude Opus for next query
/model cheap    → Force cheapest model
/model truth    → Force ablated model
/model auto     → Return to automatic routing
/costs          → Show today's model costs
```

---

## Priority 3: Cost Tracking System

### Paid Services Registry

All services that cost money, tracked in one place:

```yaml
# /opt/openclaw/config/cost-registry.yaml
paid_services:
  llm_apis:
    anthropic:
      type: per-token
      models: [opus-4-5, sonnet-4, haiku-3.5]
      billing: monthly
      dashboard: https://console.anthropic.com
      secret_ref: /opt/openclaw/secrets/anthropic-api.env
      budget_alert: $100/month

    openai:
      type: per-token
      models: [gpt-5.2-turbo, gpt-4o-mini]
      billing: monthly
      dashboard: https://platform.openai.com
      secret_ref: /opt/openclaw/secrets/openai-api.env
      budget_alert: $50/month
      status: NOT_CONFIGURED

    google:
      type: per-token
      models: [gemini-3.5-pro, gemini-3.5-flash]
      billing: monthly
      dashboard: https://console.cloud.google.com
      secret_ref: /opt/openclaw/secrets/google-ai.env
      budget_alert: $50/month
      status: NOT_CONFIGURED

  compute:
    runpod:
      type: per-second (serverless)
      purpose: Ablated models (dolphin, deepseek)
      billing: prepaid credits
      dashboard: https://runpod.io/console
      secret_ref: /opt/openclaw/secrets/runpod.env
      budget_alert: $30/month
      scaling: zero-when-idle
      status: NOT_CONFIGURED

  infrastructure:
    hostinger_vps:
      type: fixed monthly
      cost: ~$15/month
      purpose: OpenClaw host, Docker, RAG
      billing: monthly
      status: ACTIVE

    tailscale:
      type: free tier
      cost: $0
      purpose: VPN access
      status: ACTIVE

  financial:
    privacy_com:
      type: free tier (or $5/mo Plus)
      cost: $0-5/month
      purpose: Virtual cards for purchases
      status: NOT_CONFIGURED

    base_network_gas:
      type: per-transaction
      cost: <$1/month estimated
      purpose: USDC transactions
      status: WALLET_UNFUNDED
```

### Cost Dashboard Commands

```
/costs today    → Today's spend by service
/costs week     → 7-day breakdown
/costs month    → MTD with projection
/costs alert    → Set/view budget alerts
/costs optimize → Suggestions to reduce spend
```

### Cost Tracking Implementation

```yaml
# Store in TimescaleDB
cost_tracking:
  table: openclaw.cost_events
  schema:
    - timestamp
    - service (anthropic, runpod, etc)
    - model (opus, gpt-5.2, etc)
    - tokens_in
    - tokens_out
    - cost_usd
    - session_id
    - purpose_tag

  aggregations:
    - hourly rollup
    - daily rollup
    - per-model breakdown
    - per-purpose breakdown
```

---

## Priority 4: Financial Controls (Zero Trust)

### Principle
> **ALL CHARGES MUST BE VERIFIED BY ME VIA 2FA UNTIL TRUST IS EARNED**

### Implementation

```yaml
financial_authorization:
  # Phase 1: Maximum Control (CURRENT)
  phase_1_zero_trust:
    duration: "Until explicitly relaxed"
    rules:
      - ALL purchases require 2FA (fingerprint)
      - ALL API top-ups require 2FA
      - ALL subscription changes require 2FA
      - No autonomous spending of any amount
      - Daily cost report mandatory

  # Phase 2: Micro-Trust (FUTURE - requires explicit unlock)
  phase_2_micro_trust:
    unlock_criteria:
      - 30 days with zero unauthorized actions
      - 100+ successful 2FA approvals
      - User explicitly enables
    rules:
      - Subscriptions auto-renew (notify only)
      - API usage within budget (no approval)
      - One-time purchases still require 2FA

  # Phase 3: Limited Autonomy (FAR FUTURE)
  phase_3_limited_autonomy:
    unlock_criteria:
      - Phase 2 active for 90+ days
      - Zero incidents
      - User explicitly enables
    rules:
      - Purchases < $10 auto-approved (notify)
      - Purchases $10-50 require button confirm
      - Purchases > $50 require 2FA
```

### Transaction Flow (Phase 1)

```
Agent identifies need for purchase
        │
        ▼
┌───────────────────────────────┐
│  Create Authorization Request │
│  - What: RunPod credits       │
│  - Amount: $25                │
│  - Why: Depleted balance      │
│  - Urgency: Medium            │
└───────────────────────────────┘
        │
        ▼
  Send to Telegram with 2FA button
        │
        ▼
  User receives notification
        │
        ├─── Fingerprint approve ──→ Execute purchase
        ├─── Deny ─────────────────→ Cancel, log reason
        └─── Timeout (4h) ─────────→ Auto-deny, notify
```

---

## Updated Task Priority List

### Immediate (This Week)

| Task | Priority | Blocking |
|------|----------|----------|
| Set up Samsung fingerprint 2FA via Telegram | P0 | Blocks all approvals |
| Configure OpenAI API key | P1 | Blocks multi-model routing |
| Configure Google AI API key | P1 | Blocks multi-model routing |
| Create cost-registry.yaml | P1 | Blocks cost tracking |
| Create RunPod account | P1 | Blocks ablated models |

### Short-term (This Month)

| Task | Priority | Depends On |
|------|----------|------------|
| Deploy dolphin-70b on RunPod (serverless, scale-to-zero) | P1 | RunPod account |
| Implement model router in OpenClaw config | P1 | API keys configured |
| Set up cost tracking in TimescaleDB | P2 | Cost registry |
| Create /costs command for bot | P2 | Cost tracking |
| Privacy.com card setup | P2 | 2FA working |
| Fund Base wallet (small amount) | P3 | 2FA working |

### Deferred

| Task | Status | Notes |
|------|--------|-------|
| Voice 2FA enrollment | DEFERRED | Revisit after fingerprint 2FA stable |
| WhatsApp/Discord/Slack channels | DEFERRED | Telegram sufficient for now |
| System package updates | LOW | Schedule maintenance window |

---

## Secrets & Cost Services Cross-Reference

| Service | Secret Location | Cost Type | Status |
|---------|-----------------|-----------|--------|
| Anthropic Claude | `/opt/openclaw/secrets/anthropic-api.env` | Per-token | ✅ ACTIVE |
| Telegram Bot | `/opt/openclaw/secrets/telegram-bot.env` | Free | ✅ ACTIVE |
| OpenAI | `/opt/openclaw/secrets/openai-api.env` | Per-token | ❌ NOT SET |
| Google AI | `/opt/openclaw/secrets/google-ai.env` | Per-token | ❌ NOT SET |
| RunPod | `/opt/openclaw/secrets/runpod.env` | Per-second | ❌ NOT SET |
| Privacy.com | `/opt/openclaw/secrets/privacy-com.env` | Free/$5mo | ❌ NOT SET |
| Base Wallet | `/opt/openclaw/secrets/wallet.env` | Gas fees | ✅ KEY STORED |
| Hostinger VPS | N/A (external billing) | Fixed $15/mo | ✅ ACTIVE |

---

## Trust Evolution Framework

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TRUST LEVELS                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  LEVEL 0: ZERO TRUST (Current)                                      │
│  ├── All spending requires 2FA                                      │
│  ├── All external actions require approval                          │
│  └── Agent is read-only for financial systems                       │
│                                                                      │
│  LEVEL 1: MICRO TRUST (Unlock after 30 days + explicit approval)   │
│  ├── Recurring subscriptions auto-renew (notify only)               │
│  ├── API usage within daily budget proceeds                         │
│  └── One-time purchases still need 2FA                              │
│                                                                      │
│  LEVEL 2: LIMITED TRUST (Unlock after 90 days + explicit approval) │
│  ├── Purchases < $10 auto-approved with notification                │
│  ├── Purchases $10-50 need button confirm (no biometric)            │
│  └── Purchases > $50 need 2FA                                       │
│                                                                      │
│  LEVEL 3: FULL TRUST (Maybe never, requires extensive track record)│
│  ├── Agent manages budget autonomously within limits                │
│  ├── Can optimize costs without per-action approval                 │
│  └── Human reviews weekly summary, not individual actions           │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Priority 5: Phased Tool & Knowledge Access

### Goal
Gradually integrate OpenClaw bot into the full toolchain (RAG, MCP servers, Claude Code sessions) with security gates at each phase.

### Current State

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TOOL ECOSYSTEM (Available)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Claude Code Session (You + Me)                                     │
│  ├── Bash, Read, Write, Edit, Glob, Grep                           │
│  ├── GitHub MCP (issues, PRs, commits)                              │
│  ├── Playwright MCP (browser automation)                            │
│  ├── Chrome DevTools MCP (browser control)                          │
│  ├── Context7 MCP (documentation lookup)                            │
│  └── rugs-expert MCP (RAG + VPS health)                             │
│       ├── search_rugs_knowledge (3,623 vectors)                     │
│       ├── get_docker_status                                         │
│       ├── get_system_info                                           │
│       ├── ingest_knowledge                                          │
│       └── VPS service logs                                          │
│                                                                      │
│  OpenClaw Bot (@dutch_claws_bot) - Currently ISOLATED               │
│  ├── Telegram message handling                                      │
│  ├── Basic Claude API access                                        │
│  └── NO access to MCP tools, RAG, or Claude Code sessions          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Phased Integration Timeline (30-Day Experiment)

**Safety Model**: VPS sandbox isolation is the primary safety net. The bot operates in a fully
containerized environment with:
- Docker network isolation (`openclaw-net`)
- Read-only filesystem (except `/workspace`)
- Capability dropping (`--cap-drop=ALL`)
- Resource limits (memory, CPU, PIDs)
- No SSH key access, no root outside container
- All egress filtered through allowed endpoints
- Full audit logging to TimescaleDB

This sandbox allows aggressive capability rollout - if anything goes wrong, the blast radius
is contained to the VPS experiment environment.

```
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 0: FOUNDATION (Days 1-3)                          │
│              Goal: Core infrastructure + 2FA operational             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Capabilities:                                                      │
│  ├── Respond to Telegram messages via Claude API                    │
│  ├── Send authorization requests                                    │
│  ├── Report status and costs                                        │
│  └── Basic health monitoring                                        │
│                                                                      │
│  Tasks to complete:                                                 │
│  ├── Samsung fingerprint 2FA working                                │
│  ├── Cost tracking operational                                      │
│  ├── Multi-model API keys configured                                │
│  └── Audit logging verified                                         │
│                                                                      │
│  Unlock: 2FA tested successfully + cost tracking live               │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 1: KNOWLEDGE ACCESS (Days 4-7)                    │
│              Goal: Full RAG integration + VPS awareness              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NEW capabilities:                                                  │
│  ├── Query rugs-expert RAG (search_rugs_knowledge)                  │
│  │   └── Full access to 3,623+ indexed vectors                      │
│  ├── Ingest knowledge to RAG (ingest_knowledge)                     │
│  ├── Query VPS health (get_system_info, get_docker_status)          │
│  ├── Read service logs (get_service_logs)                           │
│  └── Access all indexed documentation                               │
│                                                                      │
│  Authorization:                                                     │
│  ├── RAG read: Tier 0 (autonomous)                                  │
│  ├── RAG write: Tier 1 (notify only)                                │
│  └── VPS queries: Tier 0 (autonomous)                               │
│                                                                      │
│  Unlock: Demonstrated useful RAG queries + no errors                │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 2: EXTERNAL INTEGRATION (Days 8-14)               │
│              Goal: GitHub, web access, research capabilities         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NEW capabilities:                                                  │
│  ├── GitHub read (list issues, view PRs, browse repos)              │
│  ├── GitHub write (create issues, comment on PRs)                   │
│  ├── Web fetch for documentation and research                       │
│  ├── Context7 documentation lookup                                  │
│  └── Web search for current information                             │
│                                                                      │
│  Authorization:                                                     │
│  ├── GitHub read: Tier 0 (autonomous)                               │
│  ├── GitHub write: Tier 2 (requires approval)                       │
│  ├── Web fetch: Tier 0 (autonomous)                                 │
│  └── Web search: Tier 0 (autonomous)                                │
│                                                                      │
│  Unlock: Quality research outputs + appropriate GitHub usage        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 3: EXECUTION CAPABILITIES (Days 15-21)            │
│              Goal: Limited bash, file operations, automation         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NEW capabilities:                                                  │
│  ├── Allowlisted bash commands within sandbox:                      │
│  │   ├── git status, git log, git diff                              │
│  │   ├── docker ps, docker logs                                     │
│  │   ├── systemctl status (read-only)                               │
│  │   ├── curl (GET only, allowed domains)                           │
│  │   └── Standard unix: ls, cat, grep, find, df, free               │
│  ├── File read within project directories                           │
│  ├── File write to /workspace only                                  │
│  ├── Docker container inspection (not control)                      │
│  └── Scheduled task creation (cron-like)                            │
│                                                                      │
│  Authorization:                                                     │
│  ├── Allowlisted bash: Tier 1 (notify only)                         │
│  ├── File read: Tier 0 (autonomous)                                 │
│  ├── File write: Tier 1 (notify only)                               │
│  └── Scheduled tasks: Tier 2 (requires approval)                    │
│                                                                      │
│  Unlock: No unauthorized command attempts + useful automation       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 4: CLAUDE CODE BRIDGE (Days 22-26)                │
│              Goal: Bidirectional integration with dev sessions       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  NEW capabilities:                                                  │
│  ├── Participate in Claude Code sessions (read context)             │
│  │   └── Can see conversation history when invoked                  │
│  ├── Suggest code changes (queued for human review)                 │
│  ├── Create GitHub PRs (with approval)                              │
│  ├── Browser automation for research (Playwright)                   │
│  │   └── Read-only scraping, no form submissions                    │
│  └── Initiate async research tasks                                  │
│                                                                      │
│  Bridge commands:                                                   │
│  ├── Telegram: /claude <message> → forwards to session              │
│  ├── Claude Code: @openclaw <task> → delegates to bot               │
│  └── Shared workspace: /opt/openclaw/workspace/shared               │
│                                                                      │
│  Authorization:                                                     │
│  ├── Session read: Tier 0 (autonomous)                              │
│  ├── Code suggestions: Tier 1 (notify only)                         │
│  ├── PR creation: Tier 2 (requires approval)                        │
│  └── Browser automation: Tier 1 (notify only)                       │
│                                                                      │
│  Unlock: Quality suggestions + no overreach                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│              PHASE 5: FULL SANDBOX AUTONOMY (Days 27-30)             │
│              Goal: Maximum capability within sandbox constraints     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  Full capabilities (within sandbox):                                │
│  ├── All MCP tools available to Claude Code                         │
│  ├── Expanded bash (still sandboxed, no sudo)                       │
│  ├── Docker container management (restart, logs, exec)              │
│  ├── File write to project directories                              │
│  ├── Git operations including push (with approval)                  │
│  ├── Full browser automation (including forms)                      │
│  ├── Proactive monitoring and maintenance                           │
│  └── Self-directed research and development                         │
│                                                                      │
│  Authorization at Phase 5:                                          │
│  ├── Tier 0: All read operations, RAG, web, monitoring              │
│  ├── Tier 1: File writes, bash execution, browser automation        │
│  ├── Tier 2: Git push, PR creation, container management            │
│  └── Tier 3: Financial transactions only (2FA required)             │
│                                                                      │
│  PERMANENT RESTRICTIONS (Tier 4 - hardcoded deny):                  │
│  ├── Cannot escape Docker sandbox                                   │
│  ├── Cannot disable security services                               │
│  ├── Cannot expose secrets publicly                                 │
│  ├── Cannot modify authorization system                             │
│  ├── Cannot delete critical data                                    │
│  ├── Cannot bypass audit logging                                    │
│  ├── Cannot access SSH keys or root credentials                     │
│  └── Cannot modify firewall or network config                       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### 30-Day Timeline Summary

| Phase | Days | Focus | Key Milestone |
|-------|------|-------|---------------|
| 0 | 1-3 | Foundation | 2FA + cost tracking operational |
| 1 | 4-7 | Knowledge | Full RAG access working |
| 2 | 8-14 | External | GitHub + web research active |
| 3 | 15-21 | Execution | Bash + file ops in sandbox |
| 4 | 22-26 | Bridge | Claude Code integration live |
| 5 | 27-30 | Autonomy | Maximum sandbox capabilities |

### Sandbox Security Model

```
┌─────────────────────────────────────────────────────────────────────┐
│                    VPS SANDBOX ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────── HOST (srv1216617) ───────────────────────┐    │
│  │                                                              │    │
│  │  PROTECTED ZONE (Bot cannot access):                        │    │
│  │  ├── /root/ (SSH keys, host configs)                        │    │
│  │  ├── /etc/ (system configuration)                           │    │
│  │  ├── /opt/openclaw/secrets/ (mounted read-only)             │    │
│  │  ├── Host network stack                                     │    │
│  │  └── Other containers (qdrant, timescale, etc.)             │    │
│  │                                                              │    │
│  │  ┌─────────── SANDBOX (Bot operates here) ──────────────┐   │    │
│  │  │                                                       │   │    │
│  │  │  openclaw-gateway container:                         │   │    │
│  │  │  ├── /workspace (read-write, bot's playground)       │   │    │
│  │  │  ├── /home/node/.openclaw (config, read-only)        │   │    │
│  │  │  ├── /tmp (ephemeral)                                │   │    │
│  │  │  └── Network: openclaw-net only                      │   │    │
│  │  │                                                       │   │    │
│  │  │  Constraints:                                        │   │    │
│  │  │  ├── --cap-drop=ALL                                  │   │    │
│  │  │  ├── --read-only (except /workspace, /tmp)           │   │    │
│  │  │  ├── --memory=4g --cpus=2 --pids-limit=100          │   │    │
│  │  │  ├── --security-opt=no-new-privileges               │   │    │
│  │  │  └── seccomp profile (syscall filtering)            │   │    │
│  │  │                                                       │   │    │
│  │  └───────────────────────────────────────────────────────┘   │    │
│  │                                                              │    │
│  │  ALLOWED EGRESS (network allowlist):                        │    │
│  │  ├── api.anthropic.com (Claude)                             │    │
│  │  ├── api.openai.com (GPT)                                   │    │
│  │  ├── generativelanguage.googleapis.com (Gemini)             │    │
│  │  ├── api.telegram.org (bot messaging)                       │    │
│  │  ├── api.runpod.io (when configured)                        │    │
│  │  ├── api.github.com (GitHub operations)                     │    │
│  │  ├── Internal: rag-api, qdrant, timescaledb, n8n           │    │
│  │  └── General HTTPS (for web research, documentation)        │    │
│  │                                                              │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                                                                      │
│  BLAST RADIUS: If bot goes rogue, damage limited to:               │
│  ├── /workspace contents (can be wiped)                            │
│  ├── API credits (protected by 2FA for purchases)                  │
│  ├── GitHub repos (protected by Tier 2 approval)                   │
│  └── Container resources (auto-limited)                            │
│                                                                      │
│  RECOVERY: docker stop openclaw-gateway && docker rm -f ...        │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Tool Access Matrix by Phase (30-Day Timeline)

| Tool/Capability | P0 (D1-3) | P1 (D4-7) | P2 (D8-14) | P3 (D15-21) | P4 (D22-26) | P5 (D27-30) |
|-----------------|-----------|-----------|------------|-------------|-------------|-------------|
| Telegram messaging | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Multi-model LLM | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RAG search | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| RAG ingest | ❌ | ✅¹ | ✅¹ | ✅ | ✅ | ✅ |
| VPS health | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Service logs | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| GitHub read | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| GitHub write | ❌ | ❌ | ✅² | ✅² | ✅² | ✅² |
| Web fetch/search | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Context7 docs | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ |
| Bash (allowlist) | ❌ | ❌ | ❌ | ✅¹ | ✅¹ | ✅¹ |
| File read | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ |
| File write | ❌ | ❌ | ❌ | ✅¹ | ✅¹ | ✅¹ |
| Scheduled tasks | ❌ | ❌ | ❌ | ✅² | ✅² | ✅² |
| Claude Code bridge | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| Browser automation | ❌ | ❌ | ❌ | ❌ | ✅¹ | ✅¹ |
| Docker management | ❌ | ❌ | ❌ | ❌ | ❌ | ✅² |
| Git push | ❌ | ❌ | ❌ | ❌ | ❌ | ✅² |
| Full MCP access | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Legend**: ✅ = Available | ✅¹ = Tier 1 (notify) | ✅² = Tier 2 (approval required)

### Integration Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      INTEGRATION FLOW                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │  Telegram   │────▶│  OpenClaw   │────▶│    MCP      │           │
│  │  Messages   │     │  Gateway    │     │   Router    │           │
│  └─────────────┘     └─────────────┘     └──────┬──────┘           │
│                             │                    │                   │
│                             │                    ▼                   │
│                             │           ┌───────────────┐           │
│                             │           │ Permission    │           │
│                             │           │ Checker       │           │
│                             │           │ (Phase-aware) │           │
│                             │           └───────┬───────┘           │
│                             │                   │                   │
│                             ▼                   ▼                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     TOOL LAYER                               │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐        │   │
│  │  │ rugs-   │  │ GitHub  │  │Playwright│  │ Claude  │        │   │
│  │  │ expert  │  │  MCP    │  │   MCP    │  │  Code   │        │   │
│  │  │  RAG    │  │         │  │          │  │ Bridge  │        │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    AUDIT LAYER                               │   │
│  │  - All tool invocations logged                               │   │
│  │  - Permission denials logged                                 │   │
│  │  - Anomaly detection                                         │   │
│  │  - Daily reports to Telegram                                 │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Claude Code ↔ OpenClaw Bridge (Phase 3+)

```yaml
# Bridge configuration for bidirectional communication
claude_code_bridge:
  enabled: false  # Enable at Phase 3

  # OpenClaw → Claude Code
  telegram_to_claude:
    command: "/claude"
    description: "Forward message to active Claude Code session"
    example: "/claude what's the status of the auth refactor?"
    mechanism: "WebSocket to local Claude Code server"

  # Claude Code → OpenClaw
  claude_to_telegram:
    trigger: "@openclaw"
    description: "Delegate async task to bot"
    example: "@openclaw monitor the deployment and notify me when done"
    mechanism: "Message queue via RabbitMQ"

  # Shared context
  shared_workspace:
    path: "/opt/openclaw/workspace/shared"
    purpose: "File exchange between Claude Code and OpenClaw"
    permissions:
      claude_code: "read-write"
      openclaw: "read-write (Phase 4+) / read-only (Phase 3)"
```

### Phase Transition Gates

Each phase unlock requires:

1. **Milestone completion** - Key tasks for current phase done
2. **No major incidents** - No unauthorized action attempts
3. **User approval** - `/unlock-phase <N>` or automatic if criteria met

```
/phase status      → Current phase, day, capabilities
/phase next        → Show what unlocks at next phase
/unlock-phase N    → Manually advance to phase N
/lock-phase 0      → Emergency rollback to isolation
/phase log         → Audit of all phase transitions
```

### Experiment Success Criteria (Day 30)

At the end of 30 days, evaluate:

| Metric | Target | Measurement |
|--------|--------|-------------|
| Uptime | > 95% | Gateway availability |
| Useful actions | > 100 | Queries, research, automation |
| False 2FA triggers | < 5 | Unnecessary approval requests |
| Security incidents | 0 | Unauthorized access attempts |
| Cost optimization | Measurable | Model routing savings vs Opus-only |
| Knowledge growth | +500 vectors | RAG contributions |

If successful, consider:
- Extending experiment with more capabilities
- Promoting patterns to production use
- Documenting learnings for future agents

---

## Next Session Actions

1. **Research Samsung fingerprint + Telegram WebApp integration**
2. **Create OpenAI account and API key**
3. **Create Google AI account and API key**
4. **Create RunPod account**
5. **Set up cost-registry.yaml on VPS**
6. **Test 2FA flow end-to-end**
7. **Design Phase 0 → Phase 1 unlock criteria and audit system**

---

*Refactored priorities: 2026-02-01 | Philosophy: Trust is earned, access is gradual*
