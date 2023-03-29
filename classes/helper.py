import re
from pathlib import Path


class PathManager:
    # --------------------- Class Variables -----------------------------
    PROG_PATH = Path("C:/Program Files/")
    PROG_PATH_86 = Path("C:/Program Files (x86)/")
    TV_PATH = Path("./data/TV Shows/")
    VLC_PATH = Path("C:/Program Files/VideoLAN/VLC/vlc.exe")

    # --------------------- Search Functions ----------------------------
    @staticmethod
    def tryint(string: str) -> str:
        """
        Return an int if possible, or `s` unchanged.
        """
        try:
            return int(string)
        except ValueError:
            return string

    @staticmethod
    def alphanum_key(string: Path) -> list:
        """
        Turn a string into a list of string and number chunks.

        alphanum_key("z23a")
        ["z", 23, "a"]

        """
        string = string.as_posix()
        return [ PathManager.tryint(c) for c in re.split('([0-9]+)', string) ]

    @staticmethod
    def human_sort(path_list: list) -> None:
        """
        Sort a list in the way that humans expect.
        """
        path_list.sort(key=PathManager.alphanum_key)

    # -------------------- Path Functions -----------------------
    @classmethod
    def set_vlc_path(cls):
        """
        Searches for default install directories of VLC media player. If it can't be found, validates user prompt
        and sets path.
        :return: True if path is set, else false
        """
        if cls.PROG_PATH.joinpath("VideoLAN").exists():
            cls.VLC_PATH = Path("C:/Program Files/VideoLAN/VLC/vlc.exe")
        elif cls.PROG_PATH_86.joinpath("VideoLAN").exists():
            cls.VLC_PATH = Path("C:/Program Files (x86)/VideoLAN/VLC/vlc.exe")
        else:
            # Prompt user for VLC Path. Verify that it is a valid path, otherwise, continue loop.
            while True:
                input_path = input("Unable to find VLC path. Please enter path: ")
                input_path = input_path.strip('\"')

                # If blank, quit the programme
                if input_path == "":
                    return False

                try:
                    cls.VLC_PATH = Path(input_path)
                    if cls.VLC_PATH.exists() and cls.VLC_PATH.stem == "vlc":
                        break
                except:
                    print("Invalid Path")
        return True

    def get_first_episode(self, search_path: Path) -> Path:
        """
        Returns the first episode of a show. If show is arranged into seasons, searches recursively.
        :param search_path: Path to initiate search for episode
        """

        sorted_contents: list = [path for path in search_path.glob("*[!.txt]")]
        PathManager.human_sort(sorted_contents)
        first_episode: Path = sorted_contents[0]

        # If the first value of the returned content is a directory, search in that directory
        if first_episode.is_dir():
            first_episode = self.get_first_episode(first_episode)

        return first_episode

    def get_current_episode(self, show_path: Path) -> Path:
        """
        Uses the .eps file to search and return the first episode. If .eps file does not exist, find the first episode
        """
        eps_file_path: Path = show_path.joinpath(".eps.txt")

        # If .eps file does not exist, populate with first episode of show and return first episode
        if not eps_file_path.exists() or not eps_file_path.stat().st_size:
            first_episode: Path = self.get_first_episode(show_path)
            with open(eps_file_path, "w") as file:
                file.write(first_episode.as_posix())
            return first_episode

        # Otherwise, get current episode from .eps file
        current_episode: Path = show_path.joinpath(show_path.joinpath(".eps.txt").read_text())

        return current_episode

    def find_next_path(self, search_item: Path, search_path: Path) -> Path:
        """
        Searches for the next episode or season. If the final episode or season, returns the first one
        """
        # Search for next episode of show in folder
        sorted_paths: list = [path for path in search_path.glob("*[!.txt]")]
        self.human_sort(sorted_paths)

        try:
            path_number: int = sorted_paths.index(search_item)
        except ValueError:
            return None

        # Grab the next episode if it is not the last episode
        try:
            next_path: Path = sorted_paths[path_number + 1]

        except IndexError:
            next_path: Path = sorted_paths[0]

        return next_path

    def update_next_episode(self, show_path: Path) -> Path:
        '''
        Returns the current episode for the show. Additionally, updates the .eps file marker for the next episode.
        If it has reached the final episode, resets to previous episode
        '''
        import os

        current_episode: Path = self.get_current_episode(show_path)
        next_episode: Path
        next_season: Path

        # If last episode and folder above is the TV_PATH, return to start of series
        next_episode = self.find_next_path(current_episode, current_episode.parent)

        # If no next episode was found, return the current episode
        if not next_episode:
            return current_episode

        write_string = next_episode.stem + next_episode.suffix

        # If folder above directory is not TV_PATH, we assume this directory structure is organized into series
        # Repeat search in next season
        if current_episode.parent.parent != self.TV_PATH:
            if next_episode == self.get_first_episode(current_episode.parent):
                next_season = self.find_next_path(current_episode.parent, show_path)

                # If no next seaon was found, return the current episode
                if not next_season:
                    return current_episode

                # If we cannot find the next epsiode in the subsequent season folder, do not change .eps
                if os.listdir(next_season):
                    next_episode = self.get_first_episode(next_season)

                else:
                    return current_episode

            write_string = next_episode.parts[-2] + '/' + next_episode.parts[-1]

        # Overwrite .eps file with next episode
        with open(show_path.joinpath(".eps.txt"), "w") as file:
            file.write(write_string)

        return next_episode
