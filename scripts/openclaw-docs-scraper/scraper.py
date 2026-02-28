#!/usr/bin/env python3
"""
OpenClaw Documentation Scraper

Fetches pages from docs.openclaw.ai, strips Mintlify chrome,
extracts clean markdown content, and saves with metadata.
"""

import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import html2text
import requests
from bs4 import BeautifulSoup

SCRIPT_DIR = Path(__file__).parent
URLS_FILE = SCRIPT_DIR / "urls.txt"
DATA_DIR = SCRIPT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
ERRORS_LOG = DATA_DIR / "errors.log"

REQUEST_DELAY = 1.5  # seconds between requests
RETRY_DELAY = 5  # seconds before retry
USER_AGENT = "OpenClaw-DocScraper/1.0 (internal tooling)"


def load_urls(filepath: Path) -> list[dict]:
    """Load URLs from urls.txt with tier annotations."""
    entries = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split("|", 1)
            if len(parts) != 2:
                continue
            tier = int(parts[0])
            url = parts[1].strip()
            entries.append({"url": url, "tier": tier})
    return entries


def url_to_path(url: str) -> str:
    """Convert URL to a relative file path for storage."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        path = "index"
    return path


def extract_title(soup: BeautifulSoup) -> str:
    """Extract page title from the HTML."""
    # Try meta title first
    og_title = soup.find("meta", property="og:title")
    if og_title and og_title.get("content"):
        return og_title["content"]

    # Try the h1 in the content area
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)

    # Fall back to <title> tag
    if soup.title:
        title_text = soup.title.get_text(strip=True)
        # Strip common suffixes like " | OpenClaw Docs"
        title_text = re.split(r"\s*[|–—]\s*", title_text)[0]
        return title_text

    return "Untitled"


def extract_content(html: str) -> str:
    """
    Extract main content from Mintlify HTML page.
    Strips nav, sidebar, footer, search overlays, TOC.
    Returns clean markdown.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Remove elements we don't want
    selectors_to_remove = [
        "nav",
        "header",
        "footer",
        "[data-testid='sidebar']",
        ".sidebar",
        "#sidebar",
        ".table-of-contents",
        ".toc",
        "[class*='TableOfContents']",
        "[class*='toc']",
        "[class*='search']",
        "[class*='Search']",
        "[class*='navigation']",
        "[class*='Navigation']",
        "[class*='footer']",
        "[class*='Footer']",
        "[class*='header']",
        "[class*='Header']",
        "[class*='Breadcrumb']",
        "[class*='breadcrumb']",
        "[class*='powered-by']",
        "[class*='PoweredBy']",
        "script",
        "style",
        "noscript",
        "[role='navigation']",
        "[aria-label='Table of contents']",
        "[aria-label='On this page']",
    ]

    for selector in selectors_to_remove:
        for el in soup.select(selector):
            el.decompose()

    # Try to find main content area
    content_el = (
        soup.find(id="content-area")
        or soup.find("main")
        or soup.find("article")
        or soup.find(class_=re.compile(r"(?i)content|article|page-body|markdown"))
    )

    if content_el is None:
        content_el = soup.find("body") or soup

    # Convert to markdown
    converter = html2text.HTML2Text()
    converter.body_width = 0  # No line wrapping
    converter.protect_links = True
    converter.unicode_snob = True
    converter.wrap_links = False
    converter.skip_internal_links = False
    converter.inline_links = True
    converter.ignore_images = False
    converter.ignore_emphasis = False

    markdown = converter.handle(str(content_el))

    # Clean up excessive blank lines
    markdown = re.sub(r"\n{4,}", "\n\n\n", markdown)

    # Remove any remaining Mintlify artifacts
    markdown = re.sub(r"Powered by Mintlify.*", "", markdown)

    return markdown.strip()


def get_section(url: str) -> str:
    """Extract the doc section from the URL path."""
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    return parts[0] if parts else "root"


def scrape_url(url: str, session: requests.Session) -> tuple[str, str]:
    """Fetch a URL and return (title, markdown_content)."""
    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    html = resp.text
    soup = BeautifulSoup(html, "html.parser")
    title = extract_title(soup)
    content = extract_content(html)
    return title, content


def log_error(msg: str):
    """Append error to the errors log."""
    ERRORS_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_LOG, "a") as f:
        f.write(f"[{datetime.now(timezone.utc).isoformat()}] {msg}\n")


def main():
    # Parse optional --tier flag
    tier_filter = None
    if "--tier" in sys.argv:
        idx = sys.argv.index("--tier")
        if idx + 1 < len(sys.argv):
            tier_filter = int(sys.argv[idx + 1])

    entries = load_urls(URLS_FILE)
    if tier_filter is not None:
        entries = [e for e in entries if e["tier"] <= tier_filter]

    print(f"Loaded {len(entries)} URLs to scrape")

    # Ensure directories exist
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Clear previous errors log
    if ERRORS_LOG.exists():
        ERRORS_LOG.unlink()

    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    success_count = 0
    fail_count = 0

    for i, entry in enumerate(entries):
        url = entry["url"]
        tier = entry["tier"]
        rel_path = url_to_path(url)

        print(f"[{i+1}/{len(entries)}] Scraping: {url}")

        for attempt in range(2):  # 1 try + 1 retry
            try:
                title, content = scrape_url(url, session)

                if not content or len(content.strip()) < 50:
                    print(f"  WARNING: Very little content extracted ({len(content)} chars)")

                # Save markdown
                md_path = RAW_DIR / f"{rel_path}.md"
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_path.write_text(content, encoding="utf-8")

                # Save metadata
                word_count = len(content.split())
                metadata = {
                    "url": url,
                    "title": title,
                    "fetched_at": datetime.now(timezone.utc).isoformat(),
                    "tier": tier,
                    "section": get_section(url),
                    "word_count": word_count,
                }
                json_path = RAW_DIR / f"{rel_path}.json"
                json_path.write_text(
                    json.dumps(metadata, indent=2), encoding="utf-8"
                )

                print(f"  OK — {title} ({word_count} words)")
                success_count += 1
                break

            except Exception as e:
                if attempt == 0:
                    print(f"  FAILED (attempt 1): {e} — retrying in {RETRY_DELAY}s...")
                    log_error(f"RETRY {url}: {e}")
                    time.sleep(RETRY_DELAY)
                else:
                    print(f"  FAILED (attempt 2): {e} — skipping")
                    log_error(f"SKIP {url}: {e}")
                    fail_count += 1

        # Polite delay between requests
        if i < len(entries) - 1:
            time.sleep(REQUEST_DELAY)

    print(f"\nDone. Scraped {success_count}/{len(entries)} pages. Failures: {fail_count}")
    if fail_count > 0:
        print(f"See {ERRORS_LOG} for details.")


if __name__ == "__main__":
    main()
