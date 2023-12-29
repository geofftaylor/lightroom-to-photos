"""
Compare the media files in a Photos library to the media files in a folder tree.
Creates a timestamped log file and a CSV file of media files missing from Photos in the same directory as the script.
"""

import sys, os, logging, photoscript, csv
from datetime import datetime
from pathlib import Path

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

fh = logging.FileHandler(os.path.join(script_dir, 'verify-import-%s.log' % now_str))
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)

def get_files(path, exclude_filenames=[]):
    """Return a list of the files (as Path objects) in the directory `path`."""
    files_in_path = []

    if not isinstance(path, Path):
        path = Path(path)

    if path.is_dir():
        files_in_path = [f for f in path.iterdir() if f.is_file() and f.name not in exclude_filenames]

    return files_in_path
            

def main():
    # Change this to the path of the folder where the photos were exported from Lightroom.
    photos_path = '/Path/To/Lightroom/Export'

    # Change this to the path to your Photos library.
    photo_library_path = '/Path/To/Photos.photoslibrary'

    # Setup for CSV output of missing files.
    csv_file = os.path.join(script_dir, 'missing-files.csv')
    missing_files = []
    
    # Open the Photos library
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
    
    # Get all albums.
    all_albums = photo_library.albums()

    albums_checked = 0
    albums_with_errors = []

    for a in all_albums:
        items_missing = 0

        album_path = a.path_str()
        logger.debug(f'Album: {album_path}')
        album_dir = Path(photos_path, album_path) # Path to the album's corresponding directory in the import folder.
        logger.debug(f'Directory: {album_dir}')


        # The photos in album_dir.
        photos_in_dir = [f.name for f in get_files(album_dir, exclude_filenames=['.DS_Store'])]
        photos_in_dir_count = len(photos_in_dir)

        # The photos in the album.
        photos_in_album = [p.filename for p in a.photos()]
        photos_in_album_count = len(photos_in_album)

        if photos_in_album_count != photos_in_dir_count:
            logger.error(f'COUNT MISMATCH: Directory "{album_dir}" contains {photos_in_dir_count} files but album "{album_path}" contains {photos_in_album_count} files.')
        else:
            logger.debug(f'COUNTS OK: Directory "{album_dir}" contains {photos_in_dir_count} files. Album "{album_path}" also contains {photos_in_album_count} files.')

        for p in photos_in_dir:
            if p not in photos_in_album:
                items_missing += 1
                
                missing = {
                    'Album': album_path,
                    'Directory': album_dir,
                    'File': p
                }

                missing_files.append(missing)

                logger.error(f'{p} not found in album "{album_path}"')

        if items_missing > 0:
            albums_with_errors.append(album_path)
            logger.error(f'Album "{album_path}" is missing {items_missing} items.')
    
        albums_checked += 1

        if albums_checked == 1 or albums_checked % 20 == 0 or albums_checked == len(all_albums):
            logger.info(f'Checked {albums_checked} of {(len(all_albums))} albums.')

    logger.info(f'{len(albums_with_errors)} albums are missing items.')

    if len(albums_with_errors) > 0:
        with open(csv_file, 'w', newline='') as csv_out:
            field_names = ['Album', 'Directory', 'File']
            writer = csv.DictWriter(csv_out, fieldnames=field_names)

            writer.writeheader()
            
            for row in missing_files:
                writer.writerow(row)

        logger.info(f'See {csv_file} for list of missing items.')

        logger.debug('ALBUMS MISSING ITEMS:')

        for a in sorted(albums_with_errors):
            logger.debug(a)

    logger.info('Script finished.')

    sys.exit()

if __name__ == '__main__':
    main()