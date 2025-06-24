#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.2

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
# List of strings to remove from filenames (case-insensitive)
STRINGS_TO_REMOVE = [
    r"\(Audio( Officiel)?\)",
    r"[(\[]Official Audio[)\]]",
    r"[(\[]Official Visualizer[)\]]",
    r"[(\[]Official (?:(?:[A-Za-z\s]+) )?Video[)\]]",
    r"Official Lyrics Video",
    r"[(\[]Lyrics?[)\]]",
    r"\(Clip Officiel\)",
    r"\(lyric(?:s)?\s*vid[eé]o\)",
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
    r"\s*\(official video\)",
    r"\(Videoclip\)",
    r"\(Offizielles Musikvideo\)"
]


def capitalize_after_paren(filename):
    """
    Capitalizes the first letter after an opening parenthesis in a filename.

    Args:
        filename (str): The original filename.

    Returns:
        str: The filename with corrected capitalization.
    """
    return re.sub(r'(\()\s*([a-z])', lambda m: m.group(1) + m.group(2).upper(), filename)


def clean_filename(filename):
    """
    Removes specified strings from the filename (case-insensitive) using regex and corrects capitalization,
    and standardizes various dash characters.

    Args:
        filename (str): The original filename.

    Returns:
        str: The cleaned and formatted filename.
    """
    # Separate the extension from the base name
    base_name, ext = os.path.splitext(filename)

    # Standardize the long dash (en dash '–' and em dash '—') to a standard hyphen-minus ('-')
    # Replace the spaced long dash ' – ' with the desired ' - '
    base_name = base_name.replace(' – ', ' - ')
    # Replace non-spaced en dash ('–') and em dash ('—') with standard hyphen-minus ('-')
    base_name = base_name.replace('—', '-')
    base_name = base_name.replace('–', '-')
    # Remove any resulting double spaces or double hyphens that might occur from the replacement
    base_name = base_name.replace('  ', ' ')
    base_name = base_name.replace('--', '-')


    for string_to_remove in STRINGS_TO_REMOVE:
        base_name = re.sub(string_to_remove, "", base_name, flags=re.IGNORECASE)

    # Correct capitalization after opening parentheses
    base_name = capitalize_after_paren(base_name)

    # Remove any trailing hyphens or spaces that might result from removals
    base_name = base_name.strip(' -')

    # Removes potential spaces from the filename
    base_name = re.sub(r'\s+$', '', base_name)  # Remove trailing spaces

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