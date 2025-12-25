#!/bin/bash

# Usage: ./download_video.sh <video_url> [output_name]
# Example: ./download_video.sh "https://youtube.com/watch?v=..." "my_video"

if [ $# -lt 1 ]; then
    echo "Error: Video URL required"
    echo "Usage: $0 <video_url> [output_name]"
    exit 1
fi

VIDEO_URL="$1"
OUTPUT_NAME="${2:-%(title)s}"

yt-dlp \
    -f "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]/bv*+ba/b" \
    --merge-output-format mp4 \
    --extractor-args "youtube:player_client=android,web" \
    -o "${OUTPUT_NAME}.%(ext)s" \
    "$VIDEO_URL"
