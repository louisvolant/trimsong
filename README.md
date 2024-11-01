# trimsong
Trim mp3 song and store it to mp3 (128K bitrate)

## Requirements

1. First install the required packages

Python3, pydub

````
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
# When finished, desactivate the venv using "deactivate"
````

## How to execute

After having put all mp3 files to be trimmed in the script folder.
Run the following :

````
$ python3 trimsong.py 
````
Once done, you can remove former file and rename the trimmed files using : 

````
$ python3 cleanfiletitle.py 
````
