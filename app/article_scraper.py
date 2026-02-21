import requests
from bs4 import BeautifulSoup


def scrape_full_article(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Engadget articles usually have paragraphs inside <p> tags
    paragraphs = soup.find_all("p")

    text_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if text:
            text_parts.append(text)

    full_text = "\n\n".join(text_parts)

    return full_text if full_text else None