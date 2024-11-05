# get_suno.py
import asyncio
from pyppeteer import launch
import argparse
import re
import os
import requests
import datetime
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, ID3NoHeaderError, TIT2, TALB, TPE1, TXXX, APIC
from datetime import datetime
from tqdm import tqdm

def extract_song_id(url): # Moved to utils/url_utils.py
    """Extract the song ID from the URL."""
    match = re.search(r'song/([a-f0-9\-]+)', url)
    return match.group(1) if match else None

# def is_valid_url(url): # Moved to utils/url_utils.py
#     print("Checking valid URL in get_suno.py")
#     pattern = r'^https?://suno\.com/(song|playlist|@)[a-f0-9\-]+/?$'
#     is_valid = re.match(pattern, url) is not None
#     print(f"Validating URL: {url} | Is valid: {is_valid}")  # Debugging output
#     return is_valid

def is_valid_url(url):
    # Example check - you might want to adjust this based on your criteria
    return url.startswith("https://suno.com/")



async def fetch_song_data(url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url, {'waitUntil': 'networkidle2'})

        # Get the full title
        full_title = await page.evaluate('document.title')
        # Split the title to get the song title and artist
        title, artist = full_title.split(' by @')
        artist = artist.split(' |')[0]  # Get the artist name before the separator

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

        # Return the processed values
        return title.strip(), artist.strip(), upload_date, album_art_url
    except Exception as e:
        print(f"Error fetching data for {url}: {e}")
        return None, None, None, None
    finally:
        await browser.close()



async def scrape_upload_date(page): # Moved to suno/fetch.py
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


async def scrape_album_art(page): # Moved to suno/fetch.py
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

def extract_artist_and_title(title): # Moved to utils/metadata_utils.py
    match = re.search(r'^(.*?) by @(.*?)\s*[\|\-]', title)
    if match:
        song_title = match.group(1).strip().replace(' ', '_')  # Sanitize title
        artist = match.group(2).strip()
        return song_title, artist
    return None, None

def sanitize_filename(title): # Moved to utils/file_utils.py
    return re.sub(r'[<>:"/\\|?*]', '', title).strip()

def ensure_directories_exist(artist): # Moved to utils/file_utils.py
    downloads_dir = './downloads'
    if not os.path.exists(downloads_dir):
        os.makedirs(downloads_dir)

    artist_dir = os.path.join(downloads_dir, artist)
    if not os.path.exists(artist_dir):
        os.makedirs(artist_dir)

def download_album_art(album_art_url, artist, title): # Moved to utils/file_utils.py
    if not album_art_url:
        return None

    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    try:
        response = requests.get(album_art_url, stream=True)
        response.raise_for_status()

        # Save the album art in the artist's directory
        art_filename = sanitize_filename(title) + '.jpg'
        art_path = os.path.join('./downloads', artist, art_filename)

        # Use tqdm for progress bar
        total_size = int(response.headers.get('content-length', 0))
        with open(art_path, 'wb') as art_file, tqdm(
            desc=art_filename,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                art_file.write(data)
                bar.update(len(data))

        return art_path
    except Exception as e:
        print(f"Failed to download album art: {e}")
        return None

def download_song(mp3_url, artist, title, upload_date, album_art_path, song_id): # Moved to utils/file_utils.py
    ensure_directories_exist(artist)  # Ensure directories exist before downloading

    sanitized_title = sanitize_filename(title)
    file_path = os.path.join('./downloads', artist, f'{sanitized_title}.mp3')

    if os.path.exists(file_path):
        return False, f'Skipped download. File already exists: {file_path}'

    try:
        response = requests.get(mp3_url, stream=True)
        response.raise_for_status()

        # Use tqdm for progress bar
        total_size = int(response.headers.get('content-length', 0))
        with open(file_path, 'wb') as file, tqdm(
            desc=sanitized_title,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                file.write(data)
                bar.update(len(data))

        # Set metadata using Mutagen
        audio = MP3(file_path, ID3=ID3)  # Use existing ID3 header if available
        audio.tags = ID3()  # Create ID3 tags if they don't exist
        audio.tags.add(TIT2(encoding=3, text=title))  # Title
        audio.tags.add(TPE1(encoding=3, text=artist))  # Artist
        audio.tags.add(TALB(encoding=3, text=''))  # Album
        audio.tags.add(TXXX(encoding=3, desc='Upload Date', text=upload_date))  # Upload Date
        audio.tags.add(TXXX(encoding=3, desc='Song ID', text=song_id))  # Song ID
        
        # Add album art if available
        if album_art_path:
            with open(album_art_path, 'rb') as img_file:
                img_data = img_file.read()
                audio.tags.add(APIC(
                    encoding=3,  
                    mime='image/jpeg', 
                    type=3,  
                    desc='Cover',
                    data=img_data
                ))

        audio.save()  # Save the changes
        return True, f'Downloaded and tagged: {file_path}'
    except requests.exceptions.HTTPError as http_err:
        return False, f'HTTP error occurred: {http_err}'
    except Exception as err:
        return False, f'Other error occurred: {err}'


def log_song_data(title, artist, audio_url, upload_date, status, reason=""): # MOved to utils/metadata_utils.py
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if status == "Failure" and reason:
        log_entry = f"{timestamp} | Title: {title} | Artist: {artist} | Audio URL: {audio_url} | Upload Date: {upload_date} | Status: {status} | Reason: {reason}\n"
    else:
        log_entry = f"{timestamp} | Title: {title} | Artist: {artist} | Audio URL: {audio_url} | Upload Date: {upload_date} | Status: {status}\n"
    
    with open("song_data.txt", "a") as f:
        f.write(log_entry)

def process_urls(urls): # Moved to suno/processing.py
    loop = asyncio.get_event_loop()
    for url in urls:
        title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(url))

        if title and audio_url:
            song_title, artist = extract_artist_and_title(title)
            song_id = extract_song_id(url)  # Extract the song ID
            print(f"Title: {song_title}")
            print(f"Artist: {artist}")
            print(f"Audio URL: {audio_url}")
            print(f"Upload Date: {upload_date}")

            # Download the album art
            album_art_path = download_album_art(album_art_url, artist, song_title)

            success, message = download_song(audio_url, artist, song_title, upload_date, album_art_path, song_id)
            print(message)
            if success:
                log_song_data(song_title, artist, audio_url, upload_date, "Success")
            else:
                reason = message.split('| Reason: ')[1] if '| Reason: ' in message else "Unknown reason"
                log_song_data(song_title, artist, audio_url, upload_date, "Failure", reason)
        else:
            print(f"Failed to extract song data for {url}.")


def main(url): # Added to main.py
    process_urls([url])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Extract song data from Suno page using Pyppeteer.')
    parser.add_argument('--url', type=str, help='URL of the Suno song, playlist, or artist page')
    parser.add_argument('--playlist', action='store_true', help='Prompt for multiple Suno song URLs')
    args = parser.parse_args()

    if args.url:
        main(args.url)
    elif args.playlist:
        urls = []
        while True:
            url = input("Please enter the Suno song, playlist, or artist URL (or just hit Enter to stop): ")
            if url == '':
                break
            if is_valid_url(url):
                urls.append(url)
            else:
                print("Invalid URL. Please enter a valid Suno song, playlist, or artist URL.")
        
        urls = list(set(urls))  # Remove duplicates before processing
        process_urls(urls)
    else:
        url = input("Please enter the Suno song, playlist, or artist URL: ")
        main(url)
