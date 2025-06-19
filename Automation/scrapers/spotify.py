import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def scrape_spotify(query, max_results=10):
    client_id = "72599d0bb0464d58a9589d07255e26fc"
    client_secret = "535f167abe4b4f9597fee146d621d8c4"

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
