from src.scheme import Scheme
from src.helper import PathManager
from src.playlist import Playlist
from src.gui import Interface

import PySimpleGUI as sg
from pathlib import Path

from src.show import Show

if __name__ == "__main__":
    # Get TV_PATH and VLC_PATH from file
    PathManager.load_paths()
    PathManager.set_vlc_path()

    interface = Interface()

    # Create window
    window = sg.Window("Playlist Randomizer", interface.layout, margins=(40, 20), resizable=True, finalize=True)

    # Create event loop
    while True:
        event, values = window.read(timeout=1000)
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

                    # Reload schemes from new TV Path
                    if "-LOAD_SCHEME_NAME-" in window.key_dict:
                        window["-LOAD_SCHEME_NAME-"].update(values=interface.get_schemes())

                    # If select show section is loaded, refresh
                    if "-SELECT_SHOW-" in window.key_dict:
                        window["-SELECT_SHOW-"].update(values=interface.get_shows(PathManager.TV_PATH))

                    # Hide playlist sections after scheme selection
                    interface.hide_elements(window, "-VIEW_PLAYLIST-", "-LAUNCH_VLC-")

                    # Hide Scheme info
                    interface.hide_elements(window,
                                            f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                            "-SAVE_SCHEME-",
                                            "-DISCARD_SCHEME-")

                    # Hide scheme save success message
                    interface.hide_elements(window, "-SCHEME_SUCCESS-")

                    # Hide episoode sections
                    interface.hide_elements(window, "-SELECT_EPISODE-", "-SAVE_SHOW-", "-DISCARD_SHOW-")

                    # Hide the episode save success message
                    interface.hide_elements(window, "-SHOW_SUCCESS-")

                else:
                    interface.error_message(f"Invalid Path: {tv_path.as_posix()}")
            except OSError as err:
                interface.error_message(f"Invalid Path: {err}")

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
                    interface.error_message(f"Invalid Path: {vlc_path.as_posix()}")
            except OSError as err:
                interface.error_message(f"Invalid Path: {err}")

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
            interface.hide_elements(window, "-VIEW_PLAYLIST-", "-LAUNCH_VLC-")

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
                    interface.unhide_elements(window, "-VIEW_PLAYLIST-", "-LAUNCH_VLC-")

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
            interface.hide_elements(window, "-LOAD_SCHEME_NAME-", "-CONFIRM_LOAD_SCHEME-")

            # Hide phase 4 rows
            interface.hide_elements(window,
                                    "-SAVE_SCHEME-",
                                    f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                    "-DISCARD_SCHEME-",
                                    "-SCHEME_SUCCESS-")

            # If the new scheme section is not already in the layout, add it. Otherwise, unhide it.
            if "-NEW_SCHEME_NAME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_3_new)
            else:
                interface.unhide_elements(window, "-NEW_SCHEME_NAME-", "-CONFIRM_NEW_SCHEME-")

        # Cascade Load Scheme section, hiding new scheme path if that has already been pressed
        elif event == "-LOAD_SCHEME-":
            # If New Scheme Name section is already in window, hide it
            interface.hide_elements(window, "-NEW_SCHEME_NAME-", "-CONFIRM_NEW_SCHEME-")

            # Hide phase 4 rows
            interface.hide_elements(window,
                                    "-SAVE_SCHEME-",
                                    f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                    "-DISCARD_SCHEME-",
                                    "-SCHEME_SUCCESS-")

            # If the existing scheme section is not already in the layout, add it. Otherwise, unhide it.
            if "-LOAD_SCHEME_NAME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_3_load)
            else:
                interface.unhide_elements(window, "-LOAD_SCHEME_NAME-", "-CONFIRM_LOAD_SCHEME-")

        elif event == "-NEW_SCHEME_NAME-":
            # Hide phase 4 rows
            interface.hide_elements(window,
                                    "-SAVE_SCHEME-",
                                    f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                    "-DISCARD_SCHEME-",
                                    "-SCHEME_SUCCESS-")

        elif event == "-LOAD_SCHEME_NAME-":
            # Hide phase 4 rows
            interface.hide_elements(window,
                                    "-SAVE_SCHEME-",
                                    f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                    "-DISCARD_SCHEME-",
                                    "-SCHEME_SUCCESS-")

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

            else:
                # Reset scroll bar and unhide the scheme section
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].contents_changed()
                interface.unhide_elements(window, f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-")

            interface.unhide_elements(window, "-SAVE_SCHEME-", "-DISCARD_SCHEME-")

        elif event == "-CONFIRM_LOAD_SCHEME-":
            if not values["-LOAD_SCHEME_NAME-"]:
                continue

            interface.scheme = Scheme.load_playlist_scheme(values["-LOAD_SCHEME_NAME-"][0])

            if "-SAVE_SCHEME-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], interface.scheme_phase_4)

            # If specific instance of scheme is not already loaded, extend the window with it
            elif f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-" not in window.key_dict:
                window.extend_layout(window["-SCHEME-"], [[interface.import_scheme()]])

            else:
                # Reset scroll bar and unhide the scheme section
                window[f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-"].contents_changed()
                interface.unhide_elements(window, f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-")

            interface.unhide_elements(window, "-SAVE_SCHEME-", "-DISCARD_SCHEME-")

        # When the save button is pressed, 2 key functions are performed:
        #   1. The changes are compiled in interface.scheme.data
        #   2. The changes to the dataframe are saved to file
        # If successful, extends or unhides a success message
        elif event == "-SAVE_SCHEME-":
            try:
                # Incorporate changes to frequency for show to dataframe, then save changes
                for index in interface.scheme.data.index.values:
                    # If value is not entered, fill with a 0
                    interface.scheme.data.at[index, "frequency"] = values[f"-SCHEME_FREQ_{index}-"] \
                        if values[f"-SCHEME_FREQ_{index}-"] else 0
                interface.scheme.save_scheme()

                # If a new scheme was added, make sure it is reflected in the playlist generation screen
                if "-PL_SCHEME_PATH-" in window.key_dict:
                    window["-PL_SCHEME_PATH-"].update(interface.get_schemes())

                if "-LOAD_SCHEME_NAME-" in window.key_dict:
                    window["-LOAD_SCHEME_NAME-"].update(interface.get_schemes())

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
                interface.hide_elements(window,
                                        f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                        "-SAVE_SCHEME-",
                                        "-DISCARD_SCHEME-",
                                        "-SCHEME_SUCCESS-")

            except FileNotFoundError:
                interface.hide_elements(window,
                                        f"-SCHEME_DETAILS-{interface.scheme.title.upper()}-",
                                        "-SAVE_SCHEME-",
                                        "-DISCARD_SCHEME-",
                                        "-SCHEME_SUCCESS-")

        # --------------- Show Layout Event Checks -----------------------

        # If Update Show Marker pressed, cascade related sections if not already cascaded
        elif event == "-UPDATE_SHOW-":
            if "-SELECT_SHOW-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], interface.show_phase_2)

        elif event == "-SELECT_SHOW-":
            if not values["-SELECT_SHOW-"]:
                continue

            # Assign new show to interface
            show_path = PathManager.TV_PATH.joinpath(values["-SELECT_SHOW-"][0]) \
                if values["-SELECT_SHOW-"][0] != PathManager.TV_PATH.stem else PathManager.TV_PATH
            try:
                if show_path.exists():
                    interface.show = Show(show_path)
                else:
                    interface.error_message(f"Invalid Path: {show_path.as_posix()}")
                    continue
            except OSError as err:
                interface.error_message(f"Invalid Path: {err}")
                continue

            # Hide the success message from the bottom of the frame
            interface.hide_elements(window, "-SHOW_SUCCESS-")

            # Extend phase 3 rows
            if "-SAVE_SHOW-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], interface.show_phase_3)
            else:
                # Update select episodes with current path in case it has changed
                try:
                    curr_episode = interface.show.get_current_episode(interface.show.path)
                    curr_episode_text = curr_episode.stem
                except:
                    curr_episode = interface.show.path
                    curr_episode_text = ""

                window["-SELECT_EPISODE-"].update(curr_episode_text)
                window.Element('-EPISODE_SEARCH-').InitialFolder = curr_episode.parent

                # Unhide phase 3 rows
                interface.unhide_elements(window, "-SELECT_EPISODE-", "-SAVE_SHOW-", "-DISCARD_SHOW-")

        elif event == "-SAVE_SHOW-":
            episode = Path(values["-SELECT_EPISODE-"])
            try:
                if episode.exists():
                    interface.show.write_next_episode(episode)
                else:
                    interface.error_message(f"Invalid Path: {episode.as_posix()}")
                    continue
            except OSError as err:
                interface.error_message(f"Invalid Path: {err}")
                continue

            if "-SHOW_SUCCESS-" not in window.key_dict:
                window.extend_layout(window["-SHOWS-"], [
                    [interface.success_message("Show successfully saved.", "-SHOW_SUCCESS-")]])
            else:
                window["-SHOW_SUCCESS-"].unhide_row()

        elif event == "-DISCARD_SHOW-":
            # Hide all phase 3 rows
            interface.hide_elements(window, "-SELECT_EPISODE-", "-SAVE_SHOW-", "-DISCARD_SHOW-", "-SHOW_SUCCESS-")

        elif event == "-CLEAR_MARKERS-":
            if interface.confirm_popup("Are you sure you want to do this? All show progress will be reset."):
                # Clear all show markers
                Show.clear_episode_files(PathManager.TV_PATH)
                interface.hide_elements(window, "-SELECT_EPISODE-", "-SAVE_SHOW-", "-DISCARD_SHOW-", "-SHOW_SUCCESS-")

        window.refresh()

    window.close()

    # Save any paths that have been changed during programme run
    PathManager.save_paths()
