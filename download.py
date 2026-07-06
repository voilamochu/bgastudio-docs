import argparse
import datetime
import json
import time
from pathlib import Path
from typing import Any

from common import PolitenessHttpClient, sanitize_filename, setup_logger


def load_existing_index(index_path: Path, logger) -> dict[str, dict[str, Any]]:
    if not index_path.exists():
        return {}
    try:
        with open(index_path, "r", encoding="utf-8") as handle:
            return {entry["url"]: entry for entry in json.load(handle)}
    except Exception as exc:
        logger.warning(f"Could not read existing index.json: {exc}")
        return {}


def run_download() -> None:
    parser = argparse.ArgumentParser(
        description="Download BGA Studio documentation pages with conditional caching."
    )
    parser.add_argument("--force", action="store_true", help="Ignore cache and force redownload of all pages.")
    args = parser.parse_args()

    project_dir = Path(__file__).parent.resolve()
    source_dir = project_dir / "source-html"
    source_dir.mkdir(exist_ok=True)

    logger = setup_logger("download", project_dir / "logs" / "download.log")
    start_time = time.time()
    logger.info("Starting Phase 2: Download")

    urls_path = project_dir / "urls.json"
    if not urls_path.exists():
        logger.error(
            "urls.json not found. Run discover.py first.",
            extra={"title": "", "canonical_url": "", "depth": 0, "status": "error", "elapsed": 0.0},
        )
        print("Error: urls.json not found! Please run discover.py first.")
        return

    with open(urls_path, "r", encoding="utf-8") as handle:
        pages = json.load(handle)

    existing_index = load_existing_index(project_dir / "index.json", logger)
    client = PolitenessHttpClient(delay=1.0, max_retries=3, base_backoff=2.0)

    downloaded_count = 0
    cached_count = 0
    error_count = 0
    new_index_data: list[dict[str, Any]] = []

    for idx, page in enumerate(pages, start=1):
        title = page["title"]
        url = page["url"]
        depth = page["depth"]
        filename = sanitize_filename(title)
        file_path = source_dir / filename

        existing_entry = existing_index.get(url, {})
        local_exists = file_path.exists()
        cached_timestamp = existing_entry.get("timestamp")
        headers: dict[str, str] = {}

        if local_exists and not args.force:
            if existing_entry.get("etag"):
                headers["If-None-Match"] = existing_entry["etag"]
            if existing_entry.get("last_modified"):
                headers["If-Modified-Since"] = existing_entry["last_modified"]

        logger.info(
            f"Requesting page: {title}",
            extra={
                "title": title,
                "canonical_url": url,
                "depth": depth,
                "status": "cache_check" if headers and not args.force else "downloading",
                "elapsed": time.time() - start_time,
            },
        )

        response = client.fetch(
            url=url,
            logger=logger,
            depth=depth,
            title=title,
            method="GET",
            headers=headers or None,
        )

        if response is None:
            error_count += 1
            logger.error(
                f"Failed to download {title}",
                extra={
                    "title": title,
                    "canonical_url": url,
                    "depth": depth,
                    "status": "error_fetch",
                    "elapsed": time.time() - start_time,
                },
            )
            print(f"[{idx}/{len(pages)}] Error {title} (request failed)")
            continue

        etag = response.headers.get("ETag") or existing_entry.get("etag")
        last_modified = response.headers.get("Last-Modified") or existing_entry.get("last_modified")

        if response.status_code == 304:
            cached_count += 1
            new_index_data.append(
                {
                    "title": title,
                    "url": url,
                    "depth": depth,
                    "filename": filename,
                    "timestamp": cached_timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "etag": etag,
                    "last_modified": last_modified,
                }
            )
            logger.info(
                f"Page unchanged (304): {title}",
                extra={
                    "title": title,
                    "canonical_url": url,
                    "depth": depth,
                    "status": "cached_304",
                    "elapsed": time.time() - start_time,
                },
            )
            print(f"[{idx}/{len(pages)}] Cached (304) {title}")
            continue

        if response.status_code != 200:
            error_count += 1
            logger.error(
                f"HTTP status {response.status_code} for {title}",
                extra={
                    "title": title,
                    "canonical_url": url,
                    "depth": depth,
                    "status": f"http_error_{response.status_code}",
                    "elapsed": time.time() - start_time,
                },
            )
            print(f"[{idx}/{len(pages)}] HTTP Error {response.status_code} for {title}")
            continue

        new_html = response.text
        content_unchanged = False
        if local_exists and not args.force:
            try:
                with open(file_path, "r", encoding="utf-8") as handle:
                    content_unchanged = handle.read() == new_html
            except Exception:
                content_unchanged = False

        if content_unchanged:
            cached_count += 1
            new_index_data.append(
                {
                    "title": title,
                    "url": url,
                    "depth": depth,
                    "filename": filename,
                    "timestamp": cached_timestamp or datetime.datetime.now(datetime.timezone.utc).isoformat(),
                    "etag": etag,
                    "last_modified": last_modified,
                }
            )
            logger.info(
                f"Page unchanged (content match): {title}",
                extra={
                    "title": title,
                    "canonical_url": url,
                    "depth": depth,
                    "status": "cached_hash",
                    "elapsed": time.time() - start_time,
                },
            )
            print(f"[{idx}/{len(pages)}] Cached (identical) {title}")
            continue

        try:
            with open(file_path, "w", encoding="utf-8") as handle:
                handle.write(new_html)
        except Exception as exc:
            error_count += 1
            logger.error(
                f"Failed to save file for {title}: {exc}",
                extra={
                    "title": title,
                    "canonical_url": url,
                    "depth": depth,
                    "status": "error_save",
                    "elapsed": time.time() - start_time,
                },
            )
            print(f"[{idx}/{len(pages)}] Error saving {title}: {exc}")
            continue

        downloaded_count += 1
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
        new_index_data.append(
            {
                "title": title,
                "url": url,
                "depth": depth,
                "filename": filename,
                "timestamp": timestamp,
                "etag": etag,
                "last_modified": last_modified,
            }
        )
        logger.info(
            f"Downloaded page: {title}",
            extra={
                "title": title,
                "canonical_url": url,
                "depth": depth,
                "status": "downloaded",
                "elapsed": time.time() - start_time,
            },
        )
        print(f"[{idx}/{len(pages)}] Downloaded {title}")

    with open(project_dir / "index.json", "w", encoding="utf-8") as handle:
        json.dump(new_index_data, handle, indent=4, ensure_ascii=False)

    elapsed_time = time.time() - start_time
    logger.info(
        "Download completed",
        extra={
            "title": "Summary",
            "canonical_url": "",
            "depth": 0,
            "status": "summary",
            "elapsed": elapsed_time,
        },
    )

    print("\n=== Download Complete ===")
    print(f"Downloaded (Updated): {downloaded_count}")
    print(f"Cached/Unchanged: {cached_count}")
    print(f"Errors: {error_count + client.error_count}")
    print("Index saved to: index.json")
    print("Structured logs written to: logs/download.log")


if __name__ == "__main__":
    run_download()
