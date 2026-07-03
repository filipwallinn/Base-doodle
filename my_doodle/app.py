from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from spotipy_logic import *
from flask_cors import CORS
from spotipy.exceptions import SpotifyException
from spotipy.oauth2 import SpotifyOauthError
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")

# Create logs directory if it doesn't exist
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Set up logging
log_handler = RotatingFileHandler(os.path.join(LOGS_DIR, "app.log"), maxBytes=1000000, backupCount=3)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

@app.errorhandler(SpotifyOauthError)
def handle_oauth_error(e):
    app.logger.error(f"Spotify OAuth error: {e}")
    return jsonify({
        "status": "error",
        "message": "Couldn't connect to Spotify. Open this app in your browser and log in "
                    "when Spotify's authorization page appears, then try again."
    })

@app.errorhandler(SpotifyException)
def handle_spotify_error(e):
    app.logger.error(f"Spotify API error: {e}")
    reason = (e.reason or "").upper()
    msg_lower = (e.msg or "").lower()

    if "PREMIUM" in reason or "premium" in msg_lower:
        message = "This action requires Spotify Premium."
    elif e.http_status == 404 or "NO_ACTIVE_DEVICE" in reason:
        message = "No active Spotify device found. Open Spotify on a device first."
    else:
        message = f"Spotify error: {e.msg} ({e.reason})"
    return jsonify({"status": "error", "message": message})

# Routes for HTML pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/classic-quiz")
def classic_quiz():
    return render_template("quiz.html")

@app.route("/profile-shuffle")
def profile_shuffle():
    return render_template("profile_shuffle.html")

@app.route("/music-trivia")
def music_trivia():
    return render_template("music_trivia.html")

@app.route("/finish-the-lyric")
def finish_the_lyric():
    return render_template("finish_the_lyric.html")

@app.route("/album-art-challenge")
def album_art_challenge():
    return render_template("album_art.html")

@app.route("/mystery-artist")
def mystery_artist():
    return render_template("mystery_artist.html")

# Route to serve album art images
@app.route("/album-art")
def show_album_art():
    image_path = os.path.join("resources", "album_art.jpg")
    return send_file(image_path, mimetype="image/jpeg")

# Route to serve default image
@app.route("/default-image")
def default_image():
    image_path = os.path.join(app.static_folder, "images", "default.jpg")
    return send_file(image_path, mimetype="image/jpeg")

# Spotify-related API routes
@app.route("/play-artist", methods=["POST"])
def play_artist():
    data = request.get_json()
    artist_name = data.get("artist")
    return jsonify(play_song_by_artist(artist_name))

@app.route("/play-song", methods=["POST"])
def play_song():
    data = request.get_json()
    song_uris = data.get("uris")
    return jsonify(play_song_by_uri(song_uris))

@app.route("/play-song-by-name", methods=["POST"])
def play_song_by_name_route():
    data = request.get_json()
    song_name = data.get("song")
    return jsonify(play_song_by_name(song_name))

@app.route("/pause", methods=["POST"])
def pause():
    sp.pause_playback()
    return jsonify({"status": "paused"})

@app.route("/resume", methods=["POST"])
def resume():
    sp.start_playback()
    return jsonify({"status": "resumed"})

@app.route("/hint")
def hint():
    playback = sp.current_playback()
    if playback and playback['item']:
        track = playback['item']
        album = track['album']['name']
        release_year = track['album']['release_date'][:4]
        hint = f"The song is from the album '{album}' released in {release_year}."
        return jsonify({"hint": hint})
    return jsonify({"hint": "No song is currently playing."})

@app.route("/playback-status")
def playback_status():
    playback = sp.current_playback()
    if not playback or not playback.get("item"):
        return jsonify({"isPlaying": False, "track": None, "artist": None})

    return jsonify({
        "isPlaying": bool(playback["is_playing"]),
        "track": playback["item"]["name"],
        "artist": playback["item"]["artists"][0]["name"]
    })

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    search_type = data.get("type", "track")
    return jsonify(search_spotify(query, search_type))

# New route to fetch album cover URLs
@app.route("/album-covers")
def album_covers():
    covers = get_album_cover_urls()
    app.logger.info(f"Album covers fetched: left={len(covers['left'])}, right={len(covers['right'])}")
    return jsonify(covers)


# Health check route
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# Run the app
if __name__ == "__main__":
    app.run(debug=True)