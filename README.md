# VLC Playlist Randomizer

## Main loop

* Workflow
  1. Launch programme 
  2. User selects which playlist they want 
  3. Using frequencies defined in the playlist, programme loops through to find the next videos to play and adds to VLC queue
  4. Plays videos through media player until it reaches the end of the queue
* Requirements
  * Programme uses native VLC playlist queue to populate videos so that they play one after another
	* Programme imposes a queue limit in the playlist either by number of hours or number of episodes, adjustable by user parameters
	* Programme saves off in the show directory a tracker of which episode within the show should play next based on the last episode played (sequential selection)
		* This will be set when the episode is added to the queue, or ideally when the episode plays.
	* If show folders have subfolders for seasons, ensure that they are handled appropriately by pointing the programme to the correct subfolder via another csv

## Playlist editing 

* Workflow:
	1. User creates a new playlist with a custom title as a .csv file
		1. Title: Playlist name
		2. Each row: folder_name, frequency
	2. User adds programmes to the playlist and specifies frequency 
* Optimization/Future:
	* Add provisions directly in the programme to create a new playlist

File Structure:

* Show Folder
  
  ![image](https://user-images.githubusercontent.com/24849659/227885050-9d0545e6-7d6d-497a-adb9-979f2b95c50a.png)

	
* Episodes Folder
	
  ![image](https://user-images.githubusercontent.com/24849659/227885242-6a07aa28-73cf-4eae-95ca-0073b2d99c32.png)
