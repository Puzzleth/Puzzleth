"""Visual Puzzles: pick the three pieces that make the puzzle."""
from itertools import combinations

import pygame

from ..display import mouse_pos
from .. import gfx, i18n, sound
from .. import theme as T
from ..widgets import Button
from .base import ItemSubtest

KEYS = {getattr(pygame, f"K_{i}"): i - 1 for i in range(1, 7)}
PIECE = (64, 214, 168)
PIECE_EDGE = (22, 110, 86)
SOLUTION_SHADES = [(64, 214, 168), (96, 170, 255), (255, 196, 90)]


# ---------------------------------------------------------------- polyomino helpers

def normalize(cells):
    mx = min(x for x, _ in cells)
    my = min(y for _, y in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def rotate(cells):
    return normalize({(-y, x) for x, y in cells})


def rotations(cells):
    out = []
    c = normalize(cells)
    for _ in range(4):
        if c not in out:
            out.append(c)
        c = rotate(c)
    return out


def canonical(cells):
    return min(tuple(sorted(r)) for r in rotations(cells))


def neighbors(c):
    x, y = c
    return [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]


def connected(cells):
    cells = set(cells)
    if not cells:
        return False
    seen, stack = set(), [next(iter(cells))]
    while stack:
        c = stack.pop()
        if c in seen:
            continue
        seen.add(c)
        stack.extend(n for n in neighbors(c) if n in cells and n not in seen)
    return len(seen) == len(cells)


def _key(c):
    return c[1], c[0]


def tiles(target, pieces):
    """Can the pieces (rotation allowed, no flipping) exactly cover the target?"""
    target = frozenset(target)
    if sum(len(p) for p in pieces) != len(target):
        return False
    rots = [rotations(p) for p in pieces]

    def rec(remaining, used):
        if not remaining:
            return True
        anchor = min(remaining, key=_key)
        for i in range(len(pieces)):
            if i in used:
                continue
            for rot in rots[i]:
                ra = min(rot, key=_key)   # the piece cell that must land on the anchor
                dx, dy = anchor[0] - ra[0], anchor[1] - ra[1]
                placed = {(x + dx, y + dy) for x, y in rot}
                if placed <= remaining and rec(remaining - placed, used | {i}):
                    return True
        return False

    return rec(target, frozenset())


def extent(cells):
    return max(x for x, _ in cells) + 1, max(y for _, y in cells) + 1


# ---------------------------------------------------------------- generation

def grow_shape(rng, size, w, h):
    cells = {(rng.randrange(w), rng.randrange(h))}
    while len(cells) < size:
        c = rng.choice(sorted(cells))
        n = rng.choice(neighbors(c))
        if 0 <= n[0] < w and 0 <= n[1] < h:
            cells.add(n)
    return normalize(cells)


def partition(rng, target, k=3):
    cells = sorted(target)
    seeds = rng.sample(cells, k)
    owner = {s: i for i, s in enumerate(seeds)}
    sizes = [1] * k
    while len(owner) < len(target):
        order = sorted(range(k), key=lambda i: sizes[i] + rng.random() * 2)
        for i in order:
            frontier = [n for c, o in owner.items() if o == i for n in neighbors(c) if n in target and n not in owner]
            if frontier:
                owner[rng.choice(frontier)] = i
                sizes[i] += 1
                break
        else:
            return None
    pieces = [frozenset(c for c, o in owner.items() if o == i) for i in range(k)]
    return pieces


def mutate_piece(rng, piece):
    cells = set(piece)
    for _ in range(30):
        c = set(cells)
        leaf = rng.choice(sorted(c))
        c.discard(leaf)
        if not connected(c):
            continue
        cand = sorted({n for x in c for n in neighbors(x)} - c - {leaf})
        c.add(rng.choice(cand))
        if connected(c) and canonical(c) != canonical(piece):
            return normalize(c)
    return None


class VisualPuzzles(ItemSubtest):
    code = "VP"
    name = "Visual Puzzles"
    index = "PRI"
    measures = "Spatial reasoning and mental rotation"
    n_items = 26
    start_item = 5
    discontinue_n = 3
    max_raw = 26
    challenge = True
    max_level = 32
    rules = [
        "Choose the three pieces that, put together, make the puzzle.",
        "Pieces may need to be rotated (turned), but never flipped over.",
        "Exactly three pieces; all three must be correct to earn the 1 point.",
        "30-second time limit per item.",
        "Adults start at item 5; reversal rule applies.",
        "Discontinue after 3 consecutive scores of 0.",
    ]
    controls = ["Click pieces (or press 1–6) to select three, then press Enter."]

    def time_limit(self, n):
        return None if n == 0 else 30

    def setup(self):
        # compact: the puzzle and the Confirm button on the left, the pieces on the right
        self.confirm_btn = Button((self._puzzle_x() - 120, 436 if T.compact else 648, 240, 48), "Confirm", self._confirm, self.accent,
                                  hotkeys=(pygame.K_RETURN, pygame.K_KP_ENTER), primary=True, size=17,
                                  sound=None)

    def make_item(self, n):
        r = self.rng
        for _ in range(500):
            if n <= 8:
                w, h = r.choice([(2, 3), (3, 2), (3, 3), (2, 4), (4, 2), (3, 4), (4, 3)])
                target = frozenset((x, y) for x in range(w) for y in range(h))
            elif n <= 17:
                target = grow_shape(r, r.randint(9, 12), 4, 4)
            elif n <= 26:
                target = grow_shape(r, r.randint(12, 15), 5, 4)
            else:   # challenge levels: larger, more irregular puzzles
                target = grow_shape(r, r.randint(15, 18), 5, 5)
            parts = partition(r, target)
            if not parts or min(len(p) for p in parts) < 2:
                continue
            true = [normalize(p) for p in parts]
            distract = []
            canon = {canonical(p) for p in true}
            tries = 0
            while len(distract) < 3 and tries < 60:
                tries += 1
                if n > 17 or r.random() < 0.4:
                    d = mutate_piece(r, r.choice(true))
                else:
                    d = grow_shape(r, r.randint(2, max(len(p) for p in true) + 1), 4, 4)
                if d and canonical(d) not in canon:
                    canon.add(canonical(d))
                    distract.append(d)
            if len(distract) < 3:
                continue
            options = [(p, True) for p in true] + [(d, False) for d in distract]
            r.shuffle(options)
            pieces = [p for p, _ in options]
            solutions = [c for c in combinations(range(6), 3) if tiles(target, [pieces[i] for i in c])]
            if len(solutions) != 1:
                continue
            if n >= 5:
                pieces = [r.choice(rotations(p)) for p in pieces]
            correct = set(solutions[0])
            return {"target": target, "parts": parts, "pieces": pieces, "correct": correct, "selected": []}
        raise RuntimeError("could not generate a visual puzzle")

    def on_item_start(self):
        it = self.item
        ext = max(max(extent(p)) for p in it["pieces"])
        tw, th = extent(it["target"])
        self.u = int(min(40, 132 / ext, 230 / max(tw, th)))

    # ---------------------------------------------------------- interaction
    @staticmethod
    def _puzzle_x():
        return 330 if T.compact else T.W // 2

    def _opt_rect(self, i):
        w, gap = 164, 16
        if T.compact:
            row, col = divmod(i, 3)
            return pygame.Rect(900 - (3 * w + 2 * gap) // 2 + col * (w + gap), 113 + row * (w + gap), w, w)
        x0 = T.W // 2 - (6 * w + 5 * gap) // 2
        return pygame.Rect(x0 + i * (w + gap), 470, w, 164)

    def _toggle(self, i):
        sel = self.item["selected"]
        if i in sel:
            sel.remove(i)
        elif len(sel) < 3:
            sel.append(i)
        else:
            return
        sound.play("select")

    def _confirm(self):
        sel = set(self.item["selected"])
        if len(sel) != 3:
            return
        ok = sel == self.item["correct"]
        want = ", ".join(str(i + 1) for i in sorted(self.item["correct"]))
        self.submit(1 if ok else 0, "" if ok else i18n.f("Correct pieces: {pieces}", pieces=want))

    def handle_item(self, e):
        if self.confirm_btn.enabled and self.confirm_btn.handle(e):
            return
        if e.type == pygame.KEYDOWN:
            if e.key in KEYS:
                self._toggle(KEYS[e.key])
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(6):
                if self._opt_rect(i).collidepoint(e.pos):
                    self._toggle(i)

    def update_item(self, dt):
        self.confirm_btn.enabled = len(self.item["selected"]) == 3
        self.confirm_btn.label = "Confirm" if self.touch else "Confirm  (Enter)"
        self.confirm_btn.update(dt)

    def on_timeout(self):
        want = ", ".join(str(i + 1) for i in sorted(self.item["correct"]))
        self.submit(0, i18n.f("Time limit reached. Correct pieces: {pieces}", pieces=want))

    # ---------------------------------------------------------- drawing
    def _draw_cells(self, surf, cells, origin, u, color, edge, owner=None, shades=None):
        ox, oy = origin
        cells = set(cells)
        for (x, y) in cells:
            c = shades[owner[(x, y)]] if owner else color
            pygame.draw.rect(surf, c, (ox + x * u, oy + y * u, u + 1, u + 1))
        # outline only where a cell has no neighbour (or a different owner) on that side
        for (x, y) in cells:
            px, py = ox + x * u, oy + y * u
            for (nx, ny), seg in (((x, y - 1), ((px, py), (px + u, py))), ((x, y + 1), ((px, py + u), (px + u, py + u))),
                                  ((x - 1, y), ((px, py), (px, py + u))), ((x + 1, y), ((px + u, py), (px + u, py + u)))):
                if (nx, ny) not in cells or (owner and owner[(nx, ny)] != owner[(x, y)]):
                    pygame.draw.line(surf, edge, seg[0], seg[1], 2)

    def draw_item(self, surf):
        it = self.item
        u = self.u
        tw, th = extent(it["target"])
        frame = pygame.Rect(0, 0, max(300, tw * u + 80), max(240, th * u + 70))
        frame.center = (self._puzzle_x(), 250 if T.compact else 270)
        gfx.glow(surf, frame.center, frame.w * 0.8, self.accent, 0.12)
        gfx.panel(surf, frame, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "PUZZLE", (frame.centerx, frame.y - 16), 14, self.accent, bold=True, anchor="center")
        origin = (frame.centerx - tw * u / 2, frame.centery - th * u / 2)
        if self.revealing:
            owner = {c: i for i, p in enumerate(it["parts"]) for c in p}
            self._draw_cells(surf, it["target"], origin, u, PIECE, T.BG, owner, SOLUTION_SHADES)
        else:
            self._draw_cells(surf, it["target"], origin, u, PIECE, PIECE_EDGE)

        mouse = mouse_pos()
        for i, p in enumerate(it["pieces"]):
            rect = self._opt_rect(i)
            sel = i in it["selected"]
            border = self.accent if sel else T.BORDER
            fill = gfx.lerp_color(T.PANEL, self.accent, 0.18) if sel else T.PANEL
            if self.revealing:
                if i in it["correct"]:
                    border = T.GOOD
                elif sel:
                    border = T.BAD
            elif self.state == "item" and rect.collidepoint(mouse) and not sel:
                border = gfx.lerp_color(T.BORDER, self.accent, 0.6)
            if sel:
                gfx.glow(surf, rect.center, 110, self.accent, 0.2)
            gfx.panel(surf, rect, fill, border, radius=14, border_w=2 if border != T.BORDER else 1)
            pw, ph = extent(p)
            self._draw_cells(surf, p, (rect.centerx - pw * u / 2, rect.centery - ph * u / 2), u, PIECE, PIECE_EDGE)
            gfx.text(surf, str(i + 1), (rect.x + 12, rect.y + 8), 14, T.MUTED, bold=True)
        n = len(it["selected"])
        if self.state == "item":
            if n == 3:
                self.confirm_btn.draw(surf)
            else:
                gfx.text(surf, i18n.n(3 - n, "Select {n} more piece", "Select {n} more pieces"),
                         self.confirm_btn.rect.center, 17, T.MUTED, anchor="center")
