import os
import re
from datetime import datetime

def extract_artist_and_title(title):
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None

