# OpenClaw 30-Day Experiment TODO

> **Last Updated**: 2026-02-02
> **Current Phase**: 0 → 1 (Foundation → Knowledge)
> **Current Day**: 2 of 30
> **Phase 0 Status**: ✅ COMPLETE
> **Execution Mode**: UNSANDBOXED (native host user)
> **Experiment Start**: 2026-02-01
> **Target Completion**: 2026-03-03

---

## Completed (Ahead of Schedule)

- [x] **PRIVILEGE ELEVATION: Unsandboxed Execution** (2026-02-02)
  - Migrated from Docker sandbox to native host user
  - Created user `agent-main` (uid 1002)
  - Home directory: `/home/agent-main`
  - Docker group membership granted
  - 52+ skills migrated to `~/skills`
  - Symlinks to OpenClaw workspace configured
  - Gateway config updated: `sandbox.mode: "off"`
  - Telegram exec approvals still active

- [x] **Telegram 2FA with Inline Buttons** (2026-02-02)
  - Implemented `sendPayload` in Telegram channel adapter
  - Added callback query handler for approve/reject buttons
  - Working end-to-end: approval → button tap → resolution
  - PR: https://github.com/openclaw/openclaw/pull/6892

- [x] **Base Wallet Funded** (2026-02-02)
  - Address: `0x491245D10A16552A7f6317b9d437dA8A37d35799`
  - Network: Base (ETH L2)
  - Funded with ETH (gas) and USDC from Kraken

- [x] **Fork & PR to Upstream** (2026-02-02)
  - Fork: Dutchthenomad/openclaw
  - Feature branch: feature/telegram-2fa-buttons
  - PR #6892 submitted

- [x] **Multi-Model LLM Routing** (2026-02-02)
  - Google AI: ✅ Configured (Gemini 2.0 Flash)
  - Groq: ✅ Configured (FREE llama-3.3-70b - 1000 req/day)
  - OpenRouter: ✅ Configured (Kimi K2.5, GPT-4o)
  - Anthropic: ✅ Already active (Claude)
  - Fallback chain: Groq → Anthropic → OpenRouter → Google

- [x] **Cost Tracking Infrastructure** (2026-02-02)
  - Created `/opt/openclaw/config/cost-registry.yaml`
  - TimescaleDB `cost_events` table ready (14 columns)
  - Budget alerts configured per service
  - Groq marked as free tier

- [x] **Debug Cleanup** (2026-02-02)
  - Removed 13 debug console.log statements
  - Runtime rebuilt and gateway restarted

---

## Phase 0: Foundation (Days 1-3) - ✅ COMPLETE

### Completed Tasks

- [x] **Google AI API key** ✅
  - Configured in `/root/.openclaw/.env`
  - Available for Gemini 2.0 Flash

- [x] **Groq API key** ✅ (replaces OpenAI need)
  - FREE tier with llama-3.3-70b (better than GPT-4o for reasoning)
  - 1,000 requests/day limit
  - Stored at `/opt/openclaw/secrets/groq.env`

- [x] **Cost registry configuration** ✅
  - Created `/opt/openclaw/config/cost-registry.yaml`
  - All paid services with budget alerts defined
  - TimescaleDB cost_events table ready

### Phase 0 Unlock Criteria
- [x] 2FA tested and working ✅ (inline buttons working)
- [x] Multi-model LLM APIs configured ✅ (4 providers active)
- [x] Cost tracking infrastructure ready ✅

### Optional (Deferred)
- [ ] **OpenAI API key** - Not required (Groq provides free 70B model)

---

## Phase 1: Knowledge (Days 4-7)

### Tasks
- [ ] Enable RAG read access for bot (search_rugs_knowledge)
- [ ] Enable RAG write access for bot (ingest_knowledge) - Tier 1
- [ ] Enable VPS health queries (get_system_info, get_docker_status)
- [ ] Enable service log access (get_service_logs)
- [ ] Test bot querying project knowledge
- [ ] Verify audit logging captures all RAG operations

### Phase 1 Unlock Criteria
- [ ] Bot successfully queries RAG 10+ times
- [ ] No unauthorized access attempts
- [ ] Useful knowledge retrieval demonstrated

---

## Phase 2: External (Days 8-14)

### Tasks
- [ ] **Create RunPod account**
  - Sign up at runpod.io
  - Add payment method
  - Generate API key
  - Store at `/opt/openclaw/secrets/runpod.env`

- [ ] **Deploy dolphin-llama3.1-70b** (serverless, scale-to-zero)
  - vLLM worker template
  - A100 80GB GPU
  - Min workers: 0 (no idle cost)
  - Test endpoint

- [ ] Enable GitHub read operations for bot
- [ ] Enable GitHub write operations (Tier 2 approval required)
- [ ] Enable web fetch/search for documentation
- [ ] Enable Context7 documentation lookup
- [ ] Configure model router (Claude/GPT/Gemini/Dolphin)

### Phase 2 Unlock Criteria
- [ ] RunPod endpoint responding
- [ ] Model routing working (verify cost tier selection)
- [ ] Quality research outputs from bot

---

## Phase 3: Execution (Days 15-21)

### Tasks
- [ ] Enable allowlisted bash commands:
  - `git status`, `git log`, `git diff`
  - `docker ps`, `docker logs`
  - `systemctl status` (read-only)
  - `curl` (GET only, allowed domains)
  - Standard unix: `ls`, `cat`, `grep`, `find`, `df`, `free`

