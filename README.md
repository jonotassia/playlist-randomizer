# Playlist Randomizer

The playlist randomizer is a tool that can be used to randomly select a TV show from a personal repository and continue where you left off by setting an episode marker in each show. At this moment in time, it should be used exclusively with <b>VLC Media Player</b>.

![Playlist Randomizer](https://user-images.githubusercontent.com/24849659/229719768-3028f6f9-8f0c-4e31-924c-0b9f1b2f485c.png)

## Generating a Playlist

A playlist will be created using the list of shows and frequencies provided in a playlist scheme:

* Workflow:
  1. Select a scheme to generate the playlist.
  2. Select the maximum duration of the playlist.
  3. Randomize TV Shows/Movies
  4. Launch VLC Media Player with playlist from above
  
  ![image](https://user-images.githubusercontent.com/24849659/229722204-915e0c5c-010b-4105-806c-db2c941ebce2.png)

* Requirements
  * Programme uses native VLC playlist queue to populate videos so that they play one after another
	* Programme imposes a queue limit in the playlist either by number of hours or number of episodes, adjustable by user parameters
	* Programme saves off in the show directory a tracker of which episode within the show should play next based on the last episode played (sequential selection)
		* This will be set when the user loads the playlist into VLC Media Player
	* If show folders have subfolders for seasons or other extras, these markers will correctly point to the next episode in the show using a human sort.

## Scheme Editing 

* Workflow:
	1. User creates or edits a scheme, which generates a file in the TV_PATH/.scheme/ folder, containing the following elements:
		1. Title: Playlist name
		2. Each row: folder_name, frequency
	2. User can select frequency for each show, which impacts the odds that the programme will be selected. A zero means it will be omitted entirely.
	
	![image](https://user-images.githubusercontent.com/24849659/229722111-157b730e-df1e-45df-95d8-bb8168c13d00.png)

## Episode Markers

* Workflow:
	1. User selects a TV show from the TV_PATH
	2. The show prepopulates with the first episode of the show if it is the first time it has been loaded.
	3. User can browse the folder and select the next episode in the series for that show.
	
	![image](https://user-images.githubusercontent.com/24849659/229722895-63697312-f706-4961-be3c-8bc15cf8c2e3.png)


File Structure:

There are 2 key elements in the file structure of this program:

* <b>.eps files [.txt]</b>: These files are used to point the program to the correct episode of the show. Each subdirectory beneath a show folder will have one of these files and will incrementally point it to the right episode folder by folder.
* <b>.scheme folder [.csv]</b>: The .scheme folder houses all of the schemes that a user creates. It is created dynmically when the user creates their first scheme.

Data Structure:

There are 5 main classes in this program:

* <b>Playlist</b>: Controls the functionality around building the playlist and tracking which episodes have been encountered in order to correctly write the .eps files on load into VLC.
* <b>Show</b>: Manages search methods within a TV show, including finding the first, current, or next episodes of the show.
* <b>Scheme</b>: Manages data in the form of a Pandas dataframe that is loaded from a scheme files.
* <b>Interface</b>: Controls user inputs and builds the GUI. Also contains methods to load playlist into VLC.
* <b>PathManager</b>: Controls program level paths that are needed for running the programme, such as the VLC Path and TV Path.
