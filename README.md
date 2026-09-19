# trimsong

Collection of Python audio processing scripts to equalize loudness, trim silence, and clean song titles from MP3 files.

## Requirements

1. Install system dependencies:
   - Python 3
   - `ffmpeg` / `ffprobe` (used directly for all audio processing and silence detection)

   On macOS:
   ```bash
   brew install ffmpeg
   ```

2. Set up the virtual environment:

   ```bash
   python3 -m venv myenv
   source myenv/bin/activate
   pip install -r requirements.txt
   # When finished, deactivate the venv using "deactivate"
   ```

## Available Scripts

- **`equalizesound.py`**: Calculates the average audio level via `ffprobe` (`volumedetect`). If the mean loudness is below `-15 dBFS`, exports an amplified MP3 and removes the un-amplified original to prevent duplicate conflicts.
- **`trimsong.py`**: Fast parallel leading and trailing silence trimming using `ffmpeg` `silencedetect` (128 kbps output). Leaves a configurable amount of silence (default 200 ms) and removes the untrimmed original once processed.
- **`cleanfiletitle.py`**: Standardizes MP3 filenames with advanced cleaning:
  - Strips junk promotional and technical tags (e.g. `Official Video`, `Official Audio`, `Visualizer Officiel`, `OFFICIAL _MUSIC`, `[HD]`, `[4K]`, `- Topic`, etc.) both standalone and inside parentheses/brackets while preserving legitimate information like subgenres or remix tags (e.g. `(Afro House)`).
  - Normalizes dashes and replaces orphan separator underscores with proper delimiters.
  - Applies smart title capitalization while preserving artist casing, acronyms (`RMX`, `HD`, `DJ`), and lowercase middle prepositions (`de`, `to`, `or`, etc.).
  - Protects against duplicate collisions to ensure processed files are never overwritten by untreated files.
- **`wav_to_mp3.py`**: Converts all `.wav` files in the directory to `.mp3` format using `ffmpeg`.

## How to execute

Place all MP3 files to be processed in the project directory, then run the full pipeline:

```bash
python3 equalizesound.py && python3 cleanfiletitle.py && python3 trimsong.py && python3 cleanfiletitle.py && mv *.mp3 ../cleanMp3
```
