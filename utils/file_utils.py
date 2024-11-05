import os
import re
import mutagen
import requests
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TXXX, APIC
from tqdm import tqdm

def sanitize_filename(title):
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()


def ensure_directories_exist(artist):
    # Use an absolute path for downloads
    downloads_dir = os.path.join(os.getcwd(), 'downloads')
    
    # Create downloads directory if it doesn't exist
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)
        print(f'Created directory: {downloads_dir}')

    # Create artist directory within downloads
    artist_dir = os.path.join(downloads_dir, artist)
    if not os.path.exists(artist_dir):
        os.makedirs(artist_dir)
        print(f'Created directory: {artist_dir}')


def download_album_art(album_art_url, artist, title): # unused. The download song function now handles the artwork as well
    if not album_art_url:
        return None

    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    try:
        response = requests.get(album_art_url)
        response.raise_for_status()

        # Save the album art in the artist's directory
        art_filename = sanitize_filename(title) + '.jpg'
        art_path = os.path.join('./downloads', artist, art_filename)

        with open(art_path, 'wb') as art_file:
            art_file.write(response.content)

        return art_path
    except Exception as e:
        print(f"Failed to download album art: {e}")
        return None

def download_song(mp3_url, artist, title, upload_date, album_art_url):
    ensure_directories_exist(artist)

    sanitized_title = sanitize_filename(title)
    sanitized_artist = sanitize_filename(artist)
    mp3_file_path = os.path.join('./downloads', sanitized_artist, f'{sanitized_title}.mp3')
    album_art_file_path = os.path.join('./downloads', sanitized_artist, f'{sanitized_title}.jpeg')

    if os.path.exists(mp3_file_path) and os.path.exists(album_art_file_path):
        return False, f'Skipped download. Files already exist: {mp3_file_path}, {album_art_file_path}'

    try:
        # Download the MP3 file
        download_file(mp3_url, mp3_file_path)

        # Download the album art
        if album_art_url:
            download_file(album_art_url, album_art_file_path)

        # Set metadata using Mutagen
        audio = MP3(mp3_file_path, ID3=ID3)
        audio.tags = ID3()  # Create ID3 tags if they don't exist
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        audio.tags.add(TALB(encoding=3, text=''))
        audio.tags.add(TXXX(encoding=3, desc='Upload Date', text=upload_date))

        # Embed the album art
        if os.path.exists(album_art_file_path):
            with open(album_art_file_path, 'rb') as img_file:
                img_data = img_file.read()
                audio.tags.add(APIC(
                    encoding=3,
                    mime='image/jpeg',
                    type=3,
                    desc='Cover',
                    data=img_data
                ))

        audio.save()
        return True, f'Downloaded and tagged: {mp3_file_path}'
    except requests.exceptions.HTTPError as http_err:
        return False, f'HTTP error occurred: {http_err}'
    except IOError as io_err:
        return False, f'File I/O error occurred: {io_err}'
    except mutagen.MutagenError as mutagen_err:
        return False, f'Mutagen error occurred: {mutagen_err}'
    except Exception as err:
        return False, f'Other error occurred: {err}'


def check_embedded_artwork(mp3_file):
    """Checks if there is embedded artwork in the specified MP3 file."""
    try:
        audio = MP3(mp3_file, ID3=ID3)
        if audio.tags:
            for tag in audio.tags.values():
                if isinstance(tag, APIC):
                    print(f"Artwork found in {mp3_file}: {tag.mime}, Description: {tag.desc}")
                    return True
        print(f"No artwork found in {mp3_file}.")
        return False
    except Exception as e:
        print(f"Error reading {mp3_file}: {e}")
        return False

def process_directory(downloads_dir):
    """Recursively processes the downloads directory to check for embedded artwork."""
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                check_embedded_artwork(mp3_file_path)

def download_file(url, path):
    response = requests.get(url)
    response.raise_for_status()
    with open(path, 'wb') as file:
        file.write(response.content)