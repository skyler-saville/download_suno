# suno/fetch.py
from datetime import datetime
from pyppeteer import launch
from utils.url_utils import extract_song_id, is_valid_url

async def fetch_song_data(url): # This moved to suno/fetch.py
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


async def scrape_upload_date(page):  # This moved to suno/fetch.py
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


async def scrape_album_art(page):  # This moved to suno/fetch.py
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


