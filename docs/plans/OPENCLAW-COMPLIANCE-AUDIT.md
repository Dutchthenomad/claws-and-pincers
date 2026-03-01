# OpenClaw Compliance Audit — Claws & Pincers

**Date:** 2026-03-01
**Auditor:** Claude Opus 4.6 (VPS session)
**Method:** Systematic comparison of all planning docs, configs, and agent definitions against official OpenClaw documentation (94 pages, 216 chunks in `openclaw_docs` Qdrant collection)
**Scope:** CORE-CHARTER, TODO, EXPANSION-ROADMAP, openclaw.json5, agent workspace files, SESSION-CONTINUITY, and all design docs

---

## Executive Summary

The project has a strong governance framework and a working deployment. However, there are **significant gaps** between the planning docs and how OpenClaw actually works. The CORE-CHARTER designs several systems from scratch (file-based task boards, lock files, conflict registries) that OpenClaw already provides natively via session tools, cron, heartbeats, and workspace memory. Phase 2's plan to build n8n workflows as the "universal control plane" partially duplicates OpenClaw's built-in capabilities and misses several platform features that would be more reliable and lower-maintenance.

**Critical finding:** The project is building external orchestration (n8n) for problems OpenClaw already solves internally (scheduling, memory, inter-agent communication, task tracking). This creates maintenance burden, token waste, and architectural fragility.

---

## Part 1: Compliance Issues (Plans vs OpenClaw Reality)

### C-01: CRITICAL — Memory Architecture Mismatch

**What the plans say:** Phase 2B plans to "Integrate existing OpenClaw Memory API (localhost:8002) into n8n workflows" for agent memory, with "per-agent namespaced memory contexts" and "n8n workflow for memory lifecycle."

**What OpenClaw actually does:** OpenClaw has a **native memory system** — plain Markdown files in the agent workspace (`MEMORY.md` + `memory/YYYY-MM-DD.md`). The `memory-core` plugin provides `memory_search` tools with recency decay, evergreen file support, and daily log management. Each agent already has its own workspace, so memory is already per-agent namespaced by design.

**Conflict:** The plan to route memory through n8n and a separate SQLite API (openclaw-memory at :8002) **bypasses OpenClaw's native memory** entirely. The agents will write to an external API that OpenClaw doesn't know about, meaning:
- OpenClaw's `memory_search` tool won't find anything useful
- Context assembly won't include memory from the external API
- The native recency decay and daily log system goes unused
- Double maintenance burden (external API + OpenClaw workspace)

**Required action:** Redesign Phase 2B to use OpenClaw's native workspace memory as the primary system. The external Memory API could supplement as a cross-agent shared knowledge base, but each agent's working memory should be in their workspace `memory/` directory.

---

### C-02: HIGH — Workspace File Layout Non-Compliant

**What the plans say:** CORE-CHARTER Section 9 defines a custom file structure under `~/.openclaw/` with `master-docs/`, `projects/`, `shared/`, `logging/`, `agents/`, `credentials/`, `skills/`, `cron/`.

**What OpenClaw actually does:** OpenClaw has a specific workspace layout:
- `SOUL.md` — identity and personality
- `AGENTS.md` — operational instructions (loaded every session)
- `USER.md` — information about who the agent helps
- `IDENTITY.md` — self-discovered identity metadata
- `HEARTBEAT.md` — periodic check tasks
- `BOOTSTRAP.md` — first-run instructions (deleted after use)
- `TOOLS.md` — tool-specific instructions
- `BOOT.md` — startup hook instructions
- `memory/` — daily logs + curated MEMORY.md
- `notes/` — working notes

**Conflict:** The CORE-CHARTER's `shared/task-board.json`, `active-locks.json`, `conflict-registry.json`, and `anti-patterns.md` aren't in any agent's workspace, so agents can't naturally read/write them through OpenClaw's file tools (which default to workspace cwd). The charter's file structure doesn't align with what OpenClaw actually injects into context.

