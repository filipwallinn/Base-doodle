from flask import *
from spotipy_logic import *
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../front_doodle", static_url_path="/")
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/album-art")
def album_art():
    image_path = os.path.join(os.path.dirname(__file__), "resources", "album_art.jpg")
    if not os.path.exists(image_path):
        image_path = os.path.join(os.path.dirname(__file__), "resources", "default.jpg")
    return send_file(image_path, mimetype="image/jpeg")


@app.route("/play", methods=["POST"])
def play():
    artist = request.json.get("artist")
    result = play_song(artist)
    return jsonify(result)

@app.route("/default-image")
def default_image():
    image_path = os.path.join(os.path.dirname(__file__), "resources", "default.jpg")
    return send_file(image_path, mimetype="image/jpeg")

@app.route("/pause", methods=["POST"])
def pause():
    sp.pause_playback()
    return jsonify({"status": "paused"})

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

if __name__ == "__main__":
    app.run(debug=True)
