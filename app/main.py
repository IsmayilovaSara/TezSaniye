from datetime import datetime, timezone
import hashlib
import time

from firestore_client import initialize_firestore
from rss_fetcher import fetch_rss
from duplicate_checker import article_exists
from config import SOURCES

from scrapers.engadget_scraper import scrape_full_article as scrape_engadget
from scrapers.techcrunch_scraper import scrape_full_article as scrape_techcrunch
from scrapers.wired_scraper import scrape_full_article as scrape_wired
from scrapers.arstechnica_scraper import scrape_full_article as scrape_arstechnica
from scrapers.theregister_scraper import scrape_full_article as scrape_theregister
from scrapers.techradar_scraper import scrape_full_article as scrape_techradar
from scrapers.gizmodo_scraper import scrape_full_article as scrape_gizmodo
from scrapers.mittechreview_scraper import scrape_full_article as scrape_mittech
from scrapers.infoq_scraper import scrape_full_article as scrape_infoq
from scrapers.venturebeat_scraper import scrape_full_article as scrape_venturebeat
from scrapers.zdnet_scraper import scrape_full_article as scrape_zdnet
from scrapers.thenextweb_scraper import scrape_full_article as scrape_tnw


SCRAPER_MAP = {
    "Engadget": scrape_engadget,
    "TechCrunch": scrape_techcrunch,
    "WIRED": scrape_wired,
    "Ars Technica": scrape_arstechnica,
    "The Register": scrape_theregister,
    "TechRadar": scrape_techradar,
    "Gizmodo": scrape_gizmodo,
    "MIT Tech Review": scrape_mittech,
    "InfoQ": scrape_infoq,
    "VentureBeat": scrape_venturebeat,
    "ZDNet": scrape_zdnet,
    "The Next Web": scrape_tnw,
}

def count_articles(db):
    docs = db.collection("raw_articles").stream()
    count = sum(1 for _ in docs)
    print(f"\n📊 Total articles stored: {count}")


def convert_rss_date(entry):
    """
    Convert RSS published_parsed to a timezone-aware datetime.
    Return None if the field is missing.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        return datetime.fromtimestamp(
            time.mktime(entry.published_parsed),
            tz=timezone.utc
        )
    return None


def generate_content_hash(content: str | None) -> str | None:
    """
    Generate SHA-256 hash for article content.
    Return None if content is empty.
    """
    if not content:
        return None
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def process_source(db, source):
    print(f"\n🔎 Processing source: {source['name']}")

    entries = fetch_rss(source["rss_url"])
    print(f"Found {len(entries)} articles")

    scraper_func = SCRAPER_MAP.get(source["name"])
    if not scraper_func:
        print(f"❌ No scraper configured for source: {source['name']}")
        return

    for entry in entries[:100]:
        url = getattr(entry, "link", None)
        title = getattr(entry, "title", None)
        snippet = getattr(entry, "summary", None)

        if not url or not title:
            print("⏩ Skipping entry with missing title or URL")
            continue

        if article_exists(db, url):
            print(f"⏩ Skipping duplicate: {title}")
            continue

        try:
            full_content = scraper_func(url)
        except Exception as e:
            print(f"❌ Failed scraping article body: {title}")
            print(e)
            full_content = None

        published_at = convert_rss_date(entry)
        content_hash = generate_content_hash(full_content)

        raw_article_data = {
            "title": title,
            "url": url,
            "publisher": source["name"],
            "published_at": published_at,
            "snippet": snippet,
            "content": full_content,
            "topic": source.get("topic", ""),
            "category": source.get("category", ""),
            "source_type": source.get("source_type", "rss"),
            "content_hash": content_hash,
            "ingested_at": datetime.now(timezone.utc),
            "processed": False,
        }

        db.collection("raw_articles").add(raw_article_data)
        print(f"✅ Inserted: {title}")


def main():
    db = initialize_firestore()

    for source in SOURCES:
        try:
            process_source(db, source)
        except Exception as e:
            print(f"❌ Failed source: {source['name']}")
            print(e)
            continue

    count_articles(db)


if __name__ == "__main__":
    main()