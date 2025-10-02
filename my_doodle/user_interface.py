import requests
import spotipy
import os
from PIL import Image
from spotipy.oauth2 import SpotifyOAuth
from dearpygui.dearpygui import *

# Spotify setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    scope="user-modify-playback-state,user-read-playback-state",
    redirect_uri="http://127.0.0.1:8888/callback",
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
    cache_path=r'C:\Users\walli\repo\bass_doodle\my_doodle\token_cache.txt'
))

# Paths
BASE_DIR = r"C:\Users\walli\repo\bass_doodle"
RESOURCES_PATH = os.path.join(BASE_DIR, "resources")

# Exit button
def exit_app():
    stop_dearpygui()

# Get user input
def get_user_input():
    return get_value("artist_input")

# Resize UI on viewport change
def resize_ui(sender, app_data):
    set_item_width("main_window", get_viewport_client_width())
    set_item_height("main_window", get_viewport_client_height())

# Show default image before GUI starts
def show_default_album_art():
    image_path = os.path.join(RESOURCES_PATH, "default.jpg")
    if not os.path.exists(image_path):
        print("Default image not found:", image_path)
        return

    image = Image.open(image_path).convert("RGBA")
    width, height = image.size
    data = [channel for pixel in image.getdata() for channel in pixel]

    configure_item("album_art_texture", width=width, height=height, default_value=data)

    if not does_item_exist("album_art_widget"):
        add_image(texture_tag="album_art_texture", tag="album_art_widget", parent="album_art_container")

    print("Default album art loaded.")

# Build UI
def build_ui(search_callback):
    create_context()

    with texture_registry(tag="texture_registry"):
        add_static_texture(1, 1, [255, 255, 255, 255], tag="album_art_texture")

    with window(label="Bass Doodle", tag="main_window", no_title_bar=True, no_resize=True, no_move=True):
        with child_window(tag="main_content", autosize_x=True, autosize_y=True, border=False):
            add_spacer(height=20)
            add_text("Time to Quiz", color=[255, 255, 0])
            add_spacer(height=10)
            add_input_text(label="Artist", tag="artist_input", width=-1)
            add_button(label="Search and Play", callback=lambda s, a, u: search_callback(), tag="search_button", width=-1)
            add_spacer(height=50)
            add_button(label="Exit", callback=exit_app)

        with child_window(tag="album_art_container", width=300, height=300):
            add_text("Album art will appear here", tag="album_art_placeholder")

    # ✅ Show default image BEFORE viewport is shown
    show_default_album_art()

    create_viewport(title="Bass Doodle", width=-1, height=-1)
    setup_dearpygui()
    maximize_viewport()

    set_item_width("main_window", get_viewport_client_width())
    set_item_height("main_window", get_viewport_client_height())
    set_viewport_resize_callback(resize_ui)

    show_viewport()

    set_frame_callback(get_frame_count() + 1, refresh_loop)

    start_dearpygui()
    destroy_context()

# Update album art from Spotify
def update_album_art():
    playback = sp.current_playback()
    if playback and playback['item']:
        url = playback['item']['album']['images'][0]['url']
        os.makedirs(RESOURCES_PATH, exist_ok=True)

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to download album art: {e}")
            return

        image_path = os.path.join(RESOURCES_PATH, "album_art.jpg")
        with open(image_path, "wb") as f:
            f.write(response.content)

        image = Image.open(image_path).convert("RGBA")
        width, height = image.size
        data = [channel for pixel in image.getdata() for channel in pixel]

        configure_item("album_art_texture", width=width, height=height, default_value=data)

        if not does_item_exist("album_art_widget"):
            add_image(texture_tag="album_art_texture", tag="album_art_widget", parent="album_art_container")

        print("Working directory:", os.getcwd())
    else:
        print("No playback detected. Skipping album art update.")

# Refresh loop
def refresh_loop():
    update_album_art()
    set_frame_callback(get_frame_count() + 300, refresh_loop)  # ~5 seconds at 60 FPS
