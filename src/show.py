# From src
from tinytag import TinyTag

from src.helper import PathManager

# From libraries
from pathlib import Path
import re


class Show:
    def __init__(self, show_path: Path, episode_path: Path = None, depth: int = 0):
        if show_path.is_file():
            self.path: Path = show_path.parent
        else:
            self.path: Path = show_path

        # Current episode details. Depth stored to facilitate finding next episode if end of directory reached
        self.episode_depth: int = depth
        try:
            self.current_episode: Path = episode_path
        except ValueError:
            self.current_episode = self.get_current_episode(self.path)

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
        return [Show.tryint(c) for c in re.split('([0-9]+)', string)]

    @staticmethod
    def human_sort(path_list: list) -> None:
        """
        Sort a list in the way that humans expect.
        """
        path_list.sort(key=Show.alphanum_key)

    # -------------------- Show Properties --------------------------------
    @property
    def current_episode(self):
        try:
            return self._current_episode
        except AttributeError:
            return Path()

    @current_episode.setter
    def current_episode(self, value: Path):
        if isinstance(value, Path):
            if value.exists() and value.is_file():
                self._current_episode = value

        else:
            raise ValueError("Invalid Path.")

    @property
    def episode_duration(self):
        try:
            tag = TinyTag.get(self.current_episode.as_posix())
        except:
            return 10

        if tag.duration:
            return tag.duration

        # If data not available on video length, add 10 mins to ensure we do not infinite loop
        else:
            return 10

    # -------------------- Episode Search Functions -----------------------

    def get_first_episode(self, search_path: Path, write=True) -> Path:
        """
        Returns the first episode of a show. If show is arranged into seasons, searches recursively.
        :param write: Typically, this is only false in order to preserve previous episodes in the instance
        that a user does not load Playlist into VLC media player. This will also be written again when loading into VLC.
        :param search_path: Path to initiate search for episode
        """
        # Sort contents of directory, excluding non-media files and folders. If the path is TV_PATH, exclude folders too
        if search_path == PathManager.TV_PATH:
            sorted_contents: list = [path for path in search_path.iterdir() if
                                     path.suffix not in [".csv",
                                                         ".txt"] and path.stem != ".scheme" and not path.is_dir()]
        else:
            sorted_contents: list = [path for path in search_path.iterdir() if
                                     path.suffix not in [".csv", ".txt"] and path.stem != ".scheme"]

        self.human_sort(sorted_contents)

        try:
            first_episode: Path = sorted_contents[0]
        except IndexError as err:
            raise err

        # Write the first episode to file if write is true.
        if write:
            self.write_next_episode(first_episode)

        # If the first value of the returned content is a directory, search in that directory
        if first_episode.is_dir():
            try:
                first_episode = self.get_first_episode(first_episode)
            # Handle situations where first directory is empty
            except IndexError:
                first_episode = self.find_next_episode(first_episode, first_episode.parent)

        # Increment the current episode depth and set the current episode
        self.episode_depth += 1
        self.current_episode = first_episode
        return first_episode

    def get_current_episode(self, show_path: Path) -> Path:
        """
        Uses the .eps file to search and return the first episode. If .eps file does not exist, find the first episode
        :param show_path: Path of the show to get current episode for
        """
        if self.current_episode.exists() and self.current_episode.is_file():
            return self.current_episode

        eps_file_path: Path = show_path.joinpath(".eps.txt")

        # If .eps file does not exist, populate with first episode of show and return first episode
        if not eps_file_path.exists() or not eps_file_path.stat().st_size:
            try:
                return self.get_first_episode(show_path)
            except IndexError:
                sorted_contents: list = [path for path in self.path.iterdir() if
                                         path.suffix not in [".csv", ".txt"] and path.stem != ".scheme"]

                self.human_sort(sorted_contents)

                return self.find_next_episode(sorted_contents[0], self.path)

        # Otherwise, get current episode from .eps file
        current_episode: Path = Path(eps_file_path.read_text())

        if current_episode.is_dir():
            current_episode = self.get_current_episode(current_episode)

        # Increment the current episode depth and set the current episode
        self.episode_depth += 1
        self.current_episode = current_episode
        return current_episode

    def find_next_episode(self, search_item: Path, search_path: Path) -> Path:
        """
        Searches for the next episode or season. If the final episode or season, returns the first one
        :param search_item: The target of the search. It will look for the element that is after this one.
        :param search_path: The path of the search.
        """
        # if the search item is already a media file, search only media files (assumes we are in media folder)
        if search_path == PathManager.TV_PATH:
            sorted_paths: list = [path for path in search_path.iterdir() if
                                  path.suffix not in [".csv",
                                                      ".txt"] and path.stem != ".scheme" and not path.is_dir()]
        # Search for next episode in show folder
        else:
            sorted_paths: list = [path for path in search_path.iterdir() if
                                  path.suffix not in [".csv", ".txt"] and path.stem != ".scheme"]

        self.human_sort(sorted_paths)

        # Try indexing the path in the sorted list to determine its position
        try:
            path_number: int = sorted_paths.index(search_item)
        except ValueError:
            return

        # Grab the next episode if it is not the last episode
        try:
            next_path: Path = sorted_paths[path_number + 1]

        # If final episode in the folder, move up a folder and repeat same search.
        # If we arrive in the tv path folder, return the first episode of the show and reset the episode depth
        except IndexError:
            if self.episode_depth-1 <= 0:
                self.episode_depth = 0
                return self.get_first_episode(self.path, write=False)

            self.episode_depth -= 1

            return self.find_next_episode(search_item.parent, search_path.parent)

        # If we have not reached a media file yet, continue down until one is found.
        # From the new search path, find the first episode in the new subfolder
        if next_path.is_dir():
            try:
                next_path = self.get_first_episode(next_path)
            # If the file directory is blank, increment the depth counter and return the previous episode
            except IndexError:
                self.episode_depth -= 1
                return sorted_paths[path_number]

        return next_path

    # -------------------- Static Methods -----------------------
    @staticmethod
    def write_next_episode(video: Path):
        """
        Writes the next video to the .eps file.
        :param video: Next video in series
        :return: None
        """
        # Overwrite .eps file with next episode
        with open(video.parent.joinpath(".eps.txt"), "w") as file:
            file.write(video.as_posix())

    @staticmethod
    def clear_episode_files(path: Path = PathManager.TV_PATH):
        """
        Clears all episode files across TV directory
        :return: None
        """
        # Delete .eps file from directory
        episode_file = path.joinpath(".eps.txt")
        if episode_file.exists():
            episode_file.unlink()

        # Recursively delete .eps file from all lower paths
        [Show.clear_episode_files(folder) for folder in path.iterdir() if folder.is_dir()]
