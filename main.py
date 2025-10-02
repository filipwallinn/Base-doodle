from imports import *
from my_doodle.spotipy_logic import *
from my_doodle.user_interface import *

def play_song_after_input():
    artist_name = get_user_input()
    artist_id = spotify_search(artist_name)
    if artist_id:
        play_artists_top_song(artist_id)

build_ui(search_callback=play_song_after_input)