import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

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

if __name__ == "__main__":
    downloads_dir = './downloads'  # Change this to your downloads directory if needed
    process_directory(downloads_dir)
