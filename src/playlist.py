# Defines the playlist class and its associated methods
from src.scheme import Scheme
from src.helper import PathManager
from src.show import Show

from collections import deque
from pathlib import Path
import random


class Playlist:
    def __init__(self, max_length=200):
        self.video_queue: deque = deque()
        self.length: int
        self.max_length: int = max_length
        self.next_episode_dict: dict = {}

    # -------------------- Episode Search Functions -----------------------
    def get_next_episode(self, show_path: Path) -> Show:
        """
        Returns the current episode for the show. Additionally, updates the .eps file marker for the next episode.
        If it has reached the final episode, resets to previous episode
        """
        # If the show has already been encountered, use the playlist marker rather than reading from file
        try:
            show: Show = Show(show_path, self.next_episode_dict[show_path])
        except KeyError:
            show: Show = Show(show_path)

        # Search for the next episode of the show and return it
        show.current_episode = show.find_next_episode(show.current_episode, show.current_episode.parent)

        return show

    # -------------------- Playlist Functions -----------------------
    def generate_playlist(self, playlist_scheme: Scheme) -> None:
        """
        Generates a playlist, adding  up to a maximum number of minutes
        """
        # Define variables
        queue_length_mins: int = 0
        selected_show: Path

        # Generate random list of videos
        while queue_length_mins < self.max_length:
            # Select show from list of shows and user generated frequencies
            selected_show = random.choices(playlist_scheme.data["show_path"].to_list(),
                                           weights=playlist_scheme.data["frequency"].to_list())

            # Use .eps text file to determine next episode to play
            show_path = PathManager.TV_PATH.joinpath(selected_show[0])

            # Get the next episode of the show
            show = self.get_next_episode(show_path)

            # Get duration of video and append to total duration
            queue_length_mins += show.episode_duration

            # Add path to video queue and add it to list of shows show episode dict
            self.add_to_playlist(video=self.next_episode_dict[show_path])
            self.next_episode_dict[show_path] = show.current_episode

    def add_to_playlist(self, video: Path) -> None:
        """
        Manages to simultaneous updates of video_queues and playlist backlog file. Adds one video to the queue.
        :param video: Video to add
        :param duration: Duration of video
        """
        # Add to video queue
        self.video_queue.append(video)

    def dequeue_playlist(self) -> Path:
        """
        Manages simultaneous updates of video_queues and playlist backlog file. Removes one video from the queue.
        """
        # Pop and return front of queue. If queue is empty, return None
        try:
            video = self.video_queue.popleft()

            # Set start point for iteratively setting .eps file through directory
            path = video

            while path != PathManager.TV_PATH:
                path = path.parent
                Show.write_next_episode(path)

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


if __name__ == "__main__":
    pass
