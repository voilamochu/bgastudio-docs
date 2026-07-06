#!/usr/bin/env python3
"""Extract structured documentation content from cleaned HTML files.

Reads every .html file in clean_html/, converts it to a structured JSON
representation, and writes the result to content_json/ while preserving
the directory structure.
"""

import copy
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from bs4 import BeautifulSoup, Tag

EXTRACTOR_VERSION = "1.0.0"

CLEAN_HTML_DIR = Path("clean-html")
CONTENT_JSON_DIR = Path("content_json")
LOG_FILE = Path("logs/extract_content.log")


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
    file_handler.setFormatter(
        logging.Formatter(
            '{"timestamp":"%(asctime)s","level":"%(levelname)s","message":%(message)s}',
            datefmt="%Y-%m-%dT%H:%M:%S%z",
        )
    )
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(stream_handler)
    return logger


def get_page_title(soup: BeautifulSoup) -> str:
    """Extract the page title from the HTML <title> tag.

    Strips the common ' - Board Game Arena' suffix when present.
    Falls back to the first h1/h2 if <title> is missing.
    """
    title_tag = soup.find("title")
    if title_tag:
        title = title_tag.get_text(strip=True)
        suffix = " - Board Game Arena"
        if title.endswith(suffix):
            title = title[: -len(suffix)]
        title = title.strip()
        if title:
            return title

    heading = soup.find(["h1", "h2"])
    if heading:
        text = heading.get_text(strip=True)
        if text:
            return text

    return "Untitled"


def get_article_content(soup: BeautifulSoup) -> Optional[Tag]:
    """Find the main article container in a cleaned HTML document."""
    container = soup.find("div", class_="article")
    return container if isinstance(container, Tag) else None


def collect_headings(article: Tag) -> list[dict]:
    """Collect all headings from the article, preserving order."""
    headings: list[dict] = []
    for tag in article.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
        level = int(tag.name[1])
        text = tag.get_text(strip=True)
        heading_id = tag.get("id", "")
        if not heading_id:
            span = tag.find("span", id=True)
            if span:
                heading_id = span.get("id", "")
        headings.append({"level": level, "text": text, "id": heading_id})
    return headings


def extract_inline_text(element: Tag) -> str:
    """Extract plain text from an element, preserving inline code markers.

    Replaces <code> with backtick-delimited text.
    Replaces <br> with newlines.
    Replaces <img> with '[image: alt]'.
    Omits link hrefs but keeps their text.
    Collapses multiple whitespace characters into a single space per line,
    then joins lines with spaces.
    """
    # Replace inline code with backtick-wrapped text.
    for code in element.find_all("code"):
        code.replace_with(f"`{code.get_text()}`")

    # Replace line breaks with newline characters.
    for br in element.find_all("br"):
        br.replace_with("\n")

    # Replace images with an inline marker.
    for img in element.find_all("img"):
        alt = img.get("alt", "")
        img.replace_with(f"[image: {alt}]" if alt else "[image]")

    raw_text = element.get_text(separator=" ", strip=True)
    lines = raw_text.splitlines()
    lines = [line.strip() for line in lines if line.strip()]
    return " ".join(lines)


def is_note_variant(text: str) -> Optional[str]:
    """Detect paragraph markers that indicate a note/warning/tip block."""
    text_lower = text.lower().strip()
    markers = [
        ("note:", "note"),
        ("notes:", "note"),
        ("warning:", "warning"),
        ("warnings:", "warning"),
        ("caution:", "warning"),
        ("important:", "warning"),
        ("tip:", "tip"),
        ("tips:", "tip"),
        ("info:", "info"),
        ("information:", "info"),
    ]
    for marker, variant in markers:
        if text_lower.startswith(marker):
            return variant
    return None


def process_paragraph(p: Tag) -> Optional[dict]:
    """Process a <p> tag into a paragraph or note content entry."""
    text = extract_inline_text(p)
    if not text:
        return None

    variant = is_note_variant(text)
    if variant:
        return {"type": "note", "variant": variant, "text": text}

    return {"type": "paragraph", "text": text}


def process_code_block(pre: Tag) -> dict:
    """Process a <pre> tag into a code block content entry.

    Preserves whitespace exactly.
    Does not syntax-highlight.
    """
    text = pre.get_text()
    text = text.rstrip("\n")

    language: Optional[str] = None
    classes = pre.get("class", [])
    for cls in classes:
        if cls.startswith("source-") or cls.startswith("language-"):
            language = cls.split("-", 1)[1]
            break

    return {"type": "code", "language": language, "text": text}


def process_row(cells: list[Tag], is_header: bool = False) -> list[str]:
    """Extract text from a list of table cells."""
    return [cell.get_text(strip=True) for cell in cells]


