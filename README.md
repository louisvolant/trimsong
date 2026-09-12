# trimsong

Collection of Python audio processing scripts to equalize loudness, trim silence, and clean song titles from MP3 files.

## Requirements

1. Install system dependencies:
   - Python 3
   - `ffmpeg` (required by `pydub` and silence detection)

2. Set up the virtual environment and install Python packages:

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
# When finished, deactivate the venv using "deactivate"
```

## Available Scripts

- **`equalizesound.py`**: Increases the audio volume if the average loudness is below `-15 dBFS`.
- **`trimsong.py`**: Fast parallel leading and trailing silence trimming using ffmpeg silencedetect (128 kbps output).
- **`cleanfiletitle.py`**: Cleans and standardizes MP3 filenames by removing common tags (e.g., `[HD]`, `(Official Video)`, `(Video Oficial)`, `(Visualizer)`, `- Topic`, etc.) and normalizing spacing.
- **`wav_to_mp3.py`**: Converts all `.wav` files in the directory to `.mp3` format.

## How to execute

Place all MP3 files to be processed in the project directory, then run the full pipeline:

```bash
python3 equalizesound.py && python3 cleanfiletitle.py && python3 trimsong.py && python3 cleanfiletitle.py
```
