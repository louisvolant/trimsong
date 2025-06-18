#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.0

import logging
import os
from pydub import AudioSegment

# Target bitrate for the output MP3 file
TARGET_BITRATE = "128k"


# README
# This script converts all .wav files in the current directory to .mp3 format.
#
# To execute:
# 1. Set up a virtual environment:
#    python3 -m venv myenv
#    source myenv/bin/activate
#
# 2. Install required packages (pydub requires ffmpeg/libav):
#    pip install pydub
#
# 3. Run the script:
#    python3 wav_to_mp3.py
#
# 4. Deactivate the virtual environment when finished:
#    deactivate

def handle_wav_file(input_wav_path):
    """
    Loads a .wav file and exports it as an .mp3 file with the target bitrate.

    Args:
        input_wav_path (str): The path to the input .wav file.
    """
    # Construct the output filename by replacing the extension
    output_mp3_path = os.path.splitext(input_wav_path)[0] + ".mp3"

    logging.info(f"Converting '{input_wav_path}' to '{output_mp3_path}'")

    try:
        # Load the .wav file
        audio = AudioSegment.from_wav(input_wav_path)

        # Export the audio to .mp3 format with the specified bitrate
        audio.export(output_mp3_path, format="mp3", bitrate=TARGET_BITRATE)

        logging.info(f"Successfully exported '{output_mp3_path}' with a bitrate of {TARGET_BITRATE}.")

    except FileNotFoundError:
        logging.error(f"Error: The file '{input_wav_path}' was not found.")
    except Exception as e:
        logging.error(f"An error occurred while processing '{input_wav_path}': {e}")


def main():
    """
    Finds all .wav files in the current directory and processes them.
    """
    dir_path = '.'
    # Find all files ending with .wav (case-insensitive)
    wav_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.wav')]
    total_files = len(wav_files)

    if total_files == 0:
        logging.warning("No .wav files found in the current directory. Nothing to do.")
        return

    logging.info(f"Found {total_files} .wav file(s) to process.")

    # Process each file and log the progress
    for i, file_path in enumerate(wav_files):
        logging.info(f"--- Processing file {i + 1}/{total_files}: {file_path} ---")
        handle_wav_file(file_path)


if __name__ == '__main__':
    # Initialize logging to provide informative output
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()