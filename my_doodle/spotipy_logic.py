import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    cache_path=r'C:\Users\walli\repo\bass_doodle\my_doodle\token_cache.txt'
))

def play_artists_top_song(artist_ID):
    results = sp.artist_top_tracks(artist_ID)
    top_track = results['tracks'][0]
    track_uri = top_track['uri']
#    print("Now playing:", top_track['name'])
    devices = sp.devices()
    if devices['devices']:
        device_id = devices['devices'][0]['id']
        sp.transfer_playback(device_id, force_play=True)
        sp.start_playback(uris=[track_uri])
    else:
        print("No active Spotify devices found.")


def spotify_search(user_search):
    search_result = sp.search(q=user_search, type='artist')
    artist_items = search_result['artists']['items']
    if artist_items:
        return artist_items[0]['id']
    else:
        print("No artist found.")
        return None

def get_current_album_art_url():
    playback = sp.current_playback()
    if playback and playback['item']:
        return playback['item']['album']['images'][0]['url']
    return None

