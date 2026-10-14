"""Interactive UI widgets."""
import pygame

from .display import mouse_pos
from . import gfx
from . import theme as T


def _q(x):
    return round(x * 8) / 8


class Button:
    def __init__(self, rect, label, on_click=None, accent=T.ACCENT, hotkeys=(), size=20, primary=False):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.on_click = on_click
        self.accent = accent
        self.hotkeys = tuple(hotkeys)
        self.size = size
        self.primary = primary
        self.enabled = True
        self.hover = 0.0

    def handle(self, e):
        if not self.enabled:
            return False
        hit = (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and self.rect.collidepoint(e.pos)) or \
              (e.type == pygame.KEYDOWN and e.key in self.hotkeys)
        if hit and self.on_click:
            self.on_click()
        return hit

    def update(self, dt):
        target = 1.0 if self.enabled and self.rect.collidepoint(mouse_pos()) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 14)

    def draw(self, surf):
        h = _q(self.hover)
        if self.primary:
            fill = gfx.lerp_color(gfx.lerp_color(T.PANEL, self.accent, 0.22), gfx.lerp_color(T.PANEL, self.accent, 0.38), h)
            border = self.accent
        else:
            fill = gfx.lerp_color(T.PANEL, T.PANEL_HI, h)
            border = gfx.lerp_color(T.BORDER, self.accent, h)
        if not self.enabled:
            fill, border = T.PANEL, T.TRACK
        if h > 0 and self.enabled:
            gfx.glow(surf, self.rect.center, self.rect.w * 0.45, self.accent, 0.18 * h)
        gfx.panel(surf, self.rect, fill, border, radius=min(14, self.rect.h // 2))
        color = T.TEXT if self.enabled else T.DIM
        gfx.text(surf, self.label, self.rect.center, self.size, color, bold=True, anchor="center")


class OptionCard:
    """A multiple-choice answer card with a numbered badge."""

    def __init__(self, rect, number, label, accent=T.ACCENT, size=21):
        self.rect = pygame.Rect(rect)
        self.number = number
        self.label = label
        self.accent = accent
        self.size = size
        self.hover = 0.0
        self.state = None  # None | "selected" | "good" | "partial" | "bad" | "dim"
        self.tag = None  # small badge text on the right, e.g. "2 pts"

    def hit(self, pos):
        return self.rect.collidepoint(pos)

    def update(self, dt, interactive=True):
        target = 1.0 if interactive and self.rect.collidepoint(mouse_pos()) else 0.0
        self.hover += (target - self.hover) * min(1.0, dt * 14)

    def draw(self, surf):
        h = _q(self.hover)
        state_col = {"selected": self.accent, "good": T.GOOD, "partial": T.PARTIAL, "bad": T.BAD}.get(self.state)
        fill = gfx.lerp_color(T.PANEL, T.PANEL_HI, h)
        border = gfx.lerp_color(T.BORDER, self.accent, h)
        if state_col:
            fill = gfx.lerp_color(T.PANEL, state_col, 0.22)
            border = state_col
            gfx.glow(surf, self.rect.center, self.rect.w * 0.4, state_col, 0.15)
        alpha = 120 if self.state == "dim" else 235
        gfx.panel(surf, self.rect, fill, border, radius=14, alpha=alpha)
        bx, by = self.rect.x + 34, self.rect.centery
        badge = state_col or gfx.lerp_color(T.TRACK, self.accent, 0.35 + 0.5 * h)
        gfx.circle(surf, (bx, by), 16, badge)
        gfx.text(surf, self.number, (bx, by), 17, T.BG if state_col else T.TEXT, bold=True, anchor="center")
        tcol = T.MUTED if self.state == "dim" else T.TEXT
        width = self.rect.w - 90 - (70 if self.tag else 0)
        lines = gfx.wrap(self.label, self.size, width)
        lh = T.font(self.size).get_linesize()
        y0 = self.rect.centery - lh * len(lines) / 2
        for i, line in enumerate(lines):
            gfx.text(surf, line, (self.rect.x + 66, y0 + i * lh), self.size, tcol)
        if self.tag:
            gfx.text(surf, self.tag, (self.rect.right - 22, self.rect.centery), 16, state_col or T.MUTED, bold=True,
                     anchor="midright")


class DigitEntry:
    """Keyboard-driven numeric entry rendered as glowing slots."""

    def __init__(self, center, max_len=12, slot_w=46, accent=T.ACCENT, allow_minus=False):
        self.center = center
        self.max_len = max_len
        self.slot_w = slot_w
        self.accent = accent
        self.allow_minus = allow_minus
        self.value = ""
        self.t = 0.0

    def handle(self, e):
        """Returns 'submit' on Enter, True if the value changed."""
        if e.type != pygame.KEYDOWN:
            return False
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return "submit"
        if e.key == pygame.K_BACKSPACE:
            self.value = self.value[:-1]
            return True
        ch = e.unicode
        if ch and ch.isdigit() and len(self.value) < self.max_len:
            self.value += ch
            return True
        if self.allow_minus and ch == "-" and not self.value:
            self.value = "-"
            return True
        return False

    def update(self, dt):
        self.t += dt

    def draw(self, surf, slots=None, label=None):
        cx, cy = self.center
        if slots:
            gap = 10
            total = slots * self.slot_w + (slots - 1) * gap
            x0 = cx - total / 2
            for i in range(slots):
                r = pygame.Rect(x0 + i * (self.slot_w + gap), cy - 32, self.slot_w, 64)
                filled = i < len(self.value)
                active = i == len(self.value)
                border = self.accent if (filled or active) else T.BORDER
                gfx.panel(surf, r, gfx.lerp_color(T.PANEL, self.accent, 0.12 if filled else 0), border, radius=10)
                if filled:
                    gfx.text(surf, self.value[i], r.center, 34, T.TEXT, bold=True, mono=True, anchor="center")
                elif active and int(self.t * 2) % 2 == 0:
                    pygame.draw.rect(surf, self.accent, (r.centerx - 10, r.bottom - 14, 20, 3), border_radius=2)
        else:
            w = max(220, len(self.value) * 26 + 80)
            r = pygame.Rect(0, 0, w, 72)
            r.center = (cx, cy)
            gfx.glow(surf, r.center, w * 0.5, self.accent, 0.12)
            gfx.panel(surf, r, T.PANEL, self.accent, radius=14, border_w=2)
            tr = gfx.text(surf, self.value, r.center, 38, T.TEXT, bold=True, mono=True, anchor="center") \
                if self.value else pygame.Rect(r.centerx, r.centery - 20, 0, 40)
            if int(self.t * 2) % 2 == 0:
                pygame.draw.rect(surf, self.accent, (tr.right + 4, r.centery - 18, 3, 36), border_radius=1)
        if label:
            gfx.text(surf, label, (cx, cy + 52), 15, T.MUTED, anchor="midtop")
