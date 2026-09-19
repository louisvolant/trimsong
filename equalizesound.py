#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 2.1

import json
import logging
import os
import subprocess
import time

BASIC_THRESHOLD_dBFS = -15

# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# python3 equalizesound.py
# Once finished, simply deactivate the virtual environment using "deactivate"


def get_mean_volume_dBFS(audio_file):
    """Return the mean volume in dBFS using ffprobe (volumedetect filter)."""
    cmd = [
        "ffmpeg", "-i", audio_file,
        "-af", "volumedetect",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    for line in result.stderr.splitlines():
        if "mean_volume" in line:
            # e.g. "  mean_volume: -18.3 dB"
            return float(line.split("mean_volume:")[1].split("dB")[0].strip())
    return None


def handleMp3File(audio_file):
    # Calculate the average level in dBFS
    average_level = get_mean_volume_dBFS(audio_file)
    if average_level is None:
        logging.warning(f"Could not determine volume for '{audio_file}'. Skipping.")
        return

    print(f"Average level: {average_level} dBFS")

    # Increase the volume if necessary
    if average_level < BASIC_THRESHOLD_dBFS:
        increase = BASIC_THRESHOLD_dBFS - average_level
        print(f"Volume increased by {increase:.2f} dB")

        # Create the new filename with "_soundincreased" suffix
        file_name, file_extension = os.path.splitext(audio_file)
        new_file_name = f"{file_name}_soundincreased{file_extension}"

        # Export the audio file with increased volume using ffmpeg
        cmd = [
            "ffmpeg", "-i", audio_file,
            "-af", f"volume={increase:.4f}dB",
            "-codec:a", "libmp3lame", "-q:a", "2",
            new_file_name
        ]
        subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        os.remove(audio_file)
        print(f"Exported as: {new_file_name}")
    else:
        print("The sound level is sufficient, no modification necessary.")


def main():
    dir_path = '.'
    mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    for i, file_path in enumerate(mp3_files):
        logging.info(f'Processing file {i + 1}/{total_files}: {file_path}')
        start_time = time.time()
        handleMp3File(file_path)
        elapsed = time.time() - start_time
        logging.info(f"Processed '{file_path}' in {elapsed:.2f}s")

if __name__ == '__main__':
    # Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()