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
