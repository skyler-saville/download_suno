import pytest
import asyncio
from unittest.mock import patch, MagicMock
from get_suno import fetch_song_data, scrape_upload_date, scrape_album_art, extract_artist_and_title, is_valid_url

SONG_URL = "https://suno.com/song/6a6bdd56-d583-4e0a-9869-b98a8c72a37b"
PLAYLIST_URL = "https://suno.com/playlist/99e5d0c6-b1f7-451d-830d-5c272d114cd6"
ARTIST_URL = "https://suno.com/@happygoth"

@pytest.mark.asyncio
async def test_fetch_song_data():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()

        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        mock_page.evaluate.side_effect = [
            "Shadows of the Holler by @timmo",  # Title without the '| Suno'
            "https://cdn1.suno.ai/6a6bdd56-d583-4e0a-9869-b98a8c72a37b.mp3",  # Correct Audio URL
            "February 26, 2024 at 09:51 AM",  # Correct Upload Date
            "https://cdn2.suno.ai/image_large_768adf51-ba69-44c7-9c6a-a488babb73e7.jpeg"  # Optional Album Art URL
        ]

        result = await fetch_song_data(SONG_URL)

        assert result == (
            "Shadows of the Holler",
            "timmo",
            "2024-02-26T09:51:00",
            "https://cdn2.suno.ai/image_large_768adf51-ba69-44c7-9c6a-a488babb73e7.jpeg"
        )


@pytest.mark.asyncio
async def test_scrape_upload_date():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        future = asyncio.Future()
        future.set_result("January 1, 2023 at 12:00 PM")
        mock_page.evaluate.return_value = future

        upload_date = await scrape_upload_date(mock_page)
        assert upload_date == "2023-01-01T12:00:00"

@pytest.mark.asyncio
async def test_scrape_album_art():
    with patch('pyppeteer.launch') as mock_launch:
        mock_browser = MagicMock()
        mock_page = MagicMock()
        
        mock_launch.return_value = mock_browser
        mock_browser.newPage.return_value = mock_page

        future = asyncio.Future()
        future.set_result("http://album.art/url.jpg")
        mock_page.evaluate.return_value = future

        album_art_url = await scrape_album_art(mock_page)
        assert album_art_url == "http://album.art/url.jpg"

def test_extract_artist_and_title():
    title = "Test Song Title by @TestArtist - Some Info"
    song_title, artist = extract_artist_and_title(title)
    assert song_title == "Test_Song_Title"
    assert artist == "TestArtist"

def test_is_valid_url():
    assert is_valid_url(SONG_URL) == True
    assert is_valid_url(PLAYLIST_URL) == True
    assert is_valid_url(ARTIST_URL) == True
    assert is_valid_url("https://invalid-url.com") == False
