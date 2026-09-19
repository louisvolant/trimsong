#!/usr/local/bin/python3
__author__ = 'Louis Volant'
__version__ = 2.0

import logging
import os
import re
import unicodedata

# README
# execute with
# python3 -m venv myenv
# source myenv/bin/activate
# pip install -r requirements.txt
# Once finished, simply deactivate the virtual environment using "deactivate"

# Short words that should stay lowercase in Title Case unless at the beginning/end or after a separator
LOWERCASE_WORDS = {
    'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 'to', 'by', 'of', 'in', 'as',
    'de', 'du', 'des', 'le', 'la', 'les', 'un', 'une', 'et', 'ou', 'en', 'y', 'o', 'feat', 'ft'
}

# Junk patterns that appear inside parentheses or brackets
JUNK_INSIDE_PARENS = [
    # Visualizer patterns (with or without 'Official', 'Officiel', 'Video')
    r'(?:Official[\s_]+)?(?:Video[\s_]+)?Visuali[sz](?:er|eur|ateur)?(?:[\s_]+(?:Officiel(?:le)?|Official))?(?:[\s_]+Video)?',
    # Official Music / Video / Audio patterns with possible underscores or spaces
    r'Official[\s_]+(?:Music[\s_]+)?(?:Video|Audio|Track)',
    r'Official[\s_]+Music',
    r'Official[\s_]+Lyrics?[\s_]*(?:Video)?',
    r'Lyric(?:s)?[\s_]*vid[eé]o',
    r'Lyrics?',
    r'Paroles',
    r'(?:Avec|With)[\s_]+paroles',
    # French / Spanish / German
    r'(?:Clip|Vid[eé]o|Audio)[\s_]+Officiel(?:le)?(?:[\s_]+HD)?',
    r'(?:Video[\s_]*clip|V[ií]d[eé]o(?:[\s_]+(?:musical|lyric|letra))?|Audio|Clip|Music[\s_]+Video)[\s_]+Oficial(?:[\s_]+HD)?',
    r'Offizielles[\s_]+(?:Musik)?video',
    r'Videoclip',
    r'Audio',
    r'(?:Official[\s_]+)?(?:Video[\s_]+)?reworked',
    # Quality / Resolution
    r'(?:(?:Ultra[\s_]+)?HD|HQ|4K|2K|1080p|720p)(?:[\s_]*(?:1080p|720p|60fps|UHD|HD))?',
]

# Patterns to remove outside parentheses / standalone
STRINGS_TO_REMOVE_STANDALONE = [
    r'-\s*Topic\b',
    r'-\s*Official\s+Music\s+Video\b',
    r'-\s*Official\s+Video\b',
    r'-\s*V[ií]d[eé]o\s+Oficial\b',
    r'-\s*Clip\s+Officiel\b',
    r'-\s*reworked\b',
    r'-\s*Visuali[sz](?:er|eur|ateur)?(?:\s+(?:Officiel|Official))?\b',
    r'_soundincreased\b',
    r'_trimmed\b',
]


def clean_parens_content(base_name):
    """
    Removes junk promotional tags from inside parentheses or brackets.
    If only junk was present, the empty brackets/parentheses are completely removed.
    If useful content remains (e.g. remix or genre like 'Afro House'), it is preserved.
    """
    def process_match(m):
        open_b = m.group(1)
        content = m.group(2)
        close_b = m.group(3)
        for junk in JUNK_INSIDE_PARENS:
            content = re.sub(r'(?i)\b' + junk + r'\b', '', content)
        # Strip remaining punctuation like leading/trailing dashes, slashes, spaces
        content = re.sub(r'[\s/|–—_-]+', ' ', content).strip(' -–—/|_')
        if not content:
            return ''
        return f'{open_b}{content}{close_b}'

    prev = None
    while prev != base_name:
        prev = base_name
        base_name = re.sub(r'([(\[])([^)\]]*?)([)\]])', process_match, base_name)
    return base_name


