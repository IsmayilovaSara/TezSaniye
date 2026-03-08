import requests
import feedparser
from scrapers.techcrunch_scraper import scrape_full_article
from firestore_client import initialize_firestore
from datetime import datetime, timezone

# initialize firestore
db = initialize_firestore()

BASE_RSS = "https://techcrunch.com/feed/?paged="

headers = {
    "User-Agent": "Mozilla/5.0"
}

MAX_PAGES = 10   # 10 pages ≈ 200 articles

count = 0

for page in range(1, MAX_PAGES + 1):

    rss_url = BASE_RSS + str(page)

    try:
        response = requests.get(rss_url, headers=headers, timeout=10)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print("RSS request failed:", e)
        break

    print(f"\nPage {page}: Found {len(feed.entries)} articles")

    if len(feed.entries) == 0:
        break

    for entry in feed.entries:

        url = entry.link
        title = entry.title
        summary = entry.summary if hasattr(entry, "summary") else ""

        # check duplicates
        existing = db.collection("raw_articles").where("url", "==", url).limit(1).stream()
        if any(existing):
            print("Already exists:", title)
            continue

        print("Scraping:", title)

        article_text = scrape_full_article(url)

        if not article_text:
            print("Failed:", url)
            continue

        doc = {
            "title": title,
            "url": url,
            "source": "TechCrunch",
            "mode": "global_news",
            "summary": summary,
            "content": article_text,
            "publishedAt": datetime.now(timezone.utc),
            "scrapedAt": datetime.now(timezone.utc),
            "processed": False
        }

        db.collection("raw_articles").add(doc)

        count += 1
        print("Saved:", title)

print(f"\nFinished. Inserted {count} articles.")