- [ ] Enable file read within project directories
- [ ] Enable file write to /workspace only (Tier 1)
- [ ] Enable scheduled task creation (Tier 2)
- [ ] Test bot executing status checks autonomously

### Phase 3 Unlock Criteria
- [ ] No unauthorized command attempts
- [ ] Useful automation demonstrated
- [ ] File operations working correctly

---

## Phase 4: Bridge (Days 22-26)

### Tasks
- [ ] Implement Claude Code ↔ OpenClaw bridge
  - `/claude <msg>` command in Telegram
  - `@openclaw <task>` mention in Claude Code
  - Shared workspace at `/opt/openclaw/workspace/shared`

- [ ] Enable browser automation (Playwright, read-only)
- [ ] Enable PR creation (Tier 2)
- [ ] Test bidirectional communication

### Phase 4 Unlock Criteria
- [ ] Bridge working in both directions
- [ ] Quality code suggestions from bot
- [ ] No overreach attempts

---

## Phase 5: Autonomy (Days 27-30)

### Tasks
- [ ] Enable expanded bash (still sandboxed)
- [ ] Enable Docker container management (Tier 2)
- [ ] Enable git push (Tier 2)
- [ ] Enable full browser automation
- [ ] Enable proactive monitoring
- [ ] Full capability testing

### Phase 5 Success Metrics
- [ ] Uptime > 95%
- [ ] Useful actions > 100
- [ ] Security incidents = 0
- [ ] Measurable cost optimization
- [ ] Knowledge growth +500 vectors

---

## Deferred / Low Priority

| Task | Reason | Revisit |
|------|--------|---------|
| Voice 2FA enrollment | Fingerprint is simpler | After experiment |
| Privacy.com card setup | Financial autonomy not priority | Phase 2+ |
| Base wallet funding | Financial autonomy not priority | Phase 2+ |
| System package updates | Requires reboot, low risk | Maintenance window |
| WhatsApp/Discord/Slack | Telegram sufficient | Post-experiment |

---

## Secrets Inventory

| Secret | Location | Status |
|--------|----------|--------|
| Anthropic API Key | `/root/.openclaw/.env` | ✅ Active |
| Google AI API Key | `/root/.openclaw/.env` | ✅ Active |
| Groq API Key | `/opt/openclaw/secrets/groq.env` | ✅ Active (FREE) |
| OpenRouter API Key | `/root/.openclaw/.env` | ✅ Active |
| Telegram Bot Token | `/root/.openclaw/.env` | ✅ Active |
| Fallback PIN Hash | `/root/.openclaw/.env` | ✅ Active |
| Wallet Private Key | `/opt/openclaw/secrets/wallet.env` | ✅ Stored |
| OpenAI API Key | `/opt/openclaw/secrets/openai-api.env` | ⏳ Optional |
| RunPod API Key | `/opt/openclaw/secrets/runpod.env` | ❌ Pending (Phase 2) |
| Privacy.com | `/opt/openclaw/secrets/privacy-com.env` | ❌ Deferred |

---

## Intelligence Layers (Phase 2+)

These require RunPod admin access:

| Layer | Technology | Purpose | Status |
|-------|------------|---------|--------|
| Ablated LLM | dolphin-llama3.1-70b | Uncensored reasoning | ❌ Pending |
| Code Specialist | deepseek-coder-v2 | Deep code analysis | ❌ Pending |
| Local Models | Ollama / LM Studio | Fast inference | ❌ Pending |
| Image Gen | ComfyUI | Visual content | ❌ Pending |
| Voice/TTS | Chatterbox TTS | Verbal capabilities | ❌ Pending |

All use scale-to-zero on RunPod (no idle cost).

---

## Paid Services Tracking

| Service | Type | Budget Alert | Status |
|---------|------|--------------|--------|
| Anthropic Claude | Per-token | $100/month | ✅ Active |
| Google Gemini | Per-token | $50/month | ✅ Active |
| OpenRouter | Per-token | $25/month | ✅ Active |
| Groq | FREE | N/A | ✅ Active (1000 req/day) |
| Hostinger VPS | Fixed | $15/month | ✅ Active |
| OpenAI GPT | Per-token | $50/month | ⏳ Optional |
| RunPod | Per-second | $30/month | ❌ Pending (Phase 2) |
| Privacy.com | Free/$5mo | N/A | ❌ Deferred |

---

## Quick Reference

```
Bot: @dutch_claws_bot
Wallet: 0x491245D10A16552A7f6317b9d437dA8A37d35799 (FUNDED)
Network: Base (ETH L2)
Fallback PIN: 410416
VPS: ssh vps (72.62.160.2)
MCP: http://72.62.160.2:8001/sse (rugs-expert)
Gateway: systemctl status openclaw
Logs: journalctl -u openclaw -f
```

## MCP Tools (Prefer over SSH)

```
mcp__rugs-expert__get_system_info()        # System resources
mcp__rugs-expert__get_docker_status()      # Container health
mcp__rugs-expert__get_service_logs()       # Read logs
mcp__rugs-expert__search_rugs_knowledge()  # Query RAG
mcp__rugs-expert__ingest_knowledge()       # Add to RAG
```

---

## Daily Checklist (During Experiment)

- [ ] Check gateway status
- [ ] Review audit logs for anomalies
- [ ] Check cost tracking
- [ ] Verify 2FA is working
- [ ] Note any interesting bot behaviors

---

*TODO updated: 2026-02-02 | Day 2 of 30-day experiment*
