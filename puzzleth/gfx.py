"""Drawing helpers: anti-aliased primitives, glows, panels, text and the skill-point rings."""
import math
import random

import pygame
import pygame.gfxdraw

from . import theme as T

TAU = math.tau


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(x, lo, hi):
    return lo if x < lo else hi if x > hi else x


def lerp_color(c1, c2, t):
    t = clamp(t, 0.0, 1.0)
    return tuple(int(round(a + (b - a) * t)) for a, b in zip(c1, c2))


def scale_color(c, k):
    return tuple(int(clamp(v * k, 0, 255)) for v in c[:3])


def ease_out(t):
    t = clamp(t, 0.0, 1.0)
    return 1 - (1 - t) ** 3


def ease_in_out(t):
    t = clamp(t, 0.0, 1.0)
    return 3 * t * t - 2 * t * t * t


# ---------------------------------------------------------------- text

_text_cache = {}


def set_large_text(on):
    """Switch theme.large_text; returns True if that changed anything."""
    if T.large_text == on:
        return False
    T.large_text = on
    _text_cache.clear()
    return True


def fit_size(size, fits):
    """The largest text size, from ``size`` down to no smaller than ``size`` is drawn on a desktop,
    for which ``fits(size)`` holds. Large text can otherwise push dense panels past their edges."""
    s = size
    while s > 1 and T.text_px(s - 1) >= size and not fits(s):
        s -= 1
    return s


def fit_width(s, size, width, bold=False, mono=False):
    """fit_size for a single line of text that must stay within ``width``."""
    return fit_size(size, lambda k: T.font(k, bold, mono).size(str(s))[0] <= width)


def block_height(paras, width, size, bold=False, spacing=1.35, gap=0):
    """Height text_block would use for each of ``paras``, plus ``gap`` after each."""
    lh = int(T.font(size, bold).get_linesize() * spacing)
    return sum(lh * len(wrap(p, size, width, bold)) + gap for p in paras)


def render_text(s, size, color, bold=False, mono=False):
    key = (s, size, tuple(color), bold, mono)
    img = _text_cache.get(key)
    if img is None:
        if len(_text_cache) > 3000:
            _text_cache.clear()
        img = T.font(size, bold, mono).render(s, True, color)
        _text_cache[key] = img
    return img


def text(surf, s, pos, size=20, color=T.TEXT, bold=False, mono=False, anchor="topleft", alpha=255):
    img = render_text(str(s), size, color, bold, mono)
    rect = img.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    if alpha < 255:
        img = img.copy()
        img.set_alpha(int(alpha))
    surf.blit(img, rect)
    return rect


def wrap(s, size, width, bold=False):
    f = T.font(size, bold)
    lines = []
    for para in str(s).split("\n"):
        words = para.split(" ")
        line = ""
        for w in words:
            trial = (line + " " + w).strip()
            if f.size(trial)[0] <= width or not line:
                line = trial
            else:
                lines.append(line)
                line = w
        lines.append(line)
    return lines


def text_block(surf, s, pos, width, size=20, color=T.TEXT, bold=False, spacing=1.35, align="left", alpha=255):
    """Draw wrapped text; returns total height used."""
    x, y = pos
    lh = int(T.font(size, bold).get_linesize() * spacing)
    lines = wrap(s, size, width, bold)
    for i, line in enumerate(lines):
        if align == "center":
            text(surf, line, (x + width / 2, y + i * lh), size, color, bold, anchor="midtop", alpha=alpha)
        else:
            text(surf, line, (x, y + i * lh), size, color, bold, alpha=alpha)
    return lh * len(lines)


# ---------------------------------------------------------------- primitives


def _ipts(pts):
    return [(int(round(x)), int(round(y))) for x, y in pts]


def _gfxdraw_works():
    """The browser (pygbag) build of pygame has a gfxdraw that fails on every call."""
    try:
        pygame.gfxdraw.filled_circle(pygame.Surface((4, 4)), 2, 2, 1, (255, 255, 255))
        return True
    except pygame.error:
        return False


_GFXDRAW = _gfxdraw_works()


