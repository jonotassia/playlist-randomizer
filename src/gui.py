from src.scheme import Scheme
from src.playlist import Playlist
from src.helper import PathManager

import PySimpleGUI as sg
import subprocess
from pathlib import Path


class Interface:
    def __init__(self):
        self.scheme: Scheme = Scheme("Blank")
        self.playlist: Playlist = Playlist()
        self.show: Path = Path()

    # --------------------- Main Layout ----------------------------
    @property
    def main_layout(self):
        layout = [
            [
                sg.Frame('Playlist', self.playlist_phase_1, size=(350, 800), expand_x=True, key="-PLAYLIST-"),
                sg.VSeparator(),
                sg.Frame('Scheme', self.scheme_phase_1, size=(350, 800), expand_x=True, key="-SCHEME-"),
                sg.VSeparator(),
                sg.Frame('Shows', self.show_phase_1, size=(350, 800), expand_x=True, key="-SHOWS-")
            ]
        ]

        return layout

    @property
    def layout(self):
        # Once the TV_PATH has been entered, add the remaining frames
        layout = [
            [
                sg.Text("TV/Movie Directory: "),
                sg.In(default_text=PathManager.TV_PATH, size=(25, 1), enable_events=True, key="-TV_PATH-"),
                sg.FolderBrowse(),
                sg.Button("Confirm", size=(25, 1), enable_events=True, key="-CONFIRM_TV_PATH-")
            ],
            [
                sg.Frame("", layout=[[]], key="-MAIN-")
            ]
        ]
        return layout

    # --------------------- Playlist Layout ----------------------------
    @property
    def playlist_phase_1(self):
        return [[sg.Button("Generate Playlist", size=(25, 1), key="-GEN_PLAYLIST-")]]

    @property
    def playlist_phase_2(self):
        column_layout = [
            [
                sg.Text("VLC Path: "),
                sg.In(default_text=PathManager.VLC_PATH, size=(25, 1), enable_events=True, key="-VLC_PATH-"),
                sg.FolderBrowse()
            ],
            [
                sg.Text("Max Duration of Playlist: "),
                sg.In(size=(25, 1), default_text="200", enable_events=True, key="-PL_DURATION-"),
            ],
            [
                sg.Text("Scheme: ")
            ],
            [
                sg.Listbox(values=self.get_schemes(), size=(40, 5), enable_events=True,
                           horizontal_scroll=True,  key="-PL_SCHEME_PATH-")
            ],
            [
                sg.Button("Confirm", size=(25, 1), enable_events=True, key="-PL_CONFIRM_PLAYLIST-"),
            ]
        ]

        return column_layout

    @property
    def playlist_phase_3(self):
        playlist = [vid.stem for vid in self.playlist.video_queue]

        column_layout = [
                [
                    sg.Text("Playlist: ")
                ],
                [
                    sg.Listbox(values=playlist, size=(40, 20), horizontal_scroll=True, disabled=False, key="-VIEW_PLAYLIST-")
                ],
                [
                    sg.Button("Launch VLC", enable_events=True, size=(10, 1), key="-LAUNCH_VLC-")
                ]
            ]

        return column_layout

    # --------------------- Scheme Layout ----------------------------
    @property
    def scheme_phase_1(self):
        return [[sg.Button("Modify Scheme", size=(25, 1), key="-MOD_SCHEME-")]]

    @property
    def scheme_phase_2(self):
        column_layout = [
            [
                sg.Button("New Scheme", enable_events=True, size=(10, 1), key="-NEW_SCHEME-"),
                sg.Button("Load Scheme", enable_events=True, size=(10, 1), key="-LOAD_SCHEME-")
            ]
        ]

        return column_layout

    @property
    def scheme_phase_3_new(self):
        column_layout = [
            [
                sg.Text("Scheme Name: "),
                sg.In(size=(25, 1), enable_events=True, key="-NEW_SCHEME_NAME-"),
            ],
            [
                sg.Button("Confirm", size=(20, 1), enable_events=True, key="-CONFIRM_NEW_SCHEME-")
            ]
        ]

        return column_layout

    @property
    def scheme_phase_3_load(self):
        column_layout = [
            [
                sg.Text("Scheme: ")
            ],
            [
                sg.Listbox(values=self.get_schemes(), size=(40, 5), enable_events=True,
                           horizontal_scroll=True, key="-LOAD_SCHEME_NAME-"),
            ],
            [
                sg.Button("Confirm", size=(20, 1), enable_events=True, key="-CONFIRM_LOAD_SCHEME-")
            ]
        ]

        return column_layout

    @property
    def scheme_phase_4(self):
        column_layout = [
            [
                self.import_scheme()
            ],
            [
                sg.Button("Save Scheme", enable_events=True, size=(10, 1), key="-SAVE_SCHEME-"),
                sg.Button("Discard", enable_events=True, size=(10, 1), key="-DISCARD_SCHEME-")
            ]
        ]

        return column_layout

    # --------------------- Show Layout ----------------------------
    @property
    def show_phase_1(self):
        return [[sg.Button("Update Show Marker", size=(25, 1), key="-UPDATE_SHOW-")]]

    @property
    def show_phase_2(self):
        # Loop through shows in tv directory. Add to list unless .scheme folder or not directory
        column_layout = [
            [
                sg.Text("Select a show/movie: ")
            ],
            [
                sg.Listbox(values=self.get_shows(), enable_events=True, size=(40, 20),
                           horizontal_scroll=True, key="-SELECT_SHOW-")
            ],
            [
                sg.Button("Clear All Markers", size=(20, 1), enable_events=True, button_color="red",
                          key="-CLEAR_MARKERS-")
            ]
        ]

        return column_layout

    @property
    def show_phase_3(self):
        # Get default value for episode
        try:
            episode = self.playlist.get_current_episode(self.show)
            episode_text = episode.stem
        except:
            episode = Path()
            episode_text = ""

        column_layout = [
            [
                sg.Text("Select an Episode: ")
            ],
            [
                sg.In(episode_text, size=(35, 10), enable_events=True, key=f"-SELECT_EPISODE-"),
                sg.FileBrowse(initial_folder=episode.parent, key="-EPISODE_SEARCH-")
            ],
            [
                sg.Button("Save Changes", size=(10, 1), key="-SAVE_SHOW-"),
                sg.Button("Discard", size=(10, 1), key="-DISCARD_SHOW-")
            ]
        ]

        return column_layout

    # ---------------------------- Additional Methods --------------------------
    @staticmethod
    def get_schemes() -> list:
        return [scheme.stem for scheme in PathManager.TV_PATH.joinpath(".scheme").glob("*.csv")]

    @staticmethod
    def get_shows() -> list:
        return [show.stem for show in PathManager.TV_PATH.iterdir() if show.is_dir() and show.stem != ".scheme"]

    def get_episodes(self) -> list:
        return [episode.stem for episode in PathManager.TV_PATH.joinpath(self.show).glob("*[!.txt]")]

    def import_scheme(self) -> sg.Column:
        """
        Pulls the show and associated frequency for row line in the scheme. This is sorted by index
        :return: Column for use in scheme_layout column
        """
        # Get shows and frequencies
        show_data = [[sg.Text("Frequency"), sg.Text("Show/Movie")]]
        show_data += [[sg.In(size=(10, 1), default_text=v["frequency"], enable_events=True, key=f"-SCHEME_FREQ_{k}-"),
                      sg.Text(v["show_path"], key=f"-SCHEME_SHOW_{k}-")]
                      for k, v in self.scheme.data.to_dict(orient="index").items()]

        # Merge into a list of list, then return as column
        return sg.Column(show_data, size=(290, 400), scrollable=True, key=f"-SCHEME_DETAILS-{self.scheme.title.upper()}-")

    @staticmethod
    def error_message(text: str):
        """
        Used to generate an error window if something is entered incorrectly
        :param text: Error message to display to user
        :return: None
        """
        window = sg.Window("Error", layout=[[sg.Text(text, text_color="red")]])

        while True:
            event, values = window.read()
            # End programme if user closes window
            if event == sg.WIN_CLOSED:
                break

        window.close()

    @staticmethod
    def success_message(text: str, key: str) -> sg.Text:
        """
        Used to generate an error window if something is entered incorrectly
        :param text: Error message to display to user
        :param key: A key for finding in the PySimpleGUI window
        :return: None
        """
        return sg.Text(text, text_color="green", key=key)

    @staticmethod
    def confirm_popup(text: str):
        """
        Creates a pop-up window for user to confirm action
        :param text: Message to display to user
        :return: Returns true if yes is clicked and false if no
        """
        window = sg.Window("Error", layout=[
            [
                sg.Text(text)
            ],
            [
                sg.Button("Yes", button_color="green", key="-YES-"),
                sg.Button("No", button_color="red", key="-NO-")
            ]
        ])

        while True:
            event, values = window.read()
            # End programme if user closes window
            if event == sg.WIN_CLOSED:
                break

            if event == "-YES-":
                window.close()
                return True

            if event == "-NO-":
                break

        window.close()

        return False

    def run_playlist(self):
        """
        Set VLC path, then loads and plays a playlist.
        """
        # Create list of videos from playlist, beginning with the path to the VLC executable.
        vlc_process_cmd: list = [PathManager.VLC_PATH.as_posix()]

        # Add videos from playlist. IMPORTANT: Paths of videos must be URI
        while self.playlist.video_queue:
            vlc_process_cmd.append(self.playlist.dequeue_playlist().absolute().as_uri())

        # Create subprocess
        p = subprocess.Popen(vlc_process_cmd)

    @staticmethod
    def move_center(window):
        screen_width, screen_height = window.get_screen_dimensions()
        win_width, win_height = window.size
        x, y = (screen_width - win_width) // 2, (screen_height - win_height) // 2
        window.move(x, y)


if __name__ == "__main__":
    pass
