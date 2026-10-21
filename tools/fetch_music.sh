#!/usr/bin/env bash
# Download the game's music into puzzleth/music/. The songs are kept on Vercel Blob rather than in
# the repository; puzzleth/music/songs.txt lists them. Songs already there are left as they are.
#   tools/fetch_music.sh
set -euo pipefail
cd "$(dirname "$0")/../puzzleth/music"

while IFS= read -r url; do
  [[ -z "$url" ]] && continue
  f=$(basename "$url")
  [[ -f "$f" ]] && continue
  echo "Downloading $f"
  curl -fsSL --retry 3 -o "$f.part" "$url" && mv "$f.part" "$f"
done < songs.txt
