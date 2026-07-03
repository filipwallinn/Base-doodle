import os
import requests
from PIL import Image
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
import logging
import time

# Create resources directory if it doesn't exist
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_PATH = os.path.join(BASE_DIR, "resources")
os.makedirs(RESOURCES_PATH, exist_ok=True)

load_dotenv(os.path.join(os.path.dirname(BASE_DIR), ".env"))

# Initialize Spotify client
sp = Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI", "http://127.0.0.1:8888/callback"),
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    cache_path=os.path.join(BASE_DIR, "token_cache.txt")
))

# Public Spotify client for fetching new releases
public_sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
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
    search_result = sp.search(q=user_search, type='artist', limit=2)
    artist_items = search_result.get('artists', {}).get('items', [])

    for artist in artist_items:
        if artist['name'].lower() == user_search.lower():
            return artist['id']

    # fallback to first result if no exact match
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

def _get_target_device_id():
    """Prefer the currently active device; fall back to the first available one."""
    devices = sp.devices().get('devices', [])
    if not devices:
        return None
    active = next((d for d in devices if d.get('is_active')), None)
    return (active or devices[0])['id']

def _play_uris_on_device(uris):
    """Transfer playback to a target device and start the given URIs.

    Spotify's transfer_playback is asynchronous, so calling start_playback
    immediately after it is a known race condition: the device may still be
    mid-transfer and silently ignore the new URIs, leaving the previous
    track playing. A short delay avoids that.
    """
    device_id = _get_target_device_id()
    if not device_id:
        return {"status": "error", "message": "No active Spotify devices found"}

    sp.transfer_playback(device_id, force_play=True)
    time.sleep(0.8)
    sp.start_playback(device_id=device_id, uris=uris)
    return {"status": "playing"}

def play_song_by_artist(artist_name):
    artist_id = spotify_search(artist_name)
    if not artist_id:
        return {"status": "error", "message": "Artist not found"}

    top_tracks = sp.artist_top_tracks(artist_id)
    if not top_tracks['tracks']:
        return {"status": "error", "message": "No top tracks found"}

    track = top_tracks['tracks'][0]

    result = _play_uris_on_device([track['uri']])
    if result["status"] != "playing":
        return result

    save_album_art(track['album']['images'][0]['url'])

    return {
        "status": "playing",
        "artist": artist_name,
        "track": track['name']
    }

def play_song_by_name(song_name):
    # Spotify's search endpoint has a known caching bug where limit=1 can
    # return an unrelated cached result regardless of the query. Requesting
    # more results and taking the first one avoids it.
    search_result = sp.search(q=song_name, type='track', limit=3)
    tracks = search_result.get('tracks', {}).get('items', [])

    if not tracks:
        return {"status": "error", "message": "Song not found"}

    track = tracks[0]

    result = _play_uris_on_device([track['uri']])
    if result["status"] != "playing":
        return result

    save_album_art(track['album']['images'][0]['url'])

    return {
        "status": "playing",
        "track": track['name'],
        "artist": track['artists'][0]['name']
    }


def play_song_by_uri(uris):
    logger = logging.getLogger(__name__)
    logger.info(f"Playing song with URI: {uris}")

    result = _play_uris_on_device(uris)
    if result["status"] != "playing":
        return result

    # Wait briefly to let Spotify update playback state
    time.sleep(1.5)  # 1.5 seconds is usually enough

    playback = sp.current_playback()
    if playback and playback['item']:
        image_url = playback['item']['album']['images'][0]['url']
        save_album_art(image_url)

    return {"status": "playing", "uris": uris}


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

def search_spotify(query, search_type="track", limit=50):
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

_cached_playlist_ids = {}

def find_playlist_id(query="classic rock"):
    """
    Searches Spotify for a playlist matching the query and returns its ID.
    """
    try:
        results = public_sp.search(q=query, type="playlist", limit=3)
        print("Raw playlist search result:", results)  # 👈 Debug print

        playlists = results.get('playlists')
        if not playlists:
            print(f"No 'playlists' key found in search results for query: {query}")
            return None

        items = playlists.get('items')
        if not items:
            print(f"No playlist items found for query: {query}")
            return None

        playlist = items[0]
        print(f"✅ Found playlist: {playlist['name']} (ID: {playlist['id']})")
        return playlist['id']
    except Exception as e:
        print(f"Error finding playlist: {e}")
        return None

    
# def get_album_cover_urls(limit=25):
#     try:
#         # Left: new releases
#         new_releases = public_sp.new_releases(limit=limit)
#         left_covers = [album['images'][0]['url'] for album in new_releases['albums']['items'] if album['images']]

#         # Right: classic playlist
#         classic_playlist_id = find_playlist_id("classic rock")
#         right_covers = get_classic_album_covers(classic_playlist_id, limit=limit) if classic_playlist_id else []

#         return {
#             "left": left_covers,
#             "right": right_covers
#         }
#     except Exception as e:
#         print(f"Error fetching album covers: {e}")
#         return {"left": [], "right": []}

def get_album_cover_urls(limit=25):
    try:
        # Left: new releases
        new_releases = public_sp.new_releases(limit=limit)
        left_covers = [album['images'][0]['url'] for album in new_releases['albums']['items'] if album['images']]

        # Right: hardcoded classic playlist
        classic_playlist_id = "6e93dfkUqpQ5AMw7L6FNkt"  # All Out 80s
        right_covers = get_classic_album_covers(classic_playlist_id, limit=limit)

        print(f"Left covers: {len(left_covers)}, Right covers: {len(right_covers)}")
        return {
            "left": left_covers,
            "right": right_covers
        }
    except Exception as e:
        print(f"Error fetching album covers: {e}")
        return {"left": [], "right": []}

def get_classic_album_covers(playlist_id, limit=25):
    try:
        playlist_data = public_sp.playlist_items(
            playlist_id,
            limit=limit,
            fields="items(track(album(images)))"
        )
        covers = []

        for item in playlist_data['items']:
            track = item.get('track')
            if track and track['album']['images']:
                covers.append(track['album']['images'][0]['url'])

        print(f"Fetched {len(covers)} classic album covers.")
        return covers
    except Exception as e:
        print(f"Error fetching classic album covers: {e}")
        return []