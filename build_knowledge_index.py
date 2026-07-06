#!/usr/bin/env python3
"""Build a searchable knowledge index over extracted documentation.

Reads every JSON document from content_json/ and creates a comprehensive
knowledge index in the knowledge/ directory. No network requests performed.
"""

import json
import logging
import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

CONTENT_JSON_DIR = Path("content_json")
KNOWLEDGE_DIR = Path("knowledge")
LOG_FILE = Path("logs/build_knowledge_index.log")


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


def extract_text_from_content(content_items: list) -> str:
    """Extract plain text from content items recursively."""
    text_parts = []
    for item in content_items:
        if isinstance(item, dict):
            if item.get("type") == "paragraph":
                text_parts.append(item.get("text", ""))
            elif item.get("type") == "note":
                text_parts.append(item.get("text", ""))
            elif item.get("type") == "code":
                text_parts.append(item.get("text", ""))
            elif item.get("type") == "list":
                for sub_item in item.get("items", []):
                    text_parts.append(extract_text_from_content([sub_item]))
                    if sub_item.get("nested"):
                        text_parts.append(extract_text_from_content([sub_item["nested"]]))
    return " ".join(text_parts)


def extract_keywords_from_text(text: str) -> set:
    """Extract unique keywords from text, removing common stop words."""
    stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being", "to", "of", "in", "for", "on", "with", "at", "by", "and", "or", "but", "if", "it", "this", "that", "as", "from", "not", "or", "no", "yes", "you", "your"}
    words = re.findall(r"\b[a-zA-Z]{3,}\b", text.lower())
    return set(w for w in words if w not in stop_words)


def extract_page_terms_for_glossary(page: dict) -> set:
    """Extract glossary terms from page title, headings, code, and links."""
    terms = set()

    title = page.get("title", "")
    if title:
        for match in re.findall(r"\b([A-Z][a-zA-Z]+)\b", title):
            if len(match) > 3:
                terms.add(match)

    for section in page.get("sections", []):
        heading = section.get("heading")
        if heading:
            heading_text = heading.get("text", "")
            for match in re.findall(r"\b([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)\b", heading_text):
                clean_match = match.strip()
                if len(clean_match) > 3:
                    terms.add(clean_match)

            for item in section.get("content", []):
                if item.get("type") in ("paragraph", "note"):
                    text = item.get("text", "")
                    for match in re.findall(r"(this\.bga\.[a-zA-Z]+\.[a-zA-Z]+)", text):
                        if len(match) > 10:
                            terms.add(match)
                if item.get("type") == "code":
                    code = item.get("text", "")
                    for match in re.findall(r"(this\.bga\.[a-zA-Z]+\.[a-zA-Z]+)", code):
                        if len(match) > 10:
                            terms.add(match)
                    for match in re.findall(r"\b([A-Za-z]+\.[a-zA-Z]+\.[a-zA-Z]+)\b", code):
                        if isinstance(match, tuple):
                            match = match[0]
                        if len(match) > 5:
                            terms.add(match)
                    for match in re.findall(r"\b([A-Z][a-zA-Z]+)\(\)", code):
                        if match not in ("Object", "string", "number", "boolean", "void", "Array"):
                            terms.add(match)
                    for match in re.findall(r"new ([A-Z][a-zA-Z]+)", code):
                        terms.add(match)
                    for match in re.findall(r"define\(\[.*?\"([^\"]+)\"", code):
                        clean_match = match.rstrip("}").rstrip("]")
                        if clean_match and len(clean_match) > 3:
                            terms.add(clean_match)

    for link in page.get("links", []):
        link_text = link.get("text", "")
        if ".json" in link_text or ".php" in link_text or ".js" in link_text:
            clean_name = link_text.split("#")[0].split(".")[0]
            if clean_name:
                terms.add(clean_name)

    for image in page.get("images", []):
        alt = image.get("alt", "")
        if alt:
            clean_name = alt.split(".")[0]
            if clean_name and len(clean_name) > 2:
                terms.add(clean_name)

    return terms


