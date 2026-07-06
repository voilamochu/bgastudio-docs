import csv
import json
import os
import time
from collections import deque
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from common import (
    START_URL,
    DocPage,
    PolitenessHttpClient,
    canonicalize_url,
    setup_logger,
    should_ignore_url,
)


def extract_title(link, canonical_url: str) -> str:
    title = (link.get("title") or "").strip()
    if title.endswith(" (page does not exist)"):
        title = title[: -len(" (page does not exist)")].strip()
    if not title:
        title = link.get_text(strip=True)
    if not title:
        title = os.path.basename(urlparse(canonical_url).path).replace("_", " ")
    return title or "Studio Doc"


def fetch_soup(client: PolitenessHttpClient, logger, page: DocPage, started_at: float):
    response = client.fetch(
        url=page.url,
        logger=logger,
        depth=page.depth,
        title=page.title,
        method="GET",
    )
    if response is None:
        return None, None, "failed"
    if response.status_code == 404:
        return response, None, "broken"
    if response.status_code >= 400:
        return response, None, "failed"

    soup = BeautifulSoup(response.text, "html.parser")
    heading = soup.find(id="firstHeading")
    if heading:
        actual_title = heading.get_text(strip=True)
        if actual_title:
            page.title = actual_title

    logger.info(
        f"Fetched page for discovery: {page.url}",
        extra={
            "title": page.title,
            "canonical_url": page.url,
            "depth": page.depth,
            "status": "success",
            "elapsed": time.time() - started_at,
        },
    )
    return response, soup, "success"


