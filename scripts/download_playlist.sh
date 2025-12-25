#!/bin/bash

# Usage: ./download_playlist.sh <playlist_url> [folder_name]
# Example: ./download_playlist.sh "https://youtube.com/playlist?list=..." "my_playlist"

if [ $# -lt 1 ]; then
    echo "Error: Playlist URL required"
    echo "Usage: $0 <playlist_url> [folder_name]"
    exit 1
fi

PLAYLIST_URL="$1"
FOLDER_NAME="${2:-%(playlist)s}"

yt-dlp \
    -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b" \
    --merge-output-format mp4 \
    --extractor-args "youtube:player_client=android,web" \
    -o "${FOLDER_NAME}/%(title)s.%(ext)s" \
    "$PLAYLIST_URL"
