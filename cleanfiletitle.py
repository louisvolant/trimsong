#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__= 1.0

import logging, os


# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# Once finished, simply desactivate the virtual environment using "deactivate"


def rename_file(dir_path, filename):
    # Vérifier si le fichier se termine par "_trimmed.mp3"
    if filename.endswith("_trimmed.mp3"):
        # Construire le nouveau nom de fichier
        new_filename = filename.replace("_trimmed.mp3", ".mp3")
        # Construire les chemins complets des fichiers
        old_filepath = os.path.join(dir_path, filename)
        new_filepath = os.path.join(dir_path, new_filename)
        
        # Vérifier si le fichier sans "_trimmed" existe déjà
        if os.path.exists(new_filepath):
            # Si oui, le supprimer
            os.remove(new_filepath)
            print(f"Deleted existing file: {new_filepath}")
        
        
        # Renommer le fichier
        os.rename(old_filepath, new_filepath)
        print(f"Renamed: {old_filepath} to {new_filepath}")


def main():
    dir_path = '.'

    for file_path in os.listdir(dir_path):
        logging.info('Processing: {0}'.format(file_path))
        if(file_path.title().endswith('.Mp3')):
            rename_file(dir_path, file_path)


if __name__ == '__main__':
    ## Initialize logging before hitting main, in case we need extra debuggability
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()