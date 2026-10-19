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
  # pygbag 0.9.2 does not ship the runtime in its wheel; it expects the pygame-web CDN.
  # Detect the correct CDN base for the installed pygbag version and download the exact files we need,
  # verifying SHA-256 when known.
  CDN_BASE=$(python3 - <<'PY'
import sys
try:
  import pygbag
  v = getattr(pygbag, "VERSION", getattr(pygbag, "__version__", "0.0.0"))
except Exception:
  v = "0.0.0"
def ver_tuple(s):
  try:
    x = s.split("."); return tuple(int(p) for p in x[:3])
  except Exception:
    return (0,0,0)
if ver_tuple(v) >= (0,9,3):
  print(f"https://pygame-web.github.io/cdn/{v}/", end="")
else:
  print("https://pygame-web.github.io/archives/0.9/", end="")
PY
)
  mkdir -p build/web/runtime build/web/runtime/vt
  # Known hashes for archives/0.9 (pygbag 0.9.2 compatible). Leave empty for other bases.
  EXPECT_PYTHONS="e11be94dd16c29ccbb0387735df5888e0050766b2c58eae636911259e915765f"
  EXPECT_BFS="ba01fda78db31a7ba579afe74b8b56cf4636381ca1b6c54ffba20467756a627f"
  EXPECT_XTERM="f0aea0f75f48559013ae6643c2479dd737d26da42d5524e6d2b70915ae6523c7"
  EXPECT_XTERM_IMG="a4795cf0998c595de120f79a69c6e522db5fff28dba7c50c1e872ea81a89fd81"
  EXPECT_EMPTY="b0693dc92f76e08bf1485b3dd9b514a2e31dfd6f39422a6b60edb722671dc98f"
  verify_arg() {
    local want="$1" file="$2"
    if [[ -n "$want" ]]; then
      local have
      have=$(sha256sum "$file" | awk '{print $1}')
      [[ "$have" == "$want" ]] || { echo "error: sha256 mismatch for $file (have $have want $want)" >&2; exit 1; }
    fi
  }
  # Download helper
  dl() { curl -fsSL "$1" -o "$2"; }
  # Download files
  dl "${CDN_BASE}pythons.js" build/web/runtime/pythons.js
  verify_arg "$EXPECT_PYTHONS" build/web/runtime/pythons.js || true
  dl "${CDN_BASE}browserfs.min.js" build/web/runtime/browserfs.min.js
  verify_arg "$EXPECT_BFS" build/web/runtime/browserfs.min.js || true
  dl "${CDN_BASE}vt/xterm.js" build/web/runtime/vt/xterm.js
  verify_arg "$EXPECT_XTERM" build/web/runtime/vt/xterm.js || true
  dl "${CDN_BASE}vt/xterm-addon-image.js" build/web/runtime/vt/xterm-addon-image.js
  verify_arg "$EXPECT_XTERM_IMG" build/web/runtime/vt/xterm-addon-image.js || true
  dl "${CDN_BASE}empty.html" build/web/runtime/empty.html
  verify_arg "$EXPECT_EMPTY" build/web/runtime/empty.html || true
  echo "Built build/web/ (build $build_id) — upload that folder to any static web host."
fi
