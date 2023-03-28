# Playlist scheme and related methods
from classes.helper import PathManager

import pandas as pd
from pathlib import WindowsPath


class Scheme:
    def __init__(self, title, data=pd.DataFrame(columns=['show_path', 'frequency'])):
        self.title: str = title
        self.data: pd.DataFrame = data

    @classmethod
    def new_playlist_scheme(cls, file_name: str):
        # Grab folder name for each video
        show_folders = [folder for folder in PathManager.TV_PATH.iterdir()]

        # Create and populate dataframe
        show_folder_df = pd.DataFrame(columns=["show_path", "frequency"])
        show_folder_df["show_path"] = show_folders
        show_folder_df["frequency"] = show_folder_df["frequency"].fillna(1)

        # Make relative to TV_PATH and remove playlist row
        show_folder_df["show_path"] = show_folder_df["show_path"].apply(lambda x: x.relative_to(PathManager.TV_PATH))
        show_folder_df = show_folder_df[show_folder_df["show_path"] != WindowsPath('.scheme')]

        # Create playlist file
        show_folder_df.to_csv(PathManager.TV_PATH.as_posix() + "/.scheme/" + file_name + ".csv")

        return Scheme(file_name, show_folder_df)

    @classmethod
    def load_playlist_scheme(cls, file_name: str):
        """
        Loads a playlist scheme from file. If none found, generates a new one
        """
        try:
            data = pd.read_csv(PathManager.TV_PATH.as_posix() + "/.scheme/" + file_name + ".csv", index_col=0)
        except FileNotFoundError:
            data = cls.new_playlist_scheme(file_name)

        return Scheme(file_name, data)
