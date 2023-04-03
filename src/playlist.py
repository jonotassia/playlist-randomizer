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
    def __init__(self, max_length=200):
        self.video_queue: deque = deque()
        self.length: int
        self.max_length: int = max_length

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
    def update_current_episode(self, show_path: Path) -> Path:
        """
        Returns the current episode for the show. Additionally, updates the .eps file marker for the next episode.
        If it has reached the final episode, resets to previous episode
        """
        current_episode: Path = Path()
        next_episode: Path = Path()

        # If the show has already been encountered, use the playlist marker rather than reading from file
        try:
            current_episode = self.next_episode_dict[show_path]
        except KeyError:
            current_episode = self.get_current_episode(show_path) \
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
