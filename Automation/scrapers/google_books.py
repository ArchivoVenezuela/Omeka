import requests

def scrape_google_books(query, max_results=10):
    url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    books = []
    for item in response.json().get("items", []):
        info = item.get("volumeInfo", {})

        books.append({
            "title": info.get("title", "Untitled"),
            "author": ", ".join(info.get("authors", [])),
            "description": info.get("description", ""),
            "url": info.get("infoLink", "")
        })

    return books
