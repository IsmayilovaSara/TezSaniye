import requests
from bs4 import BeautifulSoup


def scrape_full_article(url: str) -> str | None:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed for MIT Tech Review: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    container = (
        soup.find("div", class_="articleBody__content")
        or soup.find("div", class_="contentBody")
        or soup.find("div", class_="body")
        or soup.find("article")
        or soup.find("main")
    )

    if not container:
        print("MIT Tech Review article container not found")
        return None

    for tag in container.select(
        "script, style, noscript, figure, figcaption, aside, svg"
    ):
        tag.decompose()

    paragraphs = container.find_all("p")

    text_parts = []
    for p in paragraphs:
        text = p.get_text(" ", strip=True)

        if not text:
            continue
        if len(text) < 30:
            continue

        text_parts.append(text)

    full_text = "\n\n".join(text_parts)
    return full_text if full_text else None