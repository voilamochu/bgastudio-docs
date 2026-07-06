import csv
import json
import re
import sys
import time
from collections import deque
from pathlib import Path
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup

from common import (
    START_URL,
    DocPage,
    PolitenessHttpClient,
    canonicalize_url,
    setup_logger,
    should_ignore_url,
)


def canonicalize_cached(canonical_cache: dict[str, str], url: str, base_url: str = START_URL) -> str:
    cache_key = f"{base_url}|{url}"
    if cache_key not in canonical_cache:
        canonical_cache[cache_key] = canonicalize_url(url, base_url)
    return canonical_cache[cache_key]


def _resolve_alias(canonical_url: str) -> str | None:
    path = urlparse(canonical_url).path
    lower_path = path.lower()

    if lower_path.endswith(".game.php"):
        return canonical_url.replace(".game.php", ".php")
    if lower_path.endswith(".js"):
        return re.sub(r"\.js$", ".php", canonical_url, flags=re.IGNORECASE)
    if ".json" in lower_path:
        return re.sub(r"\.json.*$", ".php", canonical_url, flags=re.IGNORECASE)
    if ".inc.php" in lower_path:
        return re.sub(r"\.inc\.php$", ".php", canonical_url, flags=re.IGNORECASE)
    return None


def extract_title(soup: BeautifulSoup) -> str:
    heading = soup.find(id="firstHeading")
    if heading:
        text = heading.get_text(strip=True)
        if text:
            return text
    return "Studio Doc"


