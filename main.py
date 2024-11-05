from suno.processing import process_urls
from utils.artwork_utils import process_directory as process_artwork_directory
from utils.get_metadata_utils import process_directory as process_metadata_directory
from utils.url_utils import is_valid_url




def _menu_clear_log():
    """Clear the song_data.txt log file."""
    try:
        with open("song_data.txt", "w") as log_file:
            log_file.write("")
        print("Log file cleared successfully.")
    except Exception as e:
        print(f"Error clearing log file: {e}")

def _menu_download_song():
    """Download a single song from a URL."""
    url = input("Enter the song URL: ")
    if is_valid_url(url):
        process_urls([url])      
    else:
        print("Invalid URL.")

def _menu_download_playlist():
    """Download a playlist from a URL."""
    url = input("Enter the playlist URL: ")
    if is_valid_url(url):
        process_urls([url])
    else:
        print("Invalid URL.")

def _menu_download_artist_collection():
    """Download an artist collection from a URL."""
    url = input("Enter the artist collection URL: ")
    if is_valid_url(url):
        process_urls([url])
    else:
        print("Invalid URL.")

def main():
    downloads_dir = './downloads'  # Define the downloads directory here

    while True:
        print("\nChoose an option:")
        print("1. Check for embedded artwork in MP3 files")
        print("2. Embed artwork in MP3 files")
        print("3. Get metadata for MP3 files")
        print("4. View Log (song_data.txt)")
        print("5. Download Song")
        print("6. Download Playlist")
        print("7. Download Artist Collection")
        print("8. Clear Log")
        print("0. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            process_artwork_directory(downloads_dir)  # Check for embedded artwork
        elif choice == '2':
            process_artwork_directory(downloads_dir)  # Embed artwork
        elif choice == '3':
            process_metadata_directory(downloads_dir)  # Process metadata
        elif choice == '4':
            try:
                with open("song_data.txt", "r") as log_file:
                    print(log_file.read())
            except FileNotFoundError:
                print("Log file not found.")
        elif choice == '5':
            _menu_download_song()
        elif choice == '6':
            _menu_download_playlist()
        elif choice == '7':
            _menu_download_artist_collection()
        elif choice == '8':
            _menu_clear_log()
        elif choice == '0':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
