import argparse
import datetime
import hashlib
import json
import time
from pathlib import Path

from common import PolitenessHttpClient, sanitize_filename, setup_logger


def compute_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def verify_file(html_path: Path, meta_path: Path, expected_sha: str) -> bool:
    try:
        if not html_path.exists() or not meta_path.exists():
            return False
        if html_path.stat().st_size == 0:
            return False
        with open(html_path, "r", encoding="utf-8") as f:
            actual_sha = compute_sha256(f.read())
        if actual_sha != expected_sha:
            return False
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        if meta.get("content_sha256") != expected_sha:
            return False
        return True
    except Exception:
        return False


def check_existing(html_path: Path, meta_path: Path) -> bool:
    if not html_path.exists() or not meta_path.exists():
        return False
    try:
        if html_path.stat().st_size == 0:
            return False
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        expected_sha = meta.get("content_sha256")
        if not expected_sha:
            return False
        with open(html_path, "r", encoding="utf-8") as f:
            actual_sha = compute_sha256(f.read())
        return actual_sha == expected_sha
    except Exception:
        return False


def run_download() -> None:
    parser = argparse.ArgumentParser(
        description="Download BGA Studio documentation pages."
    )
    parser.add_argument("--force", action="store_true", help="Force redownload of all pages.")
    args = parser.parse_args()

    project_dir = Path(__file__).parent.resolve()
    source_dir = project_dir / "source-html"
    source_dir.mkdir(exist_ok=True)

    logger = setup_logger("download", project_dir / "logs" / "download.log")
    start_time = time.time()
    logger.info("Starting download phase")

    urls_path = project_dir / "urls.json"
    if not urls_path.exists():
        print("Error: urls.json not found! Please run discover.py first.")
        return

    with open(urls_path, "r", encoding="utf-8") as f:
        pages = json.load(f)

    client = PolitenessHttpClient(delay=1.0, max_retries=3, base_backoff=2.0)

    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    http_errors = 0
    total_bytes = 0
    download_times: list[float] = []

    for idx, page in enumerate(pages, start=1):
        title = page["title"]
        url = page["url"]
        depth = page["depth"]
        html_filename = sanitize_filename(title)
        html_path = source_dir / html_filename
        meta_path = source_dir / html_filename.replace(".html", ".meta.json")

        elapsed = time.time() - start_time
        avg_time = elapsed / idx if idx > 0 else 0
        remaining = (len(pages) - idx) * avg_time
        print(f"[{idx}/{len(pages)}] Downloading {title}")
        print(f"    Elapsed: {elapsed:.1f}s, Avg/page: {avg_time:.2f}s, Est. remaining: {remaining:.1f}s")

        if check_existing(html_path, meta_path) and not args.force:
            skipped_count += 1
            total_bytes += html_path.stat().st_size
            logger.info(
                f"Skipped existing file: {title}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": "skipped", "elapsed": elapsed},
            )
            print(f"[{idx}/{len(pages)}] SKIP {title}")
            continue

        page_start = time.time()
        response = client.fetch(
            url=url,
            logger=logger,
            depth=depth,
            title=title,
            method="GET",
            headers=None,
        )

        if response is None:
            failed_count += 1
            logger.error(
                f"Failed to download {title}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": "error_fetch", "elapsed": time.time() - start_time},
            )
            print(f"[{idx}/{len(pages)}] FAILED {title}")
            continue

        if response.status_code != 200:
            failed_count += 1
            http_errors += 1
            logger.error(
                f"HTTP status {response.status_code} for {title}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": f"http_{response.status_code}", "elapsed": time.time() - start_time},
            )
            print(f"[{idx}/{len(pages)}] HTTP {response.status_code} {title}")
            continue

        html_content = response.text
        content_sha256 = compute_sha256(html_content)
        content_type = response.headers.get("Content-Type", "")
        etag = response.headers.get("ETag")
        last_modified = response.headers.get("Last-Modified")
        download_duration_ms = int((time.time() - page_start) * 1000)

        try:
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
        except Exception as exc:
            failed_count += 1
            logger.error(
                f"Failed to save HTML for {title}: {exc}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": "error_save_html", "elapsed": time.time() - start_time},
            )
            print(f"[{idx}/{len(pages)}] FAILED {title} (save error)")
            continue

        meta = {
            "title": title,
            "url": url,
            "depth": depth,
            "downloaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "http_status": response.status_code,
            "content_type": content_type,
            "etag": etag,
            "last_modified": last_modified,
            "content_sha256": content_sha256,
            "html_filename": html_filename,
            "download_duration_ms": download_duration_ms,
        }

        try:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            if html_path.exists():
                html_path.unlink()
            failed_count += 1
            logger.error(
                f"Failed to save metadata for {title}: {exc}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": "error_save_meta", "elapsed": time.time() - start_time},
            )
            print(f"[{idx}/{len(pages)}] FAILED {title} (meta error)")
            continue

        if not verify_file(html_path, meta_path, content_sha256):
            if html_path.exists():
                html_path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            failed_count += 1
            logger.error(
                f"Verification failed for {title}",
                extra={"title": title, "canonical_url": url, "depth": depth, "status": "verification_failed", "elapsed": time.time() - start_time},
            )
            print(f"[{idx}/{len(pages)}] FAILED {title} (verification)")
            continue

        downloaded_count += 1
        total_bytes += len(html_content.encode("utf-8"))
        download_times.append(download_duration_ms / 1000.0)

        logger.info(
            f"Downloaded file: {title}",
            extra={"title": title, "canonical_url": url, "depth": depth, "status": "downloaded", "elapsed": time.time() - start_time},
        )
        logger.info(
            f"Metadata written: {meta_path.name}",
            extra={"title": title, "canonical_url": url, "depth": depth, "status": "metadata_written", "elapsed": time.time() - start_time},
        )
        print(f"[{idx}/{len(pages)}] DOWNLOAD {title}")

    elapsed_time = time.time() - start_time
    avg_download_time = sum(download_times) / len(download_times) if download_times else 0
    avg_page_size = total_bytes / downloaded_count if downloaded_count > 0 else 0

    report = f"""# Download Report

## Summary

| Metric | Value |
|--------|-------|
| Total pages requested | {len(pages)} |
| Downloaded | {downloaded_count} |
| Skipped | {skipped_count} |
| Failed | {failed_count} |
| HTTP errors | {http_errors} |
| Total bytes downloaded | {total_bytes:,} |
| Average page size | {avg_page_size:,.0f} bytes |
| Average download time | {avg_download_time:.2f}s |
| Total download time | {elapsed_time:.1f}s |
"""

    with open(project_dir / "download_report.md", "w", encoding="utf-8") as f:
        f.write(report)

    print("\nDownload complete")
    print(f"Pages requested: {len(pages)}")
    print(f"Downloaded: {downloaded_count}")
    print(f"Skipped: {skipped_count}")
    print(f"Failed: {failed_count}")
    print(f"Total bytes: {total_bytes:,}")
    print(f"Average page size: {avg_page_size:,.0f} bytes")
    print(f"Elapsed time: {elapsed_time:.1f}s")


if __name__ == "__main__":
    run_download()