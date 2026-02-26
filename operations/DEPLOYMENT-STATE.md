# Deployment State — srv1216617

**Last updated:** 2026-02-26
**Server:** srv1216617 (Hostinger VPS)
**OS:** Ubuntu, Linux 6.8.0-101-generic
**Resources:** 15GB RAM, 193GB disk (52% used)

---

## Running Containers (23)

| Container | Image | Port | Status |
|-----------|-------|------|--------|
| openclaw-orchestrator | ghcr.io/hostinger/hvps-openclaw:latest | 127.0.0.1:8081 | healthy |
| openclaw-researcher | ghcr.io/hostinger/hvps-openclaw:latest | 127.0.0.1:8082 | healthy |
| openclaw-developer | ghcr.io/hostinger/hvps-openclaw:latest | 127.0.0.1:8083 | healthy |
| openclaw-sysadmin | ghcr.io/hostinger/hvps-openclaw:latest | 127.0.0.1:8084 | healthy |
| openclaw-reviewer | ghcr.io/hostinger/hvps-openclaw:latest | 127.0.0.1:8085 | healthy |
| openclaw-memory | openclaw-memory (custom) | 127.0.0.1:8002 | healthy |
| rag-api | rag-api (custom) | 127.0.0.1:8000 | healthy |
| rugs-mcp | rugs-mcp (custom) | 127.0.0.1:8001 | healthy |
| rugs-feed | vectra-pipeline (custom) | 127.0.0.1:9016 | healthy |
| rugs-sanitizer | vectra-pipeline (custom) | 127.0.0.1:9017 | healthy |
| n8n | n8nio/n8n:latest | 127.0.0.1:5678 | running |
| n8n-postgres | postgres:16 | internal only | running |
| ollama | ollama/ollama:latest | 127.0.0.1:11434 | healthy |
| qdrant | qdrant/qdrant:latest | 127.0.0.1:6333-6334 | healthy |
| timescaledb | timescale/timescaledb:latest-pg15 | 127.0.0.1:5433 | healthy |
| rabbitmq | rabbitmq:3-management | 127.0.0.1:5672, 127.0.0.1:15672 | healthy |
| grafana | grafana/grafana:12.3.2 | 127.0.0.1:3000 | running |
| grafana-postgres | postgres:17-alpine | internal only | healthy |
| metabase | metabase/metabase:latest | 127.0.0.1:3002 | running |
| metabase-postgres | postgres:16 | internal only | healthy |
| uptime-kuma | louislam/uptime-kuma:latest | 127.0.0.1:3001 | healthy |
| dozzle | amir20/dozzle:v9.0.1 | 127.0.0.1:8080 | healthy |
| apprise-api | linuxserver/apprise-api:latest | 127.0.0.1:8003 | healthy |

All ports bound to 127.0.0.1 (localhost only). External access via Tailscale VPN.

---

## Docker Compose File Locations

| Stack | Path |
|-------|------|
| Discord Agents (5) | `/opt/openclaw/discord-agents/docker-compose.agents.yml` |
| n8n + Postgres | `/docker/n8n/docker-compose.yml` |
| RAG stack (rag-api, rugs-mcp, rugs-feed, rugs-sanitizer, qdrant, timescaledb, rabbitmq) | `/root/rag-stack/docker-compose.yml` |
| Grafana + Postgres | `/docker/grafana-53ys/docker-compose.yml` |
| Metabase + Postgres | `/docker/metabase-62yh/docker-compose.yml` |
| Ollama | `/docker/ollama-zlwk/docker-compose.yml` |
| Uptime Kuma | `/docker/uptime-kuma-vwqd/docker-compose.yml` |
| Apprise API | `/docker/apprise-api-khxp/docker-compose.yml` |
| Dozzle | `/docker/dozzle-t70t/docker-compose.yml` |
| OpenClaw Memory | `/root/openclaw-memory/docker-compose.yml` |
| RUGS MCP | `/root/rugs-mcp/docker-compose.yml` |

---

## Key Config Locations

| Config | Path |
|--------|------|
| Agent workspace files | `/opt/openclaw/discord-agents/{agent}-data/.openclaw/workspace/` |
| Agent runtime config | `/opt/openclaw/discord-agents/{agent}-data/.openclaw/openclaw.json` |
| Governance files (shared mount) | `/opt/openclaw/discord-agents/shared-governance/` (host) mounted read-only at `/opt/governance/` (container) |
| Model routing | `/opt/openclaw/config/model-routing.yaml` |
| Agent YAML profiles | `/opt/openclaw/config/agents/` |
| Source of truth doc | `/opt/openclaw/CONFIG-SOURCE-OF-TRUTH.md` |
| Image version pins | `/opt/openclaw/IMAGE-PINS.md` |

---

## Secrets Locations

All files chmod 600, owned by root.

| File | Contents |
|------|----------|
| `/opt/openclaw/discord-agents/.env` | Discord tokens, OpenRouter API key |
| `/root/.openclaw/.env` | All API keys, gateway auth token |
| `/docker/n8n/.env` | n8n encryption key, postgres password |
| `/root/openclaw-memory/.env` | Memory API key |

---

## Security Posture

- **Firewall (UFW):** Default deny incoming. Only SSH (22) and Tailscale Cockpit (9090) allowed.
- **SSH:** Key-only authentication. Password auth disabled (including cloud-init override).
- **Intrusion prevention:** Fail2ban protecting SSH.
- **VPN:** Tailscale connected (100.113.138.27). All service UIs accessed via Tailscale.
- **Docker:** All ports bound to 127.0.0.1. No services exposed directly to internet.
- **Monitoring:** Monarx security scanner (Hostinger), Uptime Kuma for service health.

---

## Per-Agent Model Assignments

| Agent | Model (OpenRouter) |
|-------|--------------------|
| Orchestrator | openrouter/anthropic/claude-opus-4.6 |
| Researcher | openrouter/x-ai/grok-4.1-fast |
| Developer | openrouter/minimax/minimax-m2.5 |
| Sysadmin | openrouter/moonshotai/kimi-k2.5 |
| Reviewer | openrouter/google/gemini-3-flash-preview |

Model routing configuration: `/opt/openclaw/config/model-routing.yaml`

---

## Known Issues

- 3 n8n credentials need re-entry (encrypted with old key after rotation)
- Legacy API keys pending revocation on OpenRouter dashboard (C-3)
- Network segmentation deferred: agents share n8n_default bridge with all services (H-13)
