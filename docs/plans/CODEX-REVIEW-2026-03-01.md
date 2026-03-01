# Codex Review Report — 2026-03-01

**Date:** 2026-03-01
**Author:** Codex GPT-5
**Type:** Read-only review report
**Scope:** Active OpenClaw Discord deployment project and related runtime/reference paths

---

## 1. Executive Summary

The deployment appears operational, but its control plane is not reliably trustworthy. Live behavior is being driven by deployed files under `/opt/openclaw/config` and mounted workspaces, while repo docs and operational guidance under `/root/claws-and-pincers` do not consistently match that reality. The highest-risk issues are secret exposure in active state, overly broad Discord ingress, and ambiguous ownership of config, prompts, and plugins.

### Findings by severity

- Critical: 1
- High: 4
- Medium: 5
- Low: 0
- Info: 0

### Top 5 highest-risk issues

1. Secret-bearing session transcripts are stored in readable active state paths.
2. Discord ingress is broader than the allowlist name suggests, while filesystem and exec-adjacent tools remain enabled.
3. Source-of-truth boundaries are split across repo docs, deployed config, and live workspaces.
4. A custom `cli-offload` plugin is active without deterministic provenance control.
5. Gateway exposure/auth hardening depends on a direct tailnet bind and already shows repeated failed pairing traffic.

### Top 5 highest-value cleanup or hardening opportunities

1. Establish one authoritative source of truth for runtime config and agent prompts.
2. Tighten permissions and retention for secret-bearing state and governance token material.
3. Narrow Discord access to explicit users, roles, and channels.
4. Reconcile declared tools/plugins with the runtime registry and explicit plugin allowlisting.
5. Align the RAG/MCP knowledge path with the actual OpenClaw docs corpus, or document that only the docs scraper is authoritative.

---

## 2. System Understanding

### What appears to be the active architecture

- The active Discord system is centered on a single gateway deployment defined by `/opt/openclaw/gateway/docker-compose.yml` and configured by `/opt/openclaw/config/openclaw.json`.
- The gateway is running a multi-account Discord setup with per-account agent bindings; runtime observation showed `orchestrator` as the default route and distinct Discord account bindings for the other named agents.
- Agent prompts are effectively coming from mounted workspace directories under `/opt/openclaw/config`, not only from the repo under `/root/claws-and-pincers`.
- Knowledge services are split: the dedicated docs scraper under `/root/claws-and-pincers/scripts/openclaw-docs-scraper` can ground against OpenClaw docs, while the general RAG/MCP layer does not currently expose the same corpus.

### What paths are source of truth

- Actual runtime truth for gateway behavior: `/opt/openclaw/config/openclaw.json`, `/opt/openclaw/gateway/docker-compose.yml`, and the live workspace directories under `/opt/openclaw/config`.
- Intended architecture and governance truth: `/root/claws-and-pincers/README.md`, `/root/claws-and-pincers/CLAUDE.md`, `/root/claws-and-pincers/PROJECT-REFRESHER.md`, `/root/claws-and-pincers/operations/DEPLOYMENT-STATE.md`, `/root/claws-and-pincers/governance/operations/CORE-CHARTER.md`.
- Upstream OpenClaw standard/reference truth: `/opt/openclaw/runtime/docs`, backed by the local docs scraper and the upstream runtime source under `/opt/openclaw/runtime`.

### What paths are reference only

- `/opt/openclaw/runtime`
- `/opt/openclaw/source`

### What paths are historical or drift-prone

- `/opt/openclaw/CONFIG-SOURCE-OF-TRUTH.md`
- `/opt/openclaw/scripts/sync-from-repo.sh`
- `/opt/openclaw/config/openclaw.json5`
- Several duplicated YAML policy/config files under `/opt/openclaw/config` that do not match repo versions.

### Key service relationships

- Discord traffic enters the gateway defined by `/opt/openclaw/gateway/docker-compose.yml` and is governed by `/opt/openclaw/config/openclaw.json`.
- The gateway uses mounted state and per-agent workspace directories under `/opt/openclaw/config`.
- The gateway can load local extensions from `/opt/openclaw/config/extensions`, including `cli-offload`.
- Memory and supporting infra are supplied by `/root/openclaw-memory/docker-compose.yml`.
- RAG/Qdrant infrastructure is supplied by `/root/rag-stack/docker-compose.yml` and `/root/rag-api`, but that path does not currently expose the `openclaw_docs` corpus that the docs scraper can reach directly.
- The docs scraper under `/root/claws-and-pincers/scripts/openclaw-docs-scraper` is active and should be treated as a live reference tool, not cleanup cruft.

