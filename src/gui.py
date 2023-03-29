import PySimpleGUI as sg


class Interface:
    def __init__(self):
        # Playlist Layouts
        self.playlist_phase: int = 1
        self._playlist_layout: sg.Column
        self._playlist_phase_1: sg.Column
        self._playlist_phase_2: sg.Column
        self._playlist_phase_3: sg.Column

        # Scheme Layouts
        self.scheme_phase: int = 1
        self._scheme_layout: sg.Column
        self._scheme_phase_1: sg.Column
        self._scheme_phase_2: sg.Column
        self._scheme_phase_3: sg.Column
        self._scheme_phase_4: sg.Column

        # Show Layouts
        self.show_phase: int = 1
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
                sg.In(size=(25, 1), enable_events=True, key="-VLC_PATH-"),
                sg.FolderBrowse()
            ],
            [
                sg.Text("Scheme Path: "),
                sg.In(size=(25, 1), enable_events=True, key="-PL_SCHEME_PATH-"),
                sg.FolderBrowse()
            ]
        ]
        # If the playlist column phase is set to 2 or higher, show this section
        is_visible = True if self.playlist_phase >= 2 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def playlist_phase_3(self):
        column_layout = [
                [
                    sg.Text("Scheme Path: "),
                    sg.In(size=(25, 1), enable_events=True, key="-PL_SCHEME_PATH-"),
                    sg.FolderBrowse()
                ],
                [
                    sg.Listbox(values=[], enable_events=True, size=(40, 20), key="-PLAYLIST-")
                ],
                [
                    sg.Button("Launch VLC", enable_events=True, size=(10, 1), key="-LAUNCH_VLC")
                ]
            ]

        # If the playlist column phase is set to 3 or higher, show this section
        is_visible = True if self.playlist_phase >= 3 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def playlist_layout(self):
        layout = [self.playlist_phase_1, self.playlist_phase_2, self.playlist_phase_3]
        return layout

    @property
    def scheme_phase_1(self):
        return sg.Column([[sg.Button("Modify Scheme", size=(25, 1), key="-MOD_SCHEME-")]])

    @property
    def scheme_phase_2(self):
        column_layout = [
            [
                sg.Button("New Scheme", enable_events=True, size=(10, 1), key="-NEW_SCHEME"),
                sg.Button("Load Scheme", enable_events=True, size=(10, 1), key="-LOAD_SCHEME")
            ]
        ]
        # If the playlist column phase is set to 2 or higher, show this section
        is_visible = True if self.playlist_phase >= 2 else False

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
        is_visible = True if self.playlist_phase >= 3 else False

        return sg.Column(column_layout, visible=is_visible)

    @property
    def scheme_phase_4(self):
        column_layout = [
            [
                self.import_shows()
            ],
            [
                sg.Button("Save Scheme", enable_events=True, size=(10, 1), key="-SAVE_SCHEME"),
                sg.Button("Discard Changes", enable_events=True, size=(10, 1), key="-DISCARD_SCHEME")
            ]
        ]
        # If the playlist column phase is set to 4 or higher, show this section
        is_visible = True if self.playlist_phase >= 4 else False

        return sg.Column(column_layout, visible=is_visible)

    def import_shows(self) -> sg.Column:
        pass
