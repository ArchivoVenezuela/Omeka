import requests

def scrape_youtube_api(query, api_key, max_results=10):
    search_url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "key": api_key,
        "type": "video",
        "maxResults": max_results,
        "safeSearch": "moderate"
    }

    response = requests.get(search_url, params=params)
    if response.status_code != 200:
        print(f"Error {response.status_code}: {response.text}")
        return []

    data = response.json()
    videos = []

    for item in data.get("items", []):
        snippet = item["snippet"]
        video_id = item["id"]["videoId"]
        videos.append({
            "title": snippet["title"],
            "author": snippet["channelTitle"],
            "description": snippet["description"],
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return videos