---

## 3. Findings

### [OC-001] Secret-Bearing Session Transcripts Are Stored in Readable Active State

Severity: Critical  
Category: Security  
Conflict: Live secret retention conflicts with least-privilege handling and with OpenClaw’s own security-audit expectations.  
Confidence: High  
Scope: gateway state directory, session retention, local host access

Evidence:
- `/opt/openclaw/config/agents/main/sessions/024e4975-e14c-48c3-9393-c574062c34e2.jsonl` contains raw credential-like material in plain text.
- `/opt/openclaw/config/agents/main/sessions/d2561f91-6193-4acd-a4d3-f1eea50b2496.jsonl` shows the same issue in a separate active session transcript.
- `/opt/openclaw/config` is readable by non-owner users.
- `/opt/openclaw/config/credentials` is readable by non-owner users.
- An explicit OpenClaw security audit against the deployed state dir flagged both the state dir and credentials dir as overly readable.

Why it matters:
- Any local user with filesystem access can read active transcripts containing provider or bot credentials.
- This creates an immediate compromise path that does not require container escape or Discord abuse.
- Incident response and rotation become much harder because secrets are duplicated into conversational state.

Recommendation:
- Review whether session retention is allowed to capture secrets at all.
- Restrict permissions on state, credentials, and session transcript paths before further rollout.
- Treat existing transcript retention as potentially sensitive until proven otherwise.

OpenClaw alignment check:
- `/opt/openclaw/runtime/docs/cli/security.md` and the built-in audit warnings both align with tightening state and credential exposure.
- This recommendation follows OpenClaw’s security posture rather than adding a new standard.

Example snippet:
- None needed.

Verification idea:
- Confirm whether any local account other than the intended service owner can read files under `/opt/openclaw/config/agents/main/sessions` and whether secret values are still being written into new transcripts.

### [OC-002] Discord Ingress Is Broader Than the Allowlist Name Suggests

Severity: High  
Category: Security  
Conflict: The deployed Discord policy is less restrictive than repo intent and OpenClaw’s Discord guidance imply.  
Confidence: High  
Scope: Discord ingress, bot-to-bot interaction, remote command surface

Evidence:
- `/opt/openclaw/config/openclaw.json` enables `channels.discord.allowBots`.
- `/opt/openclaw/config/openclaw.json` sets `groupPolicy` to `allowlist`.
- `/opt/openclaw/config/openclaw.json` configures the allowlisted guild with `requireMention: true` but no `users`, `roles`, or `channels`.
- `/opt/openclaw/config/openclaw.json` keeps host-interaction tools broadly enabled, including `exec`, `read`, `write`, and `edit`.
- `/opt/openclaw/runtime/docs/channels/discord.md` documents that any member in an allowlisted guild is allowed when `users` and `roles` are absent, and all channels in that guild are allowed when `channels` are absent.
- `/root/claws-and-pincers/reference/08-CONFIGURATION-REFERENCE.md` and `/root/claws-and-pincers/reference/07-SERVER-ARCHITECTURE.md` show stricter Discord scoping when bot access is enabled.

Why it matters:
- Any member or bot in the allowlisted guild can trigger agents by mention, not only a narrow operator set.
- That exposure is materially more dangerous because the agent tool surface includes host interaction and writable filesystem operations.
- Mention-only gating reduces noise, but it does not provide identity scoping.

Recommendation:
- Narrow Discord access to explicit users, roles, and channels.
- Reconfirm whether `allowBots: true` is still required for the production workflow.
- Validate the intended access matrix before additional agent/tool expansion.

OpenClaw alignment check:
- This is directly aligned with `/opt/openclaw/runtime/docs/channels/discord.md` and the repo’s own configuration reference.
- The recommendation does not change the architecture; it restores the restrictive intent already reflected in OpenClaw guidance.

Example snippet:

```json
"allowBots": true,
"groupPolicy": "allowlist",
"guilds": {
  "1472374974340665477": { "requireMention": true }
}
```

