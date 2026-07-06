# Implementation Plan - Refactoring BGA Studio Documentation Downloader

We will refactor the existing crawler/downloader to implement precise URL canonicalization, deduplication, stricter ignore rules, structured logging (JSON Lines), exponential backoff retries, conditional HTTP caching, and a new markdown discovery report.

## User Review Required

> [!IMPORTANT]
> - **URL Canonicalization** will map query-style URLs (`index.php?title=Page`) to short URLs (`/Page`), normalize percent encoding, and strip fragments to prevent duplicate pages.
> - **HTTP Caching** uses conditional headers (`If-None-Match`/`If-Modified-Since`) combined with content hashing to ensure files are never redownloaded or modified if the server content hasn't changed.
> - **Structured Logging** will output logs in JSON Lines (JSONL) format for easy programmatic analysis.
> - **Exponential Backoff** will retry on timeouts, connection issues, 429 (Rate Limit), and 500+ (Server Errors) with doubling sleep durations.

## Open Questions

None. The specifications are clear and fully address the duplicates and exclusions.

## Proposed Changes

### Core Shared Logic

#### [MODIFY] [common.py](file:///c:/Users/mOCHU/CascadeProjects/bgastudio-docs/common.py)
We will rewrite and enhance `common.py` to support:
- **`canonicalize_url(url, base_url)`**:
  - Resolves relative URLs.
  - Removes URL fragments.
  - Normalizes percent encoding using `urllib.parse.unquote`.
  - Converts `/index.php?title=Page_Name` to `/Page_Name`.
  - Normalizes spaces to underscores in paths.
  - Deduplicates consecutive slashes and strips trailing slashes in path.
- **`should_ignore_url(url)`**:
  - Excludes administrative namespaces (e.g. `Special:`, `User:`, `Talk:`, `File:`, `Category:`, `Template:`, `MediaWiki:`, `Help:`). Note that `/Help` (no colon) is permitted as the Studio Help page.
  - Excludes edit, history, login, oldid, and action query endpoints.
- **Structured JSON Formatter**:
  - Custom `StructuredJSONFormatter` for logging that formats log events as JSON with standard fields (`timestamp`, `level`, `title`, `canonical_url`, `depth`, `status`, `elapsed`, `message`).
- **Politeness & Retry Client**:
  - Implements exponential backoff: sleep duration doubles on retry (`backoff_delay = base_delay * (2 ** attempt)`).
  - Catches `requests.exceptions.Timeout`, `requests.exceptions.ConnectionError`.
  - Catches status codes: 429, 500–599 (including Cloudflare transient errors 520–526).

---

### Phase 1: Discover

#### [MODIFY] [discover.py](file:///c:/Users/mOCHU/CascadeProjects/bgastudio-docs/discover.py)
We will refactor `discover.py`:
- Use `canonicalize_url` for deduplication.
- Perform a HEAD/GET validation request on all candidate URLs (including depth 2) to resolve redirects and identify broken links/failures.
- Track precise telemetry for the report:
  - total pages discovered
  - total downloaded/fetched
  - duplicates removed (URLs seen before)
  - ignored pages (excluded by should_ignore_url)
  - broken links (404s)
  - redirects followed (number of HTTP redirects)
  - HTTP failures (transient timeouts / 5xx)
  - external links encountered
  - crawl duration
  - crawl depth summary
- Write [discovery_report.md](file:///c:/Users/mOCHU/CascadeProjects/bgastudio-docs/discovery_report.md).
- Output structured JSON logs to `logs/discover.log`.

---

### Phase 2: Download

#### [MODIFY] [download.py](file:///c:/Users/mOCHU/CascadeProjects/bgastudio-docs/download.py)
We will refactor `download.py`:
- Implement conditional caching by writing `etag` and `last_modified` fields into `index.json`.
- Perform requests using conditional headers (`If-None-Match` and `If-Modified-Since`) matching previous values.
- Skip file updates if the server returns `304 Not Modified`.
- Perform a fallback content-equality check if the server returns `200 OK` but the content is unchanged, avoiding updating the file timestamp.
- Support `--force` to ignore caches and overwrite everything.
- Output structured JSON logs to `logs/download.log`.

---

## Verification Plan

### Automated Tests
We will write a scratch test script (`test_refactored.py`) verifying:
1. `canonicalize_url` on redirects, fragments, query forms, percent encoding, and slashes.
2. Ignore patterns for namespaces and query actions.
3. Structured logging output.

### Manual Verification
1. Run `py discover.py` and inspect `discovery_report.md` for accurate metrics.
2. Check `urls.json` to ensure duplicate pages (like `Main_game_logic:_Game.php` and `index.php?title=Main_game_logic:_Game.php`) collapsed into one.
3. Run `py download.py` to download files.
4. Run `py download.py` again without `--force` to verify that all downloads are skipped/cached with 304s or unchanged logs.
5. Run `py download.py --force` to verify that files are updated.
