# OpenClaw Authorization Architecture

> **Purpose**: Define tiered autonomy with human-in-the-loop controls for sensitive operations
> **Created**: 2026-01-31
> **Status**: DESIGN PHASE

---

## Autonomy Tiers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 0: UNRESTRICTED                             │
│         (Sandbox-contained, no external impact)                     │
│                                                                     │
│  • Research & web browsing          • Code generation               │
│  • File operations in /workspace    • Conversation & memory         │
│  • Local tool execution             • RAG queries                   │
│  • Message responses                • Skill execution               │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 1: NOTIFY ONLY                              │
│         (Agent proceeds, human informed async)                      │
│                                                                     │
│  • External API calls (read-only)   • Scheduled task creation       │
│  • Email drafts (not sent)          • Webhook registrations         │
│  • Git operations (local only)      • Resource usage > threshold    │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 2: APPROVAL REQUIRED                        │
│         (Agent pauses, awaits confirmation via Telegram)            │
│                                                                     │
│  • Send emails                      • Post to social media          │
│  • Create accounts                  • Modify external services      │
│  • Git push to remote               • Install packages              │
│  • Access secrets vault             • Network config changes        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 3: 2FA REQUIRED                             │
│         (Biometric/second device verification)                      │
│                                                                     │
│  • Financial transactions           • Root/sudo commands            │
│  • Secret rotation                  • Container escape actions      │
│  • Backup/restore operations        • User permission changes       │
│  • VPS configuration changes        • Firewall modifications        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    TIER 4: HARDCODED DENY                           │
│         (Never permitted, no override)                              │
│                                                                     │
│  • Delete critical system files     • Disable security services     │
│  • Expose secrets publicly          • Modify this authorization     │
│  • rm -rf /                         • Disable logging/audit         │
│  • SSH key modifications            • Firewall disable              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Sensitive Data Registry

### Location Strategy

```
PRIMARY (Offline/Encrypted):
├── /secure/vault/                    # Encrypted volume (LUKS)
│   ├── master-secrets.yaml           # All API keys, tokens
│   ├── wallet-keys/                  # Crypto wallet private keys
│   └── recovery-codes/               # 2FA recovery codes
│
SECONDARY (Second Device):
├── Bitwarden/1Password vault         # Cloud-synced, biometric unlock
│   └── OpenClaw folder               # Dedicated section
│
RUNTIME (Agent-Accessible, Read-Only):
├── /opt/openclaw/secrets/            # Mounted read-only into container
│   ├── anthropic-api.env             # Claude API key only
│   └── telegram-bot.env              # Bot token only
```

### Secret Classification

| Secret Type | Storage | Agent Access | Unlock Method |
|-------------|---------|--------------|---------------|
| Claude API Key | Runtime | READ | None (always available) |
| Telegram Bot Token | Runtime | READ | None (always available) |
| Burner Card Number | Vault | REQUEST | Telegram approval |
| Crypto Wallet (Hot) | Vault | REQUEST | 2FA + Biometric |
| Crypto Wallet (Cold) | Offline | NEVER | Manual only |
| VPS Root Password | Vault | NEVER | Manual only |
| SSH Private Keys | Vault | NEVER | Manual only |
| OAuth Refresh Tokens | Vault | REQUEST | Telegram approval |
| Database Passwords | Runtime | READ | None (local only) |

---

## 2FA Implementation Options

### Option A: Telegram-Native (Recommended for MVP)

```
Agent requests Tier 3 action
        │
        ▼
┌───────────────────────────────┐
│  Telegram Bot sends request   │
│  with inline keyboard:        │
│                               │
│  "🔐 ROOT ACTION REQUESTED    │
│   Action: apt upgrade         │
│   Risk: TIER 3                │
│                               │
│  [✅ Approve] [❌ Deny]       │
│                               │
│  Reply with voice message     │
│  saying 'authorize' to        │
│  confirm with voice print"    │
└───────────────────────────────┘
        │
        ▼
  Voice message analyzed OR
  Inline button + PIN code
        │
        ▼
  Action proceeds or denied
```

### Option B: External 2FA Service

| Service | Biometric | Second Device | Complexity |
|---------|-----------|---------------|------------|
| Duo Security | Yes (mobile) | Push notification | Medium |
| Authelia | TOTP/WebAuthn | Yes | High |
| Teleport | Yes | Hardware key | High |
| Custom (n8n webhook) | Via mobile app | Telegram + n8n | Low |

### Option C: Hardware Security Key (Future)

- YubiKey for Tier 3+ actions
- WebAuthn integration
- Physical presence required

---

