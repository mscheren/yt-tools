# YouTube Downloader

A Python application for downloading YouTube videos and playlists in MP4 (video) or MP3 (audio) format. Provides both a command-line interface and a Streamlit web GUI.

## Requirements

- Python 3.12+
- FFmpeg (required for audio extraction and video merging)

## Installation

```bash
poetry install
```

## Usage

### CLI

The CLI provides three commands: `video`, `playlist`, and `info`.

#### Download a single video

```bash
# Download as MP4 (default)
ytdl video "https://www.youtube.com/watch?v=VIDEO_ID"

# Download as MP3
ytdl video -f mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Specify output directory
ytdl video -o ./downloads "https://www.youtube.com/watch?v=VIDEO_ID"

# Use cookies for authenticated downloads
ytdl video -c cookies.txt "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Download a playlist

```bash
# Download entire playlist as MP4
ytdl playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Download as MP3
ytdl playlist -f mp3 "https://www.youtube.com/playlist?list=PLAYLIST_ID"
```

#### Fetch video/playlist info

```bash
ytdl info "https://www.youtube.com/watch?v=VIDEO_ID"
```

### GUI

Launch the Streamlit web interface:

```bash
streamlit run src/ytdl_app/gui/app.py
```

The GUI provides:
- URL input for videos or playlists
- Format selection (MP4/MP3)
- Output directory configuration
- Optional cookies file path
- Video/playlist info lookup

## Project Structure

```
video_edit/
├── src/
│   └── ytdl_app/
│       ├── core/           # Core downloading logic
│       │   └── downloader.py
│       ├── cli/            # Command-line interface
│       │   └── main.py
│       └── gui/            # Streamlit GUI
│           └── app.py
├── scripts/                # Legacy shell scripts
├── tests/                  # Test suite
├── pyproject.toml
└── README.md
```

## Cookies

For downloading age-restricted or private videos, export cookies from your browser to a `cookies.txt` file in Netscape format. You can use browser extensions like "Get cookies.txt" for this purpose.

## License

MIT