def run_discovery() -> None:
    project_dir = Path(__file__).parent.resolve()
    logger = setup_logger("discover", project_dir / "logs" / "discover.log")
    start_time = time.time()

    http_requests_made = 0
    canonical_cache: dict[str, str] = {}
    visited_urls: set[str] = set()
    rejected_urls: set[str] = set()
    discovered: dict[str, DocPage] = {}

    duplicates_removed = 0
    ignored_pages = 0
    broken_links = 0
    http_failures = 0
    external_links = 0

    client = PolitenessHttpClient(delay=1.0, max_retries=3, base_backoff=2.0)
    queue: deque[DocPage] = deque()

    canonical_start = canonicalize_cached(canonical_cache, START_URL)
    start_page = DocPage(title="Studio", url=canonical_start, depth=0)
    discovered[canonical_start] = start_page
    queue.append(start_page)

    while queue:
        current_page = queue.popleft()

        if current_page.url in rejected_urls:
            continue

        if current_page.url in visited_urls:
            continue

        visited_urls.add(current_page.url)
        http_requests_made += 1

        print(
            f"\rVisited: {len(visited_urls)} | Queued: {len(queue)} | Depth: {current_page.depth} | "
            f"Current page: {current_page.url[:50]}",
            end="",
            file=sys.stderr,
        )

        response = client.fetch(
            url=current_page.url,
            logger=logger,
            depth=current_page.depth,
            title=current_page.title,
            method="GET",
        )

        if response is None:
            rejected_urls.add(current_page.url)
            http_failures += 1
            discovered.pop(current_page.url, None)
            continue

        if response.status_code == 404:
            rejected_urls.add(current_page.url)
            broken_links += 1
            discovered.pop(current_page.url, None)
            continue

        if response.status_code >= 400:
            rejected_urls.add(current_page.url)
            http_failures += 1
            discovered.pop(current_page.url, None)
            continue

        canonicalized = canonicalize_cached(canonical_cache, response.url)
        if canonicalized != current_page.url:
            if canonicalized in discovered:
                duplicates_removed += 1
                discovered.pop(current_page.url, None)
                visited_urls.discard(current_page.url)
                continue
            discovered.pop(current_page.url, None)
            discovered[canonicalized] = current_page
            visited_urls.discard(current_page.url)
            visited_urls.add(canonicalized)
            current_page.url = canonicalized

        soup = BeautifulSoup(response.text, "html.parser")
        current_page.title = extract_title(soup)

        logger.info(
            f"Fetched page for discovery: {current_page.url}",
            extra={
                "title": current_page.title,
                "canonical_url": current_page.url,
                "depth": current_page.depth,
                "status": "success",
                "elapsed": time.time() - start_time,
            },
        )

        body = soup.find(id="mw-content-text")
        if not body:
            continue

        for link in body.find_all("a", href=True):
            canonical_link = canonicalize_cached(
                canonical_cache, link["href"], current_page.url
            )

            ignore_flag, reason = should_ignore_url(canonical_link)
            if ignore_flag:
                if reason != "external_domain":
                    ignored_pages += 1
                else:
                    external_links += 1
                continue

            alias_target = _resolve_alias(canonical_link)
            if alias_target:
                canonical_link = alias_target

            if canonical_link in visited_urls or canonical_link in rejected_urls:
                continue

            if canonical_link in discovered:
                duplicates_removed += 1
                continue

            child_page = DocPage(
                title="TBD",
                url=canonical_link,
                depth=current_page.depth + 1,
            )
            discovered[canonical_link] = child_page

            logger.info(
                f"Discovered page: {canonical_link}",
                extra={
                    "title": child_page.title,
                    "canonical_url": canonical_link,
                    "depth": child_page.depth,
                    "status": "queued",
                    "elapsed": time.time() - start_time,
                },
            )
            if child_page.depth < 2:
                queue.append(child_page)

    print(file=sys.stderr)

    crawl_duration = time.time() - start_time
    total_discovered = len(discovered)

    depth_counts = {0: 0, 1: 0, 2: 0}
    for page in discovered.values():
        depth_counts[page.depth] = depth_counts.get(page.depth, 0) + 1

    sorted_pages = sorted(discovered.values(), key=lambda page: page.title.lower())
    json_data = [{"title": page.title, "url": page.url, "depth": page.depth} for page in sorted_pages]

    with open(project_dir / "urls.json", "w", encoding="utf-8") as handle:
        json.dump(json_data, handle, indent=4, ensure_ascii=False)

    with open(project_dir / "urls.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Title", "Depth", "URL"])
        for page in sorted_pages:
            writer.writerow([page.title, page.depth, page.url])

    report_lines = [
        "# BGA Studio Documentation Discovery Report",
        "",
        "This report summarizes Phase 1 (Discover) of the Board Game Arena Studio documentation crawler.",
        "",
        "## Crawl Telemetry Summary",
        "",
        "| Metric | Count |",
        "| :--- | :--- |",
        f"| **Total Discovered** | {total_discovered} |",
        f"| **Rejected** | {len(rejected_urls)} |",
        f"| **Duplicate Aliases Removed** | {duplicates_removed} |",
        f"| **HTTP Requests Made** | {http_requests_made} |",
        f"| **Elapsed Time** | {crawl_duration:.2f} seconds |",
        "",
        "---",
        "",
        "## Crawl Depth Summary",
        "",
        f"- **Depth 0 (Root landing page)**: {depth_counts.get(0, 0)} page",
        f"- **Depth 1 (Linked from root)**: {depth_counts.get(1, 0)} pages",
        f"- **Depth 2 (Linked from depth 1)**: {depth_counts.get(2, 0)} pages",
        "",
    ]

    with open(project_dir / "discovery_report.md", "w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines))

    logger.info(
        "Discovery completed",
        extra={
            "title": "Summary",
            "canonical_url": "",
            "depth": 0,
            "status": "summary",
            "elapsed": crawl_duration,
        },
    )

    print(f"\nDiscovery completed successfully in {crawl_duration:.2f}s!")
    print(f"Total discovered: {total_discovered}")
    print(f"Rejected: {len(rejected_urls)}")
    print(f"Duplicate aliases removed: {duplicates_removed}")
    print(f"HTTP requests made: {http_requests_made}")
    print("Structured logs written to: logs/discover.log")
    print("Discovery report written to: discovery_report.md")


if __name__ == "__main__":
    run_discovery()