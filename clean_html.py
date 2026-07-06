import hashlib
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from bs4 import BeautifulSoup

SOURCE_DIR = Path("source-html")
OUTPUT_DIR = Path("clean-html")
LOG_FILE = Path("logs/clean.log")


def setup_logger():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("clean")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if logger.handlers:
        logger.handlers.clear()
    
    file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(
        logging.Formatter('{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}', 
                         datefmt="%Y-%m-%dT%H:%M:%S%z")
    )
    logger.addHandler(file_handler)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(stream_handler)
    
    return logger


def get_article_title(soup):
    title_span = soup.find("span", class_="mw-page-title-main")
    if title_span:
        return title_span.get_text(strip=True)
    title_tag = soup.find("title")
    if title_tag:
        return title_tag.get_text(strip=True)
    return "Untitled"


def get_article_content(soup):
    content_div = soup.find("div", {"id": "mw-content-text"})
    if content_div:
        parser_output = content_div.find("div", class_="mw-parser-output")
        if parser_output:
            return parser_output
    return None


def remove_mediawiki_chrome(soup):
    elements_to_remove = [
        "mw-page-base", "mw-head-base", "siteNotice", "mw-indicators",
        "siteSub", "contentSub", "contentSub2", "jump-to-nav",
        "mw-jump-link", "mw-panel", "footer", "footer-info",
        "footer-places", "footer-icons",
    ]
    
    for element_id in elements_to_remove:
        for elem in soup.find_all(id=element_id):
            elem.decompose()
    
    for elem in soup.find_all(attrs={"data-mw": True}):
        elem.decompose()
    
    nav_ids = ["p-navigation", "p-tb", "p-search", "p-logo"]
    for nav_id in nav_ids:
        for elem in soup.find_all(id=nav_id):
            elem.decompose()
    
    for elem in soup.find_all(class_="vector-menu"):
        elem.decompose()
    
    for elem in soup.find_all("form", id="searchform"):
        elem.decompose()
    
    for elem in soup.find_all("script"):
        elem.decompose()
    
    for elem in soup.find_all("link", rel=["EditURI", "search", "canonical", "icon"]):
        elem.decompose()
    
    for elem in soup.find_all(class_="studio-framework-navigation"):
        elem.decompose()
    
    for elem in soup.find_all(attrs={"role": ["search", "navigation", "banner"]}):
        elem.decompose()
    
    for elem in soup.find_all(class_="noprint"):
        elem.decompose()
    
    return soup


def rewrite_internal_links(soup, html_files):
    links_rewritten = 0
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.startswith("/"):
            path = unquote(href.lstrip("/"))
            path = path.split("?")[0]
            if path.endswith("/"):
                path = path[:-1]
            if path and not path.startswith(("api.php", "Special:", "Help")):
                candidate = f"{path}.html"
                if candidate in html_files:
                    a["href"] = candidate
                    links_rewritten += 1
    return links_rewritten


def count_images(soup):
    return len(soup.find_all("img"))


def count_word_stats(soup):
    text = soup.get_text(separator=" ")
    words = [w for w in text.split() if w.strip()]
    return len(words)


def count_code_blocks(soup):
    return len(soup.find_all("pre"))


def count_tables(soup):
    return len(soup.find_all("table"))


def count_headings(soup):
    return len(soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]))


