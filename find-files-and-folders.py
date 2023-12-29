"""
In Lightroom, a folder can contain files (photos and videos) and other folders.
In Photos, a folder can only contain albums. Albums can only contain photos and videos.
This script finds Lightroom folders that contain both files and folders.
If any folders contain both files and folders, the files should be moved to a subfolder in preparation for the migration to Photos.
"""

import os

def main():
    # Change this to the path of your main Lightroom directory (where the photos are stored).
    photo_dir = '/Path/To/Lightroom/Photos'
    
    contains_both = []

    for root, dirs, files in os.walk(photo_dir):
        for d in dirs:
            full_path = os.path.join(root, d)
            contents = os.listdir(full_path)

            # If at least one item is a file (and is not a dot file, e.g., .DS_Store) and at least one item is a directory, this directory contains files and subdirectories.
            if any([c for c in contents if os.path.isfile(os.path.join(full_path, c)) and (not c.startswith('.'))]) and any([c for c in contents if os.path.isdir(os.path.join(full_path, c))]):
                contains_both.append(full_path)

    print('Folders that contain files and folders:')
    
    if len(contains_both) == 0:
        print('None found.')
    else:
        for c in contains_both:
            print(c)

if __name__ == '__main__':
    main()