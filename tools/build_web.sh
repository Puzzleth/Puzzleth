#!/usr/bin/env bash
# Build the browser version of Puzzleth into build/web/ (a static site: host it anywhere).
#   pip install pygbag==0.9.2 fonttools
#   tools/build_web.sh            # build only
#   tools/build_web.sh --serve    # build and try it at http://localhost:8000
set -euo pipefail
cd "$(dirname "$0")/.."

# The page loads pygbag's runtime from the CDN folder of the pygbag version that built it, and the
# template needs that folder to have browserfs.min.js. 0.9.2's (archives/0.9) has it; 0.9.3's
# (cdn/0.9.3) doesn't, and its page never gets past the loading bar. A project .venv is used if there is one.
[[ -x .venv/bin/python ]] && export PATH="$PWD/.venv/bin:$PATH"
PYGBAG_VERSION=0.9.2
found=$(python3 -c 'import pygbag; print(getattr(pygbag, "VERSION", getattr(pygbag, "__version__", "?")))' 2>/dev/null || echo none)
if [[ "$found" != "$PYGBAG_VERSION" ]]; then
  echo "error: pygbag $PYGBAG_VERSION is needed, found $found:  pip install pygbag==$PYGBAG_VERSION fonttools" >&2
  exit 1
fi

# only the game itself goes into the web package (not tests, docs or screenshots)
rm -rf build/Puzzleth build/web
mkdir -p build/Puzzleth/puzzleth
cp main.py build/Puzzleth/
cp -r puzzleth/. build/Puzzleth/puzzleth/
find build/Puzzleth -name __pycache__ -prune -exec rm -rf {} +

# browsers play .ogg most reliably, so added .wav/.mp3 sounds and music are converted (a converted
# file replaces a bundled .ogg of the same name, as it would on the desktop). Music only plays in
# the background, so it is made smaller (about 96 kbit/s) to stream well on slow connections.
while IFS= read -r -d '' f; do
  case "$f" in */music/*) q=2 ;; *) q=4 ;; esac
  if command -v ffmpeg >/dev/null 2>&1; then
    ffmpeg -y -loglevel error -i "$f" -vn -c:a libvorbis -q:a "$q" "${f%.*}.ogg" && rm "$f"
  else
    echo "warning: ffmpeg not found, $f is left as it is and may not play in every browser" >&2
  fi
done < <(find build/Puzzleth/puzzleth/sounds build/Puzzleth/puzzleth/music -type f \
           \( -iname '*.wav' -o -iname '*.mp3' \) -print0)

# Everything in the game's package is downloaded before it can start, so keep that small:
# - the music moves out of it to music/ beside the page (pygbag copies static/ there as it is),
#   listed in streamed.txt, and each song is streamed only when it starts playing (puzzleth/sound.py)
mkdir -p build/Puzzleth/static/music
# the privacy notice is published beside the page, where the leaderboard links to it (PRIVACY_URL)
cp tools/web/privacy.html tools/web/favicon.png build/Puzzleth/static/
: > build/Puzzleth/puzzleth/music/streamed.txt
while IFS= read -r -d '' f; do
  mv "$f" build/Puzzleth/static/music/
  basename "$f" >> build/Puzzleth/puzzleth/music/streamed.txt
done < <(find build/Puzzleth/puzzleth/music -maxdepth 1 -type f \
           \( -iname '*.ogg' -o -iname '*.wav' -o -iname '*.mp3' \) -print0 | sort -z)
# - the fonts keep only the letters and symbols the game can show (pip install fonttools), which
#   more than halves them
if command -v pyftsubset >/dev/null 2>&1; then
  for f in build/Puzzleth/puzzleth/fonts/*.ttf; do
    pyftsubset "$f" --output-file="$f.sub" --layout-features='*' \
      --unicodes='U+0020-007E,U+00A0-024F,U+2000-206F,U+20AC,U+2190-21FF,U+2200-22FF,U+25A0-25FF'
    mv "$f.sub" "$f"
  done
else
  echo "warning: pyftsubset not found (pip install fonttools), the fonts are bundled whole" >&2
fi

args=(--template "$PWD/tools/web/puzzleth.tmpl" --icon "$PWD/tools/web/favicon.png" --title Puzzleth --app_name puzzleth --ume_block 0 build/Puzzleth)
if [[ "${1:-}" == "--serve" ]]; then
  python3 -m pygbag "${args[@]}"
else
  python3 -m pygbag --build "${args[@]}"
  mv build/Puzzleth/build/web build/web
  # Browsers keep the page and the game's download for a while, phones for longer. Naming the download
  # after its contents means a new page never starts an old game, and version.txt (always asked for past
  # the caches) lets an open page see that a newer build is out (puzzleth_check_version in the template).
  build_id=$(python3 -c 'import hashlib, sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest()[:12])' \
             build/web/puzzleth.apk)
  mv build/web/puzzleth.apk "build/web/puzzleth-$build_id.apk"
  perl -pi -e "s/puzzleth\.apk/puzzleth-$build_id.apk/g; s/\@PUZZLETH_BUILD\@/$build_id/g" build/web/index.html
  echo "$build_id" > build/web/version.txt
  grep -q "puzzleth-$build_id.apk" build/web/index.html || { echo "error: index.html doesn't load the game" >&2; exit 1; }
  # Vendor pygbag runtime locally for offline use (no CDN at runtime).
  # Find a directory inside the installed pygbag package that contains pythons.js and browserfs.min.js.
  RUNTIME_DIR=$(python3 - <<'PY'
import os, sys
try:
  import pygbag
except Exception as e:
  print("", end="")
  sys.exit(0)
base = os.path.dirname(pygbag.__file__)
found = ""
for root, dirs, files in os.walk(base):
  if "pythons.js" in files and "browserfs.min.js" in files:
    found = root
    break
print(found, end="")
PY
)
  if [[ -z "$RUNTIME_DIR" ]]; then
    echo "error: could not locate pygbag runtime (pythons.js + browserfs.min.js) in the pygbag package" >&2
    exit 1
  fi
  mkdir -p build/web/runtime
  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete "$RUNTIME_DIR"/ build/web/runtime/
  else
    cp -R "$RUNTIME_DIR"/. build/web/runtime/
  fi
  # Keep only files we actually reference if needed; for now copy the full runtime subtree.
  echo "Built build/web/ (build $build_id) — upload that folder to any static web host."
fi
