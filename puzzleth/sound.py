"""Sound effects, spoken digits and background music.

Every sound is a file you can replace: put a file with the same name (any of .ogg, .wav, .mp3) in
one of the sound folders and it is used instead (sounds/README.md lists the names). Music is every
audio file in a music folder, played in a shuffled loop, each fading in and out. Folders, first
match wins:

    ~/.puzzleth/sounds/   ~/.puzzleth/music/       (desktop only: next to your saved progress)
    puzzleth/sounds/      puzzleth/music/          (bundled with the game, also in the web build)

Without an audio device everything here silently does nothing.
"""

import os
import random
import threading
from urllib.parse import quote

import pygame

from . import storage, web

PKG = os.path.dirname(os.path.abspath(__file__))
EXTS = (".ogg", ".wav", ".mp3")
USER_FIRST = {".wav": 0, ".mp3": 1, ".ogg": 2}
MUSIC_END = pygame.USEREVENT + 7
# written by tools/build_web.sh, which serves the music beside the page instead of packing it
STREAMED = os.path.join(PKG, "music", "streamed.txt")
DUCK = 0.25  # music volume while digits are being spoken
FADE_IN = 4.0  # seconds of fade at the start of every song
FADE_OUT = 6.0  # ... and at its end

# per-sound loudness (0..1), on top of the "Sound effects" setting
LEVELS = {
    "tap": 0.5,
    "key": 0.5,
    "select": 0.7,
    "blip": 0.6,
    "tick": 0.7,
    **{f"digit{d}": 1.0 for d in range(1, 10)},
}

_ok = False
_sounds = {}
_sfx = 0.75
_music = 0.5
_ducked = False
_tracks = []
_streaming = False  # web build: _tracks are URLs, played by web.stream_music
_queue = []
_current = None  # the music file loaded now
_started = 0  # pygame.time.get_ticks() when it started playing
_fade = 0.0  # where its fade in or out is now (0 silent .. 1 full)
_lengths = {}  # path -> seconds, measured in the background on the desktop
_check = 0.0
_silent_buffer = None  # holds the silent sound used to stabilize audio device on init


def folders(kind):
    """Where sounds ("sounds") or music ("music") are looked for, highest priority first."""
    dirs = [os.path.join(PKG, kind)]
    if not web.IS_WEB:
        dirs.insert(0, os.path.join(os.path.dirname(storage.profile_path()), kind))
    return dirs


def _create_silent_buffer():
    """Create a silent sound to stabilize the audio device on initialization.
    
    On Windows, the audio device can produce a "pop" when initialized because the output
    starts without a stabilization period. Playing a brief silent buffer immediately after
    mixer.init() prevents this artifact by letting the audio system settle before any real
    sound is played.
    """
    global _silent_buffer
    if not pygame.mixer.get_init():
        return
    try:
        # Create 100ms of silent audio (44100 Hz, 16-bit, 2 channels)
        # At 44100 Hz sampling rate: 44100 samples/sec * 0.1 sec = 4410 samples
        # 16-bit stereo = 2 bytes per sample * 2 channels = 4 bytes per sample frame
        sample_count = int(44100 * 0.1)
        silence = bytes(sample_count * 4)  # 16-bit stereo = 4 bytes per sample frame
        _silent_buffer = pygame.mixer.Sound(buffer=silence)
        _silent_buffer.set_volume(0)  # Ensure it's silent
        _silent_buffer.play()  # Play it to initialize the output device
    except (pygame.error, Exception):
        # If creating the silent buffer fails, continue anyway
        # The pop is a minor issue compared to not being able to play any sounds
        _silent_buffer = None


def init(sfx_volume=0.75, music_volume=0.5):
    global _ok
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(16)
        _create_silent_buffer()
        _ok = True
    except pygame.error:
        _ok = False
        return
    _load_sounds()
    _find_tracks()
    if _tracks and not web.IS_WEB:
        threading.Thread(
            target=_measure_lengths, args=(list(_tracks),), daemon=True
        ).start()
    pygame.mixer.music.set_endevent(MUSIC_END)
    set_volumes(sfx_volume, music_volume)


def available():
    return _ok


def _sound_files():
    """{name: path}. Earlier folders win; within a folder, .wav and .mp3 win over the bundled .ogg."""
    found = {}
    for d in folders("sounds"):
        if not os.path.isdir(d):
            continue
        files = [os.path.splitext(f) + (f,) for f in os.listdir(d)]
        for name, ext, f in sorted(
            files, key=lambda x: (x[0], USER_FIRST.get(x[1].lower(), 9))
        ):
            if ext.lower() in EXTS and name not in found:
                found[name] = os.path.join(d, f)
    return found


