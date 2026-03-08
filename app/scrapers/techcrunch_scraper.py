import requests
from bs4 import BeautifulSoup


def scrape_full_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # TechCrunch sometimes uses different containers
    article_body = (
        soup.find("div", class_="entry-content")
        or soup.find("div", class_="article-content")
        or soup.find("div", class_="wp-block-post-content")
    )

    if not article_body:
        print("Article body not found")
        return None

    # Remove unwanted elements
    for tag in article_body.select(
        "figcaption, .newsletter-signup, .ad-unit, .wp-block-techcrunch-newsletter"
    ):
        tag.decompose()

    paragraphs = article_body.find_all("p")

    text_parts = []

    for p in paragraphs:
        text = p.get_text(strip=True)

        # Skip very short promotional fragments
        if text and len(text) > 40:
            text_parts.append(text)

    full_text = "\n\n".join(text_parts)

    return full_text if full_text else None