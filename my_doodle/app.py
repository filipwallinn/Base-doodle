from flask import *
from spotipy_logic import get_album_art, play_song
from flask_cors import CORS
import os

app = Flask(__name__, static_folder="../front_doodle", static_url_path="/")
CORS(app)

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/album-art")
def album_art():
    artist = request.args.get("artist")
    image_path = get_album_art(artist)
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

if __name__ == "__main__":
    app.run(debug=True)
