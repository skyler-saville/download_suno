from pyppeteer import launch

from utils.fetch_utils import fetch_song_data
from utils.logging_utils import log_song_data
from utils.metadata_utils import extract_artist_and_title


async def fetch_playlist_songs(playlist_url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        
        await page.goto(playlist_url, {'waitUntil': 'networkidle2'})

        # Extract all song URLs from the playlist
        song_links = await page.evaluate('''
            () => {
                const links = [];
                const songElements = document.querySelectorAll('a[href^="/song/"]');
                songElements.forEach(el => links.push('https://suno.com' + el.getAttribute('href')));
                return links;
            }
        ''')
        return song_links
    except Exception as e:
        print(f"Error fetching playlist data for {playlist_url}: {e}")
        return []
    finally:
        await browser.close()
        