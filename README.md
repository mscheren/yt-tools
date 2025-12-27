# Media Tools

A Python application for downloading YouTube content and editing video/audio files. Provides both a command-line interface and a Streamlit web GUI.

## Features

### Download

- Download YouTube videos and playlists (MP4/MP3)
- Resolution selection (1080p, 720p, 480p, etc.)
- Download queue with pause/resume
- Archive tracking to avoid re-downloads

### Video Editing

- Trim, concatenate, speed adjustment, reverse, loop
- Crop, resize, rotate
- Color grading (brightness, contrast, saturation, gamma)
- Filters (grayscale, sepia, blur)
- Text overlays and subtitles

### Audio Processing

- Effects: EQ, compression, reverb, gain, limiting
- Presets: podcast, radio, reverb_light, reverb_heavy, warm
- Mixing: overlay, ducking, crossfade, fades
- Noise removal (gate and spectral methods)
- Extract audio from video

### Project Management

- Save/load projects (JSON/YAML)
- Batch processing
- Undo/redo history

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

#### Project Commands

```bash
# Create new project
ytdl project-new "My Project" --output project.json

# Show project info
ytdl project-info project.json

# List projects in directory
ytdl project-list ./projects
```

### GUI

Launch the Streamlit web interface:

```bash
cd src && streamlit run ytdl_app/gui/app.py
```

Or with poetry:

```bash
poetry run sh -c "cd src && streamlit run ytdl_app/gui/app.py"
```

The GUI provides four main tabs:

1. **Download**: YouTube video/playlist downloads with resolution selection, directory browser
2. **Video Editing**: Trim, transforms (speed/crop/resize/rotate), effects (color grading/filters), text overlays
3. **Audio Editing**: Effects with presets, mixing (overlay/ducking/crossfade), processing (noise removal/normalize)
4. **Projects**: Create, load, and manage editing projects

## Project Structure

```plaintext
src/ytdl_app/
├── models/             # Shared data models
│   ├── formats.py      # Output format, resolution, codec enums
│   └── metadata.py     # Video/audio metadata classes
├── download/           # YouTube downloading
│   ├── config.py       # Download configuration
│   ├── downloader.py   # Downloader with retry logic
│   ├── queue.py        # Download queue management
│   └── archive.py      # Track downloaded videos
├── video/              # Video editing
│   ├── editor.py       # VideoEditor class
│   ├── transforms.py   # Speed, crop, resize, rotate
│   ├── effects.py      # Color grading, filters
│   ├── subtitles.py    # Subtitle support
│   └── operations.py   # Concatenate, get info
├── audio/              # Audio processing
│   ├── editor.py       # AudioEditor class
│   ├── effects.py      # Effect chain and presets
│   ├── mixing.py       # Overlay, ducking, crossfade
│   └── processing.py   # Noise removal, extraction
├── project/            # Project management
│   ├── config.py       # Project configuration
│   ├── manager.py      # Save/load projects
│   ├── history.py      # Undo/redo
│   └── batch.py        # Batch processing
├── cli/                # Command-line interface
│   ├── main.py         # Entry point
│   ├── download_cmd.py # Download commands
│   ├── video_cmd.py    # Video commands
│   ├── audio_cmd.py    # Audio commands
│   └── project_cmd.py  # Project commands
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
