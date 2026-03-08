from firestore_client import initialize_firestore
from rss_fetcher import fetch_rss
from duplicate_checker import article_exists
from scrapers.engadget_scraper import scrape_full_article
from config import SOURCES
from datetime import datetime, timezone
import time


def convert_rss_date(entry):
    """
    Converts RSS published_parsed to timezone-aware datetime.
    Falls back to None if not available.
    """
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        dt = datetime.fromtimestamp(
            time.mktime(entry.published_parsed),
            tz=timezone.utc
        )
        return dt
    return None


def process_source(db, source):
    print(f"\n🔎 Processing source: {source['name']}")

    entries = fetch_rss(source["rss_url"])
    print(f"Found {len(entries)} articles")

    for entry in entries[:50]:  # keep limit during testing
        url = entry.link
        title = entry.title
        summary = entry.summary if hasattr(entry, "summary") else None

        if article_exists(db, url):
            print(f"⏩ Skipping duplicate: {title}")
            continue

        try:
            full_content = scrape_full_article(url)
        except Exception as e:
            print(f"❌ Failed scraping article body: {title}")
            print(e)
            full_content = None

        published_at = convert_rss_date(entry)

        db.collection("raw_articles").add({
            "title": title,
            "url": url,
            "source": source["name"],
            "summary": summary,
            "publishedAt": published_at,
            "scrapedAt": datetime.now(timezone.utc),
            "processed": False,
            "mode": source["mode"],
            "content": full_content
        })

        print(f"✅ Inserted: {title}")


def main():
    db = initialize_firestore()

    for source in SOURCES:
        process_source(db, source)


if __name__ == "__main__":
    main()