def process_table(table: Tag) -> dict:
    """Process a <table> into a structurally representative content entry.

    Captures headers (from thead) and rows (from tbody).
    Merged cells are represented with an empty string when span information
    is not explicit in the markup.
    """
    headers: list[str] = []
    rows: list[list[str]] = []

    thead = table.find("thead")
    tbody = table.find("tbody")

    # Determine where the first row of data/headers lives.
    first_row = None
    if thead:
        first_row = thead.find("tr")

    if first_row is None:
        first_row = table.find("tr")

    if first_row is not None:
        header_cells = first_row.find_all(["th", "td"])
        headers = process_row(header_cells, is_header=True)

        # Collect rows from thead (remaining) and tbody.
        remaining_rows = []
        if thead:
            for tr in thead.find_all("tr")[1:]:
                remaining_rows.append(tr.find_all(["td", "th"]))
        if tbody:
            all_trs = tbody.find_all("tr")
            start_idx = 1 if first_row in all_trs else 0
            for tr in all_trs[start_idx:]:
                remaining_rows.append(tr.find_all(["td", "th"]))
        elif first_row is not None and not thead:
            # Single-row table with headers; no data rows beneath.
            pass

        for cells in remaining_rows:
            row_texts = [cell.get_text(strip=True) for cell in cells]
            if any(row_texts):
                rows.append(row_texts)
    else:
        # Fallback: collect all rows as data rows.
        for tr in table.find_all("tr"):
            row_texts = [cell.get_text(strip=True) for cell in tr.find_all(["td", "th"])]
            if any(row_texts):
                rows.append(row_texts)

    return {"type": "table", "headers": headers, "rows": rows}


def process_list_items(li: Tag, ordered: bool) -> Optional[dict]:
    """Process a single <li> element, including any nested list.

    Works on a deep copy so nested list extraction does not mutate the
    original document tree.
    """
    li_clone = copy.deepcopy(li)

    # Extract any nested list before extracting text so that the parent
    # item's text does not include nested list item text.
    nested = None
    nested_list = li_clone.find(["ul", "ol"], recursive=False)
    if nested_list and isinstance(nested_list, Tag):
        nested = process_list_element(nested_list)
        nested_list.extract()

    text = extract_inline_text(li_clone)
    if not text:
        return None

    return {"text": text, "nested": nested}


def process_list_element(list_el: Tag) -> dict:
    """Process a <ul> or <ol> into a list content entry."""
    ordered = list_el.name == "ol"
    items: list[dict] = []

    for li in list_el.find_all("li", recursive=False):
        processed = process_list_items(li, ordered)
        if processed:
            items.append(processed)

    if not items:
        return {"type": "list", "ordered": ordered, "items": []}

    return {"type": "list", "ordered": ordered, "items": items}


def process_image(img: Tag) -> Optional[dict]:
    """Process an <img> tag into an image content entry."""
    src = img.get("src", "").strip()
    alt = img.get("alt", "")
    if not src:
        return None
    return {"type": "image", "src": src, "alt": alt}


def process_blockquote(blockquote: Tag) -> dict:
    """Process a <blockquote> tag into a blockquote content entry."""
    text = extract_inline_text(blockquote)
    return {"type": "blockquote", "text": text}


def process_element(tag: Tag) -> Optional[dict]:
    """Convert a top-level children of the article div to a content entry.

    Structural tags (<li>, <td>, <tr>, etc.) are skipped because they are
    already handled by their parent container.
    """
    if not isinstance(tag, Tag):
        return None

    name = tag.name.lower()

    if name == "p":
        return process_paragraph(tag)
    if name == "pre":
        return process_code_block(tag)
    if name == "table":
        return process_table(tag)
    if name == "ul" or name == "ol":
        return process_list_element(tag)
    if name == "img":
        return process_image(tag)
    if name == "blockquote":
        return process_blockquote(tag)

    # Skip tags that are handled by a parent element or recorded separately.
    skipped = {
        "a", "br", "span", "b", "strong", "i", "em",
        "div", "li", "td", "th", "tr", "tbody", "thead",
        "hr", "ul", "ol",
        "h1", "h2", "h3", "h4", "h5", "h6",
    }
    if name in skipped:
        return None

    # Generic fallback: emit as paragraph if it has text.
    text = tag.get_text(strip=True)
    if text:
        return {"type": "paragraph", "text": text}

    return None


def normalize_link(href: str) -> str:
    """Normalize internal relative links to a canonical form.

    Internal links that start with a slash are converted to 'Title.html'
    format.  External links are left unchanged.
    """
    href = href.strip()
    if not href:
        return href

    url = urlparse(href)
    if url.scheme in ("http", "https"):
        return href

    if href.startswith("/"):
        path = href.lstrip("/")
        path = path.split("?")[0].split("#")[0]
        if path:
            return f"{path}.html"
        return href

    return href.replace("\\", "/")


def count_words(text: str) -> int:
    """Count whitespace-separated words in a text string."""
    if not text:
        return 0
    return len(text.split())


