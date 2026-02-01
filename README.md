# Claws and Pincers

> OpenClaw Personal AI Agent - Central Command Repository
> *aka moltbot aka clawedbot centcom*

## Project Overview

Autonomous AI assistant deployment with tiered authorization, voice biometric 2FA, crypto wallet integration, and RunPod LLM routing for maximum epistemic access.

## Repository Structure

```
claws-and-pincers/
├── research/           # Due diligence, architecture, setup plans
├── docs/               # Documentation and runbooks
├── config/             # Configuration templates
└── README.md
```

## Research Documents

| Document | Purpose |
|----------|---------|
| [Due Diligence](research/openclaw-due-diligence.md) | Project evaluation and risk assessment |
| [Authorization Architecture](research/openclaw-authorization-architecture.md) | 5-tier autonomy with voice 2FA |
| [Setup Plan](research/openclaw-setup-plan.md) | Step-by-step implementation |
| [RAG Knowledge Plan](research/openclaw-rag-knowledge-plan.md) | Knowledge ingestion strategy |
| [Burner Card Comparison](research/openclaw-burner-card-comparison.md) | Virtual card provider analysis |

## Configuration Summary

| Component | Choice |
|-----------|--------|
| **Telegram** | New bot via @BotFather |
| **2FA Method** | Voice biometric + fallback PIN |
| **Crypto Wallet** | USDC on Base network |
| **Spending Card** | Privacy.com (Free tier) |
| **RunPod LLMs** | Ablated models for research integrity |
| **Deployment** | Docker sandbox with tiered authorization |

## Security Status

- [x] SSH hardened (key-only authentication)
- [ ] System packages updated
- [ ] OpenClaw deployed
- [ ] Voice enrollment completed
- [ ] Wallet configured

## Infrastructure

- **Host**: srv1216617 (Hostinger VPS)
- **OS**: Ubuntu 24.04 LTS
- **Resources**: 4 vCPU, 16GB RAM, 200GB NVMe
- **VPN**: Tailscale (100.113.138.27)

---

*Project initiated: 2026-01-31*
