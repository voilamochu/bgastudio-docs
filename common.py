import datetime
import json
import logging
import random
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional
from urllib.parse import parse_qsl, quote, unquote, urlencode, urljoin, urlparse, urlunparse

import requests

START_URL = "https://en.doc.boardgamearena.com/Studio"
ALLOWED_HOST = "en.doc.boardgamearena.com"
IGNORED_NAMESPACES = {
    "special",
    "user",
    "talk",
    "file",
    "category",
    "template",
    "mediawiki",
    "help",
}
IGNORED_PATH_PREFIXES = {
    "/gamehelp",
}
IGNORED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".zip",
    ".gz",
}
RETRYABLE_STATUS_CODES = {429, 500, 501, 502, 503, 504, 520, 521, 522, 523, 524, 525, 526}


@dataclass
class DocPage:
    title: str
    url: str
    depth: int


class StructuredJSONFormatter(logging.Formatter):
    """Format log entries as JSON Lines."""

    def format(self, record: logging.LogRecord) -> str:
        entry = {
            "timestamp": datetime.datetime.fromtimestamp(
                record.created,
                datetime.timezone.utc,
            ).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
        }
        for field in ("title", "canonical_url", "depth", "status", "elapsed"):
            if hasattr(record, field):
                entry[field] = getattr(record, field)
        return json.dumps(entry, ensure_ascii=False)


def setup_logger(name: str, log_file: Path) -> logging.Logger:
    """Configure file JSONL logging and human-readable stderr logging."""
    log_file.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        logger.handlers.clear()

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(StructuredJSONFormatter())
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(stream_handler)
    return logger


def _normalize_path(path: str) -> str:
    path = unquote(path or "/")
    path = path.replace(" ", "_")
    path = re.sub(r"/{2,}", "/", path)
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    return quote(path, safe="/:_-()'")


def _title_from_query(parsed_url) -> Optional[str]:
    if parsed_url.path != "/index.php":
        return None
    query_params = dict(parse_qsl(parsed_url.query, keep_blank_values=True))
    title = query_params.get("title")
    if not title:
        return None
    title = unquote(title).replace(" ", "_")
    return quote(title, safe="/:_-()'")


def canonicalize_url(url: str, base_url: str = START_URL) -> str:
    """Convert links into one stable canonical representation."""
    absolute_url = urljoin(base_url, url)
    parsed = urlparse(absolute_url)

    scheme = "https" if parsed.netloc.lower() == ALLOWED_HOST else parsed.scheme.lower()
    netloc = parsed.netloc.lower()

    title_path = _title_from_query(parsed)
    path = f"/{title_path}" if title_path else _normalize_path(parsed.path)

    query_items = [
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if not (parsed.path == "/index.php" and key == "title")
    ]
    query = urlencode(sorted(query_items), doseq=True)

    return urlunparse((scheme, netloc, path, "", query, ""))


def _path_title(path: str) -> str:
    return unquote(path.rsplit("/", 1)[-1]).strip().replace("_", " ")


def should_ignore_url(url: str) -> tuple[bool, str]:
    """Return whether a URL is out of scope for the documentation crawl."""
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.netloc.lower() != ALLOWED_HOST:
        return True, "external_domain"

    path = unquote(parsed.path)
    lower_path = path.lower()
    query_params = dict(parse_qsl(parsed.query, keep_blank_values=True))

    if "/cdn-cgi/" in lower_path:
        return True, "cdn_cgi_endpoint"
    if any(lower_path.endswith(ext) for ext in IGNORED_EXTENSIONS):
        return True, "binary_asset"
    if lower_path == "/api.php":
        return True, "api_endpoint"
    if lower_path == "/help":
        return True, "help_page"
    if any(lower_path.startswith(prefix) for prefix in IGNORED_PATH_PREFIXES):
        return True, "path_prefix_excluded"

    path_title = _path_title(path)
    query_title = unquote(query_params.get("title", "")).strip()
    namespace_candidates = [path_title, query_title]
    for candidate in namespace_candidates:
        if ":" not in candidate:
            continue
        namespace = candidate.split(":", 1)[0].strip().lower()
        if namespace in IGNORED_NAMESPACES:
            return True, f"namespace_{namespace}"

    if query_params.get("action"):
        return True, f"action_{query_params['action'].lower()}"
    if "oldid" in query_params:
        return True, "oldid_revision"
    if "diff" in query_params:
        return True, "diff_comparison"

    lowered_values = " ".join(value.lower() for value in query_params.values())
    if "login" in lower_path or "login" in lowered_values:
        return True, "login_endpoint"

    segments = [segment.lower() for segment in path.strip("/").split("/") if segment]
    if any(segment in {"edit", "history", "search"} for segment in segments):
        return True, "unwanted_endpoint"

    return False, ""


