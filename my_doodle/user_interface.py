from dearpygui.dearpygui import *

# def start_app():
#     print("Starting the app...")

# def open_settings():
#     print("Opening settings...")

def exit_app():
    stop_dearpygui()

# Callback function triggered when the button is clicked
def handle_input(sender, app_data, user_data):
    user_text = get_value("artist_input")
    print(f"User typed: {user_text}")
    # You can now use `user_text` to search Spotify or do anything else

# Create a simple window with input and button
# with window(label="Search Artist", width=400, height=200):
#     add_input_text(label="Enter artist name", tag="artist_input", width=300)
#     add_button(label="Search and Play", callback=handle_input)

# start_dearpygui()


# Create context
create_context()

with window(label="Bass Doodle", width=600, height=400):

#    add_child_window(autosize_x=True, autosize_y=True, border=False)

    add_spacer(height=20)
    add_text("Time to Quiz", color=[255, 255, 0])
    add_spacer(height=10)

    add_input_text(label="Enter artist name", tag="artist_input", width=300)
    add_button(label="Search and Play", callback=handle_input)

    # add_button(label="Start", callback=start_app)
    # add_button(label="Settings", callback=open_settings)

    add_spacer(height=20)
    add_text("Made for my Jules <3", wrap=0)

    add_spacer(height=50)
    add_button(label="Exit", callback=exit_app)


# Setup and show viewport
create_viewport(title='Bass Doodle', width=600, height=400)
setup_dearpygui()
show_viewport()
start_dearpygui()
destroy_context()