Verification idea:
- Build a simple access matrix for one approved human, one non-approved human, one approved bot, and one non-approved bot across allowed and disallowed channels, then verify the gateway behavior against that matrix.

### [OC-003] Source-of-Truth Boundaries Are Split and Operationally Misleading

Severity: High  
Category: Architecture  
Conflict: Active operational docs and sync artifacts still describe an older deployment model, while the live gateway uses a different one.  
Confidence: High  
Scope: deployment ownership, config management, prompt/workspace management

Evidence:
- `/opt/openclaw/CONFIG-SOURCE-OF-TRUTH.md` still points to `/tmp/claws-and-pincers` and older per-agent container data paths.
- `/opt/openclaw/scripts/sync-from-repo.sh` still syncs into old per-agent workspace paths under `/opt/openclaw/discord-agents/*-data/...`.
- `/opt/openclaw/gateway/docker-compose.yml` mounts shared config/state from `/opt/openclaw/config`, not the old per-agent layout.
- `/opt/openclaw/config/openclaw.json` is the live runtime config actually driving the gateway.
- `/root/claws-and-pincers/agents` and the live workspace directories under `/opt/openclaw/config` differ materially across multiple agents.

Why it matters:
- A human or implementation agent can easily update the wrong path and believe the system has been changed when it has not.
- This makes reviews, incident response, and future deployments unreliable.
- It also obscures whether repo commits are supposed to converge into live prompts and config at all.

Recommendation:
- Define a single authoritative path for runtime config and a single authoritative path for agent prompt content.
- Mark all older sync/docs artifacts as historical unless they are still actively executed.
- Add a pre-change verification step that traces a repo file to its mounted runtime counterpart.

OpenClaw alignment check:
- `/opt/openclaw/runtime/docs/concepts/multi-agent.md` assumes explicit agent workspace boundaries.
- The recommendation aligns with OpenClaw’s expectation that the operative config/prompt inputs be explicit and reviewable.

Example snippet:
- Historical target: `/opt/openclaw/discord-agents/{agent}-data/.openclaw/workspace`
- Live target pattern: `/opt/openclaw/config/workspace-{agent}`

Verification idea:
- For a future change, trace one config field and one prompt file from the repo location to the exact mounted runtime file consumed by the gateway.

### [OC-004] The General RAG/MCP Layer Does Not Reliably Serve the OpenClaw Corpus It Is Supposed to Ground

Severity: High  
Category: Architecture  
Conflict: The project expects OpenClaw-grounded knowledge, but the generic knowledge services do not expose the same OpenClaw corpus that the docs scraper can reach.  
Confidence: High  
Scope: docs baseline, agent grounding, knowledge tooling

Evidence:
- `/root/claws-and-pincers/scripts/openclaw-docs-scraper/README.md` documents the dedicated OpenClaw docs scraper as an active tool.
- `/root/claws-and-pincers/scripts/openclaw-docs-scraper/query.py` uses the OpenClaw docs path successfully.
- Live Qdrant state includes an `openclaw_docs` collection.
- `/root/rag-api/app/config.py` hardcodes exposed collections that exclude `openclaw_docs`.
- `/root/rugs-mcp/src/server.py` and `/root/rugs-mcp/src/tools.py` remain oriented around `rugs.fun` and Local AI knowledge, not OpenClaw.

Why it matters:
- An operator or agent using the generic RAG API or MCP server will not reliably retrieve the same OpenClaw knowledge that the docs scraper can.
- That creates a real grounding split: the “baseline” depends on which knowledge path is used.
- Incorrect grounding is especially risky in this project because OpenClaw itself is supposed to be the governing standard.

Recommendation:
- Decide whether the authoritative OpenClaw knowledge path is the dedicated docs scraper, the RAG API, the MCP server, or a supported combination.
- If RAG/MCP are intended to be authoritative, they need to expose the OpenClaw corpus explicitly.
- If only the docs scraper is authoritative, document that clearly and stop implying broader coverage.

OpenClaw alignment check:
- This recommendation aligns with the project’s own requirement to validate against OpenClaw docs and reference behavior.
- Right now, only the dedicated scraper path is consistently aligned to that standard.

Example snippet:
- Live corpus mismatch:
  - Qdrant contains `openclaw_docs`
  - `/root/rag-api/app/config.py` exposes `external_docs`, `rugs_protocol`, `rl_design`, and `localai_knowledge`