def _load_sounds():
    _sounds.clear()
    for name, path in _sound_files().items():
        try:
            _sounds[name] = pygame.mixer.Sound(path)
        except pygame.error as e:
            print(f"Puzzleth: can't load sound {os.path.basename(path)}: {e}")


def _find_tracks():
    global _streaming
    _tracks.clear()
    _streaming = web.IS_WEB and os.path.isfile(STREAMED)
    if _streaming:  # so the game starts without waiting for songs it may never play
        with open(STREAMED, encoding="utf-8") as f:
            _tracks.extend("music/" + quote(n) for n in f.read().splitlines() if n)
        return
    for d in folders("music"):
        if os.path.isdir(d):
            _tracks.extend(
                os.path.join(d, f)
                for f in sorted(os.listdir(d))
                if os.path.splitext(f)[1].lower() in EXTS
            )


def tracks():
    return list(_tracks)


def play(name):
    if not _ok or _sfx <= 0:
        return
    s = _sounds.get(name)
    if s:
        s.set_volume(_sfx * LEVELS.get(name, 1.0))
        s.play()


def set_volumes(sfx, music):
    global _sfx, _music
    _sfx, _music = sfx, music
    if not _ok:
        return
    if music <= 0 or not _tracks:
        _stop_music()
    elif _current:
        _apply_volume()
    else:
        _next_track()


def _apply_volume():
    v = _music * (DUCK if _ducked else 1.0) * _fade
    if _streaming:
        web.music_volume(v)
    else:
        pygame.mixer.music.set_volume(v)


def duck(on):
    """Turn the music down (e.g. while digits are read out) or back up."""
    global _ducked
    if on != _ducked:
        _ducked = on
        if _ok and _current:
            _apply_volume()


def _stop_music():
    global _current
    if _current and _streaming:
        web.stop_music()
        _current = None
    elif _current:
        pygame.mixer.music.stop()
        _current = None
        if web.IS_WEB:
            web.want_music(False)


def _next_track():
    global _current, _started, _fade
    if not _queue:
        _queue.extend(random.sample(_tracks, len(_tracks)))
        if len(_tracks) > 1 and _queue[-1] == _current:  # no song twice in a row
            _queue.insert(0, _queue.pop())
    path = _queue.pop()
    if _streaming:  # the next click, tap or key press starts it if the browser won't yet
        web.stream_music(path)
        _current, _started, _fade = path, pygame.time.get_ticks(), 0.0
        _apply_volume()
        return
    try:
        pygame.mixer.music.load(path)
        _current, _started, _fade = path, pygame.time.get_ticks(), 0.0
        _apply_volume()  # after loading: in browsers every track has its own volume
        pygame.mixer.music.play()  # once; the next song (or this one again) follows when it ends
    except pygame.error as e:
        print(f"Puzzleth: can't play {os.path.basename(path)}: {e}")
        _current = None
        _tracks.remove(path)
        if _tracks:
            _next_track()
        return
    if web.IS_WEB:
        web.want_music(True)  # browsers start it on the next click, tap or key press


def _measure_lengths(paths):
    """pygame can't tell how long a song is without decoding it, so do that off the main thread."""
    for path in paths:
        try:
            _lengths[path] = pygame.mixer.Sound(path).get_length()
        except pygame.error:
            pass


def _position():
    """(seconds played, song length or None) of the current song."""
    if web.IS_WEB:
        return web.music_position()
    return (pygame.time.get_ticks() - _started) / 1000, _lengths.get(_current)


def handle_event(e):
    if e.type == MUSIC_END and _ok and _music > 0 and _current:
        _next_track()


def update(dt):
    """Fade songs in and out, and in a browser notice when one ends (no MUSIC_END event comes)."""
    global _check, _fade
    if not (_ok and _current and _music > 0):
        return
    _check += dt
    if _check < 0.1:
        return
    _check = 0.0
    if web.IS_WEB and web.music_ended():
        _next_track()
        return
    pos, length = _position()
    fade = max(0.0, min(1.0, pos / FADE_IN))
    if length:
        fade = min(fade, max(0.0, (length - pos) / FADE_OUT))
    fade = round(fade, 2)
    if fade != _fade:
        _fade = fade
        _apply_volume()
