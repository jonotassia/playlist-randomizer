from src.playlist import Playlist
from src.helper import PathManager
from src.gui import Interface

import subprocess
import PySimpleGUI as sg
from pathlib import Path

def run_playlist():
    """
    Set VLC path, then loads and plays a playlist.
    """
    # Set VLC path. If it fails, return to prompt.
    if not PathManager.set_vlc_path():
        return

    playlist = Playlist()

    # # Prompt user for scheme name, and if not blank, generate spec
    scheme_name = input("Please provide a scheme name: ")

    if not scheme_name:
        return

    playlist.generate_playlist(scheme_name, 200)

    # Create list of videos from playlist, beginning with the path to the VLC executable.
    vlc_process_cmd: list = [PathManager.VLC_PATH.as_posix()]

    # Add videos from playlist. IMPORTANT: Paths of videos must be URI
    while playlist.video_queue:
        vlc_process_cmd.append(playlist.dequeue_playlist().absolute().as_uri())

    # Create subprocess
    p = subprocess.Popen(vlc_process_cmd)


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

        if event == "-TV_PATH-":
            tv_path = Path(values["-TV_PATH-"])
            if tv_path.exists():
                PathManager.TV_PATH = tv_path
                interface.main_phase = 2
                window.extend_layout(window["-MAIN-"], interface.main_layout)
            else:

                interface.error_message("Invalid Path")

        window.refresh()

    window.close()

    # Save any paths that have been changed during programme run
    PathManager.save_paths()
