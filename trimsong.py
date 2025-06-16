#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 1.1

import logging, os
from pydub import AudioSegment
from pydub.silence import detect_silence

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
# Once finished, simply desactivate the virtual environment using "deactivate"

def trim_silence(audio_file, silence_threshold=BASIC_SILENCE_THRESHOLD_dBFS,
                 min_silence_len_to_detect=BASIC_MINIMUM_SILENCE_LENGTH,
                 silence_to_leave_ms=CONFIGURABLE_SILENCE_TO_LEAVE_MS):
    """
    Trims leading and trailing silence from an audio file, leaving a configurable minimum
    amount of silence if the detected silence is longer than that minimum.

    Args:
        audio_file (str): Path to the input audio file.
        silence_threshold (int): The silence threshold in dBFS.
        min_silence_len_to_detect (int): The minimum length of silence in ms to detect.
        silence_to_leave_ms (int): The minimum amount of silence in ms to leave if
                                    the detected silence is longer than this value.

    Returns:
        pydub.AudioSegment: The trimmed audio segment.
    """
    # Load the audio file
    sound = AudioSegment.from_mp3(audio_file)

    sound_length = len(sound)

    # Detect silence
    silence_ranges = detect_silence(sound, min_silence_len=min_silence_len_to_detect, silence_thresh=silence_threshold)

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
        # Check if the last silence range extends to the end of the sound
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

    # Trim the audio
    trimmed_sound = sound[start_trim:end_trim]

    return trimmed_sound


def handleMp3File(inputFilePath):
    outputFilePath = inputFilePath.replace(".mp3", "_trimmed.mp3")
    logging.info('Trimming origin file: {0}. New file : {1}'.format(inputFilePath, outputFilePath))
    # Pass the configurable silence to leave to the trim_silence function
    trimmed_audio = trim_silence(inputFilePath, silence_to_leave_ms=CONFIGURABLE_SILENCE_TO_LEAVE_MS)
    trimmed_audio.export(outputFilePath, format="mp3", bitrate=TARGET_BITRATE)


def main():
    dir_path = '.'
    mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    for i, file_path in enumerate(mp3_files):
        logging.info(f'Processing file {i + 1}/{total_files}: {file_path}') # add progression
        handleMp3File(file_path)


if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()