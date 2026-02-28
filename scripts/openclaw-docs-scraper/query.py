#!/usr/bin/env python3
"""
OpenClaw Documentation Query Interface

Searches the openclaw_docs Qdrant collection using semantic similarity.
Supports CLI queries, metadata filtering, and verification mode.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR / "data"
VERIFICATION_LOG = DATA_DIR / "verification.log"

COLLECTION_NAME = "openclaw_docs"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

SEPARATOR = "\u2501" * 50  # ━━━ line

# Verification test queries
VERIFICATION_QUERIES = [
    "SOUL.md template structure and required sections",
    "how to configure multi-agent routing in openclaw.json5",
    "discord channel bindings per agent",
    "heartbeat interval configuration and HEARTBEAT.md format",
    "tool permissions and sandbox security model",
    "session isolation between agents",
    "cron vs heartbeat proactive behavior",
    "agent workspace directory structure",
]


def build_filter(tier: int | None = None, section: str | None = None) -> Filter | None:
    """Build a Qdrant filter from optional parameters."""
    conditions = []
    if tier is not None:
        conditions.append(
            FieldCondition(key="tier", match=MatchValue(value=tier))
        )
    if section is not None:
        conditions.append(
            FieldCondition(key="doc_section", match=MatchValue(value=section))
        )
    if conditions:
        return Filter(must=conditions)
    return None


def format_result(hit, index: int) -> str:
    """Format a single search result for display."""
    payload = hit.payload
    score = hit.score
    url = payload.get("source_url", "?")
    heading = payload.get("section_heading", "")
    page_title = payload.get("page_title", "")
    text = payload.get("text", "")
    doc_section = payload.get("doc_section", "")
    tier = payload.get("tier", "?")

    # Truncate text for display
    display_text = text[:500]
    if len(text) > 500:
        display_text += "..."

    label = f"{doc_section}/{page_title}" if doc_section else page_title
    if heading:
        label += f" — {heading}"

    lines = [
        SEPARATOR,
        f"[{score:.2f}] (T{tier}) {label}",
        f"Source: {url}",
        "",
        display_text,
    ]
    return "\n".join(lines)


def search(
    model: SentenceTransformer,
    client: QdrantClient,
    query_text: str,
    top_k: int = 5,
    tier: int | None = None,
    section: str | None = None,
) -> list:
    """Run a semantic search query."""
    embedding = model.encode(query_text).tolist()
    query_filter = build_filter(tier=tier, section=section)

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )

    return results.points


def run_verification(model: SentenceTransformer, client: QdrantClient):
    """Run verification queries and log results."""
    VERIFICATION_LOG.parent.mkdir(parents=True, exist_ok=True)

    with open(VERIFICATION_LOG, "w", encoding="utf-8") as log:
        log.write(f"Verification run: {datetime.now(timezone.utc).isoformat()}\n")
        log.write(f"Collection: {COLLECTION_NAME}\n")

        try:
            info = client.get_collection(COLLECTION_NAME)
            log.write(f"Points in collection: {info.points_count}\n")
        except Exception as e:
            log.write(f"Could not get collection info: {e}\n")

        log.write("\n" + "=" * 60 + "\n\n")

        all_ok = True
        for i, query_text in enumerate(VERIFICATION_QUERIES):
            print(f"\nVerification [{i+1}/{len(VERIFICATION_QUERIES)}]: {query_text}")
            log.write(f"Query {i+1}: {query_text}\n")
            log.write("-" * 40 + "\n")

            try:
                results = search(model, client, query_text, top_k=3)
                if not results:
                    msg = "  NO RESULTS"
                    print(msg)
                    log.write(msg + "\n")
                    all_ok = False
                else:
                    for hit in results:
                        score = hit.score
                        url = hit.payload.get("source_url", "?")
                        heading = hit.payload.get("section_heading", "")
                        line = f"  [{score:.2f}] {url} — {heading}"
                        print(line)
                        log.write(line + "\n")
            except Exception as e:
                msg = f"  ERROR: {e}"
                print(msg)
                log.write(msg + "\n")
                all_ok = False

            log.write("\n")

        status = "PASS" if all_ok else "PARTIAL (some queries had issues)"
        log.write(f"\nOverall: {status}\n")
        print(f"\nVerification: {status}")
        print(f"Log written to: {VERIFICATION_LOG}")


def main():
    parser = argparse.ArgumentParser(
        description="Search OpenClaw documentation via vector similarity"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="Natural language search query",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Number of results to return (default: 5)",
    )
    parser.add_argument(
        "--tier",
        type=int,
        choices=[1, 2],
        help="Filter by documentation tier (1=critical, 2=useful)",
    )
    parser.add_argument(
        "--section",
        type=str,
        help="Filter by doc section (e.g., concepts, gateway, tools)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Run verification test queries",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    args = parser.parse_args()

    if not args.query and not args.verify:
        parser.print_help()
        sys.exit(1)

    # Load model
    print(f"Loading model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)

    # Connect to Qdrant
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    if args.verify:
        run_verification(model, client)
        return

    # Run search
    results = search(
        model,
        client,
        args.query,
        top_k=args.top_k,
        tier=args.tier,
        section=args.section,
    )

    if not results:
        print("No results found.")
        sys.exit(0)

    if args.json:
        output = []
        for hit in results:
            output.append({
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": {
                    k: v for k, v in hit.payload.items() if k != "text"
                },
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(f"\nResults for: {args.query}\n")
        for i, hit in enumerate(results):
            print(format_result(hit, i))
        print(SEPARATOR)


if __name__ == "__main__":
    main()
