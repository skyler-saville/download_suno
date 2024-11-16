# download_suno

## Description

This project automates the processing of [Suno AI](https://suno.com/) MP3 files, including downloading songs, checking for and embedding album artwork, and retrieving metadata. Users can interact with the system via a menu interface to perform operations such as embedding artwork, viewing metadata, and downloading tracks or collections from provided URLs.

### Key Features

- **Download Management**: Download individual songs, playlists, or artist collections from URLs.
- **Artwork Handling**: Check for embedded album artwork in MP3 files and embed artwork from local JPG files.
- **Metadata Extraction**: Extract and display metadata from MP3 files, including song title, artist, and album art presence.
- **Log Management**: View and clear logs of processed songs.
  
### Technologies Used

- **Python** for scripting and logic control.
- **Mutagen** library for MP3 metadata and artwork handling.
- **OS Library** for directory navigation and file manipulation.
  
### Installation Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/skyler-saville/download_suno
   cd <repository-directory>
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have the necessary directory structure with a `downloads` folder where MP3 files will be processed.

### Usage Instructions

1. Run the main script to interact with the project:

   ```bash
   make run
   ```

2. Use the following options from the menu:
   - `1` to check for embedded artwork in MP3 files.
   - `2` to embed artwork from corresponding JPG files.
   - `3` to extract and display metadata from MP3 files.
   - `5-7` for downloading a song, playlist, or artist collection via URL input.
   - `4` to view the log of processed songs.
   - `8` to clear the log.
   - `0` to exit the application.

### Code Overview

1. **Main Script (`main.py`)**: Handles user interaction through a menu and allows the user to download songs, check metadata, and embed artwork.
2. **Metadata Processing (`get_metadata.py`)**: Extracts metadata such as song ID, title, artist, and album art presence from MP3 files. It also formats song length in mm:ss format.
3. **Artwork Check (`check_artwork.py`)**: Recursively checks for embedded artwork in MP3 files.
4. **Embed Artwork (`embed_artwork.py`)**: Embeds artwork into MP3 files from corresponding local image files (JPG format).

### Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix:

   ```bash
   git checkout -b feature/your-feature
   ```

3. Make your changes and commit them:

   ```bash
   git commit -m "Add some feature"
   ```

4. Push to the branch:

   ```bash
   git push origin feature/your-feature
   ```

5. Open a pull request for review.

### License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file in the root directory for more details.

---
