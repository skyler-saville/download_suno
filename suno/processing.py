# suno/processing.py
import asyncio

from utils.artist_song_utils import fetch_artist_songs
from utils.fetch_utils import extract_artist_and_title, fetch_song_data
from utils.file_utils import download_song
from utils.logging_utils import log_song_data
from utils.playlist_utils import fetch_playlist_songs


def process_urls(urls):
    loop = asyncio.get_event_loop()
    success_count = 0
    failure_count = 0

    for url in urls:
        if 'playlist' in url:
            song_urls = loop.run_until_complete(fetch_playlist_songs(url))
            for song_url in song_urls:
                title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(song_url))

                if title and audio_url:
                    song_title, artist = extract_artist_and_title(title)
                    print(f"Title: {song_title}")
                    print(f"Artist: {artist}")
                    print(f"Audio URL: {audio_url}")
                    print(f"Upload Date: {upload_date}")
                    print(f"Album Art URL: {album_art_url}")

                    # Download the song and log the result
                    success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                    print(message)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                    
                    # Log the song data
                    log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)
                else:
                    print(f"Failed to extract song data for {song_url}.")
                    log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract playlist")
        elif '@' in url:
            song_urls = loop.run_until_complete(fetch_artist_songs(url))
            for song_url in song_urls:
                title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(song_url))

                if title and audio_url:
                    song_title, artist = extract_artist_and_title(title)
                    print(f"Title: {song_title}")
                    print(f"Artist: {artist}")
                    print(f"Audio URL: {audio_url}")
                    print(f"Upload Date: {upload_date}")
                    print(f"Album Art URL: {album_art_url}")

                    # Download the song and log the result
                    success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                    print(message)
                    if success:
                        success_count += 1
                    else:
                        failure_count += 1
                    
                    # Log the song data
                    log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)
                else:
                    print(f"Failed to extract song data for {song_url}.")
                    log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract artist page")
        else:
            title, audio_url, upload_date, album_art_url = loop.run_until_complete(fetch_song_data(url))

            if title and audio_url:
                song_title, artist = extract_artist_and_title(title)
                print(f"Title: {song_title}")
                print(f"Artist: {artist}")
                print(f"Audio URL: {audio_url}")
                print(f"Upload Date: {upload_date}")
                print(f"Album Art URL: {album_art_url}")

                # Download the song and log the result
                success, message = download_song(audio_url, artist, song_title, upload_date, album_art_url)
                print(message)
                if success:
                    success_count += 1
                else:
                    failure_count += 1
                
                # Log the song data
                log_song_data(song_title, artist, audio_url, upload_date, "Success" if success else "Failure", message)


            else:
                print(f"Failed to extract song data for {url}.")
                log_song_data("N/A", "N/A", url, "N/A", "Failure", "Failed to extract song data")

    print(f"\nSummary: {success_count} songs downloaded successfully, {failure_count} failed.")

def main(url):
    process_urls([url])
