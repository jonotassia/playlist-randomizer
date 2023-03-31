# Playlist scheme and related methods
from src.helper import PathManager

import pandas as pd
from pathlib import Path


class Scheme:
    def __init__(self, title, data=pd.DataFrame(columns=['show_path', 'frequency'])):
        self.title: str = title
        self.data: pd.DataFrame = data

    @classmethod
    def new_playlist_scheme(cls, file_name: str):
        # Grab folder name for each video
        show_folders: list = [folder for folder in PathManager.TV_PATH.iterdir()
                              if folder.suffix not in [".csv", ".txt"]]

        # Create and populate dataframe
        show_folder_df: pd.DataFrame = pd.DataFrame(columns=["show_path", "frequency"])
        show_folder_df["show_path"] = show_folders
        show_folder_df["frequency"] = show_folder_df["frequency"].fillna(1)

        # Make relative to TV_PATH and remove playlist row
        show_folder_df["show_path"] = show_folder_df["show_path"].apply(lambda x: x.relative_to(PathManager.TV_PATH))
        show_folder_df = show_folder_df[show_folder_df["show_path"] != Path('.scheme')]

        return Scheme(file_name, show_folder_df)

    @classmethod
    def load_playlist_scheme(cls, file_name: str):
        """
        Loads a playlist scheme from file. If none found, generates a new one
        """
        # Declare variables
        scheme: Scheme
        data: pd.DataFrame

        try:
            data = pd.read_csv(PathManager.TV_PATH.as_posix() + "/.scheme/" + file_name + ".csv", index_col=0)
            scheme = Scheme(file_name, data)
        except FileNotFoundError:
            scheme = cls.new_playlist_scheme(file_name)

        return scheme

    def refresh_scheme(self):
        self.data = pd.read_csv(PathManager.TV_PATH.as_posix() + "/.scheme/" + self.title + ".csv", index_col=0)

    def save_scheme(self):
        save_path = PathManager.TV_PATH.joinpath(".scheme")
        if not save_path.exists():
            save_path.mkdir()

        self.data.to_csv(PathManager.TV_PATH.as_posix() + "/.scheme/" + self.title + ".csv")


if __name__ == "__main__":
    pass
