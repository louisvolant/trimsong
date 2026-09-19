#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 2.1

import logging
import os
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing as mp

TARGET_BITRATE = "128k"
BASIC_SILENCE_THRESHOLD_dBFS = -45
BASIC_MINIMUM_SILENCE_LENGTH = 100  # This is for detecting silence, not for trimming
CONFIGURABLE_SILENCE_TO_LEAVE_MS = 200  # Configurable parameter, in ms


# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# python3 trimsong.py
# Once finished, simply deactivate the virtual environment using "deactivate"

def get_duration_ms(audio_file):
    """Return duration of audio file in milliseconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        audio_file
    ]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return int(float(result.stdout.strip()) * 1000)


def get_silence_ranges_ffmpeg(audio_file, silence_threshold=-45, min_silence_len=0.1):
    """Return list of (start_ms, end_ms) silence ranges using ffmpeg silencedetect."""
    cmd = [
        "ffmpeg", "-i", audio_file,
        "-af", f"silencedetect=n={silence_threshold}dB:d={min_silence_len}",
        "-f", "null", "-"
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    ranges = []
    start = None
    for line in result.stderr.splitlines():
        if "silence_start" in line:
            start = float(line.split("silence_start: ")[1]) * 1000
        elif "silence_end" in line and start is not None:
            end = float(line.split("silence_end: ")[1].split(" ")[0]) * 1000
            ranges.append((int(start), int(end)))
            start = None
    return ranges


def trim_silence(audio_file, silence_threshold=BASIC_SILENCE_THRESHOLD_dBFS,
                 min_silence_len_to_detect=BASIC_MINIMUM_SILENCE_LENGTH / 1000,
                 silence_to_leave_ms=CONFIGURABLE_SILENCE_TO_LEAVE_MS):
    """
    Trims leading and trailing silence from an audio file, leaving a configurable minimum
    amount of silence if the detected silence is longer than that minimum.

    Args:
        audio_file (str): Path to the input audio file.
        silence_threshold (int): The silence threshold in dBFS.
        min_silence_len_to_detect (float): The minimum length of silence in seconds to detect.
        silence_to_leave_ms (int): The minimum amount of silence in ms to leave if
                                    the detected silence is longer than this value.

    Returns:
        tuple: (start_trim_ms, end_trim_ms) trim points in milliseconds.
    """
    sound_length = get_duration_ms(audio_file)

    # Detect silence using ffmpeg
    silence_ranges = get_silence_ranges_ffmpeg(
        audio_file,
        silence_threshold=silence_threshold,
        min_silence_len=min_silence_len_to_detect
    )

    start_trim = 0
    end_trim = sound_length

    if silence_ranges:
        logging.info('Detected silence_ranges: {0} | Sound length: {1}'.format(silence_ranges, sound_length))

        # Handle leading silence
        if silence_ranges[0][0] == 0:
            leading_silence_duration = silence_ranges[0][1] - silence_ranges[0][0]
            if leading_silence_duration > silence_to_leave_ms:
                start_trim = silence_ranges[0][1] - silence_to_leave_ms
                logging.info(
                    f'Trimming leading silence from {leading_silence_duration}ms to {silence_to_leave_ms}ms. Start trim at: {start_trim}')
            else:
                logging.info(
                    f'Leading silence ({leading_silence_duration}ms) is less than or equal to {silence_to_leave_ms}ms. No leading trim applied.')
                start_trim = 0
        else:
            logging.info('No leading silence detected starting at 0ms.')
            start_trim = 0

        # Handle trailing silence
        if silence_ranges[-1][1] == sound_length:
            trailing_silence_duration = silence_ranges[-1][1] - silence_ranges[-1][0]
            if trailing_silence_duration > silence_to_leave_ms:
                end_trim = silence_ranges[-1][0] + silence_to_leave_ms
                logging.info(
                    f'Trimming trailing silence from {trailing_silence_duration}ms to {silence_to_leave_ms}ms. End trim at: {end_trim}')
            else:
                logging.info(
                    f'Trailing silence ({trailing_silence_duration}ms) is less than or equal to {silence_to_leave_ms}ms. No trailing trim applied.')
                end_trim = sound_length
        else:
            logging.info('No trailing silence detected extending to the end of the sound.')
            end_trim = sound_length

    else:
        logging.info('No detected silence range at all.')
        start_trim = 0
        end_trim = sound_length

    # Ensure start_trim is not greater than end_trim
    if start_trim > end_trim:
        logging.warning(
            f"Calculated start_trim ({start_trim}) is greater than end_trim ({end_trim}). Resetting to default values.")
        start_trim = 0
        end_trim = sound_length

    return start_trim, end_trim


def process_file(file_path):
    """Process a single file and return timing/result info (no logging during execution)."""
    start_time = time.time()
    output_file_path = file_path.replace(".mp3", "_trimmed.mp3")

    start_trim_ms, end_trim_ms = trim_silence(
        file_path,
        silence_to_leave_ms=CONFIGURABLE_SILENCE_TO_LEAVE_MS
    )

    # Convert ms to seconds for ffmpeg
    start_sec = start_trim_ms / 1000.0
    duration_sec = (end_trim_ms - start_trim_ms) / 1000.0

    cmd = [
        "ffmpeg", "-y",
        "-i", file_path,
        "-ss", str(start_sec),
        "-t", str(duration_sec),
        "-codec:a", "libmp3lame", "-b:a", TARGET_BITRATE,
        output_file_path
    ]
    subprocess.run(cmd, check=True, stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    os.remove(file_path)

    elapsed = time.time() - start_time
    return file_path, output_file_path, elapsed


def main():
    dir_path = '.'
    mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    results = []
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as executor:
        futures = {executor.submit(process_file, f): f for f in mp3_files}
        for future in futures:
            result = future.result()
            results.append(result)

    # Print summary logs AFTER all parallel work is done (preserves timing clarity)
    for i, (file_path, outputFilePath, elapsed) in enumerate(results):
        logging.info(f'Processing file {i + 1}/{total_files}: {file_path}')
        logging.info('Trimming origin file: {0}. New file : {1}'.format(file_path, outputFilePath))
        logging.info(f"Processed '{file_path}' in {elapsed:.2f}s")


if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()