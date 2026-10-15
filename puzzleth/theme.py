"""Palette, layout constants and font loading."""
import os

import pygame

W, H = 1280, 800
FPS = 60

BG = (8, 11, 24)
BG2 = (22, 28, 58)
PANEL = (19, 25, 47)
PANEL_HI = (31, 40, 72)
BORDER = (44, 56, 96)
TEXT = (233, 237, 250)
MUTED = (140, 150, 188)
DIM = (78, 88, 124)
TRACK = (36, 45, 78)
GOOD = (86, 222, 150)
PARTIAL = (255, 206, 102)
BAD = (255, 102, 118)
GOLD = (255, 212, 112)
ACCENT = (120, 160, 255)

INDEX_COLORS = {
    "VCI": (96, 170, 255),
    "PRI": (64, 224, 170),
    "WMI": (182, 140, 255),
    "PSI": (255, 170, 80),
    "FSIQ": GOLD,
}
INDEX_NAMES = {
    "VCI": "Verbal Comprehension",
    "PRI": "Perceptual Reasoning",
    "WMI": "Working Memory",
    "PSI": "Processing Speed",
    "FSIQ": "Full Scale Score",
}

_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
# bundled so the game looks the same everywhere, including browsers (both fonts: SIL OFL 1.1)
_FILES = {(False, False): "Inter-Regular.ttf", (True, False): "Inter-Bold.ttf",
          (False, True): "JetBrainsMono-Regular.ttf", (True, True): "JetBrainsMono-Bold.ttf"}
_fonts = {}

# On a phone the 1280x800 canvas is shown at about half size, which makes the small print unreadable.
# Large text draws small sizes bigger there (14 -> 20, 20 -> 28) and leaves headings (40+) alone; layouts
# that measure text through font() adapt by themselves.
large_text = False


def text_px(size):
    if not large_text or size >= 40:
        return size
    return round(size * (1 + 0.4 * min(1.0, (40 - size) / 20)))


def font(size, bold=False, mono=False):
    size = text_px(size)
    key = (size, bold, mono)
    f = _fonts.get(key)
    if f is None:
        try:
            f = pygame.font.Font(os.path.join(_FONT_DIR, _FILES[(bold, mono)]), size)
        except (OSError, FileNotFoundError, pygame.error):
            f = pygame.font.Font(None, int(size * 1.35))
            f.set_bold(bold)
        _fonts[key] = f
    return f
