from dearpygui.dearpygui import *

def start_app():
    print("Starting the app...")

def open_settings():
    print("Opening settings...")

def exit_app():
    stop_dearpygui()

with window(label="Main Menu", width=400, height=300):
    add_spacer(height=20)
    add_text("🎮 Welcome to My App", color=[255, 255, 0], bullet=False)
    add_spacer(height=10)
    
    add_button(label="Start", callback=start_app)
    add_button(label="Settings", callback=open_settings)
    add_button(label="Exit", callback=exit_app)

    add_spacer(height=20)
    add_text("Made with ❤️ in DearPyGui", wrap=300)

start_dearpygui()