Verification idea:
- Run the same OpenClaw-specific query through the docs scraper and the generic RAG/MCP path, then compare whether both return the same corpus and guidance.

### [OC-005] Active Config Directories Contain Stale Shadow Configs and Policy Files

Severity: Medium  
Category: Config Drift  
Conflict: Active deployment paths contain multiple conflicting config artifacts from different architectural eras.  
Confidence: High  
Scope: operator guidance, future config changes, routing/policy interpretation

Evidence:
- `/opt/openclaw/config/openclaw.json5` is still present in the active config directory and reflects older architecture assumptions.
- `/opt/openclaw/config/model-routing.yaml` materially diverges from the repo version at `/root/claws-and-pincers/config/model-routing.yaml`.
- `/opt/openclaw/config/cost-registry.yaml` materially diverges from the repo version at `/root/claws-and-pincers/config/cost-registry.yaml`.
- `/opt/openclaw/config/capability-timeline.yaml` and `/opt/openclaw/config/permission-tiers.yaml` also diverge from repo-era governance/config assumptions.

Why it matters:
- Even if some of these files are not currently read at runtime, they sit in active operational paths and look authoritative.
- That makes operator error, accidental reactivation, and incorrect future automation more likely.
- Drift in model-routing or policy files is especially risky because it can look like a legitimate production override.

Recommendation:
- Inventory which config files are live inputs, which are documentation copies, and which are historical leftovers.
- Mark non-live files clearly or move them out of active operational paths later.
- Avoid keeping stale shadow configs next to the live config without explicit ownership notes.

OpenClaw alignment check:
- OpenClaw expects deterministic, reviewable configuration.
- This recommendation aligns with that principle by reducing ambiguity around what is actually operative.

Example snippet:
- None needed.

Verification idea:
- Trace actual file reads during startup and during any routing/policy resolution before treating any YAML in `/opt/openclaw/config` as authoritative.

### [OC-006] Declared Tool Policies Do Not Match the Runtime Tool Registry

Severity: Medium  
Category: Reliability  
Conflict: Agent/tool declarations advertise capabilities that the runtime warns it cannot match.  
Confidence: High  
Scope: tool policy, agent behavior, operator expectations

Evidence:
- `/opt/openclaw/config/openclaw.json` includes tool allowlist entries such as `apply_patch`, `discord`, and `cron`.
- `/opt/openclaw/data/logs/gateway.log` contains repeated warnings that `apply_patch`, `discord`, and `cron` are unknown or will not match a tool.
- `/opt/openclaw/runtime/docs/tools/apply-patch.md` states `apply_patch` is disabled by default unless explicitly enabled.
- `/opt/openclaw/runtime/src/agents/tool-policy-pipeline.ts` warns on unknown allowlist entries.

Why it matters:
- Operators can believe a tool is available because it is declared in config, while the runtime silently rejects or ignores it.
- That creates brittle workflows and false assumptions during incident handling or feature rollout.
- The mismatch is especially risky for tools that affect files or external systems.

Recommendation:
- Reconcile every declared allowlist entry against the actual runtime tool registry.
- Remove non-existent entries or explicitly enable the missing capabilities if they are truly intended.
- Treat runtime warnings about unknown tools as configuration defects, not cosmetic noise.

OpenClaw alignment check:
- This is directly aligned with `/opt/openclaw/runtime/docs/tools/index.md` and `/opt/openclaw/runtime/docs/tools/apply-patch.md`.
- The recommendation follows OpenClaw’s runtime behavior instead of inventing a stricter local rule.

Example snippet:
- Config intent: `["discord", "cron"]`
- Runtime result: warning that the entries will not match a tool

Verification idea:
- Enumerate the loaded runtime tools and compare that list directly with each agent’s configured `tools.allow` set.

### [OC-007] Plugin Loading and Provenance Controls Are Inconsistent Around `cli-offload`

Severity: High  
Category: Security  
Conflict: A custom plugin is active in runtime, but plugin provenance and allowlisting are not deterministic across validation paths.  
Confidence: High  
Scope: gateway extensions, detached subprocess execution, plugin governance

