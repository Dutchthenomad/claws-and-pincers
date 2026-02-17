# RAG Knowledge Collection - OpenClaw Platform Documentation

> **Generated**: 2026-01-31
> **Status**: Ready for ingestion
> **Target Collection**: `platform_docs` or `external_docs`

---

## Collection Summary

| Source | Priority | Chunks (Est.) | Status |
|--------|----------|---------------|--------|
| OpenClaw Docs | P0 | 400-500 | Collected |
| Telegram Bot API | P0 | 200-300 | Collected |
| SpeechBrain | P1 | 150-200 | Collected |
| Base Network | P1 | 200-300 | Collected |
| vLLM | P1 | 200-250 | Collected |

---

## 1. OpenClaw Documentation (P0)

**Base URL**: https://docs.openclaw.ai/

### URL Mapping by Section

#### Getting Started & Onboarding
- https://docs.openclaw.ai/
- https://docs.openclaw.ai/start/getting-started
- https://docs.openclaw.ai/start/onboarding

#### Installation & Setup
- https://docs.openclaw.ai/install
- https://docs.openclaw.ai/install/docker
- https://docs.openclaw.ai/install/installer
- https://docs.openclaw.ai/install/npm
- https://docs.openclaw.ai/install/pnpm
- https://docs.openclaw.ai/install/bun
- https://docs.openclaw.ai/install/railway
- https://docs.openclaw.ai/install/render
- https://docs.openclaw.ai/install/northflank
- https://docs.openclaw.ai/install/ansible
- https://docs.openclaw.ai/install/nix

#### Gateway & Architecture
- https://docs.openclaw.ai/gateway
- https://docs.openclaw.ai/gateway/configuration
- https://docs.openclaw.ai/gateway/configuration-examples
- https://docs.openclaw.ai/gateway/security
- https://docs.openclaw.ai/gateway/remote
- https://docs.openclaw.ai/gateway/background-process
- https://docs.openclaw.ai/gateway/logging
- https://docs.openclaw.ai/gateway/sandboxing
- https://docs.openclaw.ai/gateway/troubleshooting
- https://docs.openclaw.ai/gateway/doctor

#### Channels (Messaging Integration)
- https://docs.openclaw.ai/channels
- https://docs.openclaw.ai/channels/telegram
- https://docs.openclaw.ai/channels/whatsapp
- https://docs.openclaw.ai/channels/discord
- https://docs.openclaw.ai/channels/slack
- https://docs.openclaw.ai/channels/google-chat
- https://docs.openclaw.ai/channels/mattermost
- https://docs.openclaw.ai/channels/signal
- https://docs.openclaw.ai/channels/imessage
- https://docs.openclaw.ai/channels/bluebubbles
- https://docs.openclaw.ai/channels/microsoft-teams
- https://docs.openclaw.ai/channels/matrix
- https://docs.openclaw.ai/channels/zalo
- https://docs.openclaw.ai/channels/webchat

#### Tools & Skills
- https://docs.openclaw.ai/tools
- https://docs.openclaw.ai/tools/browser
- https://docs.openclaw.ai/tools/canvas
- https://docs.openclaw.ai/tools/nodes
- https://docs.openclaw.ai/tools/cron
- https://docs.openclaw.ai/tools/sessions
- https://docs.openclaw.ai/tools/skills
- https://docs.openclaw.ai/tools/clawhub
- https://docs.openclaw.ai/tools/exec-approvals

#### Concepts & Core Architecture
- https://docs.openclaw.ai/concepts/architecture
- https://docs.openclaw.ai/concepts/agent
- https://docs.openclaw.ai/concepts/agent-loop
- https://docs.openclaw.ai/concepts/agent-workspace
- https://docs.openclaw.ai/concepts/context
- https://docs.openclaw.ai/concepts/memory
- https://docs.openclaw.ai/concepts/models
- https://docs.openclaw.ai/concepts/oauth
- https://docs.openclaw.ai/token-use

#### CLI Reference
- https://docs.openclaw.ai/cli
- https://docs.openclaw.ai/cli/gateway
- https://docs.openclaw.ai/cli/approvals
- https://docs.openclaw.ai/cli/nodes
- https://docs.openclaw.ai/cli/models
- https://docs.openclaw.ai/cli/plugins
- https://docs.openclaw.ai/cli/voicecall

#### Help & Support
- https://docs.openclaw.ai/help/faq
- https://docs.openclaw.ai/help/troubleshooting

---

## 2. Telegram Bot API (P0)

**Base URL**: https://core.telegram.org/bots/api

### Key Sections for 2FA Voice System

#### Core Types
- **Update Object**: Receives incoming updates (messages, callbacks)
- **Message Object**: Contains voice messages in `voice` field
- **Voice Object**: Properties for voice notes
  - `file_id`: Identifier for downloading/reusing
  - `file_unique_id`: Persistent identifier
  - `duration`: Duration in seconds
  - `mime_type`: Typically `audio/ogg`
  - `file_size`: Size in bytes

#### Essential Methods
- **sendVoice**: Send voice message to user
  - Supports `message_thread_id` for forum topics
  - Parameters: `chat_id`, `voice`, `caption`, `duration`
- **getFile**: Retrieve file metadata and download path
  - Returns `file_path` for CDN download
  - Local server returns absolute path
- **setWebhook**: Configure update delivery
  - HTTPS required
  - Supports `secret_token` for validation
  - Max 100,000 connections with local server

