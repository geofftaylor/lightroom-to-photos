# Lightroom to Photos

A few Python scripts to help with migration from Lightroom to Apple Photos.

The only requirement outside of the Python standard library is [PhotoScript](https://github.com/RhetTbull/PhotoScript). I used these scripts on macOS Sonoma 14.2.1 with Photos 9.0, Python 3.9 and PhotoScript v0.3.1. As long as PhotoScript is compatible with your macOS and Photos version, the scripts should work.

## Installation

1. Install [Python 3.9](https://www.python.org/downloads/macos/) or higher.
2. Install PhotoScript: Open Terminal, type `pip3 install photoscript` and press Return.
3. Download the latest release from this repository and unzip to a folder of your choice.

## find-files-and-folders.py

In Lightroom, a folder can contain files (photos and videos) and other folders. In Photos, a folder can only contain albums. Albums can only contain photos and videos.

This script finds Lightroom folders that contain both files and folders, and displays the list on the screen. If any folders contain both files and folders, the files should be moved to a subfolder in preparation for the migration to Photos.

Before running the script, find this line: `photo_dir = '/Path/To/Lightroom/Photos'` and change the path to the top-level folder where your photos are stored.

To run the script, open Terminal, `cd` to the directory where you saved the script, type `python3 ./find-files-and-folders.py` and press Return.

## create-folders-and-albums.py

After running `find-files-and-folders.py` and performing any required cleanup, you can run this script to create the folder-album structure in Photos. The script reads a folder of nested subfolders and media files. For any folder than contains subfolders, it creates a folder in Photos. For any folder that contains only media files, it creates an album in Photos. The folder-album tree in Photos will mirror the folder tree in Finder.

The script displays its output on the screen and creates a timestamped log file in the same directory as the script.

Before running the script: 

1. Find the line `photos_path = '/Path/To/Lightroom/Export'` and change the path to the top-level folder of media files you want to import into Photos.
2. Find the line `photo_library_path = '/Path/To/Photos.photoslibrary'` and change the path to the full path of your Photos library. (It's a file with the extension `photoslibrary`.)

To run the script, open Terminal, `cd` to the directory where you saved the script, type `python3 ./create-folders-and-albums.py` and press Return.

## verify-import.py

After importing your photos and videos into the Photos app, run this script to verify the import. This script compares the media files in a Photos library to the media files in a folder tree.

It displays output to the screen. It also creates a timestamped log file with more detailed output in the same directory as the script. If any media files are missing from the Photos app, it creates a CSV file of media files missing from Photos in the same directory as the script.

The CSV file displays the album where it expected to find the file, the folder where it found the file, and the file name.

![](./missing-files-csv.png)

Before running the script: 

1. Find the line `photos_path = '/Path/To/Lightroom/Export'` and change the path to the top-level folder of media files you imported into Photos.
2. Find the line `photo_library_path = '/Path/To/Photos.photoslibrary'` and change the path to the full path of your Photos library. (It's a file with the extension `photoslibrary`.)

To run the script, open Terminal, `cd` to the directory where you saved the script, type `python3 ./verify-import.py` and press Return.