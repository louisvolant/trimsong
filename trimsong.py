#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__= 1.0

import logging, os
from pydub import AudioSegment
from pydub.silence import detect_silence

TARGET_BITRATE = "128k"


# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install pydub 
# python3 trimsong.py
# Once finished, simply desactivate the virtual environment using "deactivate"



def trim_silence(audio_file, silence_threshold=-50, min_silence_len=100):
    # Load the audio file
    sound = AudioSegment.from_mp3(audio_file)
    
    sound_length = len(sound)
    
    # Detect silence
    silence_ranges = detect_silence(sound, min_silence_len=min_silence_len, silence_thresh=silence_threshold)
    
    # If there's silence at the beginning or end
    if silence_ranges:
        logging.info('Detected silence_ranges: {0} | Sound length: {1}'.format(silence_ranges, sound_length))

        # Finding leading silence
        if silence_ranges[0][0] == 0:
            start_trim = silence_ranges[0][1]
        else:
            start_trim = 0
        
        # Finding trailing silence
        if (silence_ranges[-1][0] != 0 & silence_ranges[-1][1] == len(sound)) :
            end_trim = silence_ranges[-1][0]
        else:
            end_trim = len(sound)

    else:
        logging.info('No detected silence range')

        start_trim = 0
        end_trim = len(sound)
    
    # Trim the audio
    trimmed_sound = sound[start_trim:end_trim]
    
    return trimmed_sound


def handleMp3File(inputFilePath):
    outputFilePath = inputFilePath.replace(".mp3", "_trimmed.mp3")
    logging.info('Trimming origin file: {0}. New file : {1}'.format(inputFilePath, outputFilePath))
    trimmed_audio = trim_silence(inputFilePath)
    trimmed_audio.export(outputFilePath, format="mp3", bitrate=TARGET_BITRATE)



def main():
    dir_path = '.'

    for file_path in os.listdir(dir_path):
        logging.info('Processing: {0}'.format(file_path))
        if(file_path.title().endswith('.Mp3')):
            handleMp3File(file_path)




if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()