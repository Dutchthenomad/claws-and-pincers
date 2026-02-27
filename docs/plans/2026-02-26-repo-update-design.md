# Design: Repository Update & Phase Roadmap Restructure

**Date:** 2026-02-26
**Author:** Devin + Claude Code
**Status:** Approved

---

## Context

The Claws & Pincers project has evolved significantly since the last repo sync:

- All 5 Discord agents are deployed and online
- Model stack migrated from mixed Anthropic/Groq/Google to OpenRouter-first routing
- Discord multi-agent setup deployed
- OpenClaw runtime updated from 2026.1.27-beta.1 to 2026.2.25
- Static config approach identified as fragile; n8n adopted as the control plane

## Design Decisions

### 1. n8n as Universal Control Plane

Static YAML/JSON configs are state snapshots, not enforcement mechanisms. They suffer from:
- Silent omission when context degrades
- No runtime validation or conflict detection
- Difficult to debug, version, or audit in real-time

**n8n workflows become the living, enforceable, debuggable truth** for:
- Absolute Laws enforcement (the original 7 workflows)
- Memory framework orchestration (OpenClaw Memory + per-agent namespaces)
- Agent file structure lifecycle management
- Responsibility and config evolution per agent
- Discord channel/category structure (informed by all of the above)

### 2. OpenRouter as Unified Provider

All 5 Discord agents route through OpenRouter with frontier models:

| Agent | Primary Model | Fallback |
|-------|--------------|----------|
| Orchestrator | anthropic/claude-opus-4-6 | moonshotai/kimi-k2.5 |
| Developer | minimax/minimax-m2.5 | moonshotai/kimi-k2.5 |
| Researcher | x-ai/grok-4.1-fast | moonshotai/kimi-k2.5 |
| SysAdmin | moonshotai/kimi-k2.5 | google/gemini-3-flash-preview |
| Reviewer | google/gemini-3-flash-preview | moonshotai/kimi-k2.5 |

### 3. Phase Structure

- **Phase 1:** COMPLETE (agent definitions, config, deployment, housekeeping)
- **Phase 2:** n8n Core Systems Architecture (Laws, Memory, File Structures, Configs, Channels)
- **Phase 3:** Context & Token Optimization (caching audit, skills refinement, research proposal)
- **Phase 4:** Research - LangChain/LangFlow/LangGraph evaluation for orchestration augmentation

### 4. Memory Architecture

- **Existing:** OpenClaw Memory API at localhost:8002 (SQLite + FTS5, MCP server, hooks)
- **Planned:** Per-agent namespaced memory contexts, managed via n8n workflows
- **Integration:** n8n orchestrates memory lifecycle, not static config

### 5. LangChain/LangFlow/LangGraph Evaluation

Added as Phase 4 research item - evaluate whether these frameworks add meaningful scalability and capability to the n8n-based orchestration pipeline. This is exploratory, not committed. The decision criteria: does it optimize end-use goals more effectively than n8n alone?

## Files Modified

- `openclaw.json5` - Match live merged config
- `config/model-routing.yaml` - OpenRouter model stack
- `config/cost-registry.yaml` - Updated cost tracking
- `README.md` - Current status and architecture
- `PROJECT-REFRESHER.md` - Full state refresh
- `TODO.md` - New phase structure
- `governance/operations/CORE-CHARTER.md` - Model assignments and provider updates
