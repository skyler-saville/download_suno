# tests/test_utils/test_artwork_utils.py

import os
import pytest
from utils.artwork_utils import embed_artwork, check_embedded_artwork, process_directory
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

@pytest.fixture
def setup_mp3_with_artwork(tmp_path):
    """Fixture to create a temporary valid MP3 file with a temporary image file."""
    # Path for the temporary files
    mp3_file = tmp_path / "test_song.mp3"
    image_file = tmp_path / "cover.jpg"

    # Create a valid MP3 file (using a small sample MP3 for testing)
    with open(mp3_file, 'wb') as f:
        f.write(b'\x49\x44\x33\x03\x00\x00\x00\x00\x00\x00\x00\x00')  # Minimal ID3 header

    # Create a dummy image file
    with open(image_file, 'wb') as f:
        f.write(b'\0' * 1024)  # Just create a dummy image file

    return mp3_file, image_file

def test_embed_artwork(setup_mp3_with_artwork):
    mp3_file, image_file = setup_mp3_with_artwork
    embed_artwork(mp3_file, image_file)

    # Check if artwork was embedded
    audio = MP3(mp3_file, ID3=ID3)
    assert any(isinstance(tag, APIC) for tag in audio.tags.values())

def test_check_embedded_artwork(setup_mp3_with_artwork):
    mp3_file, image_file = setup_mp3_with_artwork
    embed_artwork(mp3_file, image_file)

    assert check_embedded_artwork(mp3_file) is True

def test_process_directory(tmp_path):
    """Test that process_directory correctly processes MP3 files and embeds artwork."""
    mp3_file = tmp_path / "test_song.mp3"
    image_file = tmp_path / "cover.jpg"

    # Create a valid MP3 file
    with open(mp3_file, 'wb') as f:
        f.write(b'\x49\x44\x33\x03\x00\x00\x00\x00\x00\x00\x00\x00')  # Minimal ID3 header

    # Create a dummy image file
    with open(image_file, 'wb') as f:
        f.write(b'\0' * 1024)

    # Call process_directory
    os.makedirs(tmp_path / "downloads", exist_ok=True)
    mp3_dest = (tmp_path / "downloads" / "test_song.mp3")
    mp3_file.rename(mp3_dest)

    jpg_dest = (tmp_path / "downloads" / "cover.jpg")
    image_file.rename(jpg_dest)

    # Run the function
    process_directory(tmp_path / "downloads")

    # Verify that artwork was embedded
    assert check_embedded_artwork(mp3_dest) is True
