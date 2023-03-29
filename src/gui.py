from src.scheme import Scheme
from src.playlist import Playlist
from src.helper import PathManager

import PySimpleGUI as sg


class Interface:
    def __init__(self):
        self.scheme: Scheme = Scheme("Blank")
        self.playlist: Playlist = Playlist()

        # Playlist Layouts
        self.playlist_phase: int = 3
        self._playlist_layout: sg.Column
        self._playlist_phase_1: sg.Column
        self._playlist_phase_2: sg.Column
        self._playlist_phase_3: sg.Column

        # Scheme Layouts
        self.scheme_phase: int = 4
        self._scheme_layout: sg.Column
        self._scheme_phase_1: sg.Column
        self._scheme_phase_2: sg.Column
        self._scheme_phase_3: sg.Column
        self._scheme_phase_4: sg.Column

        # Show Layouts
        self.show_phase: int = 3
        self._show_layout: sg.Column
        self._show_phase_1: sg.Column
        self._show_phase_2: sg.Column
        self._show_phase_3: sg.Column

    @property
    def playlist_phase_1(self):
        return sg.Column([[sg.Button("Generate Playlist", size=(25, 1), key="-GEN_PLAYLIST-")]])

    @property
    def playlist_phase_2(self):
        column_layout = [
            [
                sg.Text("VLC Path: "),
                sg.In(default_text=PathManager.VLC_PATH, size=(25, 1), enable_events=True, key="-VLC_PATH-"),
                sg.FolderBrowse()
            ],
            [
                sg.Text("Scheme Path: "),
                sg.In(size=(25, 1), enable_events=True, key="-PL_SCHEME_PATH-"),
                sg.FolderBrowse()
            ],
            [
                sg.Text("Duration of Playlist: "),
                sg.In(size=(25, 1), enable_events=True, key="-DURATION-"),
            ]
        ]
        # If the playlist column phase is set to 2 or higher, show this section
        is_visible = True if self.playlist_phase >= 2 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def playlist_phase_3(self):
        playlist = [vid.as_posix() for vid in self.playlist.video_queue]

        column_layout = [
                [
                    sg.Text("Playlist: "),
                    sg.Listbox(values=playlist, enable_events=True, size=(40, 20), key="-PLAYLIST-")
                ],
                [
                    sg.Button("Launch VLC", enable_events=True, size=(10, 1), key="-LAUNCH_VLC-")
                ]
            ]

        # If the playlist column phase is set to 3 or higher, show this section
        is_visible = True if self.playlist_phase >= 3 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def playlist_layout(self):
        layout = [
            [
                self.playlist_phase_1
            ],
            [
                self.playlist_phase_2
            ],
            [
                self.playlist_phase_3
            ]
        ]
        return layout

    @property
    def scheme_phase_1(self):
        return sg.Column([[sg.Button("Modify Scheme", size=(25, 1), key="-MOD_SCHEME-")]])

    @property
    def scheme_phase_2(self):
        column_layout = [
            [
                sg.Button("New Scheme", enable_events=True, size=(10, 1), key="-NEW_SCHEME-"),
                sg.Button("Load Scheme", enable_events=True, size=(10, 1), key="-LOAD_SCHEME-")
            ]
        ]
        # If the playlist column phase is set to 2 or higher, show this section
        is_visible = True if self.scheme_phase >= 2 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def scheme_phase_3(self):
        column_layout = [
            [
                sg.Text("Scheme Path: "),
                sg.In(size=(25, 1), enable_events=True, key="-SCHEME_PATH-"),
                sg.FolderBrowse()
            ]
        ]
        # If the playlist column phase is set to 3 or higher, show this section
        is_visible = True if self.scheme_phase >= 3 else False

        return sg.Column(column_layout, visible=is_visible)

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
        # If the playlist column phase is set to 4 or higher, show this section
        is_visible = True if self.scheme_phase >= 4 else False

        return sg.Column(column_layout, visible=is_visible)

    def import_scheme(self) -> sg.Column:
        """
        Pulls the show and associated frequency for row line in the scheme
        :param scheme: Scheme to pull shows and frequencies from
        :return: Column for use in scheme_layout column
        """
        # Get shows and frequencies
        shows = [sg.Checkbox(show) for show in self.scheme.data["show_path"]]
        freqs = [sg.In(size=(10, 1), default_text=freq) for freq in self.scheme.data["frequency"]]

        # Merge into a list of list, then return as column
        show_select_column = [list(element) for element in zip(shows, freqs)]
        return sg.Column(show_select_column, scrollable=True)

    @property
    def scheme_layout(self):
        layout = [
            [
                self.scheme_phase_1
            ],
            [
                self.scheme_phase_2
            ],
            [
                self.scheme_phase_3
            ],
            [
                self.scheme_phase_4
            ]
        ]
        return layout

    @property
    def show_phase_1(self):
        return sg.Column([[sg.Button("Update Show Marker", size=(25, 1), key="-UPDATE_SHOW-")]])

    @property
    def show_phase_2(self):
        # Loop through shows in tv directory. Add to list unless .scheme folder or not directory
        shows = [show.stem for show in PathManager.TV_PATH.iterdir() if show.is_dir() and show.stem != ".scheme"]

        column_layout = [
            [
                sg.Text("Select a show/movie: "),
                sg.Listbox(values=shows, enable_events=True, size=(40, 20), key="-SELECT_SHOW-")
            ]
        ]
        # If the playlist column phase is set to 2 or higher, show this section
        is_visible = True if self.show_phase >= 2 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def show_phase_3(self):
        column_layout = [
            [
                sg.Text("Select an Episode: "),
                sg.In(size=(25, 1), enable_events=True, key="-SELECT_EPISODE-"),
                sg.FolderBrowse()
            ],
            [
                sg.Button("Save Changes", size=(25, 1), key="-SAVE_SHOW-"),
                sg.Button("Discard", size=(25, 1), key="-DISC_SHOW-")
            ]
        ]
        # If the playlist column phase is set to 3 or higher, show this section
        is_visible = True if self.show_phase >= 3 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def show_layout(self):
        layout = [
            [
                self.show_phase_1
            ],
            [
                self.show_phase_2
            ],
            [
                self.show_phase_3
            ]
        ]
        return layout

    @property
    def layout(self):
        layout = [
            [
                sg.Text("TV/Movie Directory: "),
                sg.In(default_text=PathManager.TV_PATH, size=(25, 1), enable_events=True, key="-TV_PATH-"),
                sg.FolderBrowse()
            ]
        ]

        # Once the TV_PATH has been entered, add the remaining frames
        if PathManager.TV_PATH:
            layout.append([
                sg.Frame('Playlist', self.playlist_layout),
                sg.VSeparator(),
                sg.Frame('Scheme', self.scheme_layout),
                sg.VSeparator(),
                sg.Frame('Shows', self.show_layout)
            ])

        return layout


if __name__ == "__main__":
    pass
