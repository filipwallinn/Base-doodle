import spotipy
import os
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

def play_artists_top_song(artist_ID):
    results = sp.artist_top_tracks(artist_ID)
    top_track = results['tracks'][0]
    track_uri = top_track['uri']
    print("Now playing:", top_track['name'])
    sp.start_playback(uris=[track_uri])

def spotify_search(user_search):
    search_result = sp.search(q=user_search, type='artist')
    artist_items = search_result['artists']['items']
    if artist_items:
        return artist_items[0]['id']
    else:
        print("No artist found.")
        return None

def search_and_play_top_song(artist_search)
    artist_id = spotify_search(artist_search)
    if artist_id:
        play_artists_top_song(artist_id)