#### File Handling
- Download URL: `https://api.telegram.org/file/bot<TOKEN>/<file_path>`
- `file_id` is bot-specific, can be reused
- `file_unique_id` is persistent across all bots

#### Version Info
- Current: Bot API 9.3 (December 31, 2025)

---

## 3. SpeechBrain Speaker Verification (P1)

**Base URL**: https://speechbrain.readthedocs.io/en/latest/

### Core API for Voice Biometric 2FA

#### SpeakerRecognition Class
- **Location**: `speechbrain.inference.speaker`
- **Parent**: Extends `EncoderClassifier`

#### Key Methods
```python
# Verify two waveforms at 16kHz
verify_batch(wavs1, wavs2, threshold=0.25)
# Returns: (cosine_score, binary_prediction)
# 1 = same speaker, 0 = different speaker

# File-based convenience method
verify_files(file1, file2)

# Load pretrained model
SpeakerRecognition.from_hparams(
    source="speechbrain/spkrec-ecapa-voxceleb",
    savedir="./pretrained_models"
)
```

#### Required Components
- `compute_features`: Feature extraction
- `mean_var_norm`: Normalization
- `embedding_model`: ECAPA-TDNN
- `mean_var_norm_emb`: Post-processing

#### Pretrained Models
- **Primary**: `speechbrain/spkrec-ecapa-voxceleb`
- **Architecture**: ECAPA-TDNN
- **Training**: VoxCeleb 2 dataset

#### Speaker Verification Workflow
1. Load pretrained model via `from_hparams()`
2. Extract embeddings from enrollment audio
3. Compare test audio using cosine distance
4. Apply threshold (default 0.25) for decision

---

## 4. Base Network Documentation (P1)

**Base URL**: https://docs.base.org/

### Network Configuration

#### Chain Details
- **Chain ID**: 8453 (mainnet)
- **Network**: Ethereum Layer 2 (OP Stack)
- **USDC Contract**: `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`

### Key Documentation Sections

#### Base Chain
- `docs.base.org/base-chain/llms.txt`: Network infrastructure index
- Network fees: L2 execution + L1 data costs
- Base Contracts: Core contract addresses
- Ecosystem Contracts: Common addresses including USDC

#### Developer Tools
- `docs.base.org/get-started/llms.txt`: Quickstarts
- `docs.base.org/learn/llms.txt`: Development curriculum
- `docs.base.org/cookbook/llms.txt`: Task-oriented recipes

#### OnchainKit (React SDK)
- `docs.base.org/onchainkit/llms.txt`: SDK reference
- **Components**:
  - OnchainKitProvider: Project-wide configuration
  - Transaction Component: Programmatic onchain actions
  - Wallet Component: Connection and wallet UI
- **APIs**:
  - Get Swap Quote
  - Get Portfolios
  - Utilities (isBase, token formatting)

#### Cookbook Recipes
- Accept Crypto Payments: Payment flow integration
- Go Gasless: Sponsored gas transactions
- Launch Tokens: Responsible token patterns

---

## 5. vLLM Documentation (P1)

**Base URL**: https://docs.vllm.ai/en/latest/

### OpenAI-Compatible Server

#### Starting the Server
```bash
python -m vllm.entrypoints.openai.api_server \
  --model <model-name> \
  --tensor-parallel-size <num-gpus> \
  --gpu-memory-utilization 0.9 \
  --kv-cache-dtype auto \
  --max-model-len 4096 \
  --max-num-batched-tokens 8192
```

#### Key Endpoints
- `/v1/chat/completions`: Chat completion
- `/v1/completions`: Text completion
- Realtime API support

### Memory Optimization

#### Key Parameters
- `--gpu-memory-utilization`: Memory efficiency (0.0-1.0)
- `--kv-cache-dtype`: KV cache quantization
- `--max-model-len`: Context window limit
- `--max-num-batched-tokens`: Batch processing

#### Techniques
- KV cache optimization
- CPU offloading strategies
- Quantization (AWQ, GPTQ)

### Tensor Parallelism

#### Configuration
- `--tensor-parallel-size`: Multi-GPU parallelism
- Data parallel deployment
- Expert parallel deployment
- Context parallel deployment

### Docker Deployment
- Base images available
- GPU enablement in containers
- Multi-stage builds

### Cold Start Optimization
- Startup benchmarking tools
- Weight loading strategies
- Sharded state management
- Lazy loading options

---

## Ingestion Instructions

### Option 1: MCP Tool (Recommended)

Use the `mcp__rugs-expert__ingest_knowledge` tool:

```yaml
# For each section
source_name: "openclaw-docs/gateway-configuration"
collection: "external_docs"  # or "platform_docs"
content: <markdown content>
```

### Option 2: VPS Sync

1. Sync files to `/root/knowledge/external-docs/`
2. Run `ingest_knowledge.py` script
3. Verify in Qdrant UI at port 6333

### Chunking Notes

- Target: ~1000 characters per chunk
- Break at paragraph boundaries
- Preserve headings for context
- Include source URL in metadata

---

## Next Steps

1. [ ] Fetch full content from each URL
2. [ ] Chunk according to ingestion protocol
3. [ ] Ingest via MCP tool or VPS sync
4. [ ] Verify in Qdrant collection
5. [ ] Test RAG queries

---

*Document generated by documentation collection agents*