def run_discovery() -> None:
    project_dir = Path(__file__).parent.resolve()
    logger = setup_logger("discover", project_dir / "logs" / "discover.log")
    start_time = time.time()
    logger.info("Starting Phase 1: Discover")

    client = PolitenessHttpClient(delay=1.0, max_retries=3, base_backoff=2.0)
    discovered: dict[str, DocPage] = {}
    validated: set[str] = set()
    parent_map: dict[str, str] = {}
    queue: deque[DocPage] = deque()

    duplicates_removed = 0
    ignored_pages = 0
    broken_links = 0
    redirects_count = 0
    http_failures = 0
    external_links = 0
    broken_links_details: list[dict[str, str]] = []
    redirect_details: list[dict[str, str]] = []
    failure_details: list[dict[str, str]] = []

    start_page = DocPage(title="Studio", url=canonicalize_url(START_URL), depth=0)
    discovered[start_page.url] = start_page
    parent_map[start_page.url] = "Start"
    queue.append(start_page)

    while queue:
        current_page = queue.popleft()
        if current_page.depth >= 2:
            continue

        response, soup, status = fetch_soup(client, logger, current_page, start_time)
        if status != "success":
            if status == "broken":
                broken_links += 1
                broken_links_details.append(
                    {"source": parent_map.get(current_page.url, "Unknown"), "target": current_page.url}
                )
            else:
                http_failures += 1
                failure_details.append(
                    {
                        "source": parent_map.get(current_page.url, "Unknown"),
                        "target": current_page.url,
                        "error": f"Request failed with status {response.status_code}" if response else "Request failed",
                    }
                )
            continue

        validated.add(current_page.url)
        final_url = canonicalize_url(response.url)
        if final_url != current_page.url:
            redirects_count += 1
            original_url = current_page.url
            redirect_details.append(
                {
                    "source": parent_map.get(original_url, "Unknown"),
                    "original": original_url,
                    "final": final_url,
                }
            )
            if final_url in discovered and final_url != original_url:
                duplicates_removed += 1
                discovered.pop(original_url, None)
                continue
            discovered.pop(original_url, None)
            current_page.url = final_url
            discovered[final_url] = current_page
            parent_map[final_url] = parent_map.pop(original_url, "Start")
            validated.add(final_url)

        body = soup.find(id="mw-content-text")
        if not body:
            logger.warning(
                f"Could not find '#mw-content-text' on {current_page.url}",
                extra={
                    "title": current_page.title,
                    "canonical_url": current_page.url,
                    "depth": current_page.depth,
                    "status": "missing_content",
                    "elapsed": time.time() - start_time,
                },
            )
            continue

        for link in body.find_all("a", href=True):
            canonical_link = canonicalize_url(link["href"], current_page.url)
            ignore_flag, reason = should_ignore_url(canonical_link)
            if ignore_flag:
                if reason == "external_domain":
                    external_links += 1
                else:
                    ignored_pages += 1
                continue
            if canonical_link in discovered:
                duplicates_removed += 1
                continue

            child_page = DocPage(
                title=extract_title(link, canonical_link),
                url=canonical_link,
                depth=current_page.depth + 1,
            )
            discovered[canonical_link] = child_page
            parent_map[canonical_link] = current_page.url

            logger.info(
                f"Discovered page: {canonical_link}",
                extra={
                    "title": child_page.title,
                    "canonical_url": canonical_link,
                    "depth": child_page.depth,
                    "status": "discovered" if child_page.depth >= 2 else "queued",
                    "elapsed": time.time() - start_time,
                },
            )
            if child_page.depth < 2:
                queue.append(child_page)

    for page in [page for page in list(discovered.values()) if page.url not in validated]:
        response, soup, status = fetch_soup(client, logger, page, start_time)
        if status != "success":
            discovered.pop(page.url, None)
            if status == "broken":
                broken_links += 1
                broken_links_details.append(
                    {"source": parent_map.get(page.url, "Unknown"), "target": page.url}
                )
            else:
                http_failures += 1
                failure_details.append(
                    {
                        "source": parent_map.get(page.url, "Unknown"),
                        "target": page.url,
                        "error": f"Request failed with status {response.status_code}" if response else "Request failed",
                    }
                )
            continue

        validated.add(page.url)
        final_url = canonicalize_url(response.url)
        if final_url != page.url:
            redirects_count += 1
            original_url = page.url
            redirect_details.append(
                {"source": parent_map.get(original_url, "Unknown"), "original": original_url, "final": final_url}
            )
            if final_url in discovered and final_url != original_url:
                duplicates_removed += 1
                discovered.pop(original_url, None)
                continue
            discovered.pop(original_url, None)
            page.url = final_url
            discovered[final_url] = page
            parent_map[final_url] = parent_map.pop(original_url, "Unknown")

        heading = soup.find(id="firstHeading")
        if heading:
            actual_title = heading.get_text(strip=True)
            if actual_title:
                page.title = actual_title

    sorted_pages = sorted(discovered.values(), key=lambda page: page.title.lower())
    json_data = [{"title": page.title, "url": page.url, "depth": page.depth} for page in sorted_pages]

    with open(project_dir / "urls.json", "w", encoding="utf-8") as handle:
        json.dump(json_data, handle, indent=4, ensure_ascii=False)

    with open(project_dir / "urls.csv", "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["Title", "Depth", "URL"])
        for page in sorted_pages:
            writer.writerow([page.title, page.depth, page.url])

    crawl_duration = time.time() - start_time
    depth_counts = {0: 0, 1: 0, 2: 0}
    for page in discovered.values():
        depth_counts[page.depth] = depth_counts.get(page.depth, 0) + 1

    report_lines = [
        "# BGA Studio Documentation Discovery Report",
        "",
        "This report summarizes Phase 1 (Discover) of the Board Game Arena Studio documentation crawler.",
        "",
        "## Crawl Telemetry Summary",
        "",
        "| Metric | Count |",
        "| :--- | :--- |",
        f"| **Total Pages Discovered** | {len(discovered)} |",
        f"| **Total Pages Downloaded (Fetched)** | {client.success_count} |",
        f"| **Duplicates Removed** | {duplicates_removed} |",
        f"| **Ignored Pages** | {ignored_pages} |",
        f"| **Broken Links (404)** | {broken_links} |",
        f"| **Redirects Followed** | {redirects_count} |",
        f"| **HTTP Failures** | {http_failures} |",
        f"| **External Links Encountered** | {external_links} |",
        f"| **Crawl Duration** | {crawl_duration:.2f} seconds |",
        "",
        "---",
        "",
        "## Crawl Depth Summary",
        "",
        f"- **Depth 0 (Root landing page)**: {depth_counts.get(0, 0)} page",
        f"- **Depth 1 (Linked from root)**: {depth_counts.get(1, 0)} pages",
        f"- **Depth 2 (Linked from depth 1)**: {depth_counts.get(2, 0)} pages",
        "",
        "---",
        "",
        f"## Redirects Followed ({len(redirect_details)})",
        "",
    ]
    if redirect_details:
        report_lines.extend(["| Source Page | Original Link URL | Final Destination URL |", "| :--- | :--- | :--- |"])
        for detail in redirect_details:
            report_lines.append(f"| `{detail['source']}` | `{detail['original']}` | `{detail['final']}` |")
    else:
        report_lines.append("*No redirects encountered.*")

    report_lines.extend(["", "---", "", f"## Broken Links Encountered (404) ({len(broken_links_details)})", ""])
    if broken_links_details:
        report_lines.extend(["| Source Page | Target Broken URL |", "| :--- | :--- |"])
        for detail in broken_links_details:
            report_lines.append(f"| `{detail['source']}` | `{detail['target']}` |")
    else:
        report_lines.append("*No broken links encountered.*")

    report_lines.extend(["", "---", "", f"## HTTP Failures / Network Errors ({len(failure_details)})", ""])
    if failure_details:
        report_lines.extend(["| Source Page | Target URL | Error Message |", "| :--- | :--- | :--- |"])
        for detail in failure_details:
            report_lines.append(f"| `{detail['source']}` | `{detail['target']}` | {detail['error']} |")
    else:
        report_lines.append("*No HTTP failures encountered.*")
    report_lines.append("")

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
    print(f"\nPhase 1 Discovery Completed successfully in {crawl_duration:.2f}s!")
    print(f"Number of pages discovered: {len(discovered)}")
    print(f"Pages at depth 0: {depth_counts.get(0, 0)}")
    print(f"Pages at depth 1: {depth_counts.get(1, 0)}")
    print(f"Pages at depth 2: {depth_counts.get(2, 0)}")
    print(f"Broken links: {broken_links}")
    print(f"Redirects followed: {redirects_count}")
    print("Structured logs written to: logs/discover.log")
    print("Detailed discovery report written to: discovery_report.md")


if __name__ == "__main__":
    run_discovery()