**What gets injected into context:** OpenClaw builds the system prompt from `AGENTS.md`, `SOUL.md`, `USER.md`, `IDENTITY.md`, `TOOLS.md`, and `HEARTBEAT.md`. Sub-agents only get `AGENTS.md` + `TOOLS.md`. If governance rules aren't in these files, agents won't see them.

**Required action:**
1. Embed critical governance rules into each agent's `AGENTS.md` (which is always loaded)
2. Put shared state files in a location accessible from agent workspaces (or use `sessions_send` for coordination)
3. Align the CORE-CHARTER's file structure with OpenClaw's actual workspace layout

---

### C-03: HIGH — Task Coordination via JSON Files vs Session Tools

**What the plans say:** CORE-CHARTER Section 4 designs `task-board.json` and `active-locks.json` as the "source of truth" for tasks, with agents reading/writing these files.

**What OpenClaw actually does:** OpenClaw provides `sessions_send` and `sessions_spawn` as the native inter-agent coordination mechanism. The Orchestrator can:
- `sessions_spawn` to delegate work to a specialist (creates an isolated session)
- `sessions_send` to send messages to existing sessions
- `sessions_list` to see all active sessions
- `sessions_history` to review session transcripts

**Conflict:** File-based coordination (JSON task boards) requires:
- All agents to know the file path and format
- Manual lock management (race conditions)
- Polling or external triggers to detect changes
- No built-in notification when tasks change

Session tools provide all of this natively with proper isolation, notifications (announce-back from sub-agents), and no race conditions.

**Required action:** Redesign task coordination to use OpenClaw's session tools as primary, with Discord channels as the human-visible layer. The Orchestrator should use `sessions_spawn` to delegate and track work, not file-based task boards.

---

### C-04: HIGH — n8n as "Universal Control Plane" Conflicts with OpenClaw Native Features

**What the plans say:** Phase 2 positions n8n as the "universal control plane" where "n8n workflows are the living, enforceable, debuggable truth."

**What OpenClaw actually provides natively:**
- **Cron jobs** — Built-in scheduler with persistence, session isolation, model overrides, webhook delivery, and per-agent scheduling
- **Heartbeats** — Periodic agent turns for proactive monitoring
- **Webhooks** — `hooks.enabled=true` exposes webhook endpoints on the gateway
- **Session tools** — Native inter-agent orchestration
- **Slash commands** — Native command interface for agents and users

**Conflict areas by Phase 2 sub-phase:**

| Phase 2 Item | n8n Plan | OpenClaw Native Alternative |
|---|---|---|
| 2A: Project ID validator | n8n polls Discord every 30s | Orchestrator's `AGENTS.md` can enforce this natively on every message |
| 2A: Charter approval gate | n8n polls every 30s | Same — governance in AGENTS.md + Orchestrator enforces |
| 2A: Severity routing | n8n routes between channels | `sessions_send` + Discord message tool can route natively |
| 2A: Token cost monitor | n8n workflow | `/usage` slash command + cron job with cost thresholds |
| 2A: Heartbeat dead man's switch | n8n workflow | OpenClaw native heartbeats already do this |
| 2B: Memory orchestration | n8n manages lifecycle | Native `memory-core` plugin handles this |
| 2C: Workspace management | n8n creates folders | Workspace dirs already exist per-agent |
| 2D: Config drift detection | n8n workflow | Could be a cron job that diffs config |

**Required action:** Audit each Phase 2 workflow against OpenClaw's native capabilities. Use n8n only for things OpenClaw genuinely can't do (external API integrations, complex multi-step workflows with external services). Don't replicate OpenClaw's built-in features in n8n.

---

### C-05: MEDIUM — Communication Architecture Partially Redundant

**What the plans say:** CORE-CHARTER Section 8.3 states "Specialists do NOT message each other directly unless Orchestrator explicitly enables it." All cross-agent communication flows through Orchestrator.

**What OpenClaw actually does:** `tools.agentToAgent` config already controls this:
```json
agentToAgent: {
  enabled: true,
  allow: ["orchestrator", "researcher", "developer", "sysadmin", "reviewer"],
}
```

