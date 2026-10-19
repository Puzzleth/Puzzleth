"""Drawing helpers: anti-aliased primitives, glows, panels, text and the skill-point rings."""
import math
import random

import pygame
import pygame.gfxdraw

from . import i18n
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


def fit_width(s, size, width, bold=False, mono=False, translate=True):
    """fit_size for a single line of text that must stay within ``width``."""
    s = i18n._(str(s)) if translate else str(s)
    return fit_size(size, lambda k: T.font(k, bold, mono).size(str(s))[0] <= width)


def block_height(paras, width, size, bold=False, spacing=1.35, gap=0):
    """Height text_block would use for each of ``paras``, plus ``gap`` after each."""
    paras = [i18n._(str(p)) for p in paras]
    lh = int(T.font(size, bold).get_linesize() * spacing)
    return sum(lh * len(wrap(p, size, width, bold)) + gap for p in paras)


def render_text(s, size, color, bold=False, mono=False, translate=True):
    """``s`` rendered in the current language (see i18n), unless ``translate`` is False."""
    s = i18n._(str(s)) if translate else str(s)
    key = (s, size, tuple(color), bold, mono)
    img = _text_cache.get(key)
    if img is None:
        if len(_text_cache) > 3000:
            _text_cache.clear()
        img = T.font(size, bold, mono).render(s, True, color)
        _text_cache[key] = img
    return img


def text(surf, s, pos, size=20, color=T.TEXT, bold=False, mono=False, anchor="topleft", alpha=255, translate=True):
    img = render_text(str(s), size, color, bold, mono, translate)
    rect = img.get_rect(**{anchor: (int(pos[0]), int(pos[1]))})
    if alpha < 255:
        img = img.copy()
        img.set_alpha(int(alpha))
    surf.blit(img, rect)
    return rect


def wrap(s, size, width, bold=False):
    s = i18n._(str(s))
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


# Rings are drawn once into a sprite and then just blitted: working out their outlines every frame
# was most of the time a frame took, which slow phones running the browser version can't spare. The
# sprite is drawn at twice the size and scaled down, which smooths its edges in every build.
_ring_cache = {}
_SS = 2   # supersampling


def _arc_raw(surf, center, r, width, a0, a1, color, caps=False):
    """arc() without anti-aliasing, for a supersampled sprite."""
    if a1 - a0 <= 1e-3:
        return
    cx, cy = center
    steps = max(3, int((a1 - a0) * r / 3))
    outer = _arc_pts(cx, cy, r + width / 2, a0, a1, steps)
    inner = _arc_pts(cx, cy, r - width / 2, a0, a1, steps)
    pygame.draw.polygon(surf, color, _ipts(outer + inner[::-1]))
    if caps:
        for a in (a0, a1):
            pygame.draw.circle(surf, color, _ipts([(cx + r * math.sin(a), cy - r * math.cos(a))])[0], width / 2)


def _ring_sprite(surf, key, center, r, width, background, draw):
    sprite = _ring_cache.get(key)
    half = int(r + width / 2) + 3
    if sprite is None:
        if len(_ring_cache) > 1500:
            _ring_cache.clear()
        big = pygame.Surface((2 * half * _SS, 2 * half * _SS), pygame.SRCALPHA)
        big.fill((*background[:3], 0))   # (so the edges fade out in the ring's colour, not black)
        draw(big, (half * _SS, half * _SS), _SS)
        sprite = _ring_cache[key] = pygame.transform.smoothscale(big, (2 * half, 2 * half))
    surf.blit(sprite, (round(center[0]) - half, round(center[1]) - half))


def ring(surf, center, r, width, frac, color, track=T.TRACK, caps=True):
    """Progress ring starting at 12 o'clock."""
    frac = round(clamp(frac, 0, 1) * 400) / 400

    def draw(s, c, k):
        _arc_raw(s, c, r * k, width * k, 0, TAU - 1e-4, track)
        if frac > 0:
            _arc_raw(s, c, r * k, width * k, 0, TAU * frac - (1e-4 if frac >= 1 else 0), color, caps=caps and frac < 1)
    _ring_sprite(surf, ("ring", r, width, frac, tuple(color), tuple(track), caps), center, r, width, track, draw)


def pips(surf, center, r, width, n, filled, color, track=T.TRACK, ghost=0, ghost_color=None, gap=None):
    """A ring of n skill-point segments; `filled` lit, up to `ghost` shown dim (e.g. personal best)."""
    seg = TAU / n
    gap = seg * 0.22 if gap is None else gap
    ghost_color = ghost_color or lerp_color(track, color, 0.38)

    def draw(s, c, k):
        for i in range(n):
            a0 = i * seg + gap / 2
            a1 = (i + 1) * seg - gap / 2
            if i < filled:
                col = color
            elif i < ghost:
                col = ghost_color
            else:
                col = track
            _arc_raw(s, c, r * k, width * k, a0, a1, col)
    key = ("pips", r, width, n, filled, tuple(color), tuple(track), ghost, tuple(ghost_color), gap)
    _ring_sprite(surf, key, center, r, width, track, draw)


