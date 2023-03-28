from classes.playlist import Playlist
import vlc


if __name__ == "__main__":
    while True:
        selection = input("Select an option: \n"
                          "   1) Load Playlist"
                          "   2) Modify Scheme")

        # Load Playlist
        if selection == "1":
            playlist = Playlist()
            scheme_name = input("Please provide a scheme name: ")

            if not scheme_name:
                quit(1)

            # Prompt user for scheme name, and if not blank, generate spec
            playlist.generate_playlist("scheme", 200)

            # Create new VLC instance, media player, and media list
            player = vlc.Instance()
            media_list = player.media_list_new()
            media_player = player.media_list_player_new()

            # Populate media list
            while playlist.video_queue:
                media = player.media_new(playlist.dequeue_playlist())
                media_list.add_media(media)

            # Assign media list to player
            media_player.set_media_list(media_list)

            # Set loop and play
            player.vlm_set_loop(scheme_name, True)
            media_player.play()

        elif selection == "2":
            pass

        else:
            quit()