Evidence:
- `/opt/openclaw/config/openclaw.json` enables `plugins.entries.cli-offload`.
- `/opt/openclaw/config/openclaw.json` does not define a `plugins.allow` allowlist.
- `/opt/openclaw/data/logs/gateway.log` warns that non-bundled plugins may auto-load and that `cli-offload` lacks install/load-path provenance.
- `/opt/openclaw/config/extensions/cli-offload/index.ts` spawns detached `claude` CLI processes through a shell command.
- `/opt/openclaw/config/extensions/cli-offload` was flagged by an explicit security audit for suspicious ownership, and the same audit also reported the configured plugin as not found or stale under that validation path.

Why it matters:
- Custom code is executing with gateway authority, but there is not one clear validation story for whether it is trusted, loaded, or even discoverable.
- Detached shell-spawned subprocesses complicate control, logging, and incident response.
- A plugin security model that differs between runtime and audit tooling undermines trust in both.

Recommendation:
- Decide whether `cli-offload` is an approved production extension.
- Make its load path, ownership, and allowlisting explicit and consistent across runtime and audit workflows.
- Review whether detached shell-based offloading is still acceptable for this deployment’s threat model.

OpenClaw alignment check:
- `/opt/openclaw/runtime/docs/tools/plugin.md` and `/opt/openclaw/runtime/docs/cli/security.md` both support explicit trust boundaries for non-bundled code.
- This recommendation aligns with upstream plugin hygiene rather than replacing it.

Example snippet:

```sh
bash -c 'cd "/home/agent-main" && claude "<prompt>"'
```

Verification idea:
- Compare the runtime-loaded plugin inventory with the plugin inventory seen by the OpenClaw security audit, using the same config and state environment.

### [OC-008] The Shared Governance Mount Mixes Policy, Secrets, and Mutable Runtime State

Severity: Medium  
Category: Maintainability  
Conflict: A directory that should represent stable governance intent also contains token material and mutable automation state.  
Confidence: High  
Scope: governance reviewability, secret handling, n8n/state hygiene

Evidence:
- `/opt/openclaw/discord-agents/shared-governance/.discord-token` is present in the governance mount and readable by other users.
- `/opt/openclaw/discord-agents/shared-governance/.n8n-law1-state.json` is mutable runtime state living next to governance artifacts.
- `/opt/openclaw/discord-agents/shared-governance/.n8n-law2-state.json` follows the same pattern.
- `/root/claws-and-pincers/governance/operations/CORE-CHARTER.md` represents governance as stable policy intent, which is hard to preserve when mixed with state and secrets.

Why it matters:
- Governance assets become harder to review, diff, and trust when they share a directory with mutable state.
- Token material stored in the same path widens accidental disclosure risk.
- Backup, restore, and audit behavior become ambiguous because policy and runtime state are co-located.

Recommendation:
- Separate governance content from secret storage and mutable runtime state.
- Treat the governance mount as policy content, not as a general-purpose runtime scratch area.
- Tighten permissions on token-bearing files.

OpenClaw alignment check:
- This is aligned with the project’s governance model and with the security audit’s concern about readable sensitive state.
- It does not introduce a new rule; it restores clearer separation of concerns.

Example snippet:
- None needed.

Verification idea:
- Identify every service that reads from `/opt/openclaw/discord-agents/shared-governance` and classify each file there as policy, secret, or mutable state.

### [OC-009] Live Agent Workspaces Have Drifted from Repo Prompt Definitions

Severity: Medium  
Category: Maintainability  
Conflict: Repo prompts and mounted runtime prompts no longer form a trustworthy mirror of one another.  
Confidence: High  
Scope: agent behavior, prompt governance, deployment verification

Evidence:
- `/root/claws-and-pincers/agents/developer/USER.md` exists in the repo.
- `/opt/openclaw/config/workspace-developer` does not contain the repo’s `USER.md`.
- `/root/claws-and-pincers/agents/developer/TOOLS.md` exists in the repo.
- `/opt/openclaw/config/workspace-developer` does not contain the repo’s `TOOLS.md`.
- Other agent workspace files under `/root/claws-and-pincers/agents` and the corresponding live directories under `/opt/openclaw/config` also differ materially.
- `/opt/openclaw/runtime/docs/concepts/multi-agent.md` treats per-agent workspace content as operative input.

Why it matters:
- Reviewing only the repo no longer tells you how the live agents are actually behaving.
- Prompt drift is especially dangerous because it can change behavior without obvious code/config diffs.
- The missing developer prompt files are a concrete sign that sync assumptions are broken, not theoretical.

