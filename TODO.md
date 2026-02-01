# OpenClaw Deployment TODO

> **Last Updated**: 2026-02-01
> **Status**: Phase 4 Complete, Phase 5 In Progress

---

## Pending Actions (Waiting on External)

### Wallet Funding
- [ ] **Fund hot wallet with ETH** (for gas)
  - Address: `0x491245D10A16552A7f6317b9d437dA8A37d35799`
  - Amount: 0.01-0.02 ETH (~$25-50)
  - Network: Base (Chain ID 8453)
  - Status: Waiting on position orders to fill

- [ ] **Fund hot wallet with USDC**
  - Address: `0x491245D10A16552A7f6317b9d437dA8A37d35799`
  - Amount: $50-100 USDC
  - Contract: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
  - Status: Waiting on position orders to fill

### Verify Wallet
- [ ] Check balance on BaseScan: https://basescan.org/address/0x491245D10A16552A7f6317b9d437dA8A37d35799
- [ ] Test small transaction after funding

---

## Completed Setup Phases

### Phase 1: Prerequisites
- [x] SSH hardened (key-only root login)
- [x] Directory structure created (`/opt/openclaw/`)
- [ ] System packages updated (25 pending - requires reboot)

### Phase 2: Telegram Bot
- [x] Bot created: `@dutch_claws_bot`
- [x] Bot ID: `8503309726`
- [x] Owner chat ID: `6490779444`
- [x] Settings configured
- [x] Token stored securely

### Phase 3: Voice 2FA
- [x] Voiceprint config created
- [x] Fallback PIN generated: `410416`
- [x] Enrollment phrases defined
- [ ] Voice enrollment (after OpenClaw running)

### Phase 4: Crypto Wallet
- [x] Wallet generated: `0x491245D10A16552A7f6317b9d437dA8A37d35799`
- [x] Private key stored securely
- [x] Wallet config created with limits
- [ ] Wallet funded (pending)
- [ ] Test transaction (after funding)

### Phase 5: Docker Sandbox
- [ ] Docker network created
- [ ] Docker compose configured
- [ ] Container security hardening
- [ ] Test container launch

### Phase 6: Authorization System
- [ ] Tier config created
- [ ] Integration configs
- [ ] Test tier enforcement

### Phase 7: RunPod LLM
- [ ] RunPod account created
- [ ] API key stored
- [ ] Endpoint deployed
- [ ] Model router configured

---

## Secrets Inventory

| Secret | Location | Status |
|--------|----------|--------|
| Telegram Bot Token | `/opt/openclaw/secrets/telegram-bot.env` | ✅ |
| Fallback PIN Hash | `/opt/openclaw/secrets/telegram-bot.env` | ✅ |
| Anthropic API Key | `/opt/openclaw/secrets/anthropic-api.env` | ✅ |
| Wallet Private Key | `/opt/openclaw/secrets/wallet.env` | ✅ |
| RunPod API Key | `/opt/openclaw/secrets/runpod.env` | ❌ Pending |
| Privacy.com API | `/opt/openclaw/secrets/privacy-com.env` | ❌ Pending |

---

## Quick Reference

### Wallet Address (Base Network)
```
0x491245D10A16552A7f6317b9d437dA8A37d35799
```

### Fallback PIN
```
410416
```

### Bot Username
```
@dutch_claws_bot
```

### Key URLs
- BaseScan Wallet: https://basescan.org/address/0x491245D10A16552A7f6317b9d437dA8A37d35799
- Base USDC Contract: https://basescan.org/token/0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913

---

## System Maintenance

### Pending Updates (Schedule Reboot)
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

Packages waiting:
- Kernel: 6.8.0-90 → 6.8.0-94
- Docker CE: 29.1.5 → 29.2.0
- Plus 23 others

---

*This file tracks deployment progress. Update as tasks complete.*
