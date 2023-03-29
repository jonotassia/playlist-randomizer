# Defines the playlist class and its associated methods
from src.helper import PathManager
from src.scheme import Scheme

from collections import deque
from pathlib import Path, WindowsPath
import pandas as pd
from tinytag import TinyTag
import random
from vlc import Media


class Playlist:
    def __init__(self):
        self.video_queue: deque = deque()
        self.length: int

    # ----------------------- Methods --------------------------------
    def add_to_playlist(self, video: Path, duration: int) -> None:
        """
        Manages to simultaneous updates of video_queues and playlist backlog file. Adds one video to the queue.
        :param video_queue: Current playlist queue
        :param video: Video to add
        :param duration: Duration of video
        """
        # Add to video queue
        self.video_queue.append(video)

        # Add to playlist backlog file
        with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "a") as file:
            file.write(str(len(self.video_queue)) + "," + video.as_posix() + "," + str(duration) + "\n")

    def dequeue_playlist(self) -> Path:
        '''
        Manages simultaneous updates of video_queues and playlist backlog file. Removes one video from the queue.
        '''
        # Remove from playlist text file, preserving all rows after
        try:
            with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "r") as file:
                data = file.readlines()
            with open(PathManager.TV_PATH.joinpath(".playlist.csv"), "w") as file:
                file.write(",video,duration\n" + "".join(data[2:]))
        except (FileNotFoundError):
            print("Playlist does not exist")

        # Pop and return front of queue. If queue is empty, return None
        try:
            video = self.video_queue.popleft()
        except IndexError:
            video = None

        return video

    def generate_playlist(self, scheme_name: str, max_length: int) -> None:
        """
        Generates a playlist, adding  up to a maximum number of minutes
        """
        # Create path manager
        pm = PathManager()

        # Define variables
        queue_length_mins: int = 0
        selected_show: Path
        next_episode: Path

        # If a playlist already exists from a previous session, load that from file. Otherwise, create a blank version
        playlist: pd.DataFrame = self.load_playlist()

        # Populate playlist object with videos and set starting queue time
        self.video_queue = deque(playlist["video"].to_list())
        queue_length_mins += playlist["duration"].sum()

        # Get requested playlist scheme
        playlist_scheme = Scheme.load_playlist_scheme(scheme_name)

        # Generate random list of videos
        while queue_length_mins < max_length:
            # Select show from list of shows and user generated frequencies
            selected_show = random.choices(playlist_scheme.data["show_path"].to_list(),
                                           weights=playlist_scheme.data["frequency"].to_list())

            # Use .eps text file to determine next episode to play
            show_path = pm.TV_PATH.joinpath(selected_show[0])
            next_episode = pm.update_next_episode(show_path)

            # Get duration of video and append to total duration
            try:
                tag = TinyTag.get(next_episode.as_posix())
                queue_length_mins += tag.duration

                # If data not available on video length, add 10 mins to ensure we do not infinite loop
                if not tag.duration:
                    queue_length_mins += 10

            except FileNotFoundError:
                continue

            # Add path to video queue
            self.add_to_playlist(video=next_episode, duration=tag.duration)

    @classmethod
    def load_playlist(cls):
        """
        Load previous playlist from file and load into dataframe. This will load from TV_PATH/.playlist.csv.
        """
        # Try to load the playlist from file if it exists and is not empty.
        # Otherwise, return the empty playlist and save a blank csv with headers
        try:
            playlist = pd.read_csv(PathManager.TV_PATH.joinpath(".playlist.csv").as_posix(), index_col=0).reset_index(drop=True)
        except (pd.errors.EmptyDataError, FileNotFoundError):
            playlist = pd.DataFrame(columns=["video", "duration"])
            playlist.to_csv(PathManager.TV_PATH.joinpath(".playlist.csv").as_posix())
            return playlist

        # Convert videos to path
        playlist["video"] = playlist["video"].apply(lambda x: WindowsPath(x))

        return playlist


if __name__ == "__main__":
    pass
