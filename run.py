from classes.playlist import Playlist
from classes.helper import PathManager
import subprocess
import vlc


if __name__ == "__main__":
    while True:
        selection = input("Select an option: \n"
                          "   1) Load Playlist\n"
                          "   2) Modify Scheme\n"
                          "\n"
                          "Selection: ")

        # Load Playlist
        if selection == "1":
            # Set VLC path. If it fails, return to prompt.
            if not PathManager.set_vlc_path():
                continue

            playlist = Playlist()

            # # Prompt user for scheme name, and if not blank, generate spec
            scheme_name = input("Please provide a scheme name: ")

            if not scheme_name:
                continue

            playlist.generate_playlist(scheme_name, 200)

            # Create list of videos from playlist, beginning with the path to the VLC executable.
            vlc_process_cmd: list = [PathManager.VLC_PATH.as_posix()]

            # Add videos from playlist. IMPORTANT: Paths of videos must be URI
            while playlist.video_queue:
                vlc_process_cmd.append(playlist.dequeue_playlist().absolute().as_uri())

            # Create subprocess
            p = subprocess.Popen(vlc_process_cmd)

        elif selection == "2":
            pass

        if not selection:
            quit(0)
