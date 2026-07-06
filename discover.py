import csv
import json
import sys
import time
from collections import defaultdict
from collections import deque
from pathlib import Path

from bs4 import BeautifulSoup

from common import (
    START_URL,
    DocPage,
    PolitenessHttpClient,
    canonicalize_url,
    setup_logger,
    should_ignore_url,
)
from urllib.parse import parse_qsl, unquote, urlparse


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
    visited_urls: set[str] = set()
    rejected_urls: set[str] = set()
    rejection_reasons: dict[str, str] = {}
    discovered: dict[str, DocPage] = {}

    duplicates_removed = 0
    ignored_pages = 0
    broken_links = 0
    http_failures = 0
    external_links = 0

    client = PolitenessHttpClient(delay=1.0, max_retries=3, base_backoff=2.0)
    queue: deque[DocPage] = deque()

    canonical_start = canonicalize_url(START_URL)
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

        canonicalized = canonicalize_url(response.url)
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

        if current_page.depth >= 2:
            continue

        body = soup.find(id="mw-content-text")
        if not body:
            continue

        for link in body.find_all("a", href=True):
            canonical_link = canonicalize_url(link["href"], current_page.url)

            ignore_flag, reason = should_ignore_url(canonical_link)
            if ignore_flag:
                if reason != "external_domain":
                    ignored_pages += 1
                    rejected_urls.add(canonical_link)
                    rejection_reasons[canonical_link] = reason
                else:
                    external_links += 1
                continue

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
            if child_page.depth <= 2:
                queue.append(child_page)

    print(file=sys.stderr)

    crawl_duration = time.time() - start_time
    total_discovered = len(discovered)

    depth_counts = {0: 0, 1: 0, 2: 0}
    for page in discovered.values():
        depth_counts[page.depth] = depth_counts.get(page.depth, 0) + 1

    validation_results = validate_discovery(discovered, rejected_urls, rejection_reasons, depth_counts)

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
        f"| **Broken Links** | {broken_links} |",
        f"| **Duplicate Aliases Removed** | {duplicates_removed} |",
        f"| **HTTP Requests Made** | {http_requests_made} |",
        f"| **Elapsed Time** | {crawl_duration:.2f} seconds |",
        "",
        "---",
        "",
        "## Crawl Depth Summary",
        "",
        f"- **Depth 0 (Root landing page)**: {depth_counts.get(0, 0)} page{'s' if depth_counts.get(0, 0) != 1 else ''}",
        f"- **Depth 1 (Linked from root)**: {depth_counts.get(1, 0)} page{'s' if depth_counts.get(1, 0) != 1 else ''}",
        f"- **Depth 2 (Linked from depth 1)**: {depth_counts.get(2, 0)} page{'s' if depth_counts.get(2, 0) != 1 else ''}",
        "",
        "## Validation Summary",
        "",
    ]

    if validation_results["excluded_pages_remaining"] > 0:
        report_lines.append("**VALIDATION FAILED**: Excluded page types remain in results.")
        report_lines.append("")
    else:
        report_lines.append("**VALIDATION PASSED**: No excluded page types remain.")
        report_lines.append("")

    report_lines.extend([
        f"- Pages excluded (outside Studio scope): {len(validation_results['excluded_pages'])}",
        f"- Pages with missing/tbd titles: {validation_results['tbd_titles']}",
        f"- Gamehelp pages: {validation_results['gamehelp_pages']}",
        f"- Help pages: {validation_results['help_pages']}",
        f"- Special: pages: {validation_results['special_pages']}",
        f"- Category: pages: {validation_results['category_pages']}",
        f"- User: pages: {validation_results['user_pages']}",
        f"- Talk: pages: {validation_results['talk_pages']}",
    ])

    with open(project_dir / "discovery_report.md", "w", encoding="utf-8") as handle:
        handle.write("\n".join(report_lines))

    validation_report = generate_validation_report(
        discovered,
        rejected_urls,
        rejection_reasons,
        http_requests_made,
        duplicates_removed,
        crawl_duration,
        validation_results,
    )
    with open(project_dir / "validation_report.md", "w", encoding="utf-8") as handle:
        handle.write(validation_report)

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
    print(f"Pages visited: {len(visited_urls)}")
    print(f"HTTP requests: {http_requests_made}")
    print(f"Rejected: {len(rejected_urls)}")
    print(f"Broken links: {broken_links}")
    print(f"Duplicate pages: {duplicates_removed}")
    print("Structured logs written to: logs/discover.log")
    print("Discovery report written to: discovery_report.md")
    print("Validation report written to: validation_report.md")


