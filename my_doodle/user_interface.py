import requests

from dearpygui.dearpygui import *

def exit_app():
    stop_dearpygui()


def update_album_art():
    playback = sp.current_playback()
    if playback and playback['item']:
        url = playback['item']['album']['images'][0]['url']
        response = requests.get(url)
        with open("album_art.jpg", "wb") as f:
            f.write(response.content)

        # Refresh the texture
        if does_item_exist("album_art_texture"):
            delete_item("album_art_texture")
        add_image("album_art_texture", "album_art.jpg", width=300, height=300)


def get_user_input():
    return get_value("artist_input")


def resize_ui(sender, app_data):
    set_item_width("main_window", get_viewport_client_width())
    set_item_height("main_window", get_viewport_client_height())

def build_ui(search_callback):
    create_context()
    with window(label="Bass Doodle", tag="main_window", no_title_bar=True, no_resize=True, no_move=True):
        with child_window(tag="main_content", autosize_x=True, autosize_y=True, border=False):
            add_spacer(height=20)
            add_text("Time to Quiz", color=[255, 255, 0])
            add_spacer(height=10)

            add_input_text(label="Artist", tag="artist_input", width=-1)
            add_button(label="Search and Play", callback=lambda s, a, u: search_callback(), tag="search_button", width=-1)

            add_spacer(height=50)
            add_button(label="Exit", callback=exit_app)        
            # add_input_text(label="Artist", tag="artist_input", width=-1)  # -1 means fill available width
            # add_button(label="Search and Play", width=-1)
    create_viewport(title="Bass Doodle", width=-1, height=-1)
    setup_dearpygui()
    maximize_viewport()

    # Resize the main window to match the viewport
    set_item_width("main_window", get_viewport_client_width())
    set_item_height("main_window", get_viewport_client_height())

    # Register the resize_ui
    set_viewport_resize_callback(resize_ui)

    show_viewport()
    start_dearpygui()
    destroy_context()
