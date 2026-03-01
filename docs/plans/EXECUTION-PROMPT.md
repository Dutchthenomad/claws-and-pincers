# Execution Prompt — Native OpenClaw Alignment

> Copy everything below the line into a new Claude Code session to execute the full implementation plan.

---

## PROMPT START

You are executing a comprehensive implementation plan to bring the **Claws & Pincers** project into full compliance with the OpenClaw platform. This is a large, multi-phase task affecting ~65 files.

### Mandatory Session Start

Before doing ANY work, read these files IN THIS ORDER:

1. `docs/plans/OPENCLAW-COMPLIANCE-AUDIT.md` — The audit that identified 9 compliance issues (C-01 through C-09) and 10 optimization opportunities (O-01 through O-10). This is your "why."
2. `docs/plans/IMPLEMENTATION-PLAN-NATIVE-OPENCLAW.md` — The detailed implementation plan with 8 phases, file-by-file instructions, and the exact changes required. This is your "what" and "how."
3. `governance/operations/CORE-CHARTER.md` — The current v1.1 charter you'll be rewriting to v2.0.
4. `openclaw.json5` — The current gateway config you'll be hardening.

Then verify you're working on current code:
```bash
cd /root/claws-and-pincers && git fetch origin && git status
```
If behind origin/main, pull before making changes.

### OpenClaw Documentation (Gold Standard)

Before writing ANY OpenClaw config, agent workspace files, or gateway settings, you MUST consult the official docs. Query the local RAG system:

```bash
cd /root/claws-and-pincers/scripts/openclaw-docs-scraper
.venv/bin/python3 query.py "your question" --top-k 5
```

Key queries to run before starting work:
- `"sessions_spawn sessions_send session tools"` — for session-based coordination
- `"cron jobs scheduling"` — for native cron setup
- `"heartbeat configuration per-agent"` — for heartbeat intervals
- `"agent workspace layout SOUL AGENTS HEARTBEAT BOOT"` — for workspace file structure
- `"memory-core plugin workspace memory"` — for native memory
- `"agentToAgent allow deny"` — for hub-and-spoke communication
- `"sandbox mode tool policy elevated"` — for security hardening
- `"hooks webhooks"` — for webhook integration
- `"openai http api chat completions"` — for API endpoint config

Use the RAG results to inform your implementation. If a RAG result contradicts the plan, the RAG result (official docs) takes precedence. Flag the discrepancy in a comment.

### Execution Rules

