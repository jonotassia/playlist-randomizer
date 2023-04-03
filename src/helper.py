from pathlib import Path
import os


class PathManager:
    # --------------------- Class Variables -----------------------------
    PROG_PATH: Path = Path("C:/Program Files/")
    PROG_PATH_86: Path = Path("C:/Program Files (x86)/")
    USER_PATH: Path = Path(os.environ['USERPROFILE'])
    TV_PATH: Path = None
    VLC_PATH: Path = None

    @classmethod
    def save_paths(cls):
        """
        Saves the TV_PATH and VLC_PATH variables so that they can be loaded on next run.
        :return: None
        """
        write_string = f"TV_PATH,{cls.TV_PATH}\n" \
                       f"VLC_PATH,{cls.VLC_PATH}"

        with open(cls.USER_PATH.joinpath(".vlc_rand"), "w") as file:
            file.write(write_string)

    @classmethod
    def load_paths(cls):
        """
        Loads the TV_PATH and VLC_PATH variables from file.
        :return: None
        """
        try:
            with open(cls.USER_PATH.joinpath(".vlc_rand"), "r") as file:
                lines = file.readlines()
                for line in lines:
                    # Split line and assign TV_PATH and VLC_PATH if available
                    line_split = line.split(',')

                    if line_split == line:
                        return

                    # Handle \n and potential for quotes around file names before assigning
                    if line_split[0] == "TV_PATH":
                        cls.TV_PATH = Path(line_split[1].rstrip("\n").strip('\"'))
                    if line_split[0] == "VLC_PATH":
                        cls.VLC_PATH = Path(line_split[1].rstrip("\n").strip('\"'))

        except FileNotFoundError:
            return

    @classmethod
    def set_vlc_path(cls):
        """
        Searches for default install directories of VLC media player. If it can't be found, validates user prompt
        and sets path.
        :return: True if path is set, else false
        """
        # Quit if path already set
        if cls.VLC_PATH:
            return True

        if cls.PROG_PATH.joinpath("VideoLAN").exists():
            cls.VLC_PATH = Path("C:/Program Files/VideoLAN/VLC/vlc.exe")
        elif cls.PROG_PATH_86.joinpath("VideoLAN").exists():
            cls.VLC_PATH = Path("C:/Program Files (x86)/VideoLAN/VLC/vlc.exe")

        return True


if __name__ == "__main__":
    pass
