from datetime import datetime


def log_song_data(title, artist, audio_url, upload_date, status, reason=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = (
        f"{timestamp} | Title: {title} | Artist: {artist} | "
        f"Audio URL: {audio_url} | Upload Date: {upload_date} | "
        f"Status: {status}"
    )
    if status == "Failure" and reason:
        log_entry += f" | Reason: {reason}"

    log_entry += "\n"
    
    try:
        with open("song_data.txt", "a") as f:
            f.write(log_entry)
    except IOError as e:
        print(f"Failed to write to log: {e}")