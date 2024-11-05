import re

def is_valid_url(url):
    pattern = r'^https?://suno\.com/song/[a-f0-9\-]+$'
    playlist_pattern = r'^https?://suno\.com/playlist/[a-f0-9\-]+$'
    artist_pattern = r'^https?://suno\.com/@[a-zA-Z0-9_-]+$'
    return (re.match(pattern, url) or
            re.match(playlist_pattern, url) or
            re.match(artist_pattern, url))


def extract_song_id(url):
    """Extract the song ID from the URL."""
    match = re.search(r'song/([a-f0-9\-]+)', url)
    return match.group(1) if match else None
