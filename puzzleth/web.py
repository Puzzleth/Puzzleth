"""Browser support. In a pygbag (WebAssembly) build ``sys.platform`` is "emscripten" and the page's
JavaScript ``window`` is reachable as ``platform.window``."""
import sys

IS_WEB = sys.platform == "emscripten"


def _window():
    import platform
    return platform.window


def load(key):
    try:
        return _window().localStorage.getItem(key)
    except Exception:
        return None


def save(key, value):
    try:
        _window().localStorage.setItem(key, value)
        return True
    except Exception:
        return False


def copy_text(text):
    """Copy to the clipboard. Browsers may refuse silently, so callers should also show the text."""
    try:
        _window().navigator.clipboard.writeText(text)
        return True
    except Exception:
        return False


def is_portrait():
    try:
        w = _window()
        return w.innerHeight > w.innerWidth
    except Exception:
        return False


# pygbag replaces pygame.mixer.music with an HTML <audio> element per track. These call helpers in
# tools/web/puzzleth.tmpl, which start the music on the first tap (browsers allow no sooner).
def _music_track():
    import pygame
    return sys.modules[pygame.mixer.music.load.__module__].tracks["current"]


def want_music(on):
    try:
        _window().puzzleth_want_music(_music_track() if on else 0)
    except Exception:
        pass


def music_position():
    """(seconds played, length in seconds or None) of the current <audio> track."""
    try:
        w = _window()
        return float(w.puzzleth_music_pos()), float(w.puzzleth_music_length()) or None
    except Exception:
        return 0.0, None


def music_ended():
    """Browsers never send pygame's end-of-track event; ask the <audio> element instead."""
    try:
        return bool(_window().puzzleth_music_ended())
    except Exception:
        return False
