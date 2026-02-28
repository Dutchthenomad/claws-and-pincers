# OpenClaw Docs Vector Search

Standalone scraper + vector search pipeline for [docs.openclaw.ai](https://docs.openclaw.ai/). Ingests documentation into a dedicated Qdrant collection (`openclaw_docs`) for semantic search by Claude Code sessions and deployed agents.

## Prerequisites

- Python 3.10+
- Qdrant running at `localhost:6333` (already on VPS)
- Internet access (to fetch docs)

## Setup

```bash
cd scripts/openclaw-docs-scraper
pip install -r requirements.txt
```

## Usage

### Full pipeline

```bash
bash run_all.sh             # Scrape all tiers, chunk, embed, verify
bash run_all.sh --tier 1    # Tier 1 (critical) pages only
```

### Individual steps

```bash
python3 scraper.py              # Fetch docs → data/raw/
python3 scraper.py --tier 1     # Tier 1 only

python3 chunker.py              # Chunk raw markdown → data/chunks/
python3 chunker.py --tier 1     # Tier 1 only

python3 embedder.py             # Embed & store in Qdrant
python3 embedder.py --recreate  # Drop collection first

python3 query.py --verify       # Run verification test queries
```

### Querying

```bash
python3 query.py "how do multi-agent bindings work"
python3 query.py "HEARTBEAT.md template format" --top-k 5
python3 query.py "discord channel routing" --tier 1
python3 query.py "sandbox security" --section gateway
python3 query.py "agent workspace" --json
```

## Architecture

```
urls.txt          Tiered URL list (1=critical, 2=useful)
    ↓
scraper.py        Fetch HTML → extract markdown → data/raw/
    ↓
chunker.py        Split by H2/H3/paragraph → data/chunks/
    ↓
embedder.py       sentence-transformers → Qdrant (openclaw_docs)
    ↓
query.py          Semantic search CLI
```

## Configuration

| Setting | Value | Where |
|---------|-------|-------|
| Qdrant collection | `openclaw_docs` | `embedder.py`, `query.py` |
| Embedding model | `all-MiniLM-L6-v2` (384d) | `embedder.py`, `query.py` |
| Qdrant host | `localhost:6333` | `embedder.py`, `query.py` |
| Chunk target | 500-1000 tokens | `chunker.py` |

## File layout

```
scripts/openclaw-docs-scraper/
├── urls.txt           # URL list with tier annotations
├── scraper.py         # Fetch & extract
├── chunker.py         # Chunk markdown
├── embedder.py        # Embed & store in Qdrant
├── query.py           # Search interface
├── run_all.sh         # Pipeline runner
├── requirements.txt   # Python deps
├── README.md          # This file
└── data/              # Runtime output (.gitignore'd)
    ├── raw/           # Fetched markdown + JSON metadata
    ├── chunks/        # JSONL chunk files
    ├── errors.log     # Failed URLs
    └── verification.log
```