Recommendation:
- Decide whether repo prompts should overwrite live workspaces, live workspaces should be promoted back to repo, or a third generated source owns both.
- Add a drift check before future deployments or reviews.
- Treat repo-only prompt review as incomplete until this is resolved.

OpenClaw alignment check:
- This recommendation follows `/opt/openclaw/runtime/docs/concepts/multi-agent.md`, which assumes explicit, isolated, operative agent workspaces.
- It aligns the project with OpenClaw’s actual prompt model.

Example snippet:
- Repo: `agents/developer/USER.md` present
- Live: `workspace-developer/USER.md` absent

Verification idea:
- Diff each repo agent directory against its corresponding live workspace before any prompt-related rollout.

### [OC-010] Gateway Exposure and Auth Hardening Depend on a Direct Tailnet Bind, Not the Upstream Preferred Pattern

Severity: Medium  
Category: Security  
Conflict: Live gateway exposure diverges from OpenClaw’s preferred Tailscale pattern and already shows repeated failed pairing traffic.  
Confidence: Medium  
Scope: gateway ingress, auth surface, remote operator access

Evidence:
- `/opt/openclaw/gateway/docker-compose.yml` publishes port `18789` on both `127.0.0.1` and the tailnet IP.
- `/opt/openclaw/config/openclaw.json` sets `gateway.bind` to `lan`.
- An explicit OpenClaw security audit against the deployed state dir warned `gateway.auth_no_rate_limit`.
- `/opt/openclaw/data/logs/gateway.log` shows repeated `pairing-required` websocket failures from a remote tailnet client.
- `/opt/openclaw/runtime/docs/gateway/tailscale.md` recommends `gateway.bind: "loopback"` with Tailscale Serve as the preferred exposure model.

Why it matters:
- The current pattern may be intentional, but it exposes the auth/pairing surface directly on the tailnet.
- The built-in audit already sees a hardening gap, and the logs show the remote path is actively being hit.
- Even if this is not a live incident, it is an operational hazard that should be explicitly justified and documented.

Recommendation:
- Confirm whether direct tailnet binding is a deliberate exception to upstream guidance.
- If it is, document compensating controls and the expected pairing/auth workflow.
- If it is not, treat this as a priority hardening review.

OpenClaw alignment check:
- This recommendation directly follows `/opt/openclaw/runtime/docs/gateway/tailscale.md` and the OpenClaw security audit output.
- It stays within the OpenClaw model rather than substituting a different networking pattern.

Example snippet:
- Preferred upstream pattern: `loopback + tailscale serve`
- Current deployed pattern: `lan + direct tailnet bind`

Verification idea:
- Map the intended remote access flow end-to-end, including pairing, auth throttling, and operator device expectations, then compare it with the actual published ports and observed log traffic.

---

## 4. Triage Summary

### Tier 1: Immediate review recommended

- [OC-001] Secret-bearing session transcripts are stored in readable active state.
- [OC-002] Discord ingress is broader than the allowlist name suggests.
- [OC-003] Source-of-truth boundaries are split and operationally misleading.
- [OC-004] The general RAG/MCP layer does not reliably serve the OpenClaw corpus.
- [OC-007] Plugin loading and provenance controls are inconsistent around `cli-offload`.

### Tier 2: Important but not blocking

- [OC-005] Active config directories contain stale shadow configs and policy files.
- [OC-006] Declared tool policies do not match the runtime tool registry.
- [OC-008] The shared governance mount mixes policy, secrets, and mutable runtime state.
- [OC-009] Live agent workspaces have drifted from repo prompt definitions.
- [OC-010] Gateway exposure and auth hardening depend on a direct tailnet bind.

### Tier 3: Cleanup, consistency, or future hardening

- No separate Tier 3-only items. The drift and orphan matrix below contains several medium-priority cleanup targets that should be handled after Tier 1 and Tier 2 ownership is settled.

---

## 5. Drift and Orphan Matrix

