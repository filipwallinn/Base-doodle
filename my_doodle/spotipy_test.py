import spotipy
import os
from spotipy.oauth2 import *

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
))

artist_id = "36QJpDe2go2KgaRleHCDTp"  # Led Zeppelin
results = sp.artist_top_tracks(artist_id)

top_track = results['tracks'][0]  # Most popular
track_uri = top_track['uri']
print("Now playing:", top_track['name'])

sp.start_playback(uris=[track_uri])

devices = sp.devices()
print(devices)



# lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

# spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
# results = spotify.artist_top_tracks(lz_uri)

# for track in results['tracks'][:10]:
#     print('track    : ' + track['name'])

#     if track['preview_url']:
#         print('audio    : ' + track['preview_url'])
#     else:
#         print('audio    : [No preview available]')        

#     print('cover art: ' + track['album']['images'][0]['url'])
#     print()