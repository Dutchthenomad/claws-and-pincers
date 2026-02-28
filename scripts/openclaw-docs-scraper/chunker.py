#!/usr/bin/env python3
"""
OpenClaw Documentation Chunker

Reads raw markdown files from data/raw/, splits them into
semantically meaningful chunks, and outputs JSONL to data/chunks/.
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
RAW_DIR = SCRIPT_DIR / "data" / "raw"
CHUNKS_DIR = SCRIPT_DIR / "data" / "chunks"

# Token estimation: ~0.75 words per token (conservative)
# Target chunk size: 500-1000 tokens ≈ 375-750 words
MAX_CHUNK_WORDS = 750
SPLIT_THRESHOLD_WORDS = 1100  # ~1500 tokens — triggers H3 split
PARAGRAPH_TARGET_WORDS = 600  # ~800 tokens for paragraph splits


def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~1.33 tokens per word."""
    return int(len(text.split()) * 1.33)


def find_code_block_ranges(text: str) -> list[tuple[int, int]]:
    """Find character ranges of fenced code blocks."""
    ranges = []
    for m in re.finditer(r"```[^\n]*\n.*?```", text, re.DOTALL):
        ranges.append((m.start(), m.end()))
    return ranges


def is_inside_code_block(pos: int, code_ranges: list[tuple[int, int]]) -> bool:
    """Check if a character position is inside a code block."""
    for start, end in code_ranges:
        if start <= pos <= end:
            return True
    return False


def split_on_headings(text: str, level: str) -> list[dict]:
    """
    Split text on markdown headings of the given level (e.g., '## ').
    Returns list of {"heading": str, "body": str}.
    Preserves code blocks by not splitting inside them.
    """
    code_ranges = find_code_block_ranges(text)
    pattern = re.compile(r"^(" + re.escape(level) + r".+)$", re.MULTILINE)

    sections = []
    last_end = 0
    last_heading = ""

    for match in pattern.finditer(text):
        if is_inside_code_block(match.start(), code_ranges):
            continue

        body = text[last_end:match.start()].strip()
        if body or last_heading:
            sections.append({"heading": last_heading, "body": body})

        last_heading = match.group(1).strip()
        last_end = match.end()

    # Capture trailing content
    trailing = text[last_end:].strip()
    if trailing or last_heading:
        sections.append({"heading": last_heading, "body": trailing})

    return sections


def split_on_paragraphs(text: str, target_words: int) -> list[str]:
    """
    Split text on paragraph boundaries (double newline), grouping
    paragraphs to stay near target_words. Never splits inside code blocks.
    """
    code_ranges = find_code_block_ranges(text)

    # Split on double newlines that aren't inside code blocks
    parts = []
    current_start = 0
    for m in re.finditer(r"\n\n+", text):
        if not is_inside_code_block(m.start(), code_ranges):
            parts.append(text[current_start:m.start()])
            current_start = m.end()
    parts.append(text[current_start:])

    # Group paragraphs into chunks near target size
    chunks = []
    current_chunk = []
    current_words = 0

    for part in parts:
        part_words = len(part.split())
        if current_words + part_words > target_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [part]
            current_words = part_words
        else:
            current_chunk.append(part)
            current_words += part_words

    if current_chunk:
        chunks.append("\n\n".join(current_chunk))

    return chunks


