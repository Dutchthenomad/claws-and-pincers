# Debug & Deployment Fix Plan — OpenClaw Agent Team

> **Date**: 2026-02-28
> **Author**: Claude Opus 4.6 + Devin
> **Status**: APPROVED — Execute in fresh Claude Code session
> **Guild ID**: 1472374974340665477
> **Devin's Discord User ID**: 13362138764

---

## Root Cause Analysis

### Critical Finding: Wrong Architecture

The current deployment runs **5 separate OpenClaw containers**, each as its own gateway with its own config. But the OpenClaw multi-agent architecture is designed as a **single gateway with multiple agents** routed via bindings.

**Current (broken):**
```
Container 1 (orchestrator) → port 8081 → own openclaw.json → OOM crash
Container 2 (researcher)   → port 8082 → own openclaw.json → OOM crash
Container 3 (developer)    → port 8083 → own openclaw.json → OOM crash
Container 4 (sysadmin)     → port 8084 → own openclaw.json → OOM crash
Container 5 (reviewer)     → port 8085 → own openclaw.json → OOM crash
```

Each container loads the full OpenRouter model catalog independently ("Building Nexos models list"), hits the 256MB V8 heap limit, and dies. 5x the memory waste, 5x the OOM risk.

**Correct (per OpenClaw docs):**
```
Single Gateway Container → port 18789 → openclaw.json5 with agents.list[] → 5 agents
  ├── orchestrator (Discord account: orchestrator)
  ├── researcher   (Discord account: researcher)
  ├── developer    (Discord account: developer)
  ├── sysadmin     (Discord account: sysadmin)
  └── reviewer     (Discord account: reviewer)
```

From the docs: *"Each agent operates as an isolated entity... on a single Gateway instance through deterministic routing bindings."*

### All Issues

| Issue | Impact | Fix |
|-------|--------|-----|
| OpenClaw version 2026.2.9 (17 releases behind) | OOM bug, missing features, deprecated config | Update to 2026.2.26 |
| Wrong architecture: 5 containers instead of 1 | 5x resource waste, wrong multi-agent pattern | Single gateway container |
| `OPENCLAW_GATEWAY_TOKEN` never set | Gateway auth fails on restart | Generate and set in .env |
| Telegram artifacts in deployed .env | Dead config, confusion | Remove TELEGRAM_BOT_TOKEN, TELEGRAM_OWNER_ID |
| Config schema uses deprecated `identity` at root | Warning on every start | Already fixed in openclaw.json5 (uses agents.list[].identity) |
| No `NODE_OPTIONS` for V8 heap | 256MB default too small | Set `NODE_OPTIONS=--max-old-space-size=1536` |
| Per-container openclaw.json has single-agent flat config | Doesn't match multi-agent schema | Use the repo's openclaw.json5 instead |
| Bindings only route to orchestrator | Other agents unreachable | Add per-account bindings |
| Guild allowlist uses wildcard `"*"` | Any server can interact | Lock to guild 1472374974340665477 |

### Confirmed Decisions

| Decision | Answer |
|----------|--------|
| Architecture | **Single gateway** (per official OpenClaw docs) |
| Deployment method | **Docker container** (consistent with existing infra) |
| Sandbox mode | **All agents sandbox: off** initially (enable later) |
| Agent-to-agent comms | **Enabled** (all 5 agents in allow list) |
| Authority | **Official OpenClaw docs supersede repo configs** |

---

## Execution Plan

### Prerequisites (Verify Before Starting)

```bash
# 1. Verify Discord bot tokens exist and are non-empty
cat /opt/openclaw/secrets/discord-bots.env | grep -c "TOKEN="
# Expected: 5 lines with actual values

# 2. Verify OpenRouter API key
cat /opt/openclaw/secrets/openrouter-api.env | grep -c "KEY="
# Expected: 1 line with actual value

# 3. Check available memory for the new container
free -h | grep Mem
# Need at least 2GB free for the gateway
```

### Phase 0: Backup & Snapshot (5 min)

```bash
# Create timestamped backup
BACKUP_DIR="/opt/openclaw/discord-agents.bak.$(date +%Y%m%d)"
cd /opt/openclaw/discord-agents
cp -r . "$BACKUP_DIR"

# Save current container configs from inside each container
for agent in orchestrator researcher developer sysadmin reviewer; do
  docker cp openclaw-$agent:/data/.openclaw/openclaw.json \
    "$BACKUP_DIR/$agent-openclaw.json" 2>/dev/null || true
done

# Record current container state
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Image}}" | grep openclaw > "$BACKUP_DIR/container-state.txt"
echo "Backup saved to: $BACKUP_DIR"
```