def classify_topics(page: dict) -> list:
    """Classify a page into one or more topics based on title, headings, and content."""
    topics = []
    title_score = defaultdict(int)
    heading_score = defaultdict(int)
    content_score = defaultdict(int)

    topic_indicators = {
        "Architecture": ["lifecycle", "architecture", "structure", "framework"],
        "Getting Started": ["first step", "getting started", "tutorial", "setup", "environment", "join"],
        "Game Logic": ["game.php", "main game logic", "setupnewgame", "database", "dbquery", "sql", "query", "gamestate"],
        "Game Interface": ["game.js", "javascript", "dojo", "ui", "interface", "button", "animation"],
        "Database": ["database", "dbmodel", "sql", "table", "schema"],
        "State Machine": ["state", "states.inc.php", "gamestate", "transition", "active player", "multiactive"],
        "Notifications": ["notification", "notify", "notif"],
        "UI": ["css", "stylesheet", "html", "template", "dom", "element"],
        "Templates": ["template", "tpl", "jstpl"],
        "JavaScript": ["javascript", ".js", "dojo", "bga."],
        "PHP": [".php", "php ", "function", "class "],
        "Debugging": ["debug", "troubleshooting", "log", "studio log"],
        "Testing": ["test", "testing"],
        "Publishing": ["publish", "release", "deploy", "pre-release"],
        "Utilities": ["tool", "utility", "counter", "stock", "deck"],
        "Configuration": ["config", "option", "preference", "gameoptions", "gamepreferences"],
        "Assets": ["image", "sound", "font", "img", "art", "style"],
        "Internationalization": ["translat", "i18n"],
        "Artificial Intelligence": ["ai", "artificial intelligence", "bot", "zombie"],
    }

    title = page.get("title", "").lower()
    for topic, indicators in topic_indicators.items():
        for indicator in indicators:
            if indicator in title:
                title_score[topic] += 2

    for section in page.get("sections", []):
        heading = section.get("heading")
        if heading:
            heading_text = heading.get("text", "").lower()
            for topic, indicators in topic_indicators.items():
                for indicator in indicators:
                    if indicator in heading_text:
                        heading_score[topic] += 1

        content_text = extract_text_from_content(section.get("content", "")).lower()
        for topic, indicators in topic_indicators.items():
            for indicator in indicators:
                if indicator in content_text:
                    content_score[topic] += 0.5

    all_scores = defaultdict(float)
    for topic in topic_indicators:
        all_scores[topic] = title_score[topic] * 3 + heading_score[topic] * 2 + content_score[topic]

    for topic, score in all_scores.items():
        if score >= 3:
            topics.append(topic)

    if not topics:
        topics = ["Getting Started"]

    return topics


def count_internal_links(links: list) -> int:
    """Count internal links (non-http/https URLs)."""
    count = 0
    for link in links:
        url = link.get("url", "")
        if url and not url.startswith(("http://", "https://")):
            count += 1
    return count


def count_external_links(links: list) -> int:
    """Count external links (http/https URLs)."""
    count = 0
    for link in links:
        url = link.get("url", "")
        if url and url.startswith(("http://", "https://")):
            count += 1
    return count


def count_sections(sections: list) -> int:
    """Count total sections with headings."""
    return sum(1 for s in sections if s.get("heading"))


def build_heading_tree(sections: list) -> list:
    """Build a hierarchical heading tree from flat sections."""
    tree = []
    stack = []

    for section in sections:
        heading = section.get("heading")
        if not heading:
            continue

        level = heading.get("level", 1)
        node = {
            "level": level,
            "text": heading.get("text", ""),
            "id": heading.get("id", ""),
            "children": [],
        }

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        if stack:
            stack[-1]["children"].append(node)
        else:
            tree.append(node)
        stack.append(node)

    return tree


