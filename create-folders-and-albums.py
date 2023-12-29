"""
Read a folder of nested subfolders and media files.
For any folder than contains subfolders, create a folder in Photos.
For any folder that contains only media files, create an album in Photos.
The folder-album tree in Photos will mirror the folder tree in Finder.
Creates a timestamped log file in the same directory as the script.
"""

import sys, os, logging, photoscript
from datetime import datetime
from pathlib import Path

media_extensions = [] # File extensions of image and video files.
expected_folder_count = 0 # Number of folders we expect to create.
expected_album_count = 0 # Number of albums we expect to create.
folders_created = 0 # Number of folders created.
albums_created = 0 # Number of albums created.

# Log setup
script_dir = os.path.dirname(os.path.realpath(__file__))

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

now = datetime.now()
now_str = now.strftime('%Y%m%d-%H%M%S')

fh = logging.FileHandler(os.path.join(script_dir, 'create-folders-and-albums-%s.log' % now_str))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

def is_media_file(path):
    """Return True if the file's extension is in `media_extensions`."""
    media_file = False

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_file():
        ext = path.suffix[1:] # Remove the dot from the file extension.
        
        if ext in media_extensions:
            media_file = True
        
    return media_file

def get_files(path):
    """Return a list of the files (as Path objects) in the directory `path`."""
    files_in_path = []

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_dir():
        files_in_path = [f for f in path.iterdir() if f.is_file()]

    return files_in_path

def get_sub_folders(path):
    """Return a list of the subfolders (as Path objects) in the directory `path`."""
    sub_folders = []

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_dir():
        sub_folders = [d for d in path.iterdir() if d.is_dir()]

    return sub_folders

def process_folder(folder_path, parent_folder, photo_library):
    """Create folders and albums in Photos library."""
    # Use the module-level variables.
    global expected_folder_count, expected_album_count, folders_created, albums_created

    if not isinstance(folder_path, Path):
        folder_path = Path(folder_path)

    folders = get_sub_folders(folder_path) # Subfolders of folder_path

    for this_folder in folders:
        sub_folder_count = len(get_sub_folders(this_folder)) # Number of subfolders in this folder
        media_files = [f for f in get_files(this_folder) if is_media_file(f)] # Images and videos in this folder
        media_file_count = len(media_files) # Number of images and videos in this folder
        this_folder_name = this_folder.stem # Last component of the path

        if sub_folder_count > 0 and media_file_count == 0:
            # This folder contains other folders but no files, so it will be a folder in Photos.
            logger.info(f'Folder "{this_folder_name}" contains subfolders. Creating folder...')
            
            try:
                # Create a new folder under parent_folder.
                new_folder = photo_library.create_folder(this_folder_name, parent_folder) # Create the folder
                logger.info(f'Created folder "{new_folder.name}" with ID "{new_folder.uuid}"')
                folders_created += 1
            except:
                e = sys.exc_info()[1]
                logger.error(f'Failed to create folder "{this_folder_name}"')
                logger.error(str(e))
                continue # If the folder couldn't be created, we can't pass it to process_folder as parent_folder. Skip to the next folder in `folders`.

            # Continue to process this folder. new_folder is now the the parent folder.
            process_folder(this_folder, new_folder, photo_library)

        elif sub_folder_count == 0 and media_file_count > 0:
            # This folder contains media files, so it will be an album in Photos.
            logger.info(f'Folder "{this_folder_name}" contains media files. Creating album...')
            
            try:
                if parent_folder is None:
                    # If parent_folder is None, the album is not in a folder. Create the album at the root of the Photos library.
                    new_album = photo_library.create_album(this_folder_name)
                else:
                    # Else the album is in a folder.
                    new_album = parent_folder.create_album(this_folder_name)
                logger.info(f'Created album "{new_album.name}" with ID "{new_album.uuid}"')
                albums_created += 1
            except:
                e = sys.exc_info()[1]
                logger.error(f'Failed to create album "{this_folder_name}"')
                logger.error(str(e))

def main():
    # Use the module-level variables.
    global media_extensions, expected_folder_count, expected_album_count, folders_created, albums_created

    # Change this to the path of the folder where the photos were exported from Lightroom.
    photos_path = '/Path/To/Lightroom/Export'

    # Change this to the path to your Photos library.
    photo_library_path = '/Path/To/Photos.photoslibrary'

    # Find the file extensions in photos_path so that we can identify media files. If the export from Lightroom was correct, only media files will have an extension. Everything else should be a dotfile (e.g., .DS_Store).
    for root, dirs, files in os.walk(photos_path):
        for f in files:
            # Get the file extension.
            ext = os.path.splitext(f)[1]

            if len(ext) > 0:
                # If ext isn't an empty string, the file has an extension.
                # Strip the leading '.' and add ext to extensions.
                ext_no_dot = ext[1:]
                
                if ext_no_dot not in media_extensions:
                    media_extensions.append(ext_no_dot)

    # Get expected counts.
    for root, dirs, files in os.walk(photos_path):
        for d in dirs:
            dir_path = os.path.join(root, d)
            path = Path(dir_path)

            if len(get_sub_folders(path)) > 0:
                # This folder contains subfolders. It will be a folder in Photos.
                expected_folder_count += 1
            elif len([f for f in get_files(path) if is_media_file(f)]) > 0:
                # This folder contains media files. It will be an album in Photos.
                expected_album_count += 1
    
    # Open the Photos library.
    try:
        photo_library = photoscript.PhotosLibrary()
    except:
        e = sys.exc_info()[1]
        logger.critical('Failed to create an instance of PhotosLibrary')
        logger.critical(str(e))
        sys.exit()

    try:
        photo_library.open(photo_library_path)
        logger.info(f'Library "{photo_library_path}" opened')
    except:
        e = sys.exc_info()[1]
        logger.critical(f'Failed to open library "{photo_library_path}"')
        logger.critical(str(e))
        sys.exit()
    
    # Create folders and albums.
    logger.info(f'Starting in directory "{photos_path}"')
    process_folder(photos_path, None, photo_library)

    # Compare expected and actual counts.
    # Folders
    if expected_folder_count != folders_created:
        logger.error(f'Folders created: {folders_created}. Expected {expected_folder_count}.')
    else:
        logger.info(f'Folders created: {folders_created}. Expected {expected_folder_count}.')

    # Albums
    if expected_album_count != albums_created:
        logger.error(f'Albums created: {albums_created}. Expected {expected_album_count}.')
    else:
        logger.info(f'Albums created: {albums_created}. Expected {expected_album_count}.')

    logger.info('Script finished.')

if __name__ == '__main__':
    main()