#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.0

import logging
import os
import re

# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# Once finished, simply deactivate the virtual environment using "deactivate"

# List of strings to remove from filenames (case-insensitive)
STRINGS_TO_REMOVE = [
    r"\(Audio( Officiel)?\)",
    r"[(\[]Official Audio[)\]]",
    r"[(\[]Official Visualizer[)\]]",
    r"[(\[]Official (?:(?:[A-Za-z\s]+) )?Video[)\]]",
    r"Official Lyrics Video",
    r"\(Lyrics?\)",
    r"\(Clip Officiel\)",
    r"\(lyric(?:s)? Video\)",
    r"\(Paroles\)",
    r"\(Vidéo officielle\)",
    r"\(Clip officiel HD\)",
    r"\(Official Lyrics Vidéo\)",
    r"- Official Music Video",
    r"_trimmed",
    r"_soundincreased",
    r"-\s*Topic\s*",
    r"\(official video reworked\)",
    r"\(Avec paroles\)",
    r"\(Official Visualiser\)",
    r"\s*-\s*reworked",
    r"\s*\(official video\)"
]

def clean_filename(filename):
    """
    Removes specified strings from the filename (case-insensitive) using regex.

    Args:
        filename (str): The original filename.

    Returns:
        str: The cleaned filename.
    """
    # Separate the extension from the base name
    base_name, ext = os.path.splitext(filename)

    for string_to_remove in STRINGS_TO_REMOVE:
        base_name = re.sub(string_to_remove, "", base_name, flags=re.IGNORECASE)

    # Remove any trailing hyphens or spaces that might result from removals
    base_name = base_name.strip(' -')

    """
    Removes potential spaces from the filename
    """
    # This regex now applies to the base_name to clean up spaces before the extension is re-added
    base_name = re.sub(r'\s+$', '', base_name) # Remove trailing spaces

    return base_name + ext

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

        if new_filepath.lower().endswith(".mp3"): # check if it ends with .mp3
            # Check if the new filename already exists
            if os.path.exists(new_filepath):
                # If the target file already exists and is the same as the original after cleaning,
                # we don't need to do anything. Otherwise, we remove it to prevent conflicts.
                if os.path.samefile(original_filepath, new_filepath):
                    print(f"File already clean: {original_filepath}")
                    return
                else:
                    os.remove(new_filepath)
                    print(f"Deleted existing file: {new_filepath}")

            os.rename(original_filepath, new_filepath)
            print(f"Renamed: {original_filepath} to {new_filepath}")
        else :
            print(f"Error: {cleaned_filename} doesn't end with .mp3 or has an unexpected format.")


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