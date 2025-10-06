from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
import os

sp = Spotify(auth_manager=SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

playlist_id = "6e93dfkUqpQ5AMw7L6FNkt"
results = sp.playlist_items(playlist_id, limit=5)
for item in results['items']:
    print(item['track']['album']['images'][0]['url'])
