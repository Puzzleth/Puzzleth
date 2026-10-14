"""Palette, layout constants and font loading."""
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
    "FSIQ": "Full Scale IQ",
}

_SANS = ["inter", "adwaitasans", "segoeui", "helveticaneue", "sfprotext", "notosans", "dejavusans", "freesans", "arial"]
_MONO = ["jetbrainsmono", "iosevkanerdfontmono", "adwaitamono", "dejavusansmono", "consolas", "menlo", "freemono"]
_fonts = {}
_names = {}


def _pick(candidates):
    key = tuple(candidates)
    if key not in _names:
        available = set(pygame.font.get_fonts())
        _names[key] = next((c for c in candidates if c in available), None)
    return _names[key]


def font(size, bold=False, mono=False):
    key = (size, bold, mono)
    f = _fonts.get(key)
    if f is None:
        name = _pick(_MONO if mono else _SANS)
        if name:
            f = pygame.font.SysFont(name, size, bold=bold)
        else:
            f = pygame.font.Font(None, int(size * 1.35))
            f.set_bold(bold)
        _fonts[key] = f
    return f
