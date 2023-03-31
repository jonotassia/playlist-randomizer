from src.scheme import Scheme
from src.helper import PathManager
from src.playlist import Playlist
from src.gui import Interface

import PySimpleGUI as sg
from pathlib import Path

if __name__ == "__main__":
    # Get TV_PATH and VLC_PATH from file
    PathManager.load_paths()
    PathManager.set_vlc_path()

    interface = Interface()

    # Create window
    window = sg.Window("Playlist Randomizer", interface.layout, margins=(40, 20), resizable=True, finalize=True)

    # Create event loop
    while True:
        event, values = window.read(timeout=300)
        # End programme if user closes window
        if event == sg.WIN_CLOSED:
            break

        # --------------- Main Layout Event Checks -----------------------

        # If TV_PATH entered, validate and set TV_PATH variable in PathManager. Otherwise, throw error.
        elif event == "-TV_PATH-":
            tv_path = Path(values["-TV_PATH-"])
            try:
                if tv_path.exists():
                    PathManager.TV_PATH = tv_path
                    try:
                        PathManager.TV_PATH.joinpath(".scheme").mkdir()
                    except FileExistsError:
                        pass
                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # If the Confirm button is pressed, double-check the tv path in case the user kept the default value
        elif event == "-CONFIRM_TV_PATH-":
            tv_path = Path(values["-TV_PATH-"])
            try:
                if tv_path.exists():
                    PathManager.TV_PATH = tv_path

                    # If main buttons not yet cascaded, expand them.
                    if "-GEN_PLAYLIST-" not in window.key_dict:
                        window.size = 1200, 800
                        Interface.move_center(window)
                        window.extend_layout(window["-MAIN-"], interface.main_layout)

                    # If any other buttons have been expanded that require scheme or show selection,
                    # reload data and hide subsequent elements

                    # Reset scheme select box for playlist
                    if "-PL_SCHEME_PATH-" in window.key_dict:
                        window["-PL_SCHEME_PATH-"].update(values=interface.get_schemes())

                    # Hide playlist sections after scheme selection
                    if "-VIEW_PLAYLIST-" in window.key_dict:
                        window["-VIEW_PLAYLIST-"].hide_row()
                        window["-LAUNCH_VLC-"].hide_row()

                    # Reload schemes from new TV Path
                    if "-LOAD_SCHEME_NAME-" in window.key_dict:
                        window["-LOAD_SCHEME_NAME-"].update(values=interface.get_schemes())

                    # Hide Scheme info
                    if f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" in window.key_dict:
                        window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                        window["-SAVE_SCHEME-"].hide_row()
                        window["-DISCARD_SCHEME-"].hide_row()

                    # Hide scheme save success message
                    if "-SCHEME_SUCCESS-" in window.key_dict:
                        window["-SCHEME_SUCCESS-"].hide_row()

                    # Hide episoode sections
                    if "-SELECT_EPISODE-" in window.key_dict:
                        window[f"-SELECT_EPISODE-"].hide_row()
                        window["-SAVE_SHOW-"].hide_row()
                        window["-DISCARD_SHOW-"].hide_row()

                    # Hide the episode save success message
                    if "-SHOW_SUCCESS-" in window.key_dict:
                        window["-SHOW_SUCCESS-"].hide_row()

                    # If select show section is loaded, refresh
                    if "-SELECT_SHOW-" in window.key_dict:
                        window["-SELECT_SHOW-"].update(values=interface.get_shows())

                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # --------------- Playlist Layout Event Checks -----------------------

        # If Generate Playlist pressed, cascade related sections if not already cascaded
        elif event == "-GEN_PLAYLIST-":
            if "-VLC_PATH-" not in window.key_dict:
                window.extend_layout(window["-PLAYLIST-"], interface.playlist_phase_2)

        # If VLC_PATH entered, validate and set VLC_PATH variable in PathManager. Otherwise, throw error.
        elif event == "-VLC_PATH-":
            vlc_path = Path(values["-VLC_PATH-"]).joinpath("vlc.exe")
            try:
                if vlc_path.exists():
                    PathManager.VLC_PATH = vlc_path
                else:
                    interface.error_message("Invalid Path.")
            except OSError:
                interface.error_message("Invalid Path.")

        # Verify the duration entered is an int before adding it to the playlist
        elif event == "-PL_DURATION-":
            duration = values["-PL_DURATION-"]
            try:
                interface.playlist.max_length = int(duration)
            except ValueError:
                interface.error_message("Please enter a number.")

        # If Playlist Scheme selected, load the scheme and assign to the Interface
        elif event == "-PL_SCHEME_PATH-":
            if not values["-PL_SCHEME_PATH-"]:
                continue

            try:
                interface.scheme = Scheme.load_playlist_scheme(values["-PL_SCHEME_PATH-"][0])
            except FileNotFoundError:
                interface.error_message("Invalid Scheme.")

            # Hide rows if path is changed
            if "-VIEW_PLAYLIST-" in window.key_dict:
                window["-VIEW_PLAYLIST-"].hide_row()
                window["-LAUNCH_VLC-"].hide_row()

        # Display the current playlist to the user and cascade Launch VLC button if not already expanded
        elif event == "-PL_CONFIRM_PLAYLIST-":
            if values["-VLC_PATH-"] and values["-PL_DURATION-"] and values["-PL_SCHEME_PATH-"]:
                # Extend layout with phase 3 sections
                if "-LAUNCH_VLC-" not in window.key_dict:
                    interface.playlist.generate_playlist(interface.scheme)
                    window.extend_layout(window["-PLAYLIST-"], interface.playlist_phase_3)

                # If path has been changed, update view playlist element and unhide
                else:
                    # Clear playlist, then regenerate
                    interface.playlist.clear_playlist()
                    interface.playlist.generate_playlist(interface.scheme)
                    window["-VIEW_PLAYLIST-"].update(values=[vid.stem for vid in interface.playlist.video_queue])

                    # Add components back
                    window["-VIEW_PLAYLIST-"].unhide_row()
                    window["-LAUNCH_VLC-"].unhide_row()

        # Launch VLC with the current playlist
        elif event == "-LAUNCH_VLC-":
            interface.run_playlist()
            break

        # --------------- Scheme Layout Event Checks -----------------------

        # Cascade New Scheme and Load Scheme if not already done
        elif event == "-MOD_SCHEME-":
            if "-NEW_SCHEME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_2)

        # Cascade New Scheme Path section, hiding load scheme if that has already been pressed
        elif event == "-NEW_SCHEME-":
            # If New Scheme Name section is already in window, hide it
            if "-LOAD_SCHEME_NAME-" in window.key_dict:
                window["-LOAD_SCHEME_NAME-"].hide_row()
                window["-CONFIRM_LOAD_SCHEME-"].hide_row()

            # Hide phase 4 rows
            if "-SAVE_SCHEME-" in window.key_dict:
                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

                if "-SCHEME_SUCCESS-" in window.key_dict:
                    window["-SCHEME_SUCCESS-"].hide_row()

            # If the new scheme section is not already in the layout, add it. Otherwise, unhide it.
            if "-NEW_SCHEME_NAME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_3_new)
            else:
                window["-NEW_SCHEME_NAME-"].unhide_row()
                window["-CONFIRM_NEW_SCHEME-"].unhide_row()

            # Hide the success message from the bottom of the frame when new scheme loaded
            if "-SUCCESS_SCHEME-" in window.key_dict:
                window["-SUCCESS_SCHEME-"].hide_row()

        # Cascade Load Scheme section, hiding new scheme path if that has already been pressed
        elif event == "-LOAD_SCHEME-":
            # If New Scheme Name section is already in window, hide it
            if "-NEW_SCHEME_NAME-" in window.key_dict:
                window["-NEW_SCHEME_NAME-"].hide_row()
                window["-CONFIRM_NEW_SCHEME-"].hide_row()

            # Hide phase 4 rows
            if "-SAVE_SCHEME-" in window.key_dict:
                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

                if "-SCHEME_SUCCESS-" in window.key_dict:
                    window["-SCHEME_SUCCESS-"].hide_row()

            # If the existing scheme section is not already in the layout, add it. Otherwise, unhide it.
            if "-LOAD_SCHEME_NAME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_3_load)
            else:
                window["-LOAD_SCHEME_NAME-"].unhide_row()
                window["-CONFIRM_LOAD_SCHEME-"].unhide_row()

        elif event == "-NEW_SCHEME_NAME-":
            if f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" in window.key_dict:
                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

                if "-SCHEME_SUCCESS-" in window.key_dict:
                    window["-SCHEME_SUCCESS-"].hide_row()

        elif event == "-LOAD_SCHEME_NAME-":
            if f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" in window.key_dict:
                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

                if "-SCHEME_SUCCESS-" in window.key_dict:
                    window["-SCHEME_SUCCESS-"].hide_row()

        # Check if scheme exists and whether user is in load or new mode.
        # If so, load that scheme, else create a new one.
        # Cascade scheme editing windows if they are not already expanded.
        elif event == "-CONFIRM_NEW_SCHEME-":
            interface.scheme = Scheme.load_playlist_scheme(values["-NEW_SCHEME_NAME-"])

            if "-LOAD_SCHEME_NAME-" in window.key_dict:
                window["-LOAD_SCHEME_NAME-"].update(interface.get_schemes())

            if "-SAVE_SCHEME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_4)

            # If specific instance of scheme is not already loaded, extend the window with it
            elif f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], [[interface.import_scheme()]])
                window["-SAVE_SCHEME-"].unhide_row()
                window["-DISCARD_SCHEME-"].unhide_row()

            else:
                # Reset scroll bar
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].contents_changed()

                # Unhide phase 4 rows
                if f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" in window.key_dict:
                    window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].unhide_row()
                window["-SAVE_SCHEME-"].unhide_row()
                window["-DISCARD_SCHEME-"].unhide_row()

        elif event == "-CONFIRM_LOAD_SCHEME-":
            if not values["-LOAD_SCHEME_NAME-"]:
                continue

            interface.scheme = Scheme.load_playlist_scheme(values["-LOAD_SCHEME_NAME-"][0])

            if "-SAVE_SCHEME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_4)

            # If specific instance of scheme is not already loaded, extend the window with it
            elif f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], [[interface.import_scheme()]])
                window["-SAVE_SCHEME-"].unhide_row()
                window["-DISCARD_SCHEME-"].unhide_row()

            else:
                # Reset scroll bar
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].contents_changed()

                # Unhide phase 4 rows
                if f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" in window.key_dict:
                    window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].unhide_row()
                window["-SAVE_SCHEME-"].unhide_row()
                window["-DISCARD_SCHEME-"].unhide_row()

        # When the save button is pressed, 2 key functions are performed:
        #   1. The changes are compiled in interface.scheme.data
        #   2. The changes to the dataframe are saved to file
        # If successful, extends or unhides a success message
        elif event == "-SAVE_SCHEME-":
            try:
                # Incorporate changes to frequency for show to dataframe, then save changes
                for index in interface.scheme.data.index.values:
                    interface.scheme.data.at[index, "frequency"] = values[f"-SCHEME_FREQ_{index}-"]
                interface.scheme.save_scheme()

                # If a new scheme was added, make sure it is reflected in the playlist generation screen
                if "-PL_SCHEME_PATH-" in window.key_dict:
                    window["-PL_SCHEME_PATH-"].update(interface.get_schemes())

                # Cascade success message, or unhide if already there
                if "-SCHEME_SUCCESS-" not in window.key_dict:
                    window.extend_layout(window["-SCHEME-"], [
                        [interface.success_message("Scheme successfully saved.", "-SCHEME_SUCCESS-")]])
                else:
                    window["-SCHEME_SUCCESS-"].unhide_row()

            except:
                interface.error_message("Unable to save file.")

        # If Discard Scheme, reload the scheme from above and hide the success message
        elif event == "-DISCARD_SCHEME-":
            try:
                interface.scheme.refresh_scheme()

                for index in interface.scheme.data.index.values:
                    window[f"-SCHEME_SHOW_{index}-"].update(interface.scheme.data.at[index, "show_path"])
                    window[f"-SCHEME_FREQ_{index}-"].update(interface.scheme.data.at[index, "frequency"])

                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

            except FileNotFoundError:
                # Hide phase 4 rows
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].hide_row()
                window["-SAVE_SCHEME-"].hide_row()
                window["-DISCARD_SCHEME-"].hide_row()

            # Hide the success message from the bottom of the frame
            if "-SCHEME_SUCCESS-" in window.key_dict:
                window["-SCHEME_SUCCESS-"].hide_row()

        # --------------- Show Layout Event Checks -----------------------

        # If Update Show Marker pressed, cascade related sections if not already cascaded
        elif event == "-UPDATE_SHOW-":
            if "-SELECT_SHOW-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], interface.show_phase_2)

        elif event == "-SELECT_SHOW-":
            if not values["-SELECT_SHOW-"]:
                continue

            # Assign new show to interface
            show = PathManager.TV_PATH.joinpath(Path(values["-SELECT_SHOW-"][0]))
            try:
                if interface.show.exists():
                    interface.show = show
                else:
                    interface.error_message("Invalid Path.")
                    continue
            except OSError:
                interface.error_message("Invalid Path.")
                continue

            # Hide the success message from the bottom of the frame
            if "-SHOW_SUCCESS-" in window.key_dict:
                window["-SHOW_SUCCESS-"].hide_row()

            # Extend phase 3 rows
            if "-SAVE_SHOW-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], interface.show_phase_3)
            else:
                # Update select episodes with current path in case it has changed
                try:
                    curr_episode = interface.playlist.get_current_episode(interface.show)
                    curr_episode_text = curr_episode.stem
                except:
                    episode = Path()
                    curr_episode_text = ""

                window["-SELECT_EPISODE-"].update(curr_episode_text)
                window.Element('-EPISODE_SEARCH-').InitialFolder = interface.show

                # Unhide phase 3 rows
                window[f"-SELECT_EPISODE-"].unhide_row()
                window["-SAVE_SHOW-"].unhide_row()
                window["-DISCARD_SHOW-"].unhide_row()

        elif event == "-SAVE_SHOW-":
            episode = Path(values["-SELECT_EPISODE-"])
            try:
                if episode.exists():
                    interface.playlist.write_next_episode(episode)
                else:
                    interface.error_message("Invalid Path.")
                    continue
            except OSError:
                interface.error_message("Invalid Path.")
                continue

            if "-SHOW_SUCCESS-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], [
                    [interface.success_message("Show successfully saved.", "-SHOW_SUCCESS-")]])
            else:
                window["-SHOW_SUCCESS-"].unhide_row()

        elif event == "-DISCARD_SHOW-":
            # Hide all phase 3 rows
            window[f"-SELECT_EPISODE-"].hide_row()
            window["-SAVE_SHOW-"].hide_row()
            window["-DISCARD_SHOW-"].hide_row()

            # Hide the success message from the bottom of the frame
            if "-SHOW_SUCCESS-" in window.key_dict:
                window["-SHOW_SUCCESS-"].hide_row()

        elif event == "-CLEAR_MARKERS-":
            if interface.confirm_popup("Are you sure you want to do this? All show progress will be reset."):
                # Clear all show markers
                Playlist.clear_episode_files(PathManager.TV_PATH)

                if "-SELECT_EPISODE-" in window.key_dict:
                    # Hide all phase 3 rows
                    window[f"-SELECT_EPISODE-"].hide_row()
                    window["-SAVE_SHOW-"].hide_row()
                    window["-DISCARD_SHOW-"].hide_row()

                    # Hide the success message from the bottom of the frame
                    if "-SHOW_SUCCESS-" in window.key_dict:
                        window["-SHOW_SUCCESS-"].hide_row()

        window.refresh()

    window.close()

    # Save any paths that have been changed during programme run
    PathManager.save_paths()