#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__= 1.0

import logging, os
from pydub import AudioSegment
from pydub.silence import detect_silence

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

    for file_path in os.listdir(dir_path):
        logging.info('Processing: {0}'.format(file_path))
        if file_path.lower().endswith('.mp3'):
            handleMp3File(file_path)

if __name__ == '__main__':
    # Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()