def chunk_page(markdown: str, metadata: dict) -> list[dict]:
    """
    Chunk a single page's markdown into search-ready pieces.
    Returns list of chunk dicts with text and metadata.
    """
    url = metadata["url"]
    title = metadata["title"]
    tier = metadata["tier"]
    section = metadata["section"]

    # Build a page ID from the URL path
    page_id = url.replace("https://docs.openclaw.ai/", "").replace("/", "-")
    if not page_id:
        page_id = "index"

    chunks = []

    # First split on H2
    h2_sections = split_on_headings(markdown, "## ")

    # If no H2 splits, treat whole page as one section
    if len(h2_sections) <= 1:
        h2_sections = [{"heading": "", "body": markdown}]

    for h2_sec in h2_sections:
        h2_heading = h2_sec["heading"]
        h2_body = h2_sec["body"]
        full_text = f"{h2_heading}\n\n{h2_body}".strip() if h2_heading else h2_body

        word_count = len(full_text.split())

        if word_count <= MAX_CHUNK_WORDS:
            # Small enough — one chunk
            chunks.append({
                "text": full_text,
                "heading": h2_heading,
            })
        elif word_count <= SPLIT_THRESHOLD_WORDS:
            # Try splitting on H3
            h3_sections = split_on_headings(h2_body, "### ")
            if len(h3_sections) > 1:
                for h3_sec in h3_sections:
                    h3_text = h3_sec["body"]
                    if h3_sec["heading"]:
                        h3_text = f"{h3_sec['heading']}\n\n{h3_text}"
                    # Prefix with H2 context
                    if h2_heading:
                        h3_text = f"{h2_heading}\n\n{h3_text}"
                    chunks.append({
                        "text": h3_text.strip(),
                        "heading": h3_sec["heading"] or h2_heading,
                    })
            else:
                # No H3 to split on — keep as one chunk
                chunks.append({
                    "text": full_text,
                    "heading": h2_heading,
                })
        else:
            # Large section — split on H3 first, then paragraphs if needed
            h3_sections = split_on_headings(h2_body, "### ")
            sub_texts = []

            if len(h3_sections) > 1:
                for h3_sec in h3_sections:
                    h3_text = h3_sec["body"]
                    if h3_sec["heading"]:
                        h3_text = f"{h3_sec['heading']}\n\n{h3_text}"
                    sub_texts.append((h3_text, h3_sec["heading"]))
            else:
                sub_texts.append((h2_body, h2_heading))

            for sub_text, sub_heading in sub_texts:
                if len(sub_text.split()) > MAX_CHUNK_WORDS:
                    # Paragraph split
                    para_chunks = split_on_paragraphs(sub_text, PARAGRAPH_TARGET_WORDS)
                    for pc in para_chunks:
                        text = pc.strip()
                        if h2_heading and not text.startswith(h2_heading):
                            text = f"{h2_heading}\n\n{text}"
                        chunks.append({
                            "text": text,
                            "heading": sub_heading or h2_heading,
                        })
                else:
                    text = sub_text.strip()
                    if h2_heading and not text.startswith(h2_heading):
                        text = f"{h2_heading}\n\n{text}"
                    chunks.append({
                        "text": text,
                        "heading": sub_heading or h2_heading,
                    })

    # Build final chunk objects with metadata
    total_chunks = len(chunks)
    result = []
    for i, chunk in enumerate(chunks):
        has_code = "```" in chunk["text"]
        token_count = estimate_tokens(chunk["text"])
        chunk_id = f"{page_id}-{i:03d}"

        result.append({
            "text": chunk["text"],
            "metadata": {
                "chunk_id": chunk_id,
                "source_url": url,
                "page_title": title,
                "section_heading": chunk["heading"],
                "tier": tier,
                "doc_section": section,
                "has_code": has_code,
                "token_count": token_count,
                "chunk_index": i,
                "total_chunks_in_page": total_chunks,
            },
        })

    return result


def main():
    # Parse optional --tier flag
    tier_filter = None
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier_filter = int(sys.argv[idx + 1])

    if not RAW_DIR.exists():
        print(f"ERROR: {RAW_DIR} does not exist. Run scraper.py first.")
        sys.exit(1)

    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    # Find all JSON metadata files (they pair with .md files)
    json_files = sorted(RAW_DIR.rglob("*.json"))

    if not json_files:
        print("No scraped pages found. Run scraper.py first.")
        sys.exit(1)

    print(f"Found {len(json_files)} scraped pages")

    all_chunks = []

    for jf in json_files:
        metadata = json.loads(jf.read_text(encoding="utf-8"))

        if tier_filter is not None and metadata.get("tier", 99) > tier_filter:
            continue

        # Corresponding markdown file
        md_file = jf.with_suffix(".md")
        if not md_file.exists():
            print(f"  WARNING: No markdown for {jf.name}, skipping")
            continue

        markdown = md_file.read_text(encoding="utf-8")
        if not markdown.strip():
            print(f"  WARNING: Empty markdown for {metadata['url']}, skipping")
            continue

        page_chunks = chunk_page(markdown, metadata)
        all_chunks.extend(page_chunks)
        print(f"  {metadata['url']} → {len(page_chunks)} chunks")

    # Write all chunks to a single JSONL file
    output_file = CHUNKS_DIR / "all_chunks.jsonl"
    with open(output_file, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print(f"\nTotal: {len(all_chunks)} chunks written to {output_file}")

    # Print stats
    tier_counts = {}
    section_counts = {}
    for c in all_chunks:
        t = c["metadata"]["tier"]
        s = c["metadata"]["doc_section"]
        tier_counts[t] = tier_counts.get(t, 0) + 1
        section_counts[s] = section_counts.get(s, 0) + 1

    print("\nChunks by tier:")
    for t in sorted(tier_counts):
        print(f"  Tier {t}: {tier_counts[t]}")

    print("\nChunks by section:")
    for s in sorted(section_counts):
        print(f"  {s}: {section_counts[s]}")

    token_counts = [c["metadata"]["token_count"] for c in all_chunks]
    if token_counts:
        avg = sum(token_counts) / len(token_counts)
        print(f"\nToken stats: min={min(token_counts)}, max={max(token_counts)}, avg={avg:.0f}")


if __name__ == "__main__":
    main()
