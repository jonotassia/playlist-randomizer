import PySimpleGUI as sg
from src.scheme import Scheme
from src.helper import PathManager

# Define layout
playlist_column = [
    [
        sg.Text("Generate Playlist", size=(25, 1))
    ],
    [
        sg.Text("VLC Path: "),
        sg.In(size=(25, 1), enable_events=True, key="-VLC_PATH-"),
        sg.FolderBrowse()
    ],
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

scheme = Scheme.load_playlist_scheme("scheme")
shows = [sg.Checkbox(show) for show in scheme.data["show_path"]]
freqs = [sg.In(size=(10, 1), default_text=freq) for freq in scheme.data["frequency"]]
show_select_column = list(zip(shows, freqs))


# show_select_column = [
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
#     [sg.Checkbox("test"), sg.In(size=(10, 1))],
# ]

scheme_column = [
    [
        sg.Text("Modify Scheme", size=(25, 1))
    ],
    [
        sg.Button("New Scheme", enable_events=True, size=(10, 1), key="-NEW_SCHEME"),
        sg.Button("Load Scheme", enable_events=True, size=(10, 1), key="-LOAD_SCHEME")
    ],
    [
        sg.Text("Scheme Path: "),
        sg.In(size=(25, 1), enable_events=True, key="-SCHEME_PATH-"),
        sg.FolderBrowse()
    ],
    [
        sg.Column(show_select_column)
    ],
    [
        sg.Button("Save Scheme", enable_events=True, size=(10, 1), key="-SAVE_SCHEME"),
        sg.Button("Discard Changes", enable_events=True, size=(10, 1), key="-DISCARD_SCHEME")
    ]
]

layout = [
    [
        sg.Column(playlist_column),
        sg.VSeparator(),
        sg.Column(scheme_column)
    ]
]

# Create window
window = sg.Window("Playlist Randomizer", layout, margins=(200, 200))

# Create event loop
while True:
    event, values = window.read()
    # End programme if user closes window
    if event == sg.WIN_CLOSED:
        break

window.close()