### Phase 1: Stop & Remove Old Containers (2 min)

```bash
cd /opt/openclaw/discord-agents
docker compose -f docker-compose.agents.yml down

# Verify all 5 agent containers are gone (openclaw-memory should remain)
docker ps | grep openclaw
# Expected: only openclaw-memory
```

### Phase 2: Install OpenClaw CLI on Host (5 min)

Install the latest OpenClaw globally so we have `openclaw doctor`, `openclaw health`, and the Docker setup tooling.

```bash
# Install latest OpenClaw (skip onboarding wizard)
curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard

# Verify version
openclaw --version
# Expected: 2026.2.26 (or newer)

# Run doctor for initial setup and migrations
openclaw doctor
```

### Phase 3: Prepare Single-Gateway Config (10 min)

#### 3A: Create directory structure

```bash
mkdir -p ~/.openclaw/{workspace-orchestrator,workspace-researcher,workspace-developer,workspace-sysadmin,workspace-reviewer}
mkdir -p ~/.openclaw/agents/{orchestrator,researcher,developer,sysadmin,reviewer}/agent
```

#### 3B: Build the .env file

Combine all secrets into a single .env (NO Telegram artifacts):

```bash
# Source existing secrets
source /opt/openclaw/secrets/discord-bots.env
source /opt/openclaw/secrets/openrouter-api.env

# Generate gateway token
GATEWAY_TOKEN=$(openssl rand -hex 32)
echo "Gateway token: $GATEWAY_TOKEN"
echo "SAVE THIS TOKEN — you'll need it to log into the Control UI"

# Write combined .env
cat > ~/.openclaw/.env << EOF
# Discord Bot Tokens
DISCORD_ORCHESTRATOR_TOKEN=${DISCORD_ORCHESTRATOR_TOKEN}
DISCORD_RESEARCHER_TOKEN=${DISCORD_RESEARCHER_TOKEN}
DISCORD_DEVELOPER_TOKEN=${DISCORD_DEVELOPER_TOKEN}
DISCORD_SYSADMIN_TOKEN=${DISCORD_SYSADMIN_TOKEN}
DISCORD_REVIEWER_TOKEN=${DISCORD_REVIEWER_TOKEN}

# LLM API Keys (OpenRouter only — no direct Anthropic)
OPENROUTER_API_KEY=${OPENROUTER_API_KEY}

# Gateway Authentication
OPENCLAW_GATEWAY_TOKEN=${GATEWAY_TOKEN}
GATEWAY_AUTH_TOKEN=${GATEWAY_TOKEN}
EOF
chmod 600 ~/.openclaw/.env

# Also save the gateway token separately for reference
echo "$GATEWAY_TOKEN" > /opt/openclaw/secrets/gateway-token.txt
chmod 600 /opt/openclaw/secrets/gateway-token.txt
```

#### 3C: Deploy the config with fixes

Copy the repo's `openclaw.json5` and apply required fixes:

```bash
cp /root/claws-and-pincers/openclaw.json5 ~/.openclaw/openclaw.json5
```

Then edit `~/.openclaw/openclaw.json5` with these changes:

**Fix 1 — Lock guild allowlist** (replace the `guilds: { "*": ... }` wildcard):
```json5
guilds: {
  "1472374974340665477": {
    requireMention: true,
  },
},
```

**Fix 2 — Expand bindings** (replace the single orchestrator binding):
```json5
bindings: [
  { agentId: "orchestrator", match: { channel: "discord", accountId: "orchestrator" } },
  { agentId: "discord-researcher", match: { channel: "discord", accountId: "researcher" } },
  { agentId: "developer", match: { channel: "discord", accountId: "developer" } },
  { agentId: "sysadmin", match: { channel: "discord", accountId: "sysadmin" } },
  { agentId: "reviewer", match: { channel: "discord", accountId: "reviewer" } },
  // Fallback: unmatched Discord traffic goes to orchestrator
  { agentId: "orchestrator", match: { channel: "discord" } },
],
```

**Fix 3 — Set all sandbox modes to off**:
```json5
// In agents.defaults:
sandbox: { mode: "off" },

// In each agent in agents.list[]:
sandbox: { mode: "off" },
```

