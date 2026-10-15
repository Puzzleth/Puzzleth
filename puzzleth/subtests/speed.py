"""Processing Speed subtests: Symbol Search and Coding."""
import pygame

from .. import gfx, glyphs
from .. import theme as T
from ..widgets import Button
from .base import SpeedSubtest


class SymbolSearch(SpeedSubtest):
    code = "SS"
    name = "Symbol Search"
    index = "PSI"
    measures = "Visual scanning speed and discrimination"
    max_raw = 60
    duration = 120
    practice_n = 3
    rules = [
        "Each row shows two target symbols and a search group of five.",
        "Mark YES if either target appears in the search group, NO if neither does.",
        "Distractors are deliberately similar: mirrored, rotated or one stroke different.",
        "120-second limit. Work in order without skipping.",
        "Score = correct answers minus incorrect answers.",
    ]
    controls = ["YES:  Y  or  ←        NO:  N  or  →", "Or click the buttons."]

    def setup(self):
        y, w, h = (326, 240, 84) if T.compact else (520, 200, 64)
        self.yes_btn = Button((T.W // 2 - 30 - w, y, w, h), "YES", lambda: self._resp(True), T.GOOD,
                              hotkeys=(pygame.K_y, pygame.K_LEFT), size=24, sound=None)
        self.no_btn = Button((T.W // 2 + 30, y, w, h), "NO", lambda: self._resp(False), T.BAD,
                             hotkeys=(pygame.K_n, pygame.K_RIGHT), size=24, sound=None)

    def new_item(self, practice=False):
        r = self.rng
        targets = glyphs.distinct_set(r, 2, 3)
        present = r.random() < 0.5
        group = []
        while len(group) < 5:
            base = r.choice(targets) if r.random() < 0.7 else glyphs.random_glyph(r)
            g = glyphs.variant(r, base)
            if g not in targets and g not in group:
                group.append(g)
        if present:
            group[r.randrange(5)] = r.choice(targets)
        self.item = {"targets": targets, "group": group, "present": present}

    def _resp(self, yes):
        if self.state in ("practice", "run"):
            self.answer(yes == self.item["present"])

    def explain_wrong(self):
        return "a target IS in the group." if self.item["present"] else "neither target appears exactly."

    def score(self):
        return max(0, self.correct - self.wrong)

    def handle_item(self, e):
        self.yes_btn.handle(e) or self.no_btn.handle(e)

    def update(self, dt):
        super().update(dt)
        self.yes_btn.update(dt)
        self.no_btn.update(dt)

    def draw_item(self, surf):
        size = 96
        y = 212 if T.compact else 330
        # two targets, a divider, five search symbols: 112 px pitch, centred as one row
        cx = T.W // 2
        tx = [cx - 340, cx - 228]
        gx = [cx - 108 + i * 112 for i in range(5)]
        lbl_y = y - size // 2 - 26
        gfx.text(surf, "TARGETS", ((tx[0] + tx[1]) // 2, lbl_y), 14, self.accent, bold=True, anchor="center")
        gfx.text(surf, "SEARCH GROUP", ((gx[0] + gx[-1]) // 2, lbl_y), 14, T.MUTED, bold=True, anchor="center")
        for x, g in zip(tx, self.item["targets"]):
            r = pygame.Rect(0, 0, size, size)
            r.center = (x, y)
            gfx.panel(surf, r, gfx.lerp_color(T.PANEL, self.accent, 0.18), self.accent, radius=12)
            glyphs.draw(surf, g, r.center, size * 0.8, T.TEXT)
        pygame.draw.line(surf, T.BORDER, (cx - 168, y - 60), (cx - 168, y + 60), 2)
        for x, g in zip(gx, self.item["group"]):
            r = pygame.Rect(0, 0, size, size)
            r.center = (x, y)
            gfx.panel(surf, r, T.PANEL, T.BORDER, radius=12)
            glyphs.draw(surf, g, r.center, size * 0.8, T.TEXT)
        self.yes_btn.draw(surf)
        self.no_btn.draw(surf)
        if self.state == "run":
            gfx.text(surf, f"{self.correct + self.wrong} / {self.max_raw}", (T.W // 2, 450 if T.compact else 640), 16,
                     T.DIM, anchor="center")


class Coding(SpeedSubtest):
    code = "CD"
    name = "Coding"
    index = "PSI"
    measures = "Processing speed, visual-motor coordination and associative learning"
    max_raw = 135
    duration = 120
    practice_n = 3
    rules = [
        "A key pairs each digit 1–9 with a unique symbol.",
        "On the real test you draw the matching symbol under each digit.",
        "120-second limit. Work in order — skipping is not allowed.",
        "Score = number of correct responses (max 135).",
    ]
    controls = ["Here the lookup is reversed: each box shows a symbol. Find it in the key and type its digit "
                "(1–9), or tap it in the key. The key is new every session."]

    COLS = 15
    ROWS = 2

    def setup(self):
        self.key = glyphs.distinct_set(self.rng, 9, 3)
        self.run_mode = False
        self.practice_seq = self._sequence(self.practice_n)
        self.seq = self._sequence(self.max_raw)
        self.pos = -1
        self.responses = []

    def _sequence(self, n):
        out = []
        while len(out) < n:
            d = self.rng.randint(1, 9)
            if not out or d != out[-1]:
                out.append(d)
        return out

    def new_item(self, practice=False):
        if not practice and not self.run_mode:
            self.run_mode = True
            self.pos = 0
            self.responses = []
            return
        self.pos += 1

    @property
    def current(self):
        s = self.seq if self.run_mode else self.practice_seq
        return s[min(self.pos, len(s) - 1)]

    # compact: shorter boxes, so that both rows fit under the key
    @staticmethod
    def _key_y():
        return 116 if T.compact else 128

    def _key_rect(self, i):
        kw = 76
        kx0 = T.W // 2 - kw * 9 // 2
        return pygame.Rect(kx0 + i * kw, self._key_y() - 10, kw, 132)

    def handle_item(self, e):
        d = None
        if e.type == pygame.KEYDOWN and e.unicode and e.unicode in "123456789":
            d = int(e.unicode)
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            d = next((i + 1 for i in range(9) if self._key_rect(i).collidepoint(e.pos)), None)
        if d is not None:
            ok = d == self.current
            if self.run_mode:
                self.responses.append(d)
            self.answer(ok)

    def explain_wrong(self):
        return "find the symbol in the key above."

    def draw_item(self, surf):
        # key
        kw = 76
        kx0 = T.W // 2 - kw * 9 // 2
        ky = self._key_y()
        gfx.panel(surf, (kx0 - 14, ky - 10, kw * 9 + 28, 132), T.PANEL, T.BORDER, radius=14)
        gfx.text(surf, "KEY", (kx0 - 30, ky + 56), 13, self.accent, bold=True, anchor="midright")
        for i, g in enumerate(self.key):
            x = kx0 + i * kw + kw // 2
            gfx.text(surf, str(i + 1), (x, ky + 20), 24, self.accent, bold=True, mono=True, anchor="center")
            if i:
                pygame.draw.line(surf, T.TRACK, (kx0 + i * kw, ky + 4), (kx0 + i * kw, ky + 108), 1)
            glyphs.draw(surf, g, (x, ky + 74), 52, T.TEXT)

        seq = self.seq if self.run_mode else self.practice_seq
        per_page = self.COLS * self.ROWS
        page = max(0, self.pos) // per_page if self.run_mode else 0
        cw, ch = (70, 112) if T.compact else (70, 132)
        top, row_gap = (254, 14) if T.compact else (320, 22)
        sy = ch / 132   # vertical scale of the box contents
        x0 = T.W // 2 - cw * self.COLS // 2
        for k in range(per_page):
            idx = page * per_page + k
            if idx >= len(seq):
                break
            row, col = divmod(k, self.COLS)
            r = pygame.Rect(x0 + col * cw + 3, top + row * (ch + row_gap), cw - 6, ch)
            current = idx == self.pos
            border = self.accent if current else T.BORDER
            fill = gfx.lerp_color(T.PANEL, self.accent, 0.16) if current else T.PANEL
            if current:
                gfx.glow(surf, r.center, 70, self.accent, 0.25)
            gfx.panel(surf, r, fill, border, radius=10)
            glyphs.draw(surf, self.key[seq[idx] - 1], (r.centerx, r.y + 36 * sy), 44, T.TEXT if idx >= self.pos else T.DIM)
            pygame.draw.line(surf, T.TRACK, (r.x + 8, r.y + 70 * sy), (r.right - 8, r.y + 70 * sy), 1)
            if idx < self.pos:
                shown = self.responses[idx] if self.run_mode and idx < len(self.responses) else seq[idx]
                gfx.text(surf, str(shown), (r.centerx, r.y + 101 * sy), 28, self.accent, bold=True, mono=True,
                         anchor="center")
            elif current and int(self.t * 2) % 2 == 0:
                pygame.draw.rect(surf, self.accent, (r.centerx - 10, r.bottom - 18, 20, 3), border_radius=2)
