import requests
from bs4 import BeautifulSoup

def scrape_goodreads(query):
    url = f"https://www.goodreads.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "lxml")
    results = []

    rows = soup.select(".tableList tr")
    for row in rows:
        title_tag = row.select_one(".bookTitle")
        author_tag = row.select_one(".authorName")

        if not title_tag or not author_tag:
            continue

        title = title_tag.get_text(strip=True)
        author = author_tag.get_text(strip=True)
        link = "https://www.goodreads.com" + title_tag.get("href")

        results.append({
            "title": title,
            "author": author,
            "description": "",  # Description isn't available in search page
            "url": link
        })

    return results
