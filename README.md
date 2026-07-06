# BGA Studio Documentation Downloader

A production-quality documentation downloader and crawler tailored specifically for the [Board Game Arena Studio documentation](https://en.doc.boardgamearena.com/Studio). 

It builds a permanent offline knowledge base for developer reference and future conversion into developer handbooks or AI reference manuals.

---

## Features

### 1. Stricter URL Canonicalization
Two links pointing to the same page resolve to a single canonical URL. Before comparing or storing links, the crawler:
- Resolves relative URLs to absolute links.
- Strips URL fragments (`#...`).
- Normalizes percent encoding (e.g. `%3F` is resolved to `?`, spaces are replaced with underscores).
- Converts query parameters of the form `index.php?title=Page_Name` to short URLs of the form `/Page_Name`.
- Deduplicates consecutive slashes and strips trailing slashes in paths.

### 2. Precise Ignore Rules (No Noise)
Only crawls actual Board Game Arena Studio documentation pages.
- Ignores administrative namespaces: `Special:`, `User:`, `Talk:`, `File:`, `Category:`, `Template:`, `MediaWiki:`.
- Ignores general wiki help pages (`Help:Wiki_formatting` etc.), while allowing `/Help` (no colon) which is the Studio Help page.
- Ignores administrative/action endpoints: edit links, history links, login links, revisions (`oldid`), and actions (`action=*`).
- Filters out non-documentation binary assets (PDFs, images, ZIPs) and cdn utilities (`/cdn-cgi/`).

### 3. Intelligent Download Caching
The downloader avoids redownloading page contents that have not changed:
- Saves response HTTP headers `ETag` and `Last-Modified` in `index.json`.
- Uses conditional request headers `If-None-Match` and `If-Modified-Since` on subsequent runs.
- Skips file writing and maintains the original timestamp if the server returns `304 Not Modified`.
- Performs a content-equality check if the server returns `200 OK` but the downloaded page content matches the existing offline file, avoiding updating the file timestamp.
- **Rerun Option**: Supply the `--force` flag to ignore caches and refresh all pages.

### 4. Exponential Backoff Retry Logic
Protects the crawl against transient network errors:
- Retries automatically on connection errors, request timeouts, rate limits (HTTP 429), server errors (HTTP 500+), and Cloudflare transient errors (520–526).
- Implements exponential backoff (e.g. doubling delays: 2s, 4s, 8s...) with randomized jitter.

### 5. Structured JSON Logging
Both scripts replace ad-hoc logs with JSON Lines structured logging format. Each line in `logs/discover.log` and `logs/download.log` is a JSON object with:
- `timestamp`: ISO 8601 format
- `level`: Log severity (INFO, WARNING, ERROR)
- `message`: Text message
- `title`: Page Title
- `canonical_url`: The canonical URL
- `depth`: BFS crawl depth
- `status`: Execution status (`success`, `cached_304`, `cached_hash`, `downloaded`, `failed`, `broken`)
- `elapsed`: Time elapsed since request/crawl start

### 6. Comprehensive Discovery Report
Phase 1 generates a detailed `discovery_report.md` file summarizing telemetry metrics, depth counts, followed redirects, broken links (404), and HTTP errors.

---

## Directory Structure

```text
bgastudio-docs/
├── logs/
│   ├── discover.log         # JSON Lines structured crawl logs
│   └── download.log         # JSON Lines structured download logs
├── source-html/
│   ├── Studio.html          # Sanitized offline HTML file
│   └── ...                  # Other downloaded pages
├── common.py                # Shared helpers, structured logger, and retrying HTTP client
├── discover.py              # Phase 1: Crawler & URL Validator
├── download.py              # Phase 2: Conditional HTML Downloader
├── index.json               # Index map of all downloaded pages with ETag/Last-Modified data
├── discovery_report.md      # Auto-generated Phase 1 execution summary report
├── requirements.txt         # Python dependencies list
├── urls.csv                 # Discovered pages list (CSV format)
├── urls.json                # Discovered pages list (JSON format)
└── README.md                # Project manual (this file)
```

---

## Installation

1. Make sure you have Python 3.8+ installed on your system.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

### Phase 1: Discover Documentation Pages

Crawl the BGA Studio documentation up to depth 2:
```bash
py discover.py
```
*Note: If `py` is not configured, run `python discover.py`.*

#### How Discovery Works
1. Starts at `/Studio` (Depth 0).
2. Extracts links from the `#mw-content-text` article body on depth 0 and depth 1 pages.
3. Canonicalizes URLs, removes duplicates, and filters unwanted administrative paths.
4. Validates all discovered links (including depth 2 leaves) using polite HTTP requests.
5. Tracks followed redirects, broken links (404s), and transient failures.
6. Outputs sorted, valid documentation URLs to `urls.json` and `urls.csv`.
7. Generates a comprehensive crawl report in `discovery_report.md`.

---

### Phase 2: Download Documentation Pages

Download HTML contents of the discovered pages using conditional caching:
```bash
py download.py
```
*Note: If `py` is not configured, run `python download.py`.*

#### How Downloading Works
1. Loads the page list from `urls.json`.
2. Sequentially requests each page.
3. Sends HTTP validation headers (`If-None-Match` and `If-Modified-Since`) from previous runs.
4. If the server returns `304 Not Modified` or identical content is found, the script skips updating the local file.
5. Raw HTML is stored in `source-html/<Sanitized_Title>.html`.
6. Compiles a consolidated `index.json` detailing Title, URL, Depth, Filename, UTC download timestamp, ETag, and Last-Modified header value.

## How to Force Overwrite
If you want to force-redownload all pages regardless of cache status:
 ```bash
 py download.py --force
 ```

---

## Phase 3: Build Knowledge Index

Transform extracted JSON documentation into a searchable knowledge index:

```bash
py build_knowledge_index.py
```

This creates `knowledge/` containing:
- `master_index.json` - One entry per page with metadata and counts
- `toc.json` - Hierarchical table of contents per page
- `glossary.json` - Extracted API names, classes, functions
- `topics.json` - Pages grouped by topic classification
- `search_index.json` - Searchable entries with keywords
- `statistics.json` - Aggregate statistics
- `knowledge_report.md` - Summary report
