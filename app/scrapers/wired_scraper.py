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
        print(f"Request failed for WIRED: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Try likely article containers first
    article_body = (
        soup.find("div", attrs={"data-testid": "BodyWrapper"})
        or soup.find("div", class_="body__inner-container")
        or soup.find("div", class_="article__body")
        or soup.find("article")
        or soup.find("main")
    )

    if not article_body:
        print("WIRED article body not found")
        return None

    # Remove clearly unwanted elements if present
    for tag in article_body.select(
        "aside, figure, figcaption, script, style, noscript, "
        ".newsletter, .paywall-bar, .related-list, .caption, .ad"
    ):
        tag.decompose()

    paragraphs = article_body.find_all("p")

    text_parts = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)

        # Skip obvious non-content fragments
        if not text:
            continue
        if text.lower() in {"advertisement", "read more", "comments"}:
            continue
        if len(text) < 30:
            continue

        text_parts.append(text)

    full_text = "\n\n".join(text_parts)
    return full_text if full_text else None