## Financial Autonomy Controls

### Crypto Wallet Setup

```yaml
wallets:
  hot_wallet:
    purpose: "Agent-controlled spending"
    type: "ETH/EVM compatible"
    max_balance: "$500 equivalent"
    per_transaction_limit: "$50"
    daily_limit: "$200"
    approval_required: "Tier 2 (Telegram confirm)"

  cold_wallet:
    purpose: "Savings, large amounts"
    type: "Hardware wallet (Ledger/Trezor)"
    agent_access: "NEVER"
    human_only: true
```

### Burner Card Setup

```yaml
burner_card:
  provider: "Privacy.com / Revolut / etc."
  purpose: "Online purchases, subscriptions"
  per_transaction_limit: "$100"
  monthly_limit: "$500"
  merchant_locks:
    - "category:digital_goods"
    - "category:software"
  blocked_categories:
    - "gambling"
    - "crypto_exchange"  # Use dedicated wallet instead
    - "wire_transfer"
  approval_required: "Tier 2 (Telegram confirm)"
  notifications: "All transactions → Telegram"
```

---

## Authorization Flow Implementation

### Telegram Bot Commands

```
/status          - Show pending authorization requests
/approve <id>    - Approve a Tier 2 request
/deny <id>       - Deny a request with optional reason
/authorize       - Start 2FA flow for Tier 3 request
/limits          - Show current spending limits
/pause           - Pause all agent autonomous actions
/resume          - Resume autonomous operation
/audit <hours>   - Show recent actions (default: 24h)
/emergency       - Kill all agent processes immediately
```

### Request Queue Structure

```yaml
# /opt/openclaw/data/authorization-queue/pending/
request_12345.yaml:
  id: "12345"
  timestamp: "2026-01-31T15:30:00Z"
  tier: 2
  action: "send_email"
  parameters:
    to: "vendor@example.com"
    subject: "API inquiry"
    body_preview: "Hello, I am writing to inquire about..."
  context: "User asked agent to contact vendor about API pricing"
  timeout: "4h"
  status: "pending"
```

---

## Audit & Logging

### All Actions Logged To

1. **Local file**: `/opt/openclaw/data/audit/YYYY-MM-DD.jsonl`
2. **TimescaleDB**: `openclaw.action_log` table
3. **Telegram**: Daily digest + real-time for Tier 2+

### Log Schema

```json
{
  "timestamp": "2026-01-31T15:30:00.123Z",
  "action_id": "uuid",
  "tier": 1,
  "action_type": "external_api_call",
  "target": "api.example.com",
  "parameters": {},
  "authorization": {
    "method": "auto",
    "approved_by": null
  },
  "result": "success",
  "session_id": "telegram_12345",
  "tokens_used": 1500
}
```

---

## Emergency Controls

### Kill Switch Methods

| Method | Trigger | Effect |
|--------|---------|--------|
| `/emergency` | Telegram command | Stop all containers, preserve state |
| `curl localhost:18789/emergency` | Local API | Same as above |
| Docker stop | Manual | `docker stop openclaw-gateway` |
| UFW block | Nuclear | `ufw deny out from any` |

### Auto-Pause Triggers

- Failed 2FA attempts > 3 in 1 hour
- Spending > daily limit
- Unusual activity pattern detected
- Container resource limits hit
- Network egress anomaly

---

## Implementation Phases

### Phase 1: Basic Authorization (MVP)
- [x] Design authorization tiers
- [ ] Set up Telegram bot with /approve /deny commands
- [ ] Create request queue system
- [ ] Implement Tier 2 Telegram confirmation

### Phase 2: 2FA Integration
- [ ] Add voice message verification (voiceprint)
- [ ] Or: Add PIN code requirement for Tier 3
- [ ] Integrate with n8n for workflow automation

### Phase 3: Financial Controls
- [ ] Set up Privacy.com or similar burner card
- [ ] Create hot wallet with spending limits
- [ ] Implement transaction notifications

### Phase 4: Advanced Security
- [ ] Add hardware key support (YubiKey)
- [ ] Implement anomaly detection
- [ ] Add session recording for audit

---

## Questions to Resolve

1. **Voice vs PIN**: For Tier 3, prefer voice biometric or PIN code via Telegram?
2. **Timeout behavior**: If no response in X hours, auto-deny or keep pending?
3. **Crypto wallet**: Which chain/token for the hot wallet? (ETH, USDC, etc.)
4. **Burner card provider**: Privacy.com (US) or alternative?
5. **Daily digest**: What time should the audit summary arrive?

---

*Architecture document: v0.1 | Created: 2026-01-31*
