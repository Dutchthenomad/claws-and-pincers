#!/usr/bin/env python3
"""
OpenClaw Documentation Embedder

Reads chunks from data/chunks/, generates embeddings using
sentence-transformers, and upserts into Qdrant collection.
"""

import hashlib
import json
import sys
import uuid
from pathlib import Path

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

SCRIPT_DIR = Path(__file__).parent
CHUNKS_DIR = SCRIPT_DIR / "data" / "chunks"

COLLECTION_NAME = "openclaw_docs"
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
BATCH_SIZE = 32


def chunk_id_to_uuid(chunk_id: str) -> str:
    """Generate a deterministic UUID from a chunk_id for idempotent upserts."""
    h = hashlib.sha256(chunk_id.encode()).hexdigest()
    return str(uuid.UUID(h[:32]))


def load_chunks(chunks_dir: Path) -> list[dict]:
    """Load all chunks from JSONL files in the chunks directory."""
    chunks = []
    for jsonl_file in sorted(chunks_dir.glob("*.jsonl")):
        with open(jsonl_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    chunks.append(json.loads(line))
    return chunks


def ensure_collection(client: QdrantClient):
    """Create the Qdrant collection if it doesn't exist."""
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME in collections:
        print(f"Collection '{COLLECTION_NAME}' already exists — will upsert (overwrite duplicates)")
    else:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(
                size=EMBEDDING_DIM,
                distance=Distance.COSINE,
            ),
        )
        print(f"Created collection '{COLLECTION_NAME}' ({EMBEDDING_DIM}d, cosine)")


def main():
    # Optional --recreate flag to drop and recreate the collection
    recreate = "--recreate" in sys.argv

    # Load chunks
    chunks = load_chunks(CHUNKS_DIR)
    if not chunks:
        print("No chunks found. Run chunker.py first.")
        sys.exit(1)

    print(f"Loaded {len(chunks)} chunks")

    # Initialize embedding model
    print(f"Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("Model loaded.")

    # Connect to Qdrant
    client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)

    if recreate:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'")
        except Exception:
            pass

    ensure_collection(client)

    # Process in batches
    texts = [c["text"] for c in chunks]
    total = len(texts)

    for batch_start in range(0, total, BATCH_SIZE):
        batch_end = min(batch_start + BATCH_SIZE, total)
        batch_texts = texts[batch_start:batch_end]
        batch_chunks = chunks[batch_start:batch_end]

        # Generate embeddings
        embeddings = model.encode(batch_texts, show_progress_bar=False)

        # Build Qdrant points
        points = []
        for j, (embedding, chunk) in enumerate(zip(embeddings, batch_chunks)):
            chunk_id = chunk["metadata"]["chunk_id"]
            point_id = chunk_id_to_uuid(chunk_id)

            payload = {
                **chunk["metadata"],
                "text": chunk["text"],
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding.tolist(),
                    payload=payload,
                )
            )

        # Upsert batch
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
        )

        print(f"Embedded and stored {batch_end}/{total} chunks")

    # Final stats
    collection_info = client.get_collection(COLLECTION_NAME)
    print(f"\nDone. Collection '{COLLECTION_NAME}' now has {collection_info.points_count} points.")


if __name__ == "__main__":
    main()