def produce_clean_html(html_path, output_path, html_files, logger):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    title = get_article_title(soup)
    content_div = get_article_content(soup)
    
    if not content_div:
        logger.error(json.dumps({"page": html_path.name, "error": "No article content found"}))
        return None, 0, 0, None, None, 0, 0, 0, 0
    
    sha256_raw = hashlib.sha256(str(content_div).encode("utf-8")).hexdigest()
    
    clean_soup = remove_mediawiki_chrome(soup)
    
    if clean_soup.find("head"):
        head = clean_soup.find("head")
        for child in list(head.children):
            if child.name not in ["title", "meta"]:
                child.decompose()
        for elem in clean_soup.find_all("meta", content=lambda c: c and "MediaWiki" in c):
            elem.decompose()
    
    if clean_soup.find("body"):
        body = clean_soup.find("body")
        body_classes_to_remove = []
        for class_name in body.get("class", []):
            if "mediawiki" in class_name or "skin-" in class_name or "vector-" in class_name:
                body_classes_to_remove.append(class_name)
        for cls in body_classes_to_remove:
            body["class"].remove(cls)
        if not body.get("class"):
            del body["class"]
    
    article_div = clean_soup.new_tag("div", **{"class": "article"})
    for element in content_div.children:
        if element.name:
            article_div.append(element)
    
    if clean_soup.find("body"):
        clean_soup.find("body").clear()
        clean_soup.find("body").append(article_div)
    
    images_count = count_images(clean_soup)
    links_rewritten = rewrite_internal_links(clean_soup, html_files)
    sha256_clean = hashlib.sha256(str(article_div).encode("utf-8")).hexdigest()
    
    word_count = count_word_stats(clean_soup)
    code_block_count = count_code_blocks(clean_soup)
    table_count = count_tables(clean_soup)
    heading_count = count_headings(clean_soup)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(str(clean_soup))
    
    return title, images_count, links_rewritten, sha256_raw, sha256_clean, word_count, code_block_count, table_count, heading_count


def main():
    logger = setup_logger()
    start_time = time.time()
    
    html_files = {f.name for f in SOURCE_DIR.glob("*.html")}
    
    meta_files = list(SOURCE_DIR.glob("*.meta.json"))
    pages_data = []
    for meta_path in meta_files:
        with open(meta_path, "r", encoding="utf-8") as f:
            pages_data.append(json.load(f))
    
    pages_data.sort(key=lambda x: x.get("title", ""))
    
    succeeded = 0
    failed = 0
    total_images = 0
    total_links = 0
    total_output_size = 0
    
    for page_data in pages_data:
        html_filename = page_data.get("html_filename", "")
        source_path = SOURCE_DIR / html_filename
        if not source_path.exists():
            continue
        
        output_path = OUTPUT_DIR / html_filename
        meta_output_path = OUTPUT_DIR / f"{source_path.stem}.meta.json"
        
        result = produce_clean_html(source_path, output_path, html_files, logger)
        if len(result) == 9:
            title, images, links, sha256_raw, sha256_clean, word_count, code_block_count, table_count, heading_count = result
        else:
            failed += 1
            continue
        
        if title is None:
            failed += 1
            continue
        
        succeeded += 1
        total_images += images
        total_links += links
        
        if output_path.exists():
            total_output_size += output_path.stat().st_size
        
        clean_meta = {
            "title": page_data.get("title", title),
            "source_html": html_filename,
            "clean_html": html_filename,
            "url": page_data.get("url", ""),
            "depth": page_data.get("depth", 0),
            "sha256_raw": sha256_raw,
            "sha256_clean": sha256_clean,
            "word_count": word_count,
            "code_block_count": code_block_count,
            "table_count": table_count,
            "image_count": images,
            "heading_count": heading_count,
            "cleaned_at": datetime.now(timezone.utc).isoformat(),
        }
        with open(meta_output_path, "w", encoding="utf-8") as f:
            json.dump(clean_meta, f, indent=2)
    
    elapsed = time.time() - start_time
    avg_size = total_output_size / succeeded if succeeded > 0 else 0
    
    report = f"""# Clean HTML Report

Pages processed: {len(pages_data)}
Succeeded: {succeeded}
Failed: {failed}
Images preserved: {total_images}
Links rewritten: {total_links}
Average output size: {avg_size:.0f} bytes
Elapsed time: {elapsed:.2f}s
"""
    
    with open("clean_report.md", "w", encoding="utf-8") as f:
        f.write(report)
    
    logger.info(json.dumps({
        "status": "completed",
        "pages_processed": len(pages_data),
        "succeeded": succeeded,
        "failed": failed,
        "elapsed_seconds": elapsed,
    }))


if __name__ == "__main__":
    main()