def validate_discovery(
    discovered: dict[str, DocPage],
    rejected_urls: set[str],
    rejection_reasons: dict[str, str],
    depth_counts: dict[int, int],
) -> dict:
    """Validate discovered pages and return validation results."""
    results = {
        "excluded_pages": [],
        "excluded_pages_remaining": 0,
        "tbd_titles": 0,
        "gamehelp_pages": 0,
        "help_pages": 0,
        "special_pages": 0,
        "category_pages": 0,
        "user_pages": 0,
        "talk_pages": 0,
        "depth_counts": depth_counts,
    }

    for url, page in discovered.items():
        parsed = urlparse(url)
        path = unquote(parsed.path)
        lower_path = path.lower()
        query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        query_title = unquote(query_params.get("title", "")).strip()

        if page.title == "TBD" or page.title == "Studio Doc":
            results["tbd_titles"] += 1

        if lower_path.startswith("/gamehelp") or query_title.lower().startswith("gamehelp"):
            results["gamehelp_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - Gamehelp* page")

        if lower_path == "/help" or query_title.lower() == "help":
            results["help_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - Help page")

        if lower_path.startswith("/special") or query_title.lower().startswith("special:"):
            results["special_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - Special page")

        if lower_path.startswith("/category") or query_title.lower().startswith("category:"):
            results["category_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - Category page")

        if lower_path.startswith("/user") or query_title.lower().startswith("user:"):
            results["user_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - User page")

        if lower_path.startswith("/talk") or query_title.lower().startswith("talk:"):
            results["talk_pages"] += 1
            results["excluded_pages"].append(f"{page.title} ({url}) - Talk page")

    results["excluded_pages_remaining"] = (
        results["gamehelp_pages"] +
        results["help_pages"] +
        results["special_pages"] +
        results["category_pages"] +
        results["user_pages"] +
        results["talk_pages"]
    )

    return results


def generate_validation_report(
    discovered: dict[str, DocPage],
    rejected_urls: set[str],
    rejection_reasons: dict[str, str],
    http_requests_made: int,
    duplicates_removed: int,
    crawl_duration: float,
    validation_results: dict,
) -> str:
    """Generate detailed validation report."""
    reasons_count = defaultdict(int)
    for reason in rejection_reasons.values():
        reasons_count[reason] += 1

    lines = [
        "# Discovery Validation Report",
        "",
        "## Summary Statistics",
        "",
        f"- **Total discovered pages**: {len(discovered)}",
        f"- **Pages at depth 0**: {validation_results.get('depth_counts', {}).get(0, 0)}",
        f"- **Pages at depth 1**: {validation_results.get('depth_counts', {}).get(1, 0)}",
        f"- **Pages at depth 2**: {validation_results.get('depth_counts', {}).get(2, 0)}",
        f"- **HTTP requests made**: {http_requests_made}",
        f"- **Duplicate aliases removed**: {duplicates_removed}",
        f"- **Rejected pages (total)**: {len(rejected_urls)}",
        "",
        "## Rejected Pages by Reason",
        "",
        "| Reason | Count |",
        "| :--- | :--- |",
    ]

    for reason, count in sorted(reasons_count.items()):
        lines.append(f"| {reason} | {count} |")

    if not reasons_count:
        lines.append("| (none) | 0 |")

    lines.extend([
        "",
        "## Pages with Missing Titles (TBD)",
        "",
    ])

    tbd_pages = [(url, page.depth) for url, page in discovered.items() if page.title == "TBD" or page.title == "Studio Doc"]
    if tbd_pages:
        for url, depth in sorted(tbd_pages):
            lines.append(f"- {url} (depth {depth})")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Pages Outside Studio Documentation Scope",
        "",
    ])

    excluded = validation_results["excluded_pages"]
    if excluded:
        for entry in sorted(excluded):
            lines.append(f"- {entry}")
    else:
        lines.append("(none)")

    lines.extend([
        "",
        "## Validation Status",
        "",
    ])

    if validation_results["excluded_pages_remaining"] > 0:
        lines.append("**FAILED**: Excluded page types found in discovered pages.")
    else:
        lines.append("**PASSED**: No excluded page types found.")

    return "\n".join(lines)


if __name__ == "__main__":
    run_discovery()