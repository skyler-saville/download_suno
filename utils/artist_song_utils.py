from pyppeteer import launch


async def fetch_artist_songs(artist_url):
    try:
        browser = await launch(headless=True)
        page = await browser.newPage()
        
        await page.goto(artist_url, {'waitUntil': 'networkidle2'})

        # Extract all song URLs from the artist's page
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
        print(f"Error fetching artist data for {artist_url}: {e}")
        return []
    finally:
        await browser.close()