import feedparser
import requests

def fetch_rss(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    feed = feedparser.parse(response.content)

    print("Feed status:", feed.status if hasattr(feed, "status") else "No status")
    print("Feed entries length:", len(feed.entries))
    print("Feed bozo:", feed.bozo)

    return feed.entries