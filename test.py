from PIL import Image
from dearpygui.dearpygui import *
import os

# Hardcoded path to your image
image_path = r"C:\Users\walli\repo\bass_doodle\resources\default.jpg"

# Load and convert image
image = Image.open(image_path).convert("RGBA")
width, height = image.size
data = [channel for pixel in image.getdata() for channel in pixel]

# Start GUI
create_context()

with texture_registry():
    add_static_texture(width, height, data, tag="album_art_texture")

with window(label="Test Window"):
    add_image(texture_tag="album_art_texture")

create_viewport(title="Image Test", width=400, height=400)
setup_dearpygui()
show_viewport()
start_dearpygui()
destroy_context()