def sanitize_filename(title: str) -> str:
    """Create a Windows-safe HTML filename from a page title."""
    filename = title.replace(" ", "_")
    for char in '<>:"/\\|?*':
        filename = filename.replace(char, "_")
    filename = re.sub(r"_{2,}", "_", filename).strip("._ ")
    if not filename:
        filename = "index"
    if not filename.endswith(".html"):
        filename += ".html"
    return filename


class PolitenessHttpClient:
    """Rate-limited HTTP client with retry handling for transient failures."""

    def __init__(self, delay: float = 1.0, max_retries: int = 3, base_backoff: float = 2.0):
        self.delay = delay
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.last_request_time = 0.0
        self.success_count = 0
        self.retry_count = 0
        self.error_count = 0
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "BGAStudioDocsDownloader/2.0 (+https://en.doc.boardgamearena.com/Studio)"}
        )

    def fetch(
        self,
        url: str,
        logger: logging.Logger,
        depth: int,
        title: str = "",
        method: str = "GET",
        headers: Optional[dict[str, str]] = None,
    ) -> Optional[requests.Response]:
        start_time = time.time()

        for attempt in range(self.max_retries + 1):
            if attempt > 0:
                self.retry_count += 1
                backoff = self.base_backoff * (2 ** (attempt - 1)) + random.uniform(0, 1)
                logger.warning(
                    f"Retrying request ({attempt}/{self.max_retries}) for {url} in {backoff:.2f}s",
                    extra={
                        "title": title,
                        "canonical_url": url,
                        "depth": depth,
                        "status": "retry",
                        "elapsed": time.time() - start_time,
                    },
                )
                time.sleep(backoff)

            since_last = time.time() - self.last_request_time
            if since_last < self.delay:
                time.sleep(self.delay - since_last)
            self.last_request_time = time.time()

            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=15,
                    allow_redirects=True,
                )
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as exc:
                logger.warning(
                    f"Attempt {attempt + 1} raised network exception for {url}: {exc}",
                    extra={
                        "title": title,
                        "canonical_url": url,
                        "depth": depth,
                        "status": "network_exception",
                        "elapsed": time.time() - start_time,
                    },
                )
                continue
            except requests.RequestException as exc:
                self.error_count += 1
                logger.error(
                    f"Attempt {attempt + 1} raised fatal request exception for {url}: {exc}",
                    extra={
                        "title": title,
                        "canonical_url": url,
                        "depth": depth,
                        "status": "fatal_error",
                        "elapsed": time.time() - start_time,
                    },
                )
                return None

            if response.status_code in {200, 304}:
                self.success_count += 1
                return response

            if response.status_code in RETRYABLE_STATUS_CODES:
                logger.warning(
                    f"Attempt {attempt + 1} returned retryable status {response.status_code} for {url}",
                    extra={
                        "title": title,
                        "canonical_url": url,
                        "depth": depth,
                        "status": f"http_{response.status_code}",
                        "elapsed": time.time() - start_time,
                    },
                )
                continue

            self.error_count += 1
            return response

        self.error_count += 1
        return None
