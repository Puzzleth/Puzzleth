#!/usr/bin/env bash
# Build Puzzleth for Android: build/android/Puzzleth-<version>.apk, the web version (tools/build_web.sh)
# in a full-screen app (tools/android/src). Install it with:  adb install -r build/android/Puzzleth-*.apk
#
# The APK is private: build/ is never committed, and no workflow builds or publishes it.
#
# Needs a JDK (17 or newer) and the Android SDK with a platform and build-tools, e.g. on a Mac:
#   brew install openjdk@17 && brew install --cask android-commandlinetools
#   sdkmanager --sdk_root=/opt/homebrew/share/android-commandlinetools "platforms;android-35" "build-tools;35.0.0"
# and what tools/build_web.sh needs (python3 with pygbag).
#
#   tools/android/build_apk.sh              # build the web version, then the APK
#   tools/android/build_apk.sh --skip-web   # reuse build/web from the last web build
#
# The APK is signed with a key of your own, made on the first build and kept outside the repository
# (PUZZLETH_KEYSTORE, by default ~/.puzzleth/android-release.keystore, with its password in a .pass file
# beside it). Keep both safe: Android only installs an update signed with the same key.
set -euo pipefail
cd "$(dirname "$0")/../.."
ROOT=$PWD

# ---------------------------------------------------------------- tools
if [[ -z "${JAVA_HOME:-}" ]]; then
  for j in /opt/homebrew/opt/openjdk@17 /opt/homebrew/opt/openjdk "$(/usr/libexec/java_home -v 17+ 2>/dev/null || true)"; do
    [[ -n "$j" && -x "$j/bin/javac" ]] && { export JAVA_HOME=$j; break; }
  done
fi
[[ -n "${JAVA_HOME:-}" ]] && export PATH="$JAVA_HOME/bin:$PATH"
command -v javac >/dev/null || { echo "error: no JDK found (set JAVA_HOME)" >&2; exit 1; }

SDK=${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}
if [[ -z "$SDK" ]]; then
  for d in /opt/homebrew/share/android-commandlinetools "$HOME/Library/Android/sdk" "$HOME/Android/Sdk"; do
    [[ -d "$d/build-tools" ]] && { SDK=$d; break; }
  done
fi
[[ -n "$SDK" && -d "$SDK/build-tools" ]] || { echo "error: no Android SDK found (set ANDROID_HOME)" >&2; exit 1; }
BT=$(ls -d "$SDK"/build-tools/* | sort -V | tail -1)
PLATFORM=$(ls -d "$SDK"/platforms/android-* | sort -V | tail -1)
ANDROID_JAR=$PLATFORM/android.jar
[[ -f "$ANDROID_JAR" ]] || { echo "error: no Android platform in $SDK/platforms" >&2; exit 1; }

# ---------------------------------------------------------------- version
VERSION=$(python3 -c 'import re; print(re.search(r"VERSION = \"([^\"]+)\"", open("puzzleth/__init__.py").read()).group(1))')
IFS=. read -r MAJOR MINOR PATCH <<< "$VERSION"
VERSION_CODE=$((MAJOR * 10000 + MINOR * 100 + PATCH))

# ---------------------------------------------------------------- the web version
if [[ "${1:-}" != "--skip-web" ]]; then
  tools/build_web.sh
fi
[[ -f build/web/index.html ]] || { echo "error: build/web is missing: run tools/build_web.sh" >&2; exit 1; }

# ---------------------------------------------------------------- the app
OUT=build/android
WORK=$OUT/work
rm -rf "$WORK"
mkdir -p "$WORK/res/mipmap" "$WORK/assets" "$WORK/classes" "$WORK/dex"
cp tools/web/favicon.png "$WORK/res/mipmap/ic_launcher.png"
cp -R build/web "$WORK/assets/web"
rm -f "$WORK/assets/web/"*.tar.gz   # pygbag's copy of the source: not needed to play
sed -e "s/@VERSION_CODE@/$VERSION_CODE/" -e "s/@VERSION_NAME@/$VERSION/" tools/android/AndroidManifest.xml \
  > "$WORK/AndroidManifest.xml"

"$BT/aapt2" compile --dir "$WORK/res" -o "$WORK/res.zip"
# songs, pictures and the game's own archive are compressed already
"$BT/aapt2" link -o "$WORK/unsigned.apk" -I "$ANDROID_JAR" --manifest "$WORK/AndroidManifest.xml" \
  -A "$WORK/assets" -0 mp3 -0 ogg -0 png -0 apk "$WORK/res.zip"

javac --release 11 -nowarn -classpath "$ANDROID_JAR" -d "$WORK/classes" $(find tools/android/src -name '*.java')
"$BT/d8" --release --min-api 24 --lib "$ANDROID_JAR" --output "$WORK/dex" $(find "$WORK/classes" -name '*.class')
(cd "$WORK/dex" && zip -q -u "$ROOT/$WORK/unsigned.apk" classes.dex)
"$BT/zipalign" -f -p 4 "$WORK/unsigned.apk" "$WORK/aligned.apk"

# ---------------------------------------------------------------- signing
KEYSTORE=${PUZZLETH_KEYSTORE:-$HOME/.puzzleth/android-release.keystore}
PASSFILE=$KEYSTORE.pass
if [[ ! -f "$KEYSTORE" ]]; then
  mkdir -p "$(dirname "$KEYSTORE")"
  (umask 077 && openssl rand -hex 24 > "$PASSFILE")
  keytool -genkeypair -keystore "$KEYSTORE" -storepass "$(cat "$PASSFILE")" -alias puzzleth -keyalg RSA \
    -keysize 4096 -validity 10000 -dname "CN=Puzzleth" >/dev/null
  chmod 600 "$KEYSTORE"
  echo "Made a signing key: $KEYSTORE (password in $PASSFILE). Back both up somewhere private." >&2
fi
APK=$OUT/Puzzleth-$VERSION.apk
"$BT/apksigner" sign --ks "$KEYSTORE" --ks-pass "file:$PASSFILE" --ks-key-alias puzzleth --out "$APK" \
  "$WORK/aligned.apk"
"$BT/apksigner" verify "$APK"
rm -rf "$WORK"
echo "Built $APK ($(du -h "$APK" | cut -f1 | tr -d ' ')). Install it with:  adb install -r $APK"
