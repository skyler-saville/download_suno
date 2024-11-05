import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TXXX, APIC

def format_length(seconds):
    """Convert seconds to mm:ss format."""
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    return f"{minutes:02}:{seconds:02}"

def print_metadata(file_path):
    metadata = {}  # Initialize metadata dictionary
    try:
        audio = MP3(file_path, ID3=ID3)

        # Get the song ID
        song_id = audio.get('TXXX:Song ID', None)
        metadata['Song ID'] = song_id.text[0] if song_id else 'Not available'

        # Check for corresponding JPG file
        jpg_file_path = os.path.splitext(file_path)[0] + '.jpg'
        if os.path.exists(jpg_file_path):
            metadata['Album Art'] = jpg_file_path
        else:
            # Check for album art in the tags
            album_art = 'Not available'
            if audio.tags:
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        album_art = 'Embedded art found'
                        break
            metadata['Album Art'] = album_art

        title = audio.tags.get('TIT2')
        artist = audio.tags.get('TPE1')
        upload_date = audio.tags.get('TXXX:Upload Date')  # Retrieve upload date
        length = audio.info.length
        bitrate = audio.info.bitrate
        
        print("Metadata for:", file_path)
        print("Song ID:", metadata['Song ID'])
        print("Title:", title.text[0] if title else "N/A")
        print("Artist:", artist.text[0] if artist else "N/A")
        print("Upload Date:", upload_date.text[0] if upload_date else "N/A")  # Display upload date
        print("Length:", format_length(length))
        print("Bitrate: {} kbps".format(bitrate // 1000))
        print("Artwork:", metadata['Album Art'])  # Print the final result for Album Art

    except Exception as e:
        print(f"Error reading metadata for {file_path}: {e}")

def list_mp3_files(downloads_dir):
    """List all MP3 files in the downloads directory."""
    mp3_files = []
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_files.append(os.path.join(root, file))
    return mp3_files

def process_directory(downloads_dir):
    """Process all MP3 files in the downloads directory."""
    mp3_files = list_mp3_files(downloads_dir)
    
    if not mp3_files:
        print("No MP3 files found in the downloads directory.")
    else:
        for file_path in mp3_files:
            print_metadata(file_path)

if __name__ == "__main__":
    downloads_dir = './downloads'
    # List MP3 files and process them
    process_directory(downloads_dir)