**Fix 4 — Set gateway auth to use env var**:
```json5
gateway: {
  port: 18789,
  mode: "local",
  bind: "lan",  // Changed from "loopback" — container needs LAN binding
  controlUi: { enabled: true, basePath: "/" },
  auth: { mode: "token", token: "${OPENCLAW_GATEWAY_TOKEN}" },
},
```

**Fix 5 — Run `openclaw doctor`** to validate and migrate:
```bash
openclaw doctor
```

### Phase 4: Build & Deploy Docker Container (10 min)

#### 4A: Use the official Docker setup

The official OpenClaw Docker workflow is the authority. Check if the installer created a docker-compose or if we need to set one up:

```bash
# Check if docker-setup.sh exists after install
which openclaw && ls $(dirname $(which openclaw))/../docker-setup.sh 2>/dev/null

# If docker-setup.sh exists, use it:
# ./docker-setup.sh

# If not, create compose manually:
mkdir -p /opt/openclaw/gateway
```

#### 4B: Manual compose (if docker-setup.sh not available)

```yaml
# /opt/openclaw/gateway/docker-compose.yml
services:
  openclaw-gateway:
    image: ghcr.io/nicepkg/openclaw:latest
    container_name: openclaw-gateway
    init: true
    restart: unless-stopped
    ports:
      - "127.0.0.1:18789:18789"
    env_file:
      - /root/.openclaw/.env
    environment:
      - HOME=/home/node
      - TERM=xterm-256color
      - NODE_OPTIONS=--max-old-space-size=1536
      - TZ=America/New_York
    volumes:
      - /root/.openclaw:/home/node/.openclaw
    networks:
      - n8n_default
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 512M
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:18789/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

networks:
  n8n_default:
    external: true
```

**IMPORTANT**: The image name may need adjustment. Check these in order:
1. `ghcr.io/nicepkg/openclaw:latest` (official GitHub registry)
2. `ghcr.io/hostinger/hvps-openclaw:latest` (Hostinger — currently used but outdated)
3. Build locally: `docker build -t openclaw:local .` from the OpenClaw source repo

If none of the registry images are current, clone the OpenClaw repo and build:
```bash
git clone https://github.com/nicepkg/openclaw.git /opt/openclaw/source
cd /opt/openclaw/source
docker build -t openclaw:local -f Dockerfile .
# Then use image: openclaw:local in the compose file
```

#### 4C: Start the gateway

```bash
cd /opt/openclaw/gateway  # or wherever the compose file is
docker compose up -d

# Watch logs for startup
docker logs -f openclaw-gateway
```

**Expected startup sequence:**
1. "Fixing data permissions" (or similar init)
2. "Building Nexos models list" (should complete without OOM now)
3. "Gateway listening on port 18789"
4. "Discord: connected" (for each of 5 accounts)
5. Agent list loaded (5 agents)

**If OOM still occurs**: The model list fetch may still be too large. Add to environment:
```yaml
environment:
  - OPENCLAW_SKIP_MODEL_LIST=true  # If this env var exists
  # OR in openclaw.json5, check for a models.fetchList: false option
```

### Phase 5: Verify All Systems (10 min)

#### 5A: Gateway health
```bash
# From host
curl -s http://127.0.0.1:18789/health
# Expected: {"status":"ok"} or similar

# Via openclaw CLI
openclaw health

# Check gateway status
openclaw gateway status
```

#### 5B: Control UI
- Open `http://100.113.138.27:18789/` in browser (via Tailscale)
- Log in with the GATEWAY_AUTH_TOKEN generated in Phase 3B
- Verify all 5 agents visible in the dashboard
- Check Presence tab — all 5 should show as active

#### 5C: Discord — individual agent response
Test each agent in the Discord server (guild 1472374974340665477):
1. `@Orchestrator hello` → should respond
2. `@Researcher hello` → should respond
3. `@Developer hello` → should respond
4. `@Sysadmin hello` → should respond
5. `@Reviewer hello` → should respond

#### 5D: Agent-to-agent communication
In Discord, tell the Orchestrator:
> "Ask the Researcher to look up the current OpenClaw version and report back."

This tests:
- Orchestrator receives the message
- Orchestrator uses `sessions_send` to message Researcher
- Researcher processes the request
- Researcher responds (either back to Orchestrator or in the channel)

#### 5E: Stability check
```bash
# Let it run for 10 minutes, then check:
docker stats openclaw-gateway --no-stream
# Memory should be stable, not growing unbounded

# Check for any restarts
docker inspect openclaw-gateway --format='Restarts: {{.RestartCount}}'
# Expected: 0
```

