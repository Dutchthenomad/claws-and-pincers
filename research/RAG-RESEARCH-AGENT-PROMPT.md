# RAG Knowledge Research & Collection Task

> **Project**: Claws and Pincers (OpenClaw Personal AI Agent)
> **Repository**: https://github.com/Dutchthenomad/claws-and-pincers
> **Created**: 2026-01-31
> **Purpose**: Produce actionable knowledge ingestion plan for RAG system

---

## Context

I am deploying **OpenClaw** (https://openclaw.ai) - a personal AI assistant with autonomous capabilities - on a dedicated VPS. The system requires comprehensive RAG knowledge to function effectively across multiple domains.

### Current RAG Infrastructure

**Existing Collections** (already indexed - DO NOT DUPLICATE):

| Collection | Chunks | Key Content |
|------------|--------|-------------|
| `localai_knowledge` | 2000 | RunPod serverless, llama.cpp, PEFT/LoRA, abliteration guides, training docs, quantization, ComfyUI, Stable Diffusion |
| `external_docs` | 1110 | MCP servers, Anthropic cookbook, risk management, Bayesian methods, quant trading (qlib) |
| `rugs_protocol` | 442 | Domain-specific game mechanics (ignore for this task) |
| `rl_design` | 40 | Reinforcement learning design |

**Specific content already indexed:**
- `localai/02-runpod/` - RunPod serverless docs, workers, API
- `localai/08-uncensored-llms/guides/abliteration_guide.md` - FailSpy's abliteration method
- `localai/09-llama-cpp/` - Full llama.cpp documentation
- `localai/03-huggingface/peft/` - PEFT, LoRA, quantization
- `localai/16-interpretability/` - Representation engineering, abliteration tools
- `external-docs/mcp/` - MCP servers, Anthropic cookbook

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         OpenClaw Stack                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   TELEGRAM   │    │   CLAUDE     │    │   RUNPOD     │      │
│  │   Channel    │◄──►│   API        │◄──►│   LLMs       │      │
│  │   (Primary)  │    │   (Primary)  │    │   (Ablated)  │      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────────────────────────────────────────────┐      │
│  │              OpenClaw Gateway                         │      │
│  │  • Tool execution    • Authorization tiers            │      │
│  │  • Session mgmt      • Memory persistence             │      │
│  │  • Model routing     • Audit logging                  │      │
│  └──────────────────────────────────────────────────────┘      │
│         │                   │                   │               │
│         ▼                   ▼                   ▼               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐      │
│  │   VOICE      │    │   CRYPTO     │    │   SPENDING   │      │
│  │   2FA        │    │   (USDC)     │    │   (Cards)    │      │
│  │   Biometric  │    │   on Base    │    │   Privacy.com│      │
│  └──────────────┘    └──────────────┘    └──────────────┘      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Authorization Tiers

| Tier | Authorization | Example Actions |
|------|--------------|-----------------|
| 0 | Unrestricted | Research, file ops, RAG queries |
| 1 | Notify only | API reads, scheduling, git local |
| 2 | Telegram approval | Email send, social post, tx <$50 |
| 3 | Voice biometric 2FA | Tx >$50, root commands, secrets |
| 4 | Hardcoded deny | Security bypass, logging disable |

---

## Research Objectives

### Primary Goal

Produce a **detailed, prioritized action list** for knowledge collection and RAG ingestion that:
1. Fills gaps in current knowledge (see "Knowledge Gaps" below)
2. Avoids duplicating existing content
3. Provides specific URLs, page ranges, and chunk recommendations
4. Enables autonomous operation of the OpenClaw agent

### Knowledge Gaps to Fill

#### 1. OpenClaw Platform (CRITICAL - P0)

**Current State**: NOT INDEXED
**Required Knowledge**:
- OpenClaw gateway architecture and configuration
- Tool system specification and custom tool creation
- Skill definition and MCP integration
- Channel configuration (especially Telegram)
- Memory and context persistence
- Multi-model routing configuration
- Session management and sandboxing

**Sources to Investigate**:
- https://docs.openclaw.ai (if exists)
- https://github.com/openclaw/openclaw (documentation)
- https://clawhub.com (skill marketplace)
- Any blog posts, tutorials, or examples

**Deliverable**: Complete list of documentation pages with priority and estimated chunk counts.

---

#### 2. Telegram Bot API (P0)

**Current State**: NOT INDEXED
**Required Knowledge**:
- Bot creation and @BotFather commands
- Message handling (text, voice, media)
- Inline keyboards and callbacks
- Webhooks vs long polling
- Voice message handling (critical for 2FA)
- Rate limits and best practices
- Python libraries (python-telegram-bot, aiogram)

**Sources to Investigate**:
- https://core.telegram.org/bots/api
- https://core.telegram.org/bots/features
- https://docs.python-telegram-bot.org
- https://docs.aiogram.dev

**Deliverable**: Prioritized list of API sections, focusing on voice message handling.

---

#### 3. Voice Biometric Authentication (P1)

**Current State**: Only ElevenLabs (TTS) indexed - NO speaker verification
**Required Knowledge**:
- Speaker verification fundamentals
- Voiceprint enrollment processes
- Liveness detection / anti-spoofing
- Open-source implementations (Resemblyzer, SpeechBrain, pyannote)
- Threshold tuning and FAR/FRR tradeoffs
- Integration with messaging platforms

**Sources to Investigate**:
- https://speechbrain.github.io (speaker verification docs)
- https://huggingface.co/pyannote
- https://github.com/resemble-ai/Resemblyzer
- Academic papers on speaker verification
- Anti-spoofing techniques (ASVspoof challenge)

**Deliverable**: Implementation-focused documentation list with model recommendations.

---

#### 4. Crypto Wallet Integration (P1)

**Current State**: NOT INDEXED
**Required Knowledge**:
- Base network specifics (L2, gas, RPC endpoints)
- USDC on Base (contract address, decimals)
- ethers.js / viem wallet operations
- Transaction signing and broadcasting
- Gas estimation on L2
- Hot wallet security patterns
- Monitoring and alerting

**Sources to Investigate**:
- https://docs.base.org
- https://developers.circle.com/stablecoins/docs/usdc-on-main-networks
- https://docs.ethers.org/v6/
- https://viem.sh/docs
- Base network tutorials and examples

**Deliverable**: Essential documentation for programmatic USDC transfers.

---

#### 5. vLLM Deployment (P1)

**Current State**: RunPod indexed but vLLM specifics may be limited
**Required Knowledge**:
- vLLM server configuration
- Model loading and quantization
- OpenAI-compatible API endpoints
- Tensor parallelism for large models
- Memory optimization techniques
- Streaming and async inference
- RunPod + vLLM integration specifics

**Sources to Investigate**:
- https://docs.vllm.ai
- https://github.com/vllm-project/vllm (README, examples)
- RunPod vLLM worker templates
- Community guides for specific models

**Deliverable**: Configuration reference for deploying 8B-70B models on RunPod.

---

#### 6. Current SOTA Ablated Models (P1)

**Current State**: Abliteration guide indexed but model-specific info limited
**Required Knowledge**:
- Current best ablated/uncensored models (Jan 2026)
- Model cards and capabilities (Dolphin, WizardLM, etc.)
- VRAM requirements per model
- Quantization quality tradeoffs
- Prompt engineering for maximum truthfulness
- Community benchmarks (uncensored model comparisons)
- Eric Hartford's work (Cognitive Computations)

**Sources to Investigate**:
- https://huggingface.co/cognitivecomputations
- https://huggingface.co/collections/failspy/abliterated-v3-664a8ad0db255eefa7d0012b
- https://erichartford.com/uncensored-models
- Model comparison leaderboards
- Community discussions (r/LocalLLaMA, etc.)

**Deliverable**: Model comparison matrix with VRAM, quality, and use case recommendations.

---

#### 7. Docker Security Hardening (P2)

**Current State**: Limited in RAG
**Required Knowledge**:
- Seccomp profiles for LLM containers
- AppArmor profiles
- Read-only filesystems
- Capability dropping best practices
- Network namespace isolation
- Resource limits (cgroups)
- Container escape prevention

**Sources to Investigate**:
- https://docs.docker.com/engine/security/
- OWASP Container Security Cheat Sheet
- CIS Docker Benchmark
- Falco/Sysdig security guides

**Deliverable**: Security checklist and example profiles.

---

#### 8. Privacy.com / Virtual Cards (P2)

**Current State**: NOT INDEXED
**Required Knowledge**:
- Account setup and verification
- Virtual card creation patterns
- Merchant-locking functionality
- Spending limits and controls
- Transaction notifications
- API access (if available)

**Sources to Investigate**:
- https://privacy.com/virtual-card
- Privacy.com help center
- Developer documentation (if exists)

**Deliverable**: Feature summary and integration patterns (manual if no API).

---

#### 9. Anthropic Claude API (P1)

**Current State**: Cookbook indexed, but verify API completeness
**Required Knowledge**:
- Messages API (current)
- Tool use / function calling
- Streaming responses
- Token counting and context management
- Error handling and retries
- Rate limits and best practices
- Vision capabilities

**Sources to Investigate**:
- https://docs.anthropic.com/en/api
- https://docs.anthropic.com/en/docs/build-with-claude/tool-use
- Anthropic SDK (Python, TypeScript)

**Deliverable**: Confirm coverage, identify any gaps in existing indexed content.

---

## Deliverable Format

For each knowledge domain, provide:

```yaml
domain: "[Domain Name]"
priority: P0 | P1 | P2
current_state: "What's already indexed (if any)"

sources:
  - url: "https://..."
    type: "docs | github | blog | paper | api-ref"
    pages_or_sections:
      - "Section name or path"
      - "Another section"
    estimated_chunks: 50
    notes: "Any special considerations"

  - url: "..."
    # ...

ingestion_strategy:
  chunk_size: 512 | 1024
  chunk_overlap: 50 | 100
  metadata_tags:
    - "tag1"
    - "tag2"

dependencies:
  - "Must ingest X before Y because..."

verification:
  - "How to verify this knowledge is working"
```

---

## Additional Research Questions

Please also investigate and report on:

1. **OpenClaw Availability**: Is OpenClaw actually publicly available? If not, what are the alternatives (OpenHands, AgentGPT, AutoGPT, etc.)?

2. **Voice Auth Libraries**: What's the current best open-source speaker verification library for real-time use (< 2s latency)?

3. **Model Routing Patterns**: Are there existing frameworks for routing between Claude and self-hosted models based on query type?

4. **RunPod Cold Start**: What are the actual cold start times for vLLM on A100 with a 70B model?

5. **Base Gas Costs**: Current average transaction cost for USDC transfer on Base?

---

## Constraints

- **Avoid Duplication**: Cross-reference with existing collections before recommending ingestion
- **Prioritize Official Docs**: Prefer official documentation over blog posts
- **Note Freshness**: Flag any content that may be outdated (pre-2025)
- **Flag Auth Requirements**: Note any sources requiring authentication
- **Estimate Effort**: Provide rough token/chunk estimates per source

---

## Output Format

Produce a markdown report with:

1. **Executive Summary** - Key findings and recommendations
2. **Knowledge Gap Analysis** - Per-domain breakdown
3. **Prioritized Ingestion List** - Ordered by criticality
4. **Dependency Graph** - What must be ingested first
5. **Verification Checklist** - How to confirm successful ingestion
6. **Open Questions** - Things requiring human decision

---

## Project Context

This is for a **proactive research methodology** focused on:
- Maximizing epistemic access through ablated models
- Rigorous scientific method application
- Proactive identification of potential fraud/abuse vectors
- Ensuring fundamental truths aren't obscured by guardrails

The goal is an AI agent that can operate autonomously within defined safety boundaries, with the ability to escalate uncertain decisions through a tiered authorization system.

---

*Research prompt created: 2026-01-31*
*Repository: https://github.com/Dutchthenomad/claws-and-pincers*