def build_search_entry(page: dict, section: dict, heading: Optional[dict], page_terms: set) -> dict:
    """Build a search index entry for a section."""
    keywords = set()

    page_title = page.get("title", "")
    keywords.update(extract_keywords_from_text(page_title.lower()))

    if heading:
        heading_text = heading.get("text", "")
        keywords.update(extract_keywords_from_text(heading_text.lower()))

    content_text = extract_text_from_content(section.get("content", []))
    keywords.update(extract_keywords_from_text(content_text.lower()))

    for term in page_terms:
        keywords.update(extract_keywords_from_text(term.lower()))

    for item in section.get("content", []):
        if item.get("type") == "code":
            code = item.get("text", "")
            for match in re.findall(r"(this\.bga\.[a-zA-Z]+\.[a-zA-Z]+)", code):
                for word in match.split(".")[1:]:
                    keywords.add(word.lower())
            for match in re.findall(r"\b([A-Za-z]+\.[a-zA-Z]+\.[a-zA-Z]+)\b", code):
                if isinstance(match, tuple):
                    match = match[0]
                for word in match.split(".")[1:]:
                    keywords.add(word.lower())
            for match in re.findall(r"\b([A-Z][a-zA-Z]+)\(\)", code):
                if match not in ("Object", "string", "number", "boolean", "void", "Array"):
                    keywords.add(match.lower())

    relative_path = page.get("relative_path", "")
    if relative_path:
        for match in re.findall(r"\b([A-Z][a-zA-Z]+)\b", relative_path.split(".")[0]):
            keywords.add(match.lower())

    keywords_list = sorted(keywords)[:50]

    anchors = []
    if heading and heading.get("id"):
        anchors.append(heading["id"])

    return {
        "title": page_title,
        "heading": heading.get("text", "") if heading else page_title,
        "keywords": keywords_list,
        "page": page.get("relative_path", ""),
        "section": heading.get("text", "") if heading else "",
        "anchors": anchors,
    }


@dataclass
class Statistics:
    total_pages: int = 0
    total_words: int = 0
    total_headings: int = 0
    total_sections: int = 0
    total_code_blocks: int = 0
    total_tables: int = 0
    total_images: int = 0
    total_links: int = 0
    largest_page: dict = field(default_factory=dict)
    smallest_page: dict = field(default_factory=dict)
    page_sizes: list = field(default_factory=list)


@dataclass
class ValidationResult:
    errors: list = field(default_factory=list)
    pages_indexed: set = field(default_factory=set)
    glossary_entries: set = field(default_factory=set)
    topic_pages: dict = field(default_factory=dict)
    search_pages: set = field(default_factory=set)