**Issue:** The current config allows ALL agents to communicate with ALL other agents (`allow` lists all 5). This contradicts the CORE-CHARTER's hub-and-spoke model where specialists only communicate through the Orchestrator.

**Required action:** Change `agentToAgent.allow` per agent. Only the Orchestrator should be allowed to contact all agents. Specialists should only be allowed to contact the Orchestrator:
```json
// Per-agent override
orchestrator: { tools: { agentToAgent: { allow: ["*"] } } }
researcher:   { tools: { agentToAgent: { allow: ["orchestrator"] } } }
developer:    { tools: { agentToAgent: { allow: ["orchestrator"] } } }
sysadmin:     { tools: { agentToAgent: { allow: ["orchestrator"] } } }
reviewer:     { tools: { agentToAgent: { allow: ["orchestrator"] } } }
```

---

### C-06: MEDIUM — Missing BOOTSTRAP.md / BOOT.md Usage

**What OpenClaw expects:** `BOOTSTRAP.md` is a first-run file — the agent reads it, follows instructions to discover its identity, then deletes it. `BOOT.md` provides startup hook instructions (requires `hooks.internal.enabled`).

**Current state:** The deployed workspaces at `/opt/openclaw/config/workspace-*/` have `BOOTSTRAP.md` files that still exist (not deleted after first run). This suggests the agents haven't gone through proper first-run onboarding.

**Required action:**
1. Either run each agent through their BOOTSTRAP.md flow, or
2. Pre-populate IDENTITY.md with the R&M character identities and remove BOOTSTRAP.md
3. Consider adding BOOT.md with startup governance checks (read anti-patterns, check task-board)

---

### C-07: MEDIUM — Heartbeat Configuration Misaligned

**What the plans say:** Each agent has a `HEARTBEAT.md` with monitoring tasks. TODO includes "Heartbeat dead man's switch" as a Phase 2A item.

**What OpenClaw actually does:** Heartbeats are configured at `agents.defaults.heartbeat.every: "30m"` in openclaw.json5. But HEARTBEAT.md content controls what the agent actually does during a heartbeat turn. The agent reads HEARTBEAT.md and acts on it.

**Current state:** The config sets 30m heartbeats globally, but per the RAG docs: "If any agent has a heartbeat block, **only those agents** run heartbeats." No per-agent heartbeat config exists in the current openclaw.json5.

