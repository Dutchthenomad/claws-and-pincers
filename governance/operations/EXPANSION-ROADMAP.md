# EXPANSION ROADMAP

**Authority:** Devin  
**Maintained by:** Orchestrator

---

## Phase 1 — Core Crew ✅ (Current)

**Agents:**
- 🧪 Orchestrator (claude-opus-4-6) — Coordinator — Rick Sanchez
- 🔬 Researcher (x-ai/grok-4.1-fast) — Research & analysis — Beth Smith
- 💻 Developer (minimax/minimax-m2.5) — Code & automation — Morty Smith
- 🖥️ Sysadmin (moonshotai/kimi-k2.5) — Infrastructure & deployment — Summer Smith
- 🔍 Reviewer/QA (google/gemini-3-flash-preview) — Quality assurance — Jerry Smith

**Infrastructure:**
- Discord server with per-agent categories
- Shared workspace channels
- Human control channels
- Logging & reporting channels
- Full governance framework (CORE-CHARTER.md)
- File-based coordination (task-board, locks, conflict registry)
- Self-learning anti-pattern system

**Milestone:** All governance rules operational, first project completed end-to-end through the full lifecycle.

---

## Phase 2 — Capabilities Expansion (Planned)

Potential new specialists. Each addition must go through the standard project process (charter, approval, PROJ-ID).

### Candidate Specialists

**🎨 Creative Specialist**
- Image generation, video production, design assets
- Could leverage MCP integrations (e.g., Invideo for video)
- Would need its own tools/API access

**📊 Data Analyst**
- Data processing, visualization, statistical analysis
- CSV/JSON/database querying
- Report generation

**🔐 Security Specialist**
- Vulnerability assessment
- Code security audit
- Dependency scanning
- Credential rotation monitoring

**📝 Technical Writer**
- Documentation, user guides, API docs
- README generation
- Changelog maintenance

### Addition Process
1. Identify need (team proposes or Devin directs)
2. Draft specialist charter as a PROJ-XXX project
3. Charter defines: role, tools, access, boundaries, Discord channels
4. Devin approves
5. Build: bot app, workspace, SOUL.md, config, channels, bindings
6. Test: isolated task execution before integrating with team
7. Deploy: add to active roster

---

## Phase 3 — Autonomy Enhancement (Future)

### On-Demand Specialist Spawning
- Orchestrator can spawn temporary specialist agents for burst work
- Uses OpenClaw `sessions_spawn` for short-lived task sessions
- Temporary agents inherit project context but don't persist
- Reduces idle token cost for rarely-needed capabilities

### Cross-Project Knowledge Transfer
- Completed project insights feed into `knowledge-base/`
- Agents can reference past project approaches
- Pattern library for common solution architectures

### Automated Charter Generation
- For recurring project types, Orchestrator can auto-generate charter drafts
- Templates with pre-filled sections based on project type
- Still requires Devin approval — automation is for drafting, not approving

### Self-Optimization
- Team retrospectives after project completion
- Governance rule amendments proposed by Orchestrator
- Workflow efficiency improvements identified through anti-pattern trends
- Still requires Devin approval for any charter amendments

---

## Phase 4 — Scale (Speculative)

### Multi-Team Coordination
- Multiple orchestrators managing separate teams
- Cross-team project collaboration
- Shared governance but independent operations

### Custom Tool Development
- Agents build their own tools/skills as shared apps
- ClawHub skill publishing for team-built capabilities
- Self-improving toolchain

---

## Decision Log

| Date | Decision | Phase | Approved By |
|------|----------|-------|-------------|
| 2026-02-16 | Initial Phase 1 core crew defined | 1 | Devin |
| 2026-02-28 | Models rotated to OpenRouter frontier mix | 1 | Devin |
| 2026-03-01 | R&M character identities assigned to all agents | 1 | Devin |
