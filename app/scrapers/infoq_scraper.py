import requests
from bs4 import BeautifulSoup


def scrape_full_article(url: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
    except Exception as e:
        print(f"Request failed for InfoQ: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    container = (
        soup.find("div", class_="article__content")
        or soup.find("div", class_="article_content")
        or soup.find("article")
    )

    if not container:
        print("InfoQ container not found")
        return None

    for tag in container.select("script, style, noscript, figure, aside"):
        tag.decompose()

    paragraphs = container.find_all("p")

    text = "\n\n".join(
        p.get_text(" ", strip=True)
        for p in paragraphs
        if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30
    )

    return text if text else None