**Issues:**
1. All 5 agents running heartbeats every 30m = 240 API calls/day = significant token cost
2. Not all agents need heartbeats (Reviewer/QA only needs to run when there's work in review)
3. Dead man's switch is already native — if heartbeats stop, the gateway logs it

**Required action:**
1. Configure heartbeats per-agent (only Orchestrator and Sysadmin need regular heartbeats)
2. Set Researcher/Developer/Reviewer to longer intervals or disable
3. Use per-channel heartbeat visibility (`showOk`, `showAlerts`, `useIndicator`) to reduce noise
4. Consider model overrides for heartbeat runs (use cheaper models)

---

### C-08: MEDIUM — Sandbox Mode Off for All Agents

**What the plans say:** CORE-CHARTER defines strict role boundaries — Reviewer can't write, Developer can't deploy, etc.

**What OpenClaw provides:** Sandbox mode (`agents.list[].sandbox.mode`) can run tools in Docker containers with limited filesystem/process access.

**Current state:** `sandbox: { mode: "off" }` for ALL agents. Combined with `tools.exec.security: "full"`, every agent can execute arbitrary commands on the host.

**Issue:** While tool `allow`/`deny` lists provide some protection, sandbox-off means a misbehaving model can reach outside its workspace. The Reviewer (which should be read-only) has `exec` denied but could potentially be prompted to use other tools inappropriately.

**Required action:**
1. Consider sandbox mode for Developer and Sysadmin (these execute code on the host)
2. At minimum, use per-agent `tools.elevated` restrictions
3. The current tool allow/deny lists are good but could be tighter (see C-09)

---

### C-09: LOW — Tool Permissions Could Be Tighter

**Current config analysis:**

| Agent | Concerning Permissions |
|---|---|
| Orchestrator | Has `exec`, `write`, `edit` — charter says "Does not write code" |
| Researcher | Has `exec` — charter says "Cannot execute code" |
| Developer | Missing `web_search` — may need it for looking up docs while coding |
| Sysadmin | Missing `browser` — may need for monitoring dashboards |

**Required action:** Align tool permissions with CORE-CHARTER role definitions:
- Orchestrator: Remove `exec` (coordinator only) or restrict to read-only commands
- Researcher: Remove `exec`, keep `read`/`write` for workspace files only
- Consider adding `web_search` to Developer for documentation lookups

---

## Part 2: Missed Platform Features (Opportunities)

### O-01: HIGH — OpenClaw Native Cron Should Replace Most n8n Governance Workflows

OpenClaw's built-in cron system supports:
- Persistent job store (`~/.openclaw/cron/jobs.json`)
- Isolated sessions per job (`cron:<jobId>`)
- Model overrides per job (use cheaper models for routine checks)
- Webhook delivery mode (can POST results to n8n for complex processing)
- Announcement to channels
- Per-agent scoping

**Recommendation:** Replace Phase 2A's polling-based n8n workflows with OpenClaw cron jobs:
```
openclaw cron add --name "Law 1 Check" --cron "*/5 * * * *" --agent orchestrator --session isolated --message "Check #task-dispatch for any messages without PROJ-XXX tags and report violations to #severity-alerts"
```

This is more reliable than n8n polling Discord every 30s, uses the agent's own intelligence, and doesn't require maintaining separate n8n workflows.

---

### O-02: HIGH — Leverage `sessions_spawn` for the Orchestrator's Core Job

The Orchestrator's entire purpose is task decomposition and delegation. OpenClaw's `sessions_spawn` is purpose-built for this:
- Spawn a specialist with a specific task
- Get results announced back automatically
- Track via `sessions_list`
- Review work via `sessions_history`
- Optional model override per spawn
- Thread support for Discord (spawn results can go to threads)

**Recommendation:** The Orchestrator's AGENTS.md should define SOPs using `sessions_spawn` as the primary delegation mechanism, not Discord channel messages.

---

### O-03: HIGH — Use Discord Threads for Project Isolation

OpenClaw supports Discord threads natively with `sessions_spawn(thread=true)`. This maps perfectly to the project-based isolation model:
- Each PROJ-XXX gets a Discord thread
- Sub-agent work stays contained in the thread
- Orchestrator can review via `sessions_history`
- Human (Devin) can observe in Discord

**Recommendation:** Add thread-based project isolation to the CORE-CHARTER's project lifecycle. Each project dispatch creates a thread. This gives natural isolation without complex file-based tracking.

---

### O-04: MEDIUM — Discord Components v2 for Structured Interactions

OpenClaw supports Discord components v2 containers — buttons, select menus, and interactive elements. These could be used for:
- Charter approval buttons (approve/reject/revise) instead of text-based approval
- Task status updates with button interactions
- Severity classification buttons for the Reviewer
- Cost threshold approval buttons

**Recommendation:** Design Discord component interactions for critical governance touchpoints (charter approval, task dispatch acceptance, review verdicts).

---

### O-05: MEDIUM — ClawHub Skills for Team-Wide Capabilities

OpenClaw's ClawHub is a public skill registry. Skills can also be loaded from workspace or `~/.openclaw/skills/`.

**Recommendation:**
1. Create workspace-level skills per agent for their SOPs (e.g., `skills/governance-check/SKILL.md`)
2. Create shared skills in `~/.openclaw/skills/` for cross-team procedures
3. Use `skills.load.extraDirs` to load shared governance skills
4. Long-term: Publish useful skills to ClawHub for the OpenClaw community

---

### O-06: MEDIUM — Webhook Integration for n8n ↔ OpenClaw

Instead of n8n polling Discord, use OpenClaw's webhook system:
- `hooks.enabled=true` exposes webhook endpoints on the gateway
- Cron jobs can deliver to webhooks (`delivery.mode: "webhook"`)
- n8n can receive webhook POSTs from OpenClaw

**Recommendation:** Reverse the integration direction — OpenClaw pushes to n8n via webhooks rather than n8n polling Discord. This is event-driven, lower-latency, and lower-cost.

---

### O-07: MEDIUM — Lobster Workflow Engine

OpenClaw mentions Lobster as a built-in workflow automation tool:
- Runs as a local subprocess in tool mode
- Returns JSON envelopes
- Supports approval flows (`needs_approval` → `resumeToken`)
- Can be triggered by cron or heartbeat

**Recommendation:** Investigate Lobster as a potential replacement for some n8n workflows, particularly those that are pure agent-to-agent coordination.

---

### O-08: LOW — OpenAI-Compatible Chat Completions API

The gateway can serve a `POST /v1/chat/completions` endpoint. This means:
- n8n could call agents via HTTP API instead of polling Discord
- External tools could trigger agent work via standard OpenAI-compatible calls
- Programmatic integration becomes trivial

**Recommendation:** Enable this endpoint for programmatic agent interaction from n8n and other services.

---

### O-09: LOW — Exec Approval Buttons in Discord

OpenClaw supports button-based exec approvals in Discord DMs:
- `channels.discord.execApprovals.enabled`
- `channels.discord.execApprovals.approvers`

**Recommendation:** Enable this for Devin's Discord account so dangerous exec commands require button approval rather than the current text-based approval flow.

---

### O-10: LOW — Per-Agent Model Overrides for Cost Optimization

Current config gives each agent a primary model, but heartbeat runs and cron jobs don't specify cheaper models.

**Recommendation:**
- Use `heartbeat.model` to override heartbeat runs with cheaper models (e.g., `groq/llama-3.3-70b-versatile` for routine checks)
- Use `cron --model` for scheduled governance checks
- Keep frontier models for interactive work only

---

## Part 3: Recommended Plan Revisions

### Phase 2 Redesign Proposal

Instead of "n8n as universal control plane," restructure Phase 2 as:

**Phase 2A — Native Governance (Use OpenClaw Features)**
1. Embed 4 Laws enforcement in Orchestrator's AGENTS.md + SOUL.md
2. Set up OpenClaw cron jobs for periodic governance checks
3. Configure per-agent heartbeats with role-appropriate intervals
4. Fix `agentToAgent` routing to match hub-and-spoke model
5. Set up Discord threads for project isolation
6. Configure exec approval buttons for Devin

**Phase 2B — Agent Memory (Use Native + Supplement)**
1. Populate each agent's workspace `memory/` with role-relevant evergreen files
2. Use native `memory-core` for per-agent working memory
3. Keep openclaw-memory API as cross-agent shared knowledge base only
4. Connect via workspace files, not n8n workflows

**Phase 2C — n8n for External Integrations Only**
1. OpenClaw → n8n webhooks for external notifications (email, Slack, etc.)
2. n8n → OpenClaw via Chat Completions API for programmatic triggers
3. Cost tracking dashboard (aggregate from `/usage` data)
4. External service monitoring that agents can't do natively

**Phase 2D — Config Hardening**
1. Per-agent sandbox evaluation
2. Tighten tool permissions per CORE-CHARTER
3. Fix heartbeat config (per-agent, cost-optimized)
4. BOOTSTRAP.md cleanup

---

## Part 4: Config Changes Needed (openclaw.json5)

### Immediate Fixes

```jsonc
// 1. Fix agentToAgent to match hub-and-spoke model
// Move from global allow to per-agent

// 2. Add per-agent heartbeat config
agents: {
  list: [
    {
      id: "orchestrator",
      heartbeat: { every: "15m" },  // Active coordinator
    },
    {
      id: "researcher",
      heartbeat: { every: "2h" },   // Check-in only
    },
    {
      id: "developer",
      heartbeat: { every: "2h" },
    },
    {
      id: "sysadmin",
      heartbeat: { every: "30m" },  // Infrastructure monitoring
    },
    {
      id: "reviewer",
      heartbeat: { every: "4h" },   // Low-frequency check
    },
  ],
}

// 3. Enable hooks for webhooks
hooks: { enabled: true }

// 4. Enable OpenAI-compatible API
gateway: {
  openaiApi: { enabled: true }
}

// 5. Enable cron
cron: { enabled: true }

// 6. Consider enabling memory plugin explicitly
plugins: {
  slots: { memory: "memory-core" }
}
```

### Tool Permission Fixes

```jsonc
// Orchestrator: remove exec (coordinator only)
orchestrator: {
  tools: {
    allow: ["read", "write", "edit", "sessions_list", "sessions_history",
            "sessions_send", "sessions_spawn", "discord", "web_search", "cron"],
    deny: ["exec", "apply_patch"],
  }
}

// Researcher: remove exec
researcher: {
  tools: {
    allow: ["read", "write", "sessions_list", "sessions_history",
            "sessions_send", "web_search", "browser", "discord"],
    deny: ["exec", "edit", "apply_patch", "cron", "gateway", "nodes",
           "canvas", "sessions_spawn"],
  }
}
```

---

## Part 5: CORE-CHARTER Amendment Recommendations

| Section | Issue | Recommendation |
|---------|-------|----------------|
| Section 4.4 (Task Dispatch) | Relies on `task-board.json` | Switch to `sessions_spawn` as primary, Discord as visibility layer |
| Section 4.5 (Execution) | Lock files for collision prevention | Use OpenClaw session isolation instead |
| Section 8.2 (File Coordination) | "Actual coordination state lives in files" | Coordination state should live in sessions; files for persistence |
| Section 8.3 (Communication) | "Specialists do NOT message each other directly" | Enforce via `agentToAgent` config, not just policy |
| Section 9 (File Structure) | Custom layout under `~/.openclaw/` | Align with OpenClaw's native workspace layout |
| Section 7 (Self-Learning) | `anti-patterns.md` in shared files | Put in each agent's workspace as an evergreen memory file |

---

## Priority Matrix

| ID | Severity | Effort | Description |
|----|----------|--------|-------------|
| C-01 | CRITICAL | HIGH | Memory architecture — use native workspace memory |
| C-02 | HIGH | MEDIUM | Workspace file layout — align with OpenClaw |
| C-03 | HIGH | MEDIUM | Task coordination — use session tools |
| C-04 | HIGH | HIGH | n8n scope — reduce to external integrations only |
| C-05 | MEDIUM | LOW | agentToAgent config — fix hub-and-spoke |
| C-06 | MEDIUM | LOW | BOOTSTRAP.md cleanup |
| C-07 | MEDIUM | LOW | Heartbeat per-agent config |
| C-08 | MEDIUM | MEDIUM | Sandbox evaluation |
| C-09 | LOW | LOW | Tool permission tightening |
| O-01 | HIGH | MEDIUM | Native cron for governance |
| O-02 | HIGH | LOW | sessions_spawn for delegation |
| O-03 | HIGH | MEDIUM | Discord threads for project isolation |
| O-04 | MEDIUM | MEDIUM | Discord components v2 |
| O-05 | MEDIUM | MEDIUM | ClawHub skills |
| O-06 | MEDIUM | LOW | Webhook integration direction |
| O-07 | MEDIUM | LOW | Lobster investigation |
| O-08 | LOW | LOW | OpenAI-compatible API |
| O-09 | LOW | LOW | Exec approval buttons |
| O-10 | LOW | LOW | Heartbeat model overrides |

---

## Conclusion

The Claws & Pincers project has solid governance thinking but is building external infrastructure for problems OpenClaw already solves. The biggest wins come from:

1. **Using OpenClaw's native features** (session tools, cron, heartbeats, workspace memory) instead of reimplementing them in n8n
2. **Aligning workspace files** with OpenClaw's expected layout so agents get governance context automatically
3. **Restricting n8n** to what it's actually good at — external integrations, dashboards, and things outside OpenClaw's scope
4. **Hardening the config** to enforce the CORE-CHARTER's rules at the platform level, not just as policy documents

The governance framework (4 Laws, severity classification, anti-patterns) is excellent and should be preserved — it just needs to be expressed through OpenClaw's native mechanisms rather than bolted-on external systems.
