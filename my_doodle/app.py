from flask import Flask, render_template, request, jsonify, send_file
from spotipy_logic import *
from flask_cors import CORS
import os
import logging
from logging.handlers import RotatingFileHandler
import sys

# Create logs directory if it doesn't exist
if not os.path.exists("logs"):
    os.makedirs("logs")

# Redirect stdout and stderr to log files
sys.stdout = open("logs/stdout.log", "a")
sys.stderr = open("logs/stderr.log", "a")

# Initialize Flask app
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Set up logging
log_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=3)
log_handler.setLevel(logging.INFO)
app.logger.addHandler(log_handler)

# Routes for HTML pages
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/classic-quiz")
def classic_quiz():
    return render_template("quiz.html")

# Static image route
@app.route("/album-art")
def album_art():
    image_path = os.path.join(app.static_folder, "resources", "album_art.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(app.static_folder, "resources", "default.jpg")
    return send_file(image_path, mimetype="image/jpeg")

@app.route("/default-image")
def default_image():
    image_path = os.path.join(app.static_folder, "resources", "default.jpg")
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
    return jsonify({"isPlaying": bool(playback and playback['is_playing'])})

@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    query = data.get("query")
    search_type = data.get("type", "track")
    return jsonify(search_spotify(query, search_type))

if __name__ == "__main__":
    app.run(debug=True)