# ---------------------------------------------------------------- glow & panels

_glow_cache = {}


_glow_falloff = None


def _glow_surface(radius, color, strength):
    global _glow_falloff
    key = (radius, color, strength)
    s = _glow_cache.get(key)
    if s is None:
        if len(_glow_cache) > 1500:
            _glow_cache.clear()
        if _glow_falloff is None:   # the soft round shape, made once; each glow is it scaled and tinted
            n = 40
            _glow_falloff = pygame.Surface((n, n))
            half = n / 2
            for y in range(n):
                for x in range(n):
                    d = math.hypot(x - half + 0.5, y - half + 0.5) / half
                    v = int(255 * max(0.0, 1.0 - d) ** 2.2)
                    _glow_falloff.set_at((x, y), (v, v, v))
        s = pygame.transform.smoothscale(_glow_falloff, (radius * 2, radius * 2))
        s.fill(tuple(min(255, int(c * strength)) for c in color), special_flags=pygame.BLEND_MULT)
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


_overlay_cache = {}


def overlay(surf, color=(0, 0, 0), alpha=150):
    # on the game canvas this covers the whole stage around it too (see display.py)
    surf = surf.get_abs_parent()
    key = (surf.get_size(), tuple(color))
    s = _overlay_cache.get(key)
    if s is None:   # one plain surface per stage size, faded with set_alpha: no new surface every frame
        _overlay_cache.clear()
        s = _overlay_cache[key] = pygame.Surface(surf.get_size())
        s.fill(color)
    s.set_alpha(int(alpha))
    surf.blit(s, (0, 0))


# ---------------------------------------------------------------- grades

# (top of the letter, bottom of the letter, outline) for each grade (see scoring.GRADES)
_GRADE_STYLE = {
    "S": ((255, 248, 200), (226, 150, 30), (88, 48, 4)),
    "A": ((196, 255, 224), (52, 186, 116), (8, 58, 34)),
    "B": ((206, 220, 255), (88, 124, 238), (14, 28, 78)),
    "C": ((255, 222, 176), (214, 124, 46), (76, 38, 10)),
    "D": ((150, 142, 136), (82, 76, 72), (24, 21, 21)),
}
_grade_cache = {}


def _gradient(size, top, bottom):
    w, h = size
    strip = pygame.Surface((1, h), pygame.SRCALPHA)
    for y in range(h):
        strip.set_at((0, y), (*lerp_color(top, bottom, y / max(1, h - 1)), 255))
    return pygame.transform.scale(strip, (w, h))


def _masked(layer, mask):
    """``layer`` kept only where the letter ``mask`` (white, anti-aliased) is."""
    layer.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return layer


def _tatter(surf, size, rng):
    """Batter a D: grime, chipped edges, holes and cracks right through it."""
    w, h = surf.get_size()
    clear = (0, 0, 0, 0)
    for _ in range(4):   # cracks: jagged lines from an edge in towards the middle
        x, y = rng.choice([(rng.uniform(0, w), 0), (rng.uniform(0, w), h), (0, rng.uniform(0, h)),
                           (w, rng.uniform(0, h))])
        pts = [(x, y)]
        for _ in range(4):
            x += (w / 2 - x) * rng.uniform(0.2, 0.45) + rng.uniform(-1, 1) * size * 0.08
            y += (h / 2 - y) * rng.uniform(0.2, 0.45) + rng.uniform(-1, 1) * size * 0.08
            pts.append((x, y))
        pygame.draw.lines(surf, clear, False, _ipts(pts), max(1, round(size / 26)))
    for _ in range(7):   # chips bitten out of the edges
        cx, cy = rng.uniform(0, w), rng.choice([rng.uniform(0, h * 0.2), rng.uniform(h * 0.8, h)])
        r = size * rng.uniform(0.04, 0.09)
        pygame.draw.polygon(surf, clear, _ipts([(cx + r * math.cos(a), cy + r * math.sin(a))
                                                for a in (rng.uniform(0, TAU) for _ in range(5))]))
    for _ in range(6):   # small holes
        pygame.draw.circle(surf, clear, (rng.uniform(0, w), rng.uniform(0, h)), max(1, size * rng.uniform(0.015, 0.035)))


