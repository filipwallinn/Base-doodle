from dearpygui.dearpygui import *

def start_app():
    print("Starting the app...")

def open_settings():
    print("Opening settings...")

def exit_app():
    stop_dearpygui()

# Create context
create_context()

with window(label="Bass Doodle", width=600, height=400):

    add_child_window(autosize_x=True, autosize_y=True, border=False)

    add_spacer(height=20)
    add_text("Time to Quiz", color=[255, 255, 0])
    add_spacer(height=10)
    
    add_button(label="Start", callback=start_app)
    add_button(label="Settings", callback=open_settings)
    add_button(label="Exit", callback=exit_app)

    add_spacer(height=20)
    add_text("Made for my Jules <3", wrap=0)

# Setup and show viewport
create_viewport(title='Bass Doodle', width=600, height=400)
setup_dearpygui()
show_viewport()
start_dearpygui()
destroy_context()
