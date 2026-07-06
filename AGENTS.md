# BGA Studio Documentation Downloader - Agent Guidelines

## Key Commands
- Discovery phase: py discover.py (or python discover.py)
- Download phase: py download.py (or python download.py)
- Force re-download: py download.py --force

## Project Structure & Conventions
- Two-phase process: Always run discover.py before download.py
- Outputs: 
  - urls.json/urls.csv -> input for downloader
  - source-html/ -> stores downloaded HTML files
  - index.json -> tracks ETag/Last-Modified for caching
  - logs/ -> structured JSONL logs (discover.log, download.log)
- Virtual environment: Uses .venv/ - activate if needed

## Important Implementation Details
- URL canonicalization: Critical for deduplication - see canonicalize_url() in common.py
- URL filtering: should_ignore_url() excludes admin/help namespaces, binaries, APIs
- Caching logic: Uses ETag/Last-Modified + content hash check to avoid re-downloads
- Retry logic: Exponential backoff (2s, 4s, 8s...) with jitter for network resilience
- Logging: Structured JSONL format - each line is a parseable JSON object

## Code Organization
- common.py: Shared utilities (DO NOT modify lightly - affects both scripts)
- discover.py: Phase 1 - BFS crawl depth=2, URL validation, report generation
- download.py: Phase 2 - Sequential download with conditional requests

## Testing & Validation
- Check discovery_report.md after discovery for crawl stats
- Verify index.json contains all downloaded pages with correct metadata
- Monitor logs/*.log for errors (JSONL format - use jq or similar to parse)

## Common Gotchas
- Always run discovery before download (download requires urls.json)
- The --force flag bypasses ALL caching - use only when needed
- URL canonicalization affects deduplication - changes impact URL mapping
- Logging format is JSON Lines - each line is independently parseable
