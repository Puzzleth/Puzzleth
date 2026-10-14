"""Block Design: rebuild a red-and-white pattern from two-colour blocks."""
import pygame

from ..display import mouse_pos
from .. import gfx
from .. import theme as T
from .base import ItemSubtest

WHITE, RED, TL, TR, BR, BL = range(6)   # TL = red triangle in the top-left half, etc.
CYCLE = [TL, TR, BR, BL, WHITE, RED]
ROT = {TL: TR, TR: BR, BR: BL, BL: TL}
MIRROR_H = {TL: TR, TR: TL, BL: BR, BR: BL}
MIRROR_V = {TL: BL, BL: TL, TR: BR, BR: TR}
DIAG = (TL, TR, BR, BL)

C_WHITE = (238, 233, 222)
C_RED = (222, 64, 82)


def rot(f, k=1):
    for _ in range(k):
        f = ROT.get(f, f)
    return f


def draw_face(surf, rect, face, gap_radius=0):
    rect = pygame.Rect(rect)
    pygame.draw.rect(surf, C_RED if face == RED else C_WHITE, rect, border_radius=gap_radius)
    if face in DIAG:
        x0, y0, x1, y1 = rect.left, rect.top, rect.right - 1, rect.bottom - 1
        tri = {TL: [(x0, y0), (x1, y0), (x0, y1)], TR: [(x0, y0), (x1, y0), (x1, y1)],
               BR: [(x1, y0), (x1, y1), (x0, y1)], BL: [(x0, y0), (x1, y1), (x0, y1)]}[face]
        gfx.poly(surf, tri, C_RED)