def smart_capitalize(text):
    """
    Capitalizes words in title case style while:
    - Preserving existing uppercase letters (acronyms like RMX, VIP, HD, names like Delavega, de Pretto).
    - Always capitalizing the first and last word.
    - Always capitalizing words following major separators like '-', '(', '[', ':', '. '.
    - Keeping short transition words (de, du, to, in, or, etc.) lowercase when in middle position.
    """
    tokens = re.split(r'([a-zA-ZÀ-ÿ0-9]+)', text)
    word_indices = [i for i, t in enumerate(tokens) if re.match(r'^[a-zA-ZÀ-ÿ0-9]+$', t)]
    if not word_indices:
        return text
    first_word_idx = word_indices[0]
    last_word_idx = word_indices[-1]
    new_tokens = []

    for i, token in enumerate(tokens):
        if i in word_indices:
            prev_sep = tokens[i - 1] if i > 0 else ''
            is_first = (i == first_word_idx)
            is_last = (i == last_word_idx)
            after_major_sep = bool(re.search(r'[-–—:(\[]|\.\s+$', prev_sep))

            if token.islower():
                if not is_first and not is_last and not after_major_sep and token in LOWERCASE_WORDS:
                    new_tokens.append(token)
                else:
                    new_tokens.append(token.capitalize())
            else:
                new_tokens.append(token)
        else:
            new_tokens.append(token)

    return ''.join(new_tokens)


def clean_filename(filename):
    """
    Cleans and standardizes the filename:
    - Normalizes unicode (NFC).
    - Standardizes long dashes to standard hyphen.
    - Removes junk tags inside parentheses/brackets and standalone.
    - Resolves isolated underscores used as separators.
    - Applies smart title capitalization.
    - Cleans up duplicate spaces and dashes.
    """
    filename = unicodedata.normalize('NFC', filename)
    base_name, ext = os.path.splitext(filename)

    # Standardize long dashes
    base_name = base_name.replace(' – ', ' - ').replace('—', '-').replace('–', '-')

    # Standalone removals
    for pat in STRINGS_TO_REMOVE_STANDALONE:
        base_name = re.sub(pat, '', base_name, flags=re.IGNORECASE)

    # Clean inside parens/brackets
    base_name = clean_parens_content(base_name)

    # Remove any leftover empty brackets/parens
    base_name = re.sub(r'[(\[]\s*[)\]]', '', base_name)

    # Resolve isolated underscores ' _ ' when no ' - ' is present
    if ' - ' not in base_name and ' _ ' in base_name:
        parts = base_name.split(' _ ')
        if len(parts) == 2:
            base_name = ' - '.join(parts)
        elif len(parts) > 2:
            artist = ' '.join(parts[:-1])
            title = parts[-1]
            base_name = f'{artist} - {title}'

    # Smart title capitalization
    base_name = smart_capitalize(base_name)

    # Clean up duplicate spaces and dashes
    base_name = re.sub(r' +', ' ', base_name)
    base_name = re.sub(r'\s*-\s*-+\s*', ' - ', base_name)
    base_name = base_name.strip(' -')

    return base_name + ext


def rename_file(dir_path, filename):
    """
    Renames a file after cleaning its name.
    Protects against overwriting a processed file (_soundincreased or _trimmed) with an untreated file.
    """
    original_filepath = os.path.join(dir_path, filename)
    cleaned_filename = clean_filename(filename)

    if cleaned_filename != filename:
        new_filepath = os.path.join(dir_path, cleaned_filename)

        if new_filepath.lower().endswith(".mp3"):
            if os.path.exists(new_filepath):
                if os.path.samefile(original_filepath, new_filepath):
                    print(f"File already clean: {original_filepath}")
                    return

                # If target already exists and original is a processed version (_soundincreased or _trimmed),
                # the processed version takes priority and replaces the older file.
                # If original is NOT processed, it is a redundant untreated file that should be removed.
                is_processed = "_soundincreased" in filename or "_trimmed" in filename
                if is_processed:
                    os.remove(new_filepath)
                    print(f"Deleted existing file to replace with processed version: {new_filepath}")
                else:
                    os.remove(original_filepath)
                    print(f"Deleted redundant untreated file: {original_filepath}")
                    return

            os.rename(original_filepath, new_filepath)
            print(f"Renamed: {original_filepath} to {new_filepath}")
        else:
            print(f"Error: {cleaned_filename} doesn't end with .mp3 or has an unexpected format.")


def main():
    """
    Main function to process files in the current directory.
    """
    dir_path = '.'

    mp3_files = [f for f in os.listdir(dir_path) if f.lower().endswith('.mp3')]
    total_files = len(mp3_files)

    for i, file_path in enumerate(mp3_files):
        logging.info(f'Processing file {i + 1}/{total_files}: {file_path}')
        rename_file(dir_path, file_path)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    main()