from src.playlist import Playlist
from src.scheme import Scheme
from src.helper import PathManager
from src.gui import Interface

import subprocess
import PySimpleGUI as sg
from pathlib import Path


if __name__ == "__main__":
    # Get TV_PATH and VLC_PATH from file
    PathManager.load_paths()
    PathManager.set_vlc_path()

    interface = Interface()

    # Create window
    window = sg.Window("Playlist Randomizer", interface.layout, margins=(40, 20))

    # Create event loop
    while True:
        event, values = window.read(timeout=1000)
        # End programme if user closes window
        if event == sg.WIN_CLOSED:
            break

        # --------------- Main Layout Event Checks -----------------------

        # If TV_PATH entered, validate and set TV_PATH variable in PathManager. Otherwise, throw error.
        if event == "-TV_PATH-":
            tv_path = Path(values["-TV_PATH-"])
            try:
                if tv_path.exists():
                    PathManager.TV_PATH = tv_path
                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # If the Confirm button is pressed, double-check the tv path in case the user kept the default value
        if event == "-CONFIRM_TV_PATH-":
            tv_path = Path(values["-TV_PATH-"])
            try:
                if tv_path.exists():
                    PathManager.TV_PATH = tv_path
                    window.extend_layout(window["-MAIN-"], interface.main_layout)
                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # --------------- Playlist Layout Event Checks -----------------------

        # If Generate Playlist pressed, cascade related sections
        if event == "-GEN_PLAYLIST-":
            window.extend_layout(window["-PLAYLIST-"], interface.playlist_phase_2)

        # If VLC_PATH entered, validate and set VLC_PATH variable in PathManager. Otherwise, throw error.
        if event == "-VLC_PATH-":
            vlc_path = Path(values["-VLC_PATH-"])
            try:
                if vlc_path.exists():
                    PathManager.VLC_PATH = vlc_path
                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # Verify the duration entered is an int before adding it to the playlist
        if event == "-PL_DURATION-":
            duration = values["-PL_DURATION-"]
            try:
                interface.playlist.max_length = int(duration)
            except ValueError:
                interface.error_message("Please enter a number.")

        # If Playlist Scheme selected, load the scheme and assign to the Interface
        if event == "-PL_SCHEME_PATH-":
            try:
                interface.scheme = Scheme.load_playlist_scheme(values["-PL_SCHEME_PATH-"][0])
            except FileNotFoundError:
                interface.error_message("Invalid Scheme.")

        # Display the current playlist to the user
        if event == "-PL_CONFIRM_PLAYLIST-":
            if values["-VLC_PATH-"] and values["-PL_DURATION-"] and values["-PL_SCHEME_PATH-"]:
                interface.playlist.generate_playlist(interface.scheme)
                window.extend_layout(window["-PLAYLIST-"], interface.playlist_phase_3)

        # Launch VLC with the current playlist
        if event == "-LAUNCH_VLC-":
            interface.run_playlist()
            break

        # --------------- Scheme Layout Event Checks -----------------------

        # --------------- Show Layout Event Checks -----------------------

        window.refresh()

    window.close()

    # Save any paths that have been changed during programme run
    PathManager.save_paths()
