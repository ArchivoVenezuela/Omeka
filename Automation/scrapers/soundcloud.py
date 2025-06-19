import requests
from bs4 import BeautifulSoup
import urllib.parse

def scrape_soundcloud(query, max_results=10):
    search_url = f"https://soundcloud.com/search/sounds?q={urllib.parse.quote_plus(query)}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(search_url, headers=headers)

    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]
        title = a_tag.get_text(strip=True)

        # Only collect links that look like tracks (avoid /search, /users etc.)
        if "/search" in href or not title or len(href.strip("/").split("/")) != 2:
            continue

        # Clean any weird Unicode characters
        try:
            cleaned_title = title.encode('latin1').decode('utf-8')
        except:
            cleaned_title = title.encode('ascii', 'ignore').decode()

        results.append({
            "title": cleaned_title,
            "author": "",  # not available without deeper scraping
            "description": "",
            "url": f"https://soundcloud.com{href}"
        })

        if len(results) >= max_results:
            break

    return results
