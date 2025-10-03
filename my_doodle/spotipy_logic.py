import os
import requests
from PIL import Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = os.path.join(BASE_DIR, "resources")
os.makedirs(RESOURCES_PATH, exist_ok=True)

sp = Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    cache_path=os.path.join(BASE_DIR, "token_cache.txt")
))

def save_album_art(image_url):
    image_path = os.path.join(RESOURCES_PATH, "album_art.jpg")
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        with open(image_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        print(f"Failed to download album art: {e}")

def get_album_art(artist):
    playback = sp.current_playback()
    if playback and playback['item']:
        url = playback['item']['album']['images'][0]['url']
        save_album_art(url)
        return os.path.join(RESOURCES_PATH, "album_art.jpg")
    return os.path.join(RESOURCES_PATH, "default.jpg")

def spotify_search(user_search):
    search_result = sp.search(q=user_search, type='artist', limit=1)
    artist_items = search_result.get('artists', {}).get('items', [])
    if artist_items:
        return artist_items[0]['id']
    else:
        print("No artist found.")
        return None

def play_artists_top_song(artist_id):
    results = sp.artist_top_tracks(artist_id)
    if not results['tracks']:
        print("No top tracks found.")
        return None

    top_track = results['tracks'][0]
    track_uri = top_track['uri']

    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
        sp.transfer_playback(device_id, force_play=True)
        sp.start_playback(device_id=device_id, uris=[track_uri])
        return top_track['name']
    else:
        print("No active Spotify devices found.")
        return None

def play_song_by_artist(artist_name):
    artist_id = spotify_search(artist_name)
    if not artist_id:
        return {"status": "error", "message": "Artist not found"}

    top_tracks = sp.artist_top_tracks(artist_id)
    if not top_tracks['tracks']:
        return {"status": "error", "message": "No top tracks found"}

    track = top_tracks['tracks'][0]
    track_uri = track['uri']

    devices = sp.devices()
    if not devices['devices']:
        return {"status": "error", "message": "No active Spotify devices found"}

    device_id = devices['devices'][0]['id']
    sp.transfer_playback(device_id, force_play=True)
    sp.start_playback(device_id=device_id, uris=[track_uri])

    save_album_art(track['album']['images'][0]['url'])

    return {
        "status": "playing",
        "artist": artist_name,
        "track": track['name']
    }

def play_song_by_name(song_name):
    search_result = sp.search(q=song_name, type='track', limit=1)
    tracks = search_result.get('tracks', {}).get('items', [])

    if not tracks:
        return {"status": "error", "message": "Song not found"}

    track = tracks[0]
    track_uri = track['uri']

    devices = sp.devices()
    if not devices['devices']:
        return {"status": "error", "message": "No active Spotify devices found"}

    device_id = devices['devices'][0]['id']
    sp.transfer_playback(device_id, force_play=True)
    sp.start_playback(device_id=device_id, uris=[track_uri])

    save_album_art(track['album']['images'][0]['url'])

    return {
        "status": "playing",
        "track": track['name'],
        "artist": track['artists'][0]['name']
    }

def update_album_art():
    playback = sp.current_playback()
    if playback and playback['item']:
        url = playback['item']['album']['images'][0]['url']
        save_album_art(url)
    else:
        print("No playback detected. Skipping album art update.")

def pause_playback():
    sp.pause_playback()

def resume_playback():
    sp.start_playback()

def search_spotify(query, search_type="track", limit=10):
    results = sp.search(q=query, type=search_type, limit=limit)
    items = results.get(search_type + "s", {}).get("items", [])
    
    if not items:
        return []

    if search_type == "track":
        return [{
            "name": item["name"],
            "artist": item["artists"][0]["name"],
            "album": item["album"]["name"],
            "uri": item["uri"],
            "duration_ms": item["duration_ms"]
        } for item in items]

    # You can expand this for albums, artists, etc.
    return items