| Item / Path | Active / Inactive / Unclear | Why it appears orphaned or drifted | Risk if left alone | Recommendation |
|---|---|---|---|---|
| `/root/claws-and-pincers/scripts/openclaw-docs-scraper` | Active | Primary reliable OpenClaw reference path; not cleanup cruft | Low | Keep |
| `/opt/openclaw/config/openclaw.json5` | Inactive or stale | Sits in active config dir but reflects older architecture | High operator confusion risk | Archive later |
| `/opt/openclaw/config/model-routing.yaml` | Unclear | Diverges from `/root/claws-and-pincers/config/model-routing.yaml` with no clear ownership rule | Misrouting or policy confusion | Investigate further |
| `/opt/openclaw/config/cost-registry.yaml` | Unclear | Diverges from repo copy in an active path | Cost/governance drift | Investigate further |
| `/opt/openclaw/config/capability-timeline.yaml` | Unclear | Diverges from repo copy in an active path | Capability/policy confusion | Investigate further |
| `/opt/openclaw/config/permission-tiers.yaml` | Unclear | Diverges from repo copy in an active path | Permission model drift | Investigate further |
| `/opt/openclaw/CONFIG-SOURCE-OF-TRUTH.md` | Active but drifted | Describes an older per-agent deployment model | Humans update the wrong path | Investigate further |
| `/opt/openclaw/scripts/sync-from-repo.sh` | Historical | Writes to old per-agent workspace paths | Accidental bad sync into dead targets | Archive later |
| `/opt/openclaw/discord-agents/shared-governance/.n8n-law1-state.json` | Active but misplaced | Mutable runtime state inside governance mount | Review noise and backup ambiguity | Investigate further |
| `/opt/openclaw/discord-agents/shared-governance/.n8n-law2-state.json` | Active but misplaced | Mutable runtime state inside governance mount | Same | Investigate further |
| `/root/rugs-mcp` | Active but domain-stale | Still centered on `rugs.fun` and Local AI semantics, not OpenClaw | Incorrect knowledge grounding | Investigate further |
| `/opt/openclaw/config/extensions/cli-offload` | Active but provenance-unclear | Runtime loads it, audit/provenance story is inconsistent | Untrusted extension risk | Investigate further |
| `/opt/openclaw/config/workspace-developer` | Active but drifted | Missing repo prompt files and diverges from repo intent | Live behavior not reproducible from repo | Investigate further |

---

## 6. Open Questions

- Is `/opt/openclaw/config/openclaw.json` the only intended runtime config source, or are repo files under `/root/claws-and-pincers` supposed to converge into it automatically?
- Are the duplicated YAML policy/config files under `/opt/openclaw/config` still consumed by any live process, or are they only historical carryovers?
- Is `cli-offload` intentionally approved for production use, and what path and owner should be treated as authoritative for that plugin?
- Is the allowlisted Discord guild fully private and trusted, or is the current absence of `users` or `roles` or `channels` a misconfiguration rather than a deliberate choice?
- Should `openclaw_docs` be exposed through `/root/rag-api` and `/root/rugs-mcp`, or is the dedicated docs scraper the only sanctioned OpenClaw knowledge interface?
- Are session transcripts expected to retain raw credential material, or is that an unintended side effect of current tooling/logging behavior?
- Is the client repeatedly hitting pairing-required responses an expected operator device, and if so, what is the intended pairing/auth flow?

---

## 7. Recommended Next Actions

1. Review `/opt/openclaw/config/agents/main/sessions`, `/opt/openclaw/config`, and `/opt/openclaw/discord-agents/shared-governance` as sensitive state, then decide ownership, retention, and permission requirements before any other expansion work.
2. Validate the Discord access model in `/opt/openclaw/config/openclaw.json` against the intended human/bot/channel matrix and OpenClaw’s Discord rules.
3. Establish and document one authoritative source of truth for runtime config and one for agent prompt content, then verify that repo and live workspaces converge.
4. Reconcile the configured tool/plugin surface with the actual runtime registry, especially `apply_patch`, `discord`, `cron`, and `cli-offload`.
5. Decide whether the supported OpenClaw knowledge baseline is the docs scraper only or a docs-scraper-plus-RAG/MCP model, then align `/root/rag-api` and `/root/rugs-mcp` to that decision.
6. Inventory stale shadow config files in `/opt/openclaw/config` and older operational artifacts such as `/opt/openclaw/CONFIG-SOURCE-OF-TRUTH.md` and `/opt/openclaw/scripts/sync-from-repo.sh`.
7. Review the gateway’s remote exposure and pairing/auth workflow against `/opt/openclaw/runtime/docs/gateway/tailscale.md` and the current audit warnings before future remote-access changes.
