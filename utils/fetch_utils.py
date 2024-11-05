import os

import re
from utils.file_utils import download_album_art, download_file, sanitize_filename
from utils.get_metadata_utils import embed_metadata
from utils.logging_utils import log_song_data
from pyppeteer import launch
from datetime import datetime


async def fetch_song_data(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})

        title = await page.evaluate('document.title')
        audio_url = await page.evaluate('''
            () => {
                const metaTags = document.getElementsByTagName('meta');
                for (let tag of metaTags) {
                    if (tag.getAttribute('property') === 'og:audio') {
                        return tag.getAttribute('content');
                    }
                }
                return null;
            }
        ''')
        
        upload_date = await scrape_upload_date(page)
        album_art_url = await scrape_album_art(page)

        return title, audio_url, upload_date, album_art_url
    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None, None, None, None
    finally:
        await browser.close()


async def scrape_upload_date(page):
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')
    
    # Normalize the date format
    if upload_date_str:
        try:
            # Parse the date string
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            # Convert to ISO 8601 format
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None



async def scrape_album_art(page):
    album_art_url = await page.evaluate('''
        () => {
            const metaTags = document.getElementsByTagName('meta');
            for (let tag of metaTags) {
                if (tag.getAttribute('property') === 'og:image') {
                    return tag.getAttribute('content');
                }
            }
            return null;
        }
    ''')
    return album_art_url

async def scrape_upload_date(page):
    upload_date_str = await page.evaluate('''
        () => {
            const dateSpan = document.querySelector('.items-center.mt-6 span[title]');
            return dateSpan ? dateSpan.getAttribute('title') : null;
        }
    ''')
    
    if upload_date_str:
        try:
            upload_date = datetime.strptime(upload_date_str, '%B %d, %Y at %I:%M %p')
            return upload_date.isoformat()
        except ValueError:
            print(f"Error parsing date: {upload_date_str}")
            return None

    return None


def extract_artist_and_title(title):
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None


async def process_song(url):
    title, audio_url, upload_date, album_art_url = await fetch_song_data(url)

    if title and audio_url:
        song_title, artist = extract_artist_and_title(title)

        print(f"Processing song: {song_title} by {artist}")
        print(f"Audio URL: {audio_url}")
        print(f"Upload Date: {upload_date}")

        # Download the album art
        album_art_path = await download_album_art(album_art_url, artist, song_title)

        # Download the song
        sanitized_title = sanitize_filename(song_title)
        file_path = f'./downloads/{artist}/{sanitized_title}.mp3'

        if os.path.exists(file_path):
            print(f"Skipped download. File already exists: {file_path}")
            log_song_data(song_title, artist, audio_url, upload_date, "Failure", "File already exists")
            return

        try:
            await download_file(audio_url, file_path)
            print(f"Downloaded song to: {file_path}")

            # Embed metadata
            embed_metadata(file_path, song_title, artist, upload_date, album_art_path)
            log_song_data(song_title, artist, audio_url, upload_date, "Success")

        except Exception as e:
            print(f"Error downloading song: {e}")
            log_song_data(song_title, artist, audio_url, upload_date, "Failure", str(e))
    else:
        print(f"Failed to extract song data for {url}.")
        log_song_data("", "", "", "", "Failure", "Failed to extract song data")
