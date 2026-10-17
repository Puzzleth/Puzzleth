"""Palette, layout constants and font loading."""
import os

import pygame

# The canvas every scene is laid out on: 1422x800, the 16:9 shape of most screens, so that the skill
# tree can spread across a widescreen display; W x H is COMPACT_W x COMPACT_H in the compact layout.
FULL_W, FULL_H = 1422, 800
COMPACT_W, COMPACT_H = 1280, 600
W, H = FULL_W, FULL_H
FPS = 60

# Phones in landscape are about twice as wide as tall, so the full canvas only fills their height and
# leaves the sides to the background. The compact layout is a shorter 1280x600 canvas, about the shape
# of the phone, which the page can show larger; scenes arrange themselves to fit it.
compact = False

# Screens wider than the canvas (most phones, ultrawide monitors) widen it to their own shape, up to
# MAX_ASPECT, so that the screens laid out from its edges reach the edges of the screen.
MAX_ASPECT = 2.4


def canvas_width(on, aspect=None):
    """The canvas width for the compact (``on``) or full layout on a screen ``aspect`` times wider than tall."""
    base, h = (COMPACT_W, COMPACT_H) if on else (FULL_W, FULL_H)
    if aspect is None:
        return base
    return max(base, min(round(h * MAX_ASPECT), round(h * aspect)))


def set_compact(on, aspect=None):
    global compact, W, H
    compact = on
    W, H = canvas_width(on, aspect), COMPACT_H if on else FULL_H

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
    "GS": GOLD,
}
INDEX_NAMES = {
    "VCI": "Verbal Comprehension",
    "PRI": "Perceptual Reasoning",
    "WMI": "Working Memory",
    "PSI": "Processing Speed",
    "GS": "Grade Score",
}

# Letter grades (see scoring.py): S is gold, D is a dull, battered grey (see gfx.grade_badge)
GRADE_COLORS = {
    "S": GOLD,
    "A": (86, 222, 150),
    "B": (120, 160, 255),
    "C": (255, 170, 80),
    "D": (150, 140, 136),
}

_FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
# bundled so the game looks the same everywhere, including browsers (both fonts: SIL OFL 1.1)
_FILES = {(False, False): "Inter-Regular.ttf", (True, False): "Inter-Bold.ttf",
          (False, True): "JetBrainsMono-Regular.ttf", (True, True): "JetBrainsMono-Bold.ttf"}
_fonts = {}

# On a phone the full canvas is shown at about half size, which makes the small print unreadable.
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