class BlockDesign(ItemSubtest):
    code = "BD"
    name = "Block Design"
    index = "PRI"
    measures = "Visual-spatial analysis and construction"
    n_items = 14
    start_item = 5
    discontinue_n = 2
    max_raw = 70
    rules = [
        "Recreate the model design using blocks with red, white and half-red/half-white faces.",
        "Items 1–8 use 4 blocks (2×2); items 9–14 use 9 blocks (3×3).",
        "Time limits: 30 s (items 1–4), 60 s (5–8), 120 s (9–14).",
        "Items 1–2: 2 pts. Items 3–8: 4 pts. Items 9–14: 4 pts plus up to 3 speed-bonus points.",
        "Later models have no guide lines — you must work out where each block's edges are.",
        "Adults start at item 5; reversal rule applies. Discontinue after 2 consecutive scores of 0.",
    ]
    controls = ["Left-click a block to cycle its face forward, right-click to cycle back",
                "(the scroll wheel also works). The design is checked automatically.  Space gives up."]

    def item_max(self, n):
        return 2 if n <= 2 else 4 if n <= 8 else 7

    def time_limit(self, n):
        if n == 0:
            return None
        return 30 if n <= 4 else 60 if n <= 8 else 120

    def footer_rule(self):
        return "Stops after 2 consecutive scores of 0"

    # --- generation
    def _gen(self, n):
        for _ in range(200):
            g = self._gen2(n) if n <= 8 else self._gen3(n)
            flat = [f for row in g for f in row]
            has_diag = any(f in DIAG for f in flat)
            if len(set(flat)) >= 2 and (n <= 2 or has_diag):
                return g
        return [[TL, TR], [BL, BR]]

    def _gen2(self, n):
        r = self.rng
        if n <= 2:
            # solid halves / quarters
            a, b = r.sample([WHITE, RED], 2)
            pat = r.choice([[[a, a], [b, b]], [[a, b], [a, b]], [[a, b], [b, a]], [[a, a], [a, b]]])
            return pat
        if n <= 4:
            d = r.choice(DIAG)
            s = r.choice([WHITE, RED])
            g = [[s, s], [s, s]]
            cells = r.sample([(0, 0), (0, 1), (1, 0), (1, 1)], 2)
            for (y, x) in cells:
                g[y][x] = d if r.random() < 0.5 else rot(d, 2)
            return g
        f = r.choice(DIAG)
        kind = r.choice(["mirror", "rot", "free"] if n >= 7 else ["mirror", "rot"])
        if kind == "mirror":
            return [[f, MIRROR_H[f]], [MIRROR_V[f], MIRROR_V[MIRROR_H[f]]]]
        if kind == "rot":
            return [[f, rot(f)], [rot(f, 3), rot(f, 2)]]
        return [[r.choice(DIAG) for _ in range(2)] for _ in range(2)]

    def _gen3(self, n):
        r = self.rng
        g = [[WHITE] * 3 for _ in range(3)]
        kind = r.choice(["mirror", "rot"] if n <= 11 else ["rot", "free", "mirror"])
        if kind == "mirror":
            c = r.choice(DIAG + (WHITE, RED))
            e = r.choice([WHITE, RED])        # middle column/row must be symmetric -> solid
            m = r.choice([WHITE, RED])
            g[0][0] = c
            g[0][2] = MIRROR_H.get(c, c)
            g[2][0] = MIRROR_V.get(c, c)
            g[2][2] = MIRROR_V.get(MIRROR_H.get(c, c), MIRROR_H.get(c, c))
            side = r.choice(DIAG)
            g[0][1] = g[2][1] = e
            g[1][0] = side
            g[1][2] = MIRROR_H[side]
            g[1][1] = m
            if r.random() < 0.5:   # transpose for variety
                g = [list(row) for row in zip(*g)]
                g = [[{TR: BL, BL: TR}.get(f, f) for f in row] for row in g]
            return g
        if kind == "rot":
            c, e = r.choice(DIAG), r.choice(DIAG + (WHITE, RED))
            corners = [(0, 0), (0, 2), (2, 2), (2, 0)]
            edges = [(0, 1), (1, 2), (2, 1), (1, 0)]
            for k in range(4):
                g[corners[k][0]][corners[k][1]] = rot(c, k)
                g[edges[k][0]][edges[k][1]] = rot(e, k)
            g[1][1] = r.choice([WHITE, RED])
            return g
        return [[r.choice(DIAG + (WHITE, RED, TL, BR)) for _ in range(3)] for _ in range(3)]

    def make_item(self, n):
        design = self._gen(n)
        size = len(design)
        work = [[WHITE] * size for _ in range(size)]
        if work == design:
            work[0][0] = RED
        return {"design": design, "work": work, "size": size, "guides": n <= 4, "solved_at": None}

    def on_item_start(self):
        self.hover_cell = None

    # --- interaction
    def _cell_rect(self, y, x):
        size = self.item["size"]
        bs = 112 if size == 2 else 92
        gap = 8
        total = size * bs + (size - 1) * gap
        ox, oy = 880 - total // 2, 410 - total // 2
        return pygame.Rect(ox + x * (bs + gap), oy + y * (bs + gap), bs, bs)

    def _cell_at(self, pos):
        s = self.item["size"]
        for y in range(s):
            for x in range(s):
                if self._cell_rect(y, x).collidepoint(pos):
                    return y, x
        return None

    def _check(self):
        it = self.item
        if it["work"] == it["design"]:
            t = self.item_t
            pts = self.item_max(self.cur)
            if self.cur >= 9:
                lim = self.time_limit(self.cur)
                bonus = 3 if t <= lim * 0.3 else 2 if t <= lim * 0.45 else 1 if t <= lim * 0.6 else 0
                pts = 4 + bonus
                expl = f"Completed in {t:.1f} s — speed bonus +{bonus}"
            else:
                expl = f"Completed in {t:.1f} s"
            self.submit(pts, expl)

    def handle_item(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            self.submit(0, "Item abandoned.")
            return
        step = 0
        pos = None
        if e.type == pygame.MOUSEBUTTONDOWN and e.button in (1, 3):
            step = 1 if e.button == 1 else -1
            pos = e.pos
        elif e.type == pygame.MOUSEWHEEL:
            step = -1 if e.y > 0 else 1
            pos = mouse_pos()
        if step and pos:
            c = self._cell_at(pos)
            if c:
                y, x = c
                w = self.item["work"]
                w[y][x] = CYCLE[(CYCLE.index(w[y][x]) + step) % len(CYCLE)]
                self._check()

    def on_timeout(self):
        self.submit(0, "Time limit reached.")

    def update_item(self, dt):
        self.hover_cell = self._cell_at(mouse_pos())

    # --- drawing
    def draw_item(self, surf):
        it = self.item
        size = it["size"]
        # model
        gfx.text(surf, "MODEL", (380, 160), 14, self.accent, bold=True, anchor="center")
        gfx.text(surf, "YOUR BLOCKS", (880, 160), 14, T.MUTED, bold=True, anchor="center")
        ms = 240 if size == 2 else 252
        mrect = pygame.Rect(0, 0, ms, ms)
        mrect.center = (380, 410)
        frame = mrect.inflate(36, 36)
        gfx.glow(surf, frame.center, 260, self.accent, 0.12)
        gfx.panel(surf, frame, T.PANEL, T.BORDER, radius=16)
        cs = ms // size
        for y in range(size):
            for x in range(size):
                draw_face(surf, (mrect.x + x * cs, mrect.y + y * cs, cs, cs), it["design"][y][x], gap_radius=0)
        if it["guides"]:
            for k in range(1, size):
                pygame.draw.line(surf, (150, 140, 135), (mrect.x + k * cs, mrect.y), (mrect.x + k * cs, mrect.bottom - 1), 1)
                pygame.draw.line(surf, (150, 140, 135), (mrect.x, mrect.y + k * cs), (mrect.right - 1, mrect.y + k * cs), 1)
        # workspace
        for y in range(size):
            for x in range(size):
                r = self._cell_rect(y, x)
                hov = self.hover_cell == (y, x) and self.state == "item"
                if hov:
                    gfx.glow(surf, r.center, r.w * 0.85, self.accent, 0.25)
                shadow = r.move(0, 5)
                pygame.draw.rect(surf, (6, 8, 18), shadow, border_radius=8)
                draw_face(surf, r, it["work"][y][x], gap_radius=0)
                pygame.draw.rect(surf, self.accent if hov else (60, 66, 92), r, 2 if hov else 1)
        if self.revealing and self.fb["points"] == 0:
            gfx.text(surf, "The model is on the left — compare edge by edge.", (880, 640), 16, T.MUTED, anchor="center")
