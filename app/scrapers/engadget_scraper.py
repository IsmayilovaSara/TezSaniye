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
        print(f"Request failed for Engadget: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = soup.find_all("p")

    text_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            text_parts.append(text)

    full_text = "\n\n".join(text_parts)
    return full_text if full_text else None