import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def scrape_spotify(query, max_results=10):
    client_id = "your_spotify_client_id"
    client_secret = "your_spotify_client_secret"

    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(auth_manager=auth_manager)

    results = sp.search(q=query, limit=max_results, type="track")

    tracks = []
    for item in results["tracks"]["items"]:
        name = item["name"]
        artist = item["artists"][0]["name"]
        url = item["external_urls"]["spotify"]

        tracks.append({
            "title": name,
            "author": artist,
            "description": "",
            "url": url
        })

    return tracks
