#!/usr/bin/env bash
#
# OpenClaw Docs Vector Search — Full Pipeline
#
# Usage: bash run_all.sh [--tier 1]
#
# Runs: scrape → chunk → embed → verify
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

TIER_FLAG=""
if [[ "${1:-}" == "--tier" ]] && [[ -n "${2:-}" ]]; then
    TIER_FLAG="--tier $2"
    echo "=== Filtering to tier $2 and below ==="
fi

echo ""
echo "=== Step 1/4: Scraping documentation ==="
echo ""
"$SCRIPT_DIR/.venv/bin/python3" scraper.py $TIER_FLAG

echo ""
echo "=== Step 2/4: Chunking content ==="
echo ""
"$SCRIPT_DIR/.venv/bin/python3" chunker.py $TIER_FLAG

echo ""
echo "=== Step 3/4: Embedding and storing in Qdrant ==="
echo ""
"$SCRIPT_DIR/.venv/bin/python3" embedder.py

echo ""
echo "=== Step 4/4: Running verification queries ==="
echo ""
"$SCRIPT_DIR/.venv/bin/python3" query.py --verify

echo ""
echo "=== Pipeline complete ==="
echo ""
echo "Query the docs with:"
echo "  .venv/bin/python3 query.py \"your question here\""
echo "  .venv/bin/python3 query.py \"your question\" --top-k 10 --tier 1"
