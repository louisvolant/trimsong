#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__= 1.0

import logging, os
from pydub import AudioSegment

BASIC_THRESHOLD_dBFS = -15

# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# python3 equalizesound.py
# Once finished, simply deactivate the virtual environment using "deactivate"

def handleMp3File(audio_file):
    # Load the MP3 file
    audio = AudioSegment.from_mp3(audio_file)

    # Calculate the average level in dBFS
    average_level = audio.dBFS

    print(f"Average level: {average_level} dBFS")

    # Increase the volume if necessary
    if average_level < BASIC_THRESHOLD_dBFS:
        increase = BASIC_THRESHOLD_dBFS - average_level
        audio_increased = audio + increase

        print(f"Volume increased by {increase} dB")

        # Create the new filename with "_soundincreased" suffix
        file_name, file_extension = os.path.splitext(audio_file)
        new_file_name = f"{file_name}_soundincreased{file_extension}"

        # Export the audio file with increased volume
        audio_increased.export(new_file_name, format="mp3")
        print(f"Exported as: {new_file_name}")
    else:
        print("The sound level is sufficient, no modification necessary.")

def main():
    dir_path = '.'
    mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    for i, file_path in enumerate(mp3_files):
        logging.info(f'Processing file {i + 1}/{total_files}: {file_path}') # Add progression
        handleMp3File(file_path)

if __name__ == '__main__':
    # Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()