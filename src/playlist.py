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

        # This dictionary will take a show path as a key and return a list with an episode and duration in a list
        self.next_episode_dict: dict = {}

    # -------------------- Episode Search Functions -----------------------
    def get_next_episode(self, show_path: Path) -> Show:
        """
        Returns the current episode for the show. Additionally, updates the .eps file marker for the next episode.
        If it has reached the final episode, resets to previous episode
        """
        # If the show has already been encountered, use the playlist marker rather than reading from file
        try:
            show: Show = Show(show_path,
                              self.next_episode_dict[show_path][0],
                              self.next_episode_dict[show_path][1]
                              )
            # Search for the next episode of the show and return it
            try:
                show.current_episode = show.find_next_episode(show.current_episode, show.current_episode.parent)
            except ValueError:
                pass

        # If the show hasn't been encountered, return the current episode
        except KeyError:
            show: Show = Show(show_path)

        return show

    # -------------------- Playlist Functions -----------------------
    def generate_playlist(self, playlist_scheme: Scheme) -> None:
        """
        Generates a playlist, adding  up to a maximum number of minutes
        """
        # Define variables
        queue_length_mins: int = 0
        selected_show: Path
        timeout_counter: int = 0

        # Generate random list of videos
        while queue_length_mins < self.max_length and timeout_counter <= 50:
            # Select show from list of shows and user generated frequencies
            selected_show = random.choices(playlist_scheme.data["show_path"].to_list(),
                                           weights=playlist_scheme.data["frequency"].to_list())

            # Use .eps text file to determine next episode to play
            show_path = PathManager.TV_PATH.joinpath(selected_show[0])

            # Get the next episode of the show
            show = self.get_next_episode(show_path)

            if not show.current_episode.is_file():
                timeout_counter += 1
                continue

            # Get duration of video and append to total duration
            queue_length_mins += show.episode_duration

            # Add path to video queue and add it to the show episode dict
            self.video_queue.append(show.current_episode)
            self.next_episode_dict[show_path] = [show.current_episode, show.episode_depth]

    def dequeue_playlist(self) -> Path:
        """
        Manages simultaneous updates of video_queues and playlist backlog file. Removes one video from the queue.
        """
        # Pop and return front of queue. If queue is empty, return None
        try:
            video: Path = self.video_queue.popleft()

            # Set start point for iteratively setting .eps file through directory
            path = video

            # Get limiter to stop shows from saving over .eps file in TV_PATH
            show_directories = [path for path in PathManager.TV_PATH.iterdir() if path.is_dir()]

            while path != PathManager.TV_PATH and path not in show_directories:
                Show.write_next_episode(path)
                path = path.parent

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
