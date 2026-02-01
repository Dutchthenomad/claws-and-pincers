# OpenClaw 30-Day Experiment TODO

> **Last Updated**: 2026-02-01
> **Current Phase**: 0 (Foundation)
> **Experiment Start**: 2026-02-01
> **Target Completion**: 2026-03-03

---

## Phase 0: Foundation (Days 1-3)

### Critical Path
- [ ] **Samsung fingerprint 2FA** via Telegram WebApp
  - Create WebAuthn page on VPS (Tailscale-only)
  - Configure Telegram deep link to auth page
  - Test fingerprint → webhook → approval flow

- [ ] **OpenAI API key**
  - Create account at platform.openai.com
  - Generate API key
  - Store at `/opt/openclaw/secrets/openai-api.env`

- [ ] **Google AI API key**
  - Create project at console.cloud.google.com
  - Enable Generative Language API
  - Generate API key
  - Store at `/opt/openclaw/secrets/google-ai.env`

- [ ] **Cost registry configuration**
  - Create `/opt/openclaw/config/cost-registry.yaml`
  - Define all paid services with budget alerts
  - Set up TimescaleDB cost_events table

### Phase 0 Unlock Criteria
- [ ] 2FA tested and working (3+ successful authentications)
- [ ] All 3 LLM API keys configured
- [ ] Cost tracking capturing events

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
| Anthropic API Key | `/opt/openclaw/secrets/anthropic-api.env` | ✅ Active |
| Telegram Bot Token | `/opt/openclaw/secrets/telegram-bot.env` | ✅ Active |
| Fallback PIN Hash | `/opt/openclaw/secrets/telegram-bot.env` | ✅ Active |
| Wallet Private Key | `/opt/openclaw/secrets/wallet.env` | ✅ Stored |
| OpenAI API Key | `/opt/openclaw/secrets/openai-api.env` | ❌ Pending |
| Google AI API Key | `/opt/openclaw/secrets/google-ai.env` | ❌ Pending |
| RunPod API Key | `/opt/openclaw/secrets/runpod.env` | ❌ Pending |
| Privacy.com | `/opt/openclaw/secrets/privacy-com.env` | ❌ Deferred |

---

## Paid Services Tracking

| Service | Type | Budget Alert | Status |
|---------|------|--------------|--------|
| Anthropic Claude | Per-token | $100/month | ✅ Active |
| OpenAI GPT | Per-token | $50/month | ❌ Pending |
| Google Gemini | Per-token | $50/month | ❌ Pending |
| RunPod | Per-second | $30/month | ❌ Pending |
| Hostinger VPS | Fixed | $15/month | ✅ Active |
| Privacy.com | Free/$5mo | N/A | ❌ Deferred |

---

## Quick Reference

```
Bot: @dutch_claws_bot
Wallet: 0x491245D10A16552A7f6317b9d437dA8A37d35799
Fallback PIN: 410416
VPS: ssh vps
Gateway: systemctl status openclaw
Logs: journalctl -u openclaw -f
```

---

## Daily Checklist (During Experiment)

- [ ] Check gateway status
- [ ] Review audit logs for anomalies
- [ ] Check cost tracking
- [ ] Verify 2FA is working
- [ ] Note any interesting bot behaviors

---

*TODO updated: 2026-02-01 | 30-day experiment in progress*
