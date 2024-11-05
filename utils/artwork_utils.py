import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

def embed_artwork(mp3_file, image_file):
    """Embeds artwork into the specified MP3 file."""
    audio = MP3(mp3_file, ID3=ID3)

    # Read the image file
    with open(image_file, 'rb') as img:
        image_data = img.read()

    # Create an APIC tag for the artwork
    audio.tags.add(APIC(
        encoding=3,  # 3 is for ID3v2.3
        mime='image/jpeg',  # Change to 'image/png' if the image is a PNG
        type=3,  # 3 is for front cover
        desc='Cover',
        data=image_data
    ))

    # Save changes to the MP3 file
    audio.save()
    print(f"Artwork embedded in {mp3_file}")

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
    """Recursively processes the downloads directory for MP3 files."""
    for root, _, files in os.walk(downloads_dir):
        for file in files:
            if file.endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                # Check for embedded artwork
                check_embedded_artwork(mp3_file_path)
                # Construct the expected JPG file path for embedding
                jpg_file_path = os.path.splitext(mp3_file_path)[0] + '.jpg'
                if os.path.exists(jpg_file_path):
                    embed_artwork(mp3_file_path, jpg_file_path)  # Embed artwork
                else:
                    print(f"No artwork found for {mp3_file_path}")

if __name__ == "__main__":
    downloads_dir = './downloads'  # Change this to your downloads directory if needed
    process_directory(downloads_dir)  # Start processing the directory