### Phase 6: Clean Up (5 min)

```bash
# Remove deprecated compose files (keep backups for 7 days)
mv /opt/openclaw/docker/docker-compose.yml /opt/openclaw/docker/docker-compose.yml.deprecated
mv /opt/openclaw/runtime/docker-compose.yml /opt/openclaw/runtime/docker-compose.yml.deprecated

# Clean stale Docker images
docker image prune -f

# Remove Telegram artifacts from any remaining .env files
grep -rl "TELEGRAM" /opt/openclaw/ --include="*.env" 2>/dev/null
# Manually remove TELEGRAM_BOT_TOKEN and TELEGRAM_OWNER_ID lines from those files
```

### Phase 7: Update Project Documentation (10 min)

After successful deployment, update these files in the repo:

1. **`openclaw.json5`** — Commit the fixed version with:
   - Expanded bindings (per-account routing)
   - Guild locked to `1472374974340665477`
   - All sandbox modes set to `off`
   - Gateway bind set to `lan`

2. **`TODO.md`** — Add deployment fix as completed Phase 1F item

3. **`docs/plans/SESSION-CONTINUITY.md`** — Update:
   - Architecture: single gateway on port 18789 (not 5 containers on 8081-8085)
   - Container count: reduced from 23 to 19 (5 agents → 1 gateway)
   - Docker service map: single `openclaw-gateway` entry

4. **`operations/DEPLOYMENT-STATE.md`** — Reflect new container topology

5. **`CLAUDE.md`** — Update:
   - Infrastructure section: single gateway, port 18789
   - Remove references to ports 8081-8085
   - Update key commands section

6. **`deployment/discord-agents/docker-compose.agents.yml`** — Archive or delete (replaced by gateway compose)

7. **Commit and push**:
   ```bash
   cd /root/claws-and-pincers
   git add -A
   git commit -m "fix: replace 5 OOM containers with single gateway architecture

   Root cause: OpenClaw multi-agent runs as single gateway with routing
   bindings, not 5 separate containers. All 5 were OOM crash-looping
   (v2026.2.9 → v2026.2.26). Fixed bindings, guild allowlist, sandbox
   mode, and gateway auth."
   git push origin main
   ```

---

## Rollback Plan

If the new deployment fails:

```bash
# Restore old compose and data
BACKUP_DIR="/opt/openclaw/discord-agents.bak.<YYYYMMDD>"
cp "$BACKUP_DIR/docker-compose.agents.yml" /opt/openclaw/discord-agents/
cd /opt/openclaw/discord-agents
docker compose -f docker-compose.agents.yml up -d
```

Note: The old containers will still OOM, but you're back to the known state while debugging further.

---

## Reference: OpenClaw Docs Consulted

| Doc | Key Takeaway |
|-----|-------------|
| [install/docker](https://docs.openclaw.ai/install/docker) | Use `docker-setup.sh` or manual compose; gateway token in `.env`; container runs as `node` user |
| [install/updating](https://docs.openclaw.ai/install/updating) | `curl -fsSL https://openclaw.ai/install.sh \| bash` for upgrade; always run `openclaw doctor` after |
| [channels/discord](https://docs.openclaw.ai/channels/discord) | Multi-account under `channels.discord.accounts`; `groupPolicy: allowlist`; `requireMention: true`; `allowBots: true` with strict allowlist |
| [concepts/multi-agent](https://docs.openclaw.ai/concepts/multi-agent) | Single gateway, multiple agents in `agents.list[]`; agent-to-agent explicitly enabled; never share `agentDir` |
| [concepts/presence](https://docs.openclaw.ai/concepts/presence) | Gateway self-registers; 5-min TTL; max 200 entries; used for agent discovery |

---

## Success Criteria

- [ ] Single `openclaw-gateway` container running on port 18789
- [ ] OpenClaw version 2026.2.26+ (not 2026.2.9)
- [ ] All 5 Discord bots online and responding to @mentions
- [ ] Orchestrator can send messages to other agents via `sessions_send`
- [ ] Other agents can respond back to Orchestrator
- [ ] No OOM crashes for 1 hour of runtime
- [ ] Control UI accessible via Tailscale at `http://100.113.138.27:18789/`
- [ ] `openclaw health` returns healthy
- [ ] Memory usage stable (not growing unbounded)
- [ ] No Telegram artifacts in any active config
- [ ] All project docs updated to reflect new architecture