def _grade_surface(letter, size):
    """The letter itself (without its animated glow and sparkles), cached."""
    key = (letter, size, T.large_text)
    img = _grade_cache.get(key)
    if img is not None:
        return img
    top, bottom, edge = _GRADE_STYLE[letter]
    font = T.font(size, True)
    mask = font.render(letter, True, (255, 255, 255))
    outline = font.render(letter, True, edge)
    o = max(1, round(T.text_px(size) / 22))   # outline thickness
    pad = 3 * o
    img = pygame.Surface((mask.get_width() + 2 * pad, mask.get_height() + 2 * pad), pygame.SRCALPHA)
    shadow = outline.copy()
    shadow.set_alpha(150)
    img.blit(shadow, (pad + o, pad + 2 * o))
    for k in range(12):
        a = k * TAU / 12
        img.blit(outline, (pad + round(o * math.cos(a)), pad + round(o * math.sin(a))))
    face = _masked(_gradient(mask.get_size(), top, bottom), mask)
    if letter == "S":   # a polished shine across the top half
        shine = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        shine.fill((255, 255, 255, 110), (0, 0, mask.get_width(), round(mask.get_height() * 0.47)))
        face.blit(_masked(shine, mask), (0, 0))
    elif letter == "D":   # dull and grimy
        rng = random.Random(size * 31 + 7)
        grime = pygame.Surface(mask.get_size(), pygame.SRCALPHA)
        for _ in range(mask.get_width() * mask.get_height() // 40):
            grime.set_at((rng.randrange(mask.get_width()), rng.randrange(mask.get_height())),
                         (30, 26, 24, rng.randrange(60, 200)))
        face.blit(_masked(grime, mask), (0, 0))
    img.blit(face, (pad, pad))
    if letter == "D":
        _tatter(img, T.text_px(size), random.Random(size * 17 + 3))
        img = pygame.transform.rotozoom(img, 7, 1)   # knocked askew
    if len(_grade_cache) > 200:
        _grade_cache.clear()
    _grade_cache[key] = img
    return img


def _sparkle(surf, center, r, color):
    x, y = center
    poly(surf, [(x, y - r), (x + r * 0.22, y), (x, y + r), (x - r * 0.22, y)], color)
    poly(surf, [(x - r, y), (x, y - r * 0.22), (x + r, y), (x, y + r * 0.22)], color)


def grade_badge(surf, letter, center, size, t=0.0, alpha=255):
    """Draw a grade letter centred on ``center``: S in shining gold with sparkles, A to C clean and
    coloured, D battered and cracked. Returns its rect."""
    img = _grade_surface(letter, size)
    rect = img.get_rect(center=(int(center[0]), int(center[1])))
    px = T.text_px(size)
    if letter == "S":
        glow(surf, rect.center, px * 1.5, T.GOLD, (0.32 + 0.12 * math.sin(t * 2.2)) * alpha / 255)
    elif letter == "A":
        glow(surf, rect.center, px * 1.2, T.GRADE_COLORS["A"], 0.16 * alpha / 255)
    if alpha < 255:
        img = img.copy()
        img.set_alpha(int(alpha))
    surf.blit(img, rect)
    if letter == "S" and alpha >= 255:
        for k, (fx, fy) in enumerate(((0.92, 0.18), (0.08, 0.72), (0.78, 0.9))):
            twinkle = max(0.0, math.sin(t * 2.6 + k * 2.1))
            if twinkle > 0.05:
                at = (rect.x + rect.w * fx, rect.y + rect.h * fy)
                glow(surf, at, px * 0.35 * twinkle + 4, T.GOLD, 0.6 * twinkle)
                _sparkle(surf, at, px * 0.16 * twinkle + 1, (255, 252, 230))
    return rect


# ---------------------------------------------------------------- background

# Set on devices too slow for the full background (see App._check_speed): it then has fewer motes.
low_power = False


class Background:
    """Soft radial gradient with nebula tints and drifting motes. It is laid out on the canvas
    and continues past its edges to fill a stage of any shape (see display.py)."""

    def __init__(self):
        self.size = None

    def _build(self, w, h):
        self.size = (w, h)
        self.canvas_h = T.H
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
        if surf.get_size() != self.size or T.H != self.canvas_h:
            self._build(*surf.get_size())
        h = self.size[1]
        surf.blit(self.base, (0, 0))
        for x, y, size, phase, speed in self.motes[::4] if low_power else self.motes:
            yy = (y - t * speed) % (h + 40) - 20
            xx = x + math.sin(t * 0.2 + phase) * 12
            a = 0.25 + 0.35 * (0.5 + 0.5 * math.sin(t * 0.9 + phase))
            glow(surf, (xx, yy), size * 3, (120, 145, 220), a)