def poly(surf, pts, color):
    p = _ipts(pts)
    if len(p) < 3:
        return
    if not _GFXDRAW:
        pygame.draw.polygon(surf, color, p)
        pygame.draw.aalines(surf, color, True, p)
        return
    pygame.gfxdraw.filled_polygon(surf, p, color)
    pygame.gfxdraw.aapolygon(surf, p, color)


def circle(surf, center, r, color, width=0):
    if r <= 0:
        return
    if hasattr(pygame.draw, "aacircle"):
        pygame.draw.aacircle(surf, color, (center[0], center[1]), r, width)
        return
    x, y, r = int(round(center[0])), int(round(center[1])), int(round(r))
    if not _GFXDRAW:
        pygame.draw.circle(surf, color, (x, y), r, int(width))
        return
    if width:
        for i in range(int(width)):
            pygame.gfxdraw.aacircle(surf, x, y, r - i, color)
    else:
        pygame.gfxdraw.filled_circle(surf, x, y, r, color)
        pygame.gfxdraw.aacircle(surf, x, y, r, color)


def thick_line(surf, p1, p2, w, color, caps=True):
    (x1, y1), (x2, y2) = p1, p2
    dx, dy = x2 - x1, y2 - y1
    length = math.hypot(dx, dy) or 1e-6
    nx, ny = -dy / length * w / 2, dx / length * w / 2
    poly(surf, [(x1 + nx, y1 + ny), (x2 + nx, y2 + ny), (x2 - nx, y2 - ny), (x1 - nx, y1 - ny)], color)
    if caps:
        circle(surf, p1, w / 2, color)
        circle(surf, p2, w / 2, color)


def _arc_pts(cx, cy, r, a0, a1, steps):
    # angle 0 = 12 o'clock, increasing clockwise
    out = []
    for i in range(steps + 1):
        a = a0 + (a1 - a0) * i / steps
        out.append((cx + r * math.sin(a), cy - r * math.cos(a)))
    return out


def arc(surf, center, r, width, a0, a1, color, caps=False):
    if a1 - a0 <= 1e-3:
        return
    cx, cy = center
    steps = max(3, int((a1 - a0) * r / 3))
    outer = _arc_pts(cx, cy, r + width / 2, a0, a1, steps)
    inner = _arc_pts(cx, cy, r - width / 2, a0, a1, steps)
    poly(surf, outer + inner[::-1], color)
    if caps:
        for a in (a0, a1):
            circle(surf, (cx + r * math.sin(a), cy - r * math.cos(a)), width / 2, color)


def ring(surf, center, r, width, frac, color, track=T.TRACK, caps=True):
    """Progress ring starting at 12 o'clock."""
    arc(surf, center, r, width, 0, TAU - 1e-4, track)
    frac = clamp(frac, 0, 1)
    if frac > 0:
        arc(surf, center, r, width, 0, TAU * frac - (1e-4 if frac >= 1 else 0), color, caps=caps and frac < 1)


def pips(surf, center, r, width, n, filled, color, track=T.TRACK, ghost=0, ghost_color=None, gap=None):
    """A ring of n skill-point segments; `filled` lit, up to `ghost` shown dim (e.g. personal best)."""
    seg = TAU / n
    gap = seg * 0.22 if gap is None else gap
    ghost_color = ghost_color or lerp_color(track, color, 0.38)
    for i in range(n):
        a0 = i * seg + gap / 2
        a1 = (i + 1) * seg - gap / 2
        if i < filled:
            c = color
        elif i < ghost:
            c = ghost_color
        else:
            c = track
        arc(surf, center, r, width, a0, a1, c)


# ---------------------------------------------------------------- glow & panels

_glow_cache = {}


def _glow_surface(radius, color, strength):
    key = (radius, color, strength)
    s = _glow_cache.get(key)
    if s is None:
        if len(_glow_cache) > 600:
            _glow_cache.clear()
        n = 40
        small = pygame.Surface((n, n))
        half = n / 2
        for y in range(n):
            for x in range(n):
                d = math.hypot(x - half + 0.5, y - half + 0.5) / half
                f = max(0.0, 1.0 - d) ** 2.2 * strength
                small.set_at((x, y), tuple(min(255, int(c * f)) for c in color))
        s = pygame.transform.smoothscale(small, (radius * 2, radius * 2))
        _glow_cache[key] = s
    return s


