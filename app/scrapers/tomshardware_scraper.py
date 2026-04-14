import requests
from bs4 import BeautifulSoup


def scrape_full_article(url: str) -> str | None:
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        r = requests.get(url, headers=headers, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"Tom's Hardware request failed: {e}")
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    container = soup.find("div", class_="text-copy") or soup.find("article")

    if not container:
        print("Tom's Hardware container not found")
        return None

    for tag in container.select("script, style, figure, aside"):
        tag.decompose()

    paragraphs = container.find_all("p")

    return "\n\n".join(
        p.get_text(" ", strip=True)
        for p in paragraphs
        if p.get_text(strip=True) and len(p.get_text(strip=True)) > 30
    )