# Defines the playlist class and its associated methods
from src.scheme import Scheme
from src.helper import PathManager

from collections import deque
from pathlib import Path, WindowsPath
import pandas as pd
from tinytag import TinyTag
import random
import os
import re


class Playlist:
    # --------------------- Class Variables -----------------------------
    PROG_PATH: Path = Path("C:/Program Files/")
    PROG_PATH_86: Path = Path("C:/Program Files (x86)/")
    USER_PATH: Path = Path(os.environ['USERPROFILE'])
    TV_PATH: Path = None
    VLC_PATH: Path = None

    def __init__(self, max_length=200):
        self.video_queue: deque = deque()
        self.length: int
        self.max_length: int = max_length
        self.next_episode_dict: dict = dict()

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
        return [Playlist.tryint(c) for c in re.split('([0-9]+)', string)]

    @staticmethod
    def human_sort(path_list: list) -> None:
        """
        Sort a list in the way that humans expect.
        """
        path_list.sort(key=Playlist.alphanum_key)

    # -------------------- Episode Search Functions -----------------------
    def get_first_episode(self, search_path: Path) -> Path:
        """
        Returns the first episode of a show. If show is arranged into seasons, searches recursively.
        :param search_path: Path to initiate search for episode
        """
        # Sort contents of directory, excluding non-media files and folders. If the path is TV_PATH, exclude folders too
        if search_path == PathManager.TV_PATH:
            sorted_contents: list = [path for path in search_path.iterdir() if
                                     path.suffix not in [".csv", ".txt"] and path.stem != ".scheme" and not path.is_dir()]
        else:
            sorted_contents: list = [path for path in search_path.iterdir() if
                                     path.suffix not in [".csv", ".txt"] and path.stem != ".scheme"]

        self.human_sort(sorted_contents)

        try:
            first_episode: Path = sorted_contents[0]
        except IndexError as err:
            raise err

        # Write the first episode to file
        with open(search_path.joinpath(".eps.txt"), "w") as file:
            file.write(first_episode.as_posix())

        # If the first value of the returned content is a directory, search in that directory
        if first_episode.is_dir():
            first_episode = self.get_first_episode(first_episode)

        return first_episode

    def get_current_episode(self, show_path: Path) -> Path:
        """
        Uses the .eps file to search and return the first episode. If .eps file does not exist, find the first episode
        :param show_path: Path of the show to get current episode for
        """
        eps_file_path: Path = show_path.joinpath(".eps.txt")

        # If .eps file does not exist, populate with first episode of show and return first episode
        if not eps_file_path.exists() or not eps_file_path.stat().st_size:
            first_episode: Path = self.get_first_episode(show_path)
            return first_episode

        # Otherwise, get current episode from .eps file
        current_episode: Path = Path(eps_file_path.read_text())

        if current_episode.is_dir():
            current_episode = self.get_current_episode(current_episode)

        return current_episode

    def find_next_episode(self, search_item: Path, search_path: Path) -> Path:
        """
        Searches for the next episode or season. If the final episode or season, returns the first one
        :param search_item: The target of the search. It will look for the element that is after this one.
        :param search_path: The path of the search.
        """
        # if the search item is already a media file, search only media files (assumes we are in media folder)

        # Search for next episode of show in folder
        sorted_paths: list = [path for path in search_path.iterdir()
                              if path.suffix not in [".csv", ".txt"] and path.stem != ".scheme"]
        self.human_sort(sorted_paths)

        try:
            path_number: int = sorted_paths.index(search_item)
        except ValueError:
            return

        # Grab the next episode if it is not the last episode
        try:
            next_path: Path = sorted_paths[path_number + 1]

        except IndexError:
            return search_item.parent

        # If we have not reached a media file yet, continue until one is found.
        # Use get_current_episode as your search item
        if next_path.is_dir():
            try:
                next_path = self.find_next_episode(self.get_current_episode(next_path), next_path)
            # If the file directory is blank, return the previous episode
            except IndexError:
                return sorted_paths[path_number]

        return next_path

    def update_current_episode(self, show_path: Path) -> Path:
        """
        Returns the current episode for the show. Additionally, updates the .eps file marker for the next episode.
        If it has reached the final episode, resets to previous episode
        """
        current_episode: Path = Path()
        next_episode: Path = Path()

        # If the show has already been encountered, use the playlist marker rather than reading from file
        try:
            next_episode = self.next_episode_dict[show_path]
        except KeyError:
            next_episode = self.get_current_episode(show_path) \
                            if show_path.is_dir() else self.get_current_episode(show_path.parent)

        # Search for the next episode of the show if it has already reached the end of the series
        while True:
            # If find_next_episode returns a media file, we will return it
            next_episode = self.find_next_episode(next_episode, next_episode.parent)

            # Otherwise, if it returns a directory, go to the next directory
            if next_episode.is_dir():
                next_episode = self.find_next_episode(next_episode, next_episode.parent)

                # Then search for the current episode in that folder
                next_episode = self.get_current_episode(next_episode)

            if next_episode.is_file() or not next_episode:
                break

        return next_episode

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
        [Playlist.clear_episode_files(folder) for folder in path.iterdir() if folder.is_dir()]

    # -------------------- Playlist Functions -----------------------
    @classmethod
    def load_playlist(cls):
        """
        Load previous playlist from file and load into dataframe. This will load from TV_PATH/.playlist.csv.
        """
        # Try to load the playlist from file if it exists and is not empty.
        # Otherwise, return the empty playlist and save a blank csv with headers
        try:
            # Load videos and convert videos to path
            playlist = pd.read_csv(PathManager.TV_PATH.joinpath(".playlist.csv").as_posix(), index_col=0).reset_index(
                drop=True)
            playlist["video"] = playlist["video"].apply(lambda x: WindowsPath(x))
        except:
            playlist = pd.DataFrame(columns=["video", "duration"])
            playlist.to_csv(PathManager.TV_PATH.joinpath(".playlist.csv").as_posix())
            return playlist

        return playlist

    def generate_playlist(self, playlist_scheme: Scheme) -> None:
        """
        Generates a playlist, adding  up to a maximum number of minutes
        """
        # Define variables
        queue_length_mins: int = 0
        selected_show: Path

        # If a playlist already exists from a previous session, load that from file. Otherwise, create a blank version
        playlist: pd.DataFrame = self.load_playlist()

        # Populate playlist object with videos and set starting queue time
        self.video_queue = deque(playlist["video"].to_list())
        queue_length_mins += playlist["duration"].sum()

        # Generate random list of videos
        while queue_length_mins < self.max_length:
            # Select show from list of shows and user generated frequencies
            selected_show = random.choices(playlist_scheme.data["show_path"].to_list(),
                                           weights=playlist_scheme.data["frequency"].to_list())

            # Use .eps text file to determine next episode to play
            show_path = PathManager.TV_PATH.joinpath(selected_show[0])

            try:
                self.next_episode_dict[show_path] = self.update_current_episode(show_path)
            except:
                continue

            # Get duration of video and append to total duration
            try:
                tag = TinyTag.get(self.next_episode_dict[show_path].as_posix())
                queue_length_mins += tag.duration

                # If data not available on video length, add 10 mins to ensure we do not infinite loop
                if not tag.duration:
                    queue_length_mins += 10

            except:
                continue

            # Add path to video queue
            self.add_to_playlist(video=self.next_episode_dict[show_path], duration=tag.duration)

    def add_to_playlist(self, video: Path, duration: int) -> None:
        """
        Manages to simultaneous updates of video_queues and playlist backlog file. Adds one video to the queue.
        :param video: Video to add
        :param duration: Duration of video
        """
        # Add to video queue
        self.video_queue.append(video)

        # Add to playlist backlog file
        with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "a") as file:
            file.write(str(len(self.video_queue)) + "," + video.as_posix() + "," + str(duration) + "\n")

    def dequeue_playlist(self) -> Path:
        """
        Manages simultaneous updates of video_queues and playlist backlog file. Removes one video from the queue.
        """
        pm = PathManager()

        # Remove from playlist text file, preserving all rows after
        try:
            with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "r") as file:
                data = file.readlines()
            with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "w") as file:
                file.write(",video,duration\n" + "".join(data[2:]))
        except FileNotFoundError:
            print("Playlist does not exist")

        # Pop and return front of queue. If queue is empty, return None
        try:
            video = self.video_queue.popleft()
            self.write_next_episode(video)

        except IndexError:
            video = None

        return video

    def clear_playlist(self):
        """
        Removes all videos from current playlist queue and backlog (.playlist.txt)
        :return: None
        """
        # Clear playlist object
        self.video_queue = deque()
        self.next_episode_dict = dict()

        # Clear .txt file
        playlist = pd.DataFrame(columns=["video", "duration"])
        playlist.to_csv(PathManager.TV_PATH.joinpath(".playlist.csv").as_posix())


if __name__ == "__main__":
    pass
