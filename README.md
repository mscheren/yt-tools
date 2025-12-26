# Media Tools

A Python application for downloading YouTube content and editing video/audio files. Provides both a command-line interface and a Streamlit web GUI.

## Features

- Download YouTube videos and playlists (MP4/MP3)
- Video editing: trim, concatenate, add text overlays
- Audio processing: effects, EQ, compression, reverb, normalization

## Requirements

- Python 3.12+
- FFmpeg (required for media processing)

## Installation

```bash
poetry install
```

## Usage

### CLI

#### Download Commands

```bash
# Download video as MP4
ytdl video "https://www.youtube.com/watch?v=VIDEO_ID"

# Download as MP3
ytdl video -f mp3 "https://www.youtube.com/watch?v=VIDEO_ID"

# Download playlist
ytdl playlist "https://www.youtube.com/playlist?list=PLAYLIST_ID"

# Fetch metadata
ytdl info "https://www.youtube.com/watch?v=VIDEO_ID"
```

#### Video Editing Commands

```bash
# Trim video
ytdl trim input.mp4 output.mp4 --start 10 --end 60

# Concatenate videos
ytdl concat output.mp4 video1.mp4 video2.mp4 video3.mp4

# Add text overlay
ytdl overlay input.mp4 output.mp4 --text "Hello" --font-size 50

# Get video info
ytdl video-info input.mp4
```

#### Audio Editing Commands

```bash
# Apply effects with preset
ytdl effects input.wav output.wav --preset podcast

# Apply custom effects
ytdl effects input.wav output.wav --gain 3 --highpass 80 --compress --normalize

# Trim audio
ytdl trim-audio input.mp3 output.mp3 --start 0 --end 30

# Normalize audio
ytdl normalize-audio input.wav output.wav --target-db -1

# Get audio info
ytdl audio-info input.mp3
```

Available effect presets: `radio`, `podcast`, `reverb_light`, `reverb_heavy`, `warm`

### GUI

Launch the Streamlit web interface:

```bash
streamlit run src/ytdl_app/gui/app.py
```

The GUI provides three tabs:

1. **Download**: YouTube video/playlist downloads with directory browser
2. **Video Editing**: Trim videos, add text overlays, view metadata
3. **Audio Editing**: Apply effects (presets or custom), trim, normalize

## Project Structure

```plaintext
src/ytdl_app/
├── models/             # Shared data models
│   ├── formats.py      # Output format enums
│   └── metadata.py     # Video/audio metadata classes
├── download/           # YouTube downloading
│   └── downloader.py   # Downloader class
├── video/              # Video editing
│   ├── editor.py       # VideoEditor class
│   ├── operations.py   # Concatenate, get info
│   └── overlay.py      # Text overlay config
├── audio/              # Audio processing
│   ├── editor.py       # AudioEditor class
│   └── effects.py      # Effect chain and presets
├── cli/                # Command-line interface
│   ├── main.py         # Entry point
│   ├── download_cmd.py # Download commands
│   ├── video_cmd.py    # Video commands
│   └── audio_cmd.py    # Audio commands
└── gui/                # Streamlit GUI
    ├── app.py          # Main entry
    ├── state.py        # Session state
    ├── components/     # Reusable UI components
    └── tabs/           # Tab implementations
```

## Cookies

For age-restricted or private videos, export cookies from your browser to a `cookies.txt` file in Netscape format.

## License

MIT