def main() -> None:
    """Entry point: build knowledge index from extracted JSON documents."""
    project_root = Path(__file__).parent.resolve()
    content_dir = project_root / CONTENT_JSON_DIR
    output_dir = project_root / KNOWLEDGE_DIR

    logger = setup_logger("knowledge_index", project_root / LOG_FILE)
    start_time = time.time()

    if not content_dir.exists():
        logger.error(f"Input directory not found: {content_dir}")
        sys.exit(1)

    json_files = sorted(content_dir.rglob("*.json"))

    if not json_files:
        logger.error(f"No JSON files found in {content_dir}")
        sys.exit(1)

    master_index = []
    toc = {}
    glossary = {}
    topics_index = defaultdict(list)
    search_index = []
    stats = Statistics()
    validation = ValidationResult()

    stats.total_pages = len(json_files)
    stats.largest_page = {"path": "", "words": 0}
    stats.smallest_page = {"path": "", "words": float("inf")}

    for json_path in json_files:
        try:
            with open(json_path, "r", encoding="utf-8") as fh:
                page = json.load(fh)
        except Exception as exc:
            logger.error(f"Error reading {json_path}: {exc}")
            validation.errors.append({"file": str(json_path), "error": f"Failed to read: {exc}"})
            continue

        relative_path = page.get("relative_path", json_path.stem)

        validation.pages_indexed.add(relative_path)

        word_count = page.get("metadata", {}).get("word_count", 0)
        heading_count = page.get("metadata", {}).get("heading_count", 0)
        code_block_count = page.get("metadata", {}).get("code_block_count", 0)
        table_count = page.get("metadata", {}).get("table_count", 0)
        image_count = page.get("metadata", {}).get("image_count", 0)
        list_count = page.get("metadata", {}).get("list_count", 0)
        section_count = count_sections(page.get("sections", []))
        internal_link_count = count_internal_links(page.get("links", []))
        external_link_count = count_external_links(page.get("links", []))

        headings = [
            {"level": s["heading"]["level"], "text": s["heading"]["text"], "id": s["heading"].get("id", "")}
            for s in page.get("sections", [])
            if s.get("heading")
        ]

        master_entry = {
            "title": page.get("title", ""),
            "relative_path": relative_path,
            "source_file": page.get("source_file", ""),
            "content_json_path": page.get("content_json_path", ""),
            "word_count": word_count,
            "heading_count": heading_count,
            "code_block_count": code_block_count,
            "table_count": table_count,
            "image_count": image_count,
            "list_count": list_count,
            "section_count": section_count,
            "internal_link_count": internal_link_count,
            "external_link_count": external_link_count,
            "headings": headings,
        }
        master_index.append(master_entry)

        toc[relative_path] = build_heading_tree(page.get("sections", []))

        page_terms = extract_page_terms_for_glossary(page)
        for term in page_terms:
            validation.glossary_entries.add(term)
            if term not in glossary:
                glossary[term] = {"term": term, "pages": []}
            glossary[term]["pages"].append({
                "path": relative_path,
                "title": page.get("title", ""),
            })

        page_topics = classify_topics(page)
        for topic in page_topics:
            validation.topic_pages.setdefault(topic, set()).add(relative_path)
            topics_index[topic].append({
                "path": relative_path,
                "title": page.get("title", ""),
            })

        for section in page.get("sections", []):
            heading = section.get("heading")
            search_entry = build_search_entry(page, section, heading, page_terms)
            if search_entry["keywords"]:
                search_index.append(search_entry)
                validation.search_pages.add(relative_path)

        stats.total_words += word_count
        stats.total_headings += heading_count
        stats.total_sections += section_count
        stats.total_code_blocks += code_block_count
        stats.total_tables += table_count
        stats.total_images += image_count
        stats.total_links += len(page.get("links", []))
        stats.page_sizes.append({"path": relative_path, "words": word_count})

        if word_count > stats.largest_page["words"]:
            stats.largest_page = {"path": relative_path, "words": word_count}
        if word_count < stats.smallest_page["words"]:
            stats.smallest_page = {"path": relative_path, "words": word_count}

    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "master_index.json", "w", encoding="utf-8") as f:
        json.dump(master_index, f, indent=2, ensure_ascii=False)

    with open(output_dir / "toc.json", "w", encoding="utf-8") as f:
        json.dump(toc, f, indent=2, ensure_ascii=False)

    sorted_glossary = sorted(glossary.values(), key=lambda x: x["term"].lower())
    with open(output_dir / "glossary.json", "w", encoding="utf-8") as f:
        json.dump(sorted_glossary, f, indent=2, ensure_ascii=False)

    topics_output = {topic: pages for topic, pages in sorted(topics_index.items())}
    with open(output_dir / "topics.json", "w", encoding="utf-8") as f:
        json.dump(topics_output, f, indent=2, ensure_ascii=False)

    with open(output_dir / "search_index.json", "w", encoding="utf-8") as f:
        json.dump(search_index, f, indent=2, ensure_ascii=False)

    page_sizes_sorted = sorted(stats.page_sizes, key=lambda x: x["words"], reverse=True)
    avg_size = stats.total_words / stats.total_pages if stats.total_pages > 0 else 0

    stats_output = {
        "total_pages": stats.total_pages,
        "total_words": stats.total_words,
        "total_headings": stats.total_headings,
        "total_sections": stats.total_sections,
        "total_code_blocks": stats.total_code_blocks,
        "total_tables": stats.total_tables,
        "total_images": stats.total_images,
        "total_links": stats.total_links,
        "largest_page": stats.largest_page,
        "smallest_page": stats.smallest_page,
        "average_page_size": round(avg_size, 2),
        "top_pages_by_size": page_sizes_sorted[:10],
    }

    with open(output_dir / "statistics.json", "w", encoding="utf-8") as f:
        json.dump(stats_output, f, indent=2, ensure_ascii=False)

    validation_errors = []

    duplicate_pages = len(master_index) - len(validation.pages_indexed)
    if duplicate_pages != 0:
        validation_errors.append({"error": f"Duplicate page entries detected: {abs(duplicate_pages)}"})

    duplicate_glossary = len(glossary) - len(validation.glossary_entries)
    if duplicate_glossary != 0:
        validation_errors.append({"error": f"Duplicate glossary entries detected: {abs(duplicate_glossary)}"})

    all_indexed_pages = set(p["relative_path"] for p in master_index)
    for topic, pages in validation.topic_pages.items():
        missing = pages - all_indexed_pages
        if missing:
            validation_errors.append({"error": f"Topic '{topic}' references non-existent pages: {missing}"})

    if validation.search_pages - all_indexed_pages:
        validation_errors.append({
            "error": f"Search index references non-existent pages: {validation.search_pages - all_indexed_pages}"
        })

    for err in validation.errors:
        validation_errors.append(err)

    report_lines = [
        "# Knowledge Index Report",
        "",
        "## Summary",
        "",
        f"- **Pages indexed**: {len(master_index)}",
        f"- **Topics created**: {len(topics_index)}",
        f"- **Glossary entries**: {len(glossary)}",
        f"- **Search entries**: {len(search_index)}",
        "",
        "## Statistics",
        "",
        f"- **Total words**: {stats.total_words}",
        f"- **Total headings**: {stats.total_headings}",
        f"- **Total sections**: {stats.total_sections}",
        f"- **Total code blocks**: {stats.total_code_blocks}",
        f"- **Total tables**: {stats.total_tables}",
        f"- **Total images**: {stats.total_images}",
        f"- **Total links**: {stats.total_links}",
        f"- **Largest page**: {stats.largest_page['path']} ({stats.largest_page['words']} words)",
        f"- **Smallest page**: {stats.smallest_page['path']} ({stats.smallest_page['words']} words)",
        f"- **Average page size**: {avg_size:.2f} words",
        "",
        "## Topics",
        "",
    ]

    for topic in sorted(topics_index.keys()):
        report_lines.append(f"- {topic}: {len(topics_index[topic])} pages")

    report_lines.extend([
        "",
        "## Validation",
        "",
    ])

    if validation_errors:
        report_lines.append("### Errors")
        report_lines.append("")
        for err in validation_errors:
            report_lines.append(f"- {err}")
    else:
        report_lines.append("All validations passed.")

    with open(output_dir / "knowledge_report.md", "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    elapsed = time.time() - start_time

    summary = (
        f"Files processed: {len(json_files)}\n"
        f"Pages indexed: {len(master_index)}\n"
        f"Glossary entries: {len(glossary)}\n"
        f"Search entries: {len(search_index)}\n"
        f"Elapsed time: {elapsed:.2f}s"
    )
    print(summary)

    logger.info(
        json.dumps(
            {
                "status": "completed",
                "files_processed": len(json_files),
                "pages_indexed": len(master_index),
                "glossary_entries": len(glossary),
                "search_entries": len(search_index),
                "errors": len(validation_errors),
                "elapsed_seconds": elapsed,
            }
        )
    )


if __name__ == "__main__":
    main()