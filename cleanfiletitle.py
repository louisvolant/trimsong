#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.0

import logging
import os

# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# Once finished, simply deactivate the virtual environment using "deactivate"

# List of strings to remove from filenames
STRINGS_TO_REMOVE = [
    "(Official Audio)",
    "(Official HD Video)",
    "(Official Video)",
    "(Official Lyric Video)",
    "(Official Music Video)",
    "(Lyrics)",
    "(Clip Officiel)",
    "_trimmed",
    "_soundincreased"
]

def clean_filename(filename):
    """
    Removes specified strings from the filename.

    Args:
        filename (str): The original filename.

    Returns:
        str: The cleaned filename.
    """
    for string_to_remove in STRINGS_TO_REMOVE:
        filename = filename.replace(string_to_remove, "").strip()  # Remove and strip whitespace
    return filename

def rename_file(dir_path, filename):
    """
    Renames a file after cleaning its name.

    Args:
        dir_path (str): The directory path of the file.
        filename (str): The original filename.
    """
    original_filepath = os.path.join(dir_path, filename)
    cleaned_filename = clean_filename(filename)

    if cleaned_filename != filename:  # Only rename if the filename was modified
        new_filepath = os.path.join(dir_path, cleaned_filename)

        # Check if the new filename already exists
        if os.path.exists(new_filepath):
            os.remove(new_filepath)
            print(f"Deleted existing file: {new_filepath}")

        os.rename(original_filepath, new_filepath)
        print(f"Renamed: {original_filepath} to {new_filepath}")

def main():
    """
    Main function to process files in the current directory.
    """
    dir_path = '.'

    for file_path in os.listdir(dir_path):
        logging.info('Processing: {0}'.format(file_path))
        if file_path.lower().endswith('.mp3'): # case insensitive check
            rename_file(dir_path, file_path)

if __name__ == '__main__':
    # Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()