1. **Follow the plan phases in order.** Phase dependencies exist (see plan's Dependencies section).
2. **Read every file before editing it.** Do not edit a file you haven't read in this session.
3. **Preserve what works.** The 4 Laws, severity system, R&M character identities, and anti-patterns are all good. You're changing HOW they're implemented, not WHAT they say.
4. **Use the plan's decision points.** Where the plan says "Option A (Recommended)" — use Option A unless you discover a concrete reason not to.
5. **Commit after each phase** using the commit sequence in Phase 8.5 of the plan. Use conventional commit format (`feat:`, `docs:`, `chore:`).
6. **Do NOT push to remote.** Commit locally only. I will review and push.
7. **Do NOT modify files in `docs/archive/`** — those are historical records.
8. **Do NOT modify `CLAUDE.md`** — that's separate from the repo docs.
9. **Use the TaskCreate/TaskUpdate tools** to track your progress through the phases.

### Phase Execution Guide

#### Phase 1: Config Hardening (`openclaw.json5`)

Read the current `openclaw.json5` carefully. Apply ALL changes from Phase 1 of the plan:
- 1.1: Per-agent `agentToAgent` (hub-and-spoke)
- 1.2: Per-agent heartbeat intervals with model overrides
- 1.3: Tool permission tightening (deny exec for Orchestrator/Researcher, add session tools)
- 1.4: Enable hooks, cron, openaiApi, memory-core plugin, execApprovals
- 1.5: Developer sandbox to `lenient`

For `execApprovals.approvers`, use a placeholder `"<DEVIN_DISCORD_USER_ID>"` — I'll fill it in.

Query the RAG before making config changes to verify syntax:
```bash
.venv/bin/python3 query.py "openclaw.json5 configuration syntax example"
```

**Commit:** `feat: harden openclaw.json5 (hub-and-spoke, heartbeats, tool policy, native features)`

#### Phase 2: CORE-CHARTER v2.0

Read the current charter at `governance/operations/CORE-CHARTER.md`. Rewrite it to v2.0 following the plan's section-by-section table. Key transformations:
- `task-board.json` → `sessions_spawn` / `sessions_list`
- `active-locks.json` → session isolation
- `conflict-registry.json` → Discord channel + agent memory
- File-based coordination → session-based coordination
- n8n governance enforcement → native OpenClaw cron + AGENTS.md enforcement
- Custom file layout → OpenClaw native workspace layout

The 4 Laws stay. The governance philosophy stays. The enforcement mechanism changes from external (n8n + JSON files) to native (OpenClaw sessions + cron + AGENTS.md).

Add two new sections:
1. "OpenClaw Native Features" — documenting cron, heartbeats, sessions, memory-core, threads, webhooks
2. "n8n Scope" — clarifying n8n is for external integrations only

**Commit:** `docs: rewrite CORE-CHARTER v2.0 (session-based coordination)`

#### Phase 3: Agent Workspace Files (35 files)

This is the largest phase. Work through it agent-by-agent (orchestrator first, then researcher, developer, sysadmin, reviewer).

For EACH agent, read ALL 6 of their workspace files before editing any of them. Then:

**AGENTS.md (5 files):** Apply ALL common changes listed in the plan (remove JSON file refs, add session tools, embed 4 Laws summary, add anti-patterns summary). Then apply agent-specific changes.

**HEARTBEAT.md (5 files):** Replace file-polling tasks with session-based checks per the plan's per-agent table.

**SOUL.md (5 files):** Minor updates — remove stale coordination refs, keep R&M identities.

**TOOLS.md (5 files):** Add session tool docs where appropriate, remove denied tool references.

**USER.md (5 files):** Remove any n8n-as-control-plane or file-coordination references.

**IDENTITY.md (5 files):** Verify consistency with SOUL.md. No content changes unless inconsistent.

**BOOT.md (5 NEW files):** Create for each agent with startup governance checklist per the plan.

**BOOTSTRAP.md (5 files):** Remove from all agent dirs (Option A — identities are pre-populated in IDENTITY.md).

**Commit:** `docs: update all agent workspace files for native OpenClaw alignment`

#### Phase 4: Governance & Template Docs (7 files)

Update the 4 governance templates to replace file-based references with session-based equivalents. Update `anti-patterns.md` with the replication note. Update `PROJECT-REGISTRY.md` and `EXPANSION-ROADMAP.md`.

For the shared JSON files (`task-board.json`, `active-locks.json`, `conflict-registry.json`): move them to `docs/archive/governance/` to preserve history.

**Commit:** `docs: update governance templates and shared files`

#### Phase 5: Reference, Operations, Planning & Config Docs (~20 files)

Work through ALL files listed in Phase 5 of the plan. The plan categorizes each file by change severity (CRITICAL REWRITE, MAJOR, MODERATE, MINOR, NONE).

Start with the CRITICAL REWRITES:
- `reference/03-MULTI-AGENT-ARCHITECTURE.md`
- `reference/04-AGENT-COMMUNICATION.md`

Then MAJOR rewrites:
- `reference/07-SERVER-ARCHITECTURE.md`
- `reference/08-CONFIGURATION-REFERENCE.md`
- `reference/11-DEPLOYMENT-GUIDE.md`
- `docs/plans/SESSION-CONTINUITY.md`
- `TODO.md`

Then moderate and minor changes.

Archive the two legacy config files:
```bash
mkdir -p docs/archive/config
git mv config/capability-timeline.yaml docs/archive/config/
git mv config/permission-tiers.yaml docs/archive/config/
```

**Commit (split into 2):**
1. `chore: archive legacy config files (capability-timeline, permission-tiers)`
2. `docs: update reference, operations, planning, and top-level docs`

#### Phase 6: n8n Scope Reduction

This phase involves config changes and documentation updates, NOT disabling live n8n workflows (I'll do that manually). Focus on:
- Adding cron job configs to `openclaw.json5` (the cron commands in the plan are illustrative — add the config-file equivalents)
- Adding webhook config to `openclaw.json5`
- Updating `docs/plans/2026-02-27-phase2a-laws-enforcement-design.md` with deprecation addendum

**Commit:** `feat: add cron jobs and webhook config for native governance`

#### Phase 7: README.md Marketing Landing Page

Read the current `README.md`, then rewrite it completely following the plan's structure and quality standards:
- Professional, marketing-quality writing
- Mermaid architecture diagram (must render on GitHub)
- Clean agent team table
- Brief governance section highlighting the 4 Laws
- Tech stack, project structure, getting started
- Current status
- Author credit (Dutchthenomad / Devin)

The tone should make someone on GitHub think "this is a serious, well-organized project" within 5 seconds of landing on it. No fluff, no over-explaining — concise and impressive.

**Commit:** `docs: rewrite README.md as marketing landing page`

#### Phase 8: Verification & Cleanup

Run the verification scans from Phase 8.1 of the plan:
```bash
cd /root/claws-and-pincers

# Scan for stale references in active docs (exclude archive and .venv)
for term in "task-board.json" "active-locks.json" "conflict-registry.json"; do
  echo "=== Searching for: $term ==="
  grep -r "$term" --include="*.md" --include="*.yaml" --include="*.json5" \
    --exclude-dir=docs/archive --exclude-dir=.venv --exclude-dir=.git . || echo "CLEAN"
done

grep -rP "n8n.*(universal control plane|governance)" --include="*.md" \
  --exclude-dir=docs/archive --exclude-dir=.venv --exclude-dir=.git . || echo "CLEAN"
```

If any stale references remain, fix them. Then report what you found.

Do NOT run the deployment commands (8.2, 8.3) — I will do that manually after review.

### Context Management

This is a large task (~65 files). To manage context effectively:
- Use parallel subagents where phases allow independent work
- After completing each phase, consider if compaction is needed
- If you hit context limits mid-phase, commit what you have and note where you stopped
- The plan document itself (`IMPLEMENTATION-PLAN-NATIVE-OPENCLAW.md`) is your single source of truth — re-read it if you lose track

### What Success Looks Like

When you're done:
1. All 8 phases completed with individual commits
2. Zero stale references to `task-board.json`, `active-locks.json`, `conflict-registry.json` in active docs
3. Zero references to n8n as "universal control plane" in active docs
4. `openclaw.json5` has hub-and-spoke routing, per-agent heartbeats, native features enabled
5. CORE-CHARTER is v2.0 with session-based coordination
6. All 30 agent workspace files updated + 5 new BOOT.md files + 5 BOOTSTRAP.md files removed
7. README.md is a professional marketing landing page
8. Two legacy config files archived
9. All changes committed locally (not pushed)

Report a summary of every commit made and any issues encountered when finished.