def glow(surf, center, radius, color, strength=0.6):
    radius = max(2, int(radius) // 2 * 2)
    strength = round(clamp(strength, 0, 2) * 20) / 20
    if strength <= 0:
        return
    g = _glow_surface(radius, tuple(color[:3]), strength)
    surf.blit(g, g.get_rect(center=(int(center[0]), int(center[1]))), special_flags=pygame.BLEND_ADD)


_panel_cache = {}


def panel(surf, rect, fill=T.PANEL, border=T.BORDER, radius=14, alpha=235, border_w=1):
    rect = pygame.Rect(rect)
    key = (rect.size, tuple(fill), tuple(border) if border else None, radius, alpha, border_w)
    s = _panel_cache.get(key)
    if s is None:
        if len(_panel_cache) > 800:
            _panel_cache.clear()
        s = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(s, (*fill, alpha), s.get_rect(), border_radius=radius)
        if border:
            pygame.draw.rect(s, (*border, 255), s.get_rect(), border_w, border_radius=radius)
        _panel_cache[key] = s
    surf.blit(s, rect)


def overlay(surf, color=(0, 0, 0), alpha=150):
    # on the game canvas this covers the whole stage around it too (see display.py)
    surf = surf.get_abs_parent()
    s = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    s.fill((*color, int(alpha)))
    surf.blit(s, (0, 0))


# ---------------------------------------------------------------- background


class Background:
    """Soft radial gradient with nebula tints and drifting motes. It is laid out on the 1280x800
    canvas and continues past its edges to fill a stage of any shape (see display.py)."""

    def __init__(self):
        self.size = None

    def _build(self, w, h):
        self.size = (w, h)
        ox, oy = (w - T.W) / 2, (h - T.H) / 2
        sw, sh = max(2, round(96 * w / T.W)), max(2, round(60 * h / T.H))
        small = pygame.Surface((sw, sh))
        blobs = [((0.18, 0.2), T.INDEX_COLORS["VCI"], 0.10), ((0.85, 0.8), T.INDEX_COLORS["WMI"], 0.09),
                 ((0.9, 0.15), T.INDEX_COLORS["PRI"], 0.05)]
        for y in range(sh):
            for x in range(sw):
                u, v = (x / (sw - 1) * w - ox) / T.W, (y / (sh - 1) * h - oy) / T.H   # canvas fractions
                d = math.hypot((u - 0.5) * 1.25, v - 0.38)
                c = list(lerp_color(T.BG2, T.BG, clamp(d * 1.5, 0, 1) ** 0.9))
                for (bx, by), col, k in blobs:
                    f = max(0.0, 1 - math.hypot(u - bx, (v - by) * 0.8) / 0.45) ** 2 * k
                    c = [min(255, int(ci + cc * f)) for ci, cc in zip(c, col)]
                small.set_at((x, y), c)
        self.base = pygame.transform.smoothscale(small, (w, h))
        rng = random.Random(11)
        self.motes = [(rng.uniform(0, w), rng.uniform(0, h), rng.uniform(1.5, 4.5), rng.uniform(0, TAU),
                       rng.uniform(3, 12)) for _ in range(round(70 * w * h / (T.W * T.H)))]

    def draw(self, surf, t):
        """Draws on the whole stage: ``surf`` may be the canvas or the stage itself."""
        surf = surf.get_abs_parent()
        if surf.get_size() != self.size:
            self._build(*surf.get_size())
        h = self.size[1]
        surf.blit(self.base, (0, 0))
        for x, y, size, phase, speed in self.motes:
            yy = (y - t * speed) % (h + 40) - 20
            xx = x + math.sin(t * 0.2 + phase) * 12
            a = 0.25 + 0.35 * (0.5 + 0.5 * math.sin(t * 0.9 + phase))
            glow(surf, (xx, yy), size * 3, (120, 145, 220), a)