def extract_page(
    html_path: Path,
    project_root: Path,
    clean_html_dir: Path,
) -> Optional[dict]:
    """Extract structured documentation content from a cleaned HTML file.

    Returns a dictionary ready for JSON serialisation, or None if the file
    cannot be processed.
    """
    try:
        with open(html_path, "r", encoding="utf-8") as fh:
            soup = BeautifulSoup(fh, "html.parser")
    except Exception as exc:
        logging.getLogger("extract").error(
            f"Error reading {html_path}: {exc}"
        )
        return None

    article = get_article_content(soup)
    if article is None:
        logging.getLogger("extract").warning(
            f"No article content found in {html_path.name}"
        )
        return None

    title = get_page_title(soup)
    headings = collect_headings(article)

    content: list[dict] = []
    links: list[dict] = []
    images: list[dict] = []
    seen_links: set[tuple[str, str]] = set()
    seen_images: set[tuple[str, str]] = set()

    for child in article.children:
        if not isinstance(child, Tag):
            continue

        # Skip empty paragraph wrappers used for spacing.
        if child.name == "p" and not child.get_text(strip=True) and not child.find_all("img"):
            continue

        # Collect links and images before processing the element so that
        # text extraction mutations do not destroy the original tree.
        for a_tag in child.find_all("a", href=True, recursive=True):
            href = a_tag.get("href", "").strip()
            if not href:
                continue
            img = a_tag.find("img")
            if img:
                alt = img.get("alt", "")
                text = alt if alt else href
            else:
                text = a_tag.get_text(strip=True) or href
            normalized = normalize_link(href)
            key = (normalized, text)
            if key not in seen_links:
                seen_links.add(key)
                links.append({"text": text, "url": normalized})

        for img_tag in child.find_all("img", recursive=True):
            src = img_tag.get("src", "").strip()
            alt = img_tag.get("alt", "")
            if not src:
                continue
            key = (src, alt)
            if key not in seen_images:
                seen_images.add(key)
                images.append({"src": src, "alt": alt})

        element = process_element(child)
        if element:
            content.append(element)

    # Compute document-level metadata.
    all_content_text = " ".join(
        item.get("text", "") for item in content if "text" in item
    )
    word_count = count_words(all_content_text)
    code_block_count = sum(1 for item in content if item.get("type") == "code")
    table_count = sum(1 for item in content if item.get("type") == "table")
    image_count = len(images)
    heading_count = len(headings)
    list_count = sum(1 for item in content if item.get("type") == "list")

    rel_path = html_path.relative_to(clean_html_dir)
    output_rel = CONTENT_JSON_DIR / rel_path.with_suffix(".json")

    return {
        "title": title,
        "source_file": html_path.name,
        "relative_path": str(rel_path).replace("\\", "/"),
        "content_json_path": str(output_rel).replace("\\", "/"),
        "headings": headings,
        "content": content,
        "links": links,
        "images": images,
        "metadata": {
            "extractor_version": EXTRACTOR_VERSION,
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "word_count": word_count,
            "heading_count": heading_count,
            "code_block_count": code_block_count,
            "table_count": table_count,
            "image_count": image_count,
            "list_count": list_count,
        },
    }


def write_output(result: dict, output_path: Path) -> None:
    """Write the extracted result as indented JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2, ensure_ascii=False)


def main() -> None:
    """Entry point: extract content from every cleaned HTML document."""
    project_root = Path(__file__).parent.resolve()
    clean_html_dir = project_root / CLEAN_HTML_DIR
    output_dir = project_root / CONTENT_JSON_DIR

    logger = setup_logger("extract", project_root / LOG_FILE)
    start_time = time.time()

    if not clean_html_dir.exists():
        logger.error(f"Input directory not found: {clean_html_dir}")
        sys.exit(1)

    html_files = sorted(clean_html_dir.rglob("*.html"))

    if not html_files:
        logger.error(f"No HTML files found in {clean_html_dir}")
        sys.exit(1)

    succeeded = 0
    failed = 0
    warnings = 0

    for html_path in html_files:
        rel_path = html_path.relative_to(clean_html_dir)
        print(
            f"\rProcessing: {rel_path} ({succeeded + failed}/{len(html_files)})",
            end="",
            file=sys.stderr,
        )

        result = extract_page(html_path, project_root, clean_html_dir)
        if result is None:
            logger.warning(f"Failed to extract: {rel_path}")
            failed += 1
            warnings += 1
            continue

        output_path = output_dir / rel_path.with_suffix(".json")
        try:
            write_output(result, output_path)
            succeeded += 1
        except Exception as exc:
            logger.error(f"Failed to write output for {rel_path}: {exc}")
            failed += 1
            warnings += 1

    print(file=sys.stderr)

    elapsed = time.time() - start_time
    total = len(html_files)

    summary = (
        f"Files processed: {total}\n"
        f"Succeeded: {succeeded}\n"
        f"Failed: {failed}\n"
        f"Warnings: {warnings}\n"
        f"Elapsed time: {elapsed:.2f}s"
    )
    print(summary)

    logger.info(
        json.dumps(
            {
                "status": "completed",
                "files_processed": total,
                "succeeded": succeeded,
                "failed": failed,
                "warnings": warnings,
                "elapsed_seconds": elapsed,
            }
        )
    )

    report_path = project_root / "extraction_report.md"
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("# Content Extraction Report\n\n")
        fh.write(summary)
        fh.write("\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
