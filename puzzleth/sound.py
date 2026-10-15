"""Sound effects, spoken digits and background music.

Every sound is a file you can replace: put a file with the same name (any of .ogg, .wav, .mp3) in
one of the sound folders and it is used instead (sounds/README.md lists the names). Music is every
audio file in a music folder, played in a shuffled loop. Folders, first match wins:

    ~/.puzzleth/sounds/   ~/.puzzleth/music/       (desktop only: next to your saved progress)
    puzzleth/sounds/      puzzleth/music/          (bundled with the game, also in the web build)

Without an audio device everything here silently does nothing.
"""
import os
import random

import pygame

from . import storage, web

PKG = os.path.dirname(os.path.abspath(__file__))
EXTS = (".ogg", ".wav", ".mp3")
USER_FIRST = {".wav": 0, ".mp3": 1, ".ogg": 2}
MUSIC_END = pygame.USEREVENT + 7
DUCK = 0.25          # music volume while digits are being spoken

# per-sound loudness (0..1), on top of the "Sound effects" setting
LEVELS = {"tap": 0.5, "key": 0.5, "select": 0.7, "blip": 0.6, "tick": 0.7,
          **{f"digit{d}": 1.0 for d in range(1, 10)}}

_ok = False
_sounds = {}
_sfx = 0.75
_music = 0.5
_ducked = False
_tracks = []
_queue = []


def folders(kind):
    """Where sounds ("sounds") or music ("music") are looked for, highest priority first."""
    dirs = [os.path.join(PKG, kind)]
    if not web.IS_WEB:
        dirs.insert(0, os.path.join(os.path.dirname(storage.profile_path()), kind))
    return dirs


def init(sfx_volume=0.75, music_volume=0.5):
    global _ok
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
        pygame.mixer.set_num_channels(16)
        _ok = True
    except pygame.error:
        _ok = False
        return
    _load_sounds()
    _find_tracks()
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
        for name, ext, f in sorted(files, key=lambda x: (x[0], USER_FIRST.get(x[1].lower(), 9))):
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
    _tracks.clear()
    for d in folders("music"):
        if os.path.isdir(d):
            _tracks.extend(os.path.join(d, f) for f in sorted(os.listdir(d))
                           if os.path.splitext(f)[1].lower() in EXTS)


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
        pygame.mixer.music.stop()
        return
    pygame.mixer.music.set_volume(music * (DUCK if _ducked else 1.0))
    if not pygame.mixer.music.get_busy():
        _next_track()


def duck(on):
    """Turn the music down (e.g. while digits are read out) or back up."""
    global _ducked
    if on != _ducked:
        _ducked = on
        if _ok and _music > 0:
            pygame.mixer.music.set_volume(_music * (DUCK if on else 1.0))


def _next_track():
    if not _queue:
        _queue.extend(random.sample(_tracks, len(_tracks)))
    path = _queue.pop()
    try:
        pygame.mixer.music.load(path)
        # a single track simply loops; several play one after another
        pygame.mixer.music.play(-1 if len(_tracks) == 1 else 0, fade_ms=2000)
    except pygame.error as e:
        print(f"Puzzleth: can't play {os.path.basename(path)}: {e}")
        _tracks.remove(path)
        if _tracks:
            _next_track()


def handle_event(e):
    if e.type == MUSIC_END and _ok and _music > 0 and len(_tracks) > 1:
        _next_track()
