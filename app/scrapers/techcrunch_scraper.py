import requests
from bs4 import BeautifulSoup


def scrape_full_article(url: str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed for TechCrunch: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    article_body = (
        soup.find("div", class_="entry-content")
        or soup.find("div", class_="article-content")
        or soup.find("div", class_="wp-block-post-content")
    )

    if not article_body:
        print("Article body not found")
        return None

    for tag in article_body.select(
        "figcaption, .newsletter-signup, .ad-unit, .wp-block-techcrunch-newsletter"
    ):
        tag.decompose()

    paragraphs = article_body.find_all("p")

    text_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text and len(text) > 40:
            text_parts.append(text)

    full_text = "\n\n".join(text_parts)
    return full_text if full_text else None