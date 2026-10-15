#!/usr/bin/env bash
# Build the browser version of Puzzleth into build/web/ (a static site: host it anywhere).
#   pip install pygbag==0.9.2
#   tools/build_web.sh            # build only
#   tools/build_web.sh --serve    # build and try it at http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")/.."

# only the game itself goes into the web package (not tests, docs or screenshots)
rm -rf build/Puzzleth build/web
mkdir -p build/Puzzleth/puzzleth
cp main.py build/Puzzleth/
cp -r puzzleth/. build/Puzzleth/puzzleth/
find build/Puzzleth -name __pycache__ -prune -exec rm -rf {} +

# browsers play .ogg most reliably, so added .wav/.mp3 sounds and music are converted (a converted
# file replaces a bundled .ogg of the same name, as it would on the desktop)
while IFS= read -r -d '' f; do
  if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -y -loglevel error -i "$f" -vn -c:a libvorbis -q:a 4 "${f%.*}.ogg" && rm "$f"
  else
    echo "warning: ffmpeg not found, $f is left as it is and may not play in every browser" >&2
  fi
done < <(find build/Puzzleth/puzzleth/sounds build/Puzzleth/puzzleth/music -type f \
           \( -iname '*.wav' -o -iname '*.mp3' \) -print0)

args=(--template "$PWD/tools/web/puzzleth.tmpl" --icon "$PWD/tools/web/favicon.png" --title Puzzleth --app_name puzzleth --ume_block 0 build/Puzzleth)
if [[ "${1:-}" == "--serve" ]]; then
  python3 -m pygbag "${args[@]}"
else
  python3 -m pygbag --build "${args[@]}"
  mv build/Puzzleth/build/web build/web
  echo "Built build/web/ — upload that folder to any static web host."
fi
