"""Matrix Reasoning: procedurally generated 2x2 analogies and 3x3 matrices."""
import pygame

from ..display import mouse_pos
from .. import gfx, i18n, shapes
from .. import theme as T
from .base import ItemSubtest

COLORS = [(96, 170, 255), (255, 110, 130), (255, 196, 90), (90, 220, 160), (196, 140, 255)]
POOLS = {
    "shape": shapes.SHAPES,
    "color": list(range(len(COLORS))),
    "count": [1, 2, 3, 4],
    "size": [0, 1, 2],
    "fill": ["solid", "hollow", "dot"],
    "rot": [0, 90, 180, 270],
}
ORDERED = {"count", "size", "rot"}
SIZE_K = [0.58, 0.79, 1.0]
LAYOUT = {1: [(0, 0)], 2: [(-0.46, 0), (0.46, 0)], 3: [(0, -0.44), (-0.46, 0.4), (0.46, 0.4)],
          4: [(-0.43, -0.43), (0.43, -0.43), (-0.43, 0.43), (0.43, 0.43)]}
KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3, pygame.K_5: 4,
        pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3, pygame.K_KP5: 4}
CELL_BG = (24, 31, 58)


def draw_cell(surf, cell, rect, bg=CELL_BG):
    count = cell["count"]
    base = rect.w * (0.34 if count == 1 else 0.19)
    r = base * SIZE_K[cell["size"]]
    spread = rect.w * 0.5 * (0.62 if count > 1 else 0)
    for ox, oy in LAYOUT[count]:
        c = (rect.centerx + ox * spread, rect.centery + oy * spread)
        shapes.draw(surf, cell["shape"], c, r, COLORS[cell["color"]], cell["fill"], cell["rot"], bg)


def _visible_key(cell):
    """Two cells that render identically compare equal (rotation only matters for rotatable shapes)."""
    rot = cell["rot"] if cell["shape"] in shapes.ROTATABLE else 0
    return cell["shape"], cell["color"], cell["count"], cell["size"], cell["fill"], rot


class MatrixReasoning(ItemSubtest):
    code = "MR"
    name = "Matrix Reasoning"
    index = "PRI"
    measures = "Fluid reasoning and abstract pattern detection"
    n_items = 26
    start_item = 4
    discontinue_n = 3
    max_raw = 26
    challenge = True
    max_level = 32
    rules = [
        "Look at an incomplete matrix or analogy and pick the option that completes it.",
        "Rules can act along rows, columns, or both: shape, colour, number, size, fill, rotation.",
        "There are five response options; exactly one is correct. 1 point each.",
        "No strict limit, but examiners prompt after about 30 seconds.",
        "Adults start at item 4; reversal rule applies.",
        "Discontinue after 3 consecutive scores of 0.",
    ]
    controls = ["Click an option or press 1–5."]

    def setup(self):
        self.choice = None

    # ---------------------------------------------------------- generation
    def _difficulty(self, n):
        if n <= 2:
            return 2, 1, ["col"]
        if n <= 5:
            return 2, 2, ["col"]
        if n <= 10:
            return 3, 1, ["col", "row", "latin"]
        if n <= 16:
            return 3, 2, ["col", "row", "latin"]
        if n <= 22:
            return 3, 3, ["latin", "latin", "col", "row"]
        if n <= 29:   # 27+ only exist in challenge modes
            return 3, 4, ["latin"]
        return 3, 5, ["latin"]

    def make_item(self, n):
        r = self.rng
        size, n_vary, rule_pool = self._difficulty(n)
        attrs = ["shape", "color", "count", "size", "fill", "rot"]
        vary = r.sample(attrs, n_vary)
        const = {}
        if "rot" in vary and "shape" in vary:
            # rotation is only meaningful for one fixed asymmetric shape
            vary[vary.index("shape")] = r.choice([a for a in attrs if a not in vary and a != "shape"])
        if "rot" in vary or ("shape" not in vary and r.random() < 0.3):
            const["shape"] = r.choice(shapes.ROTATABLE)
        for a in attrs:
            if a not in vary and a not in const:
                const[a] = r.choice(POOLS[a]) if a != "rot" else 0
        if size == 2:
            grid = self._gen2(vary, const)
        else:
            grid = self._gen3(vary, const, rule_pool)
        answer = grid[size - 1][size - 1]
        options = self._distractors(answer, vary, grid)
        options.append(answer)
        r.shuffle(options)
        return {"grid": grid, "size": size, "options": options, "answer": options.index(answer)}

    def _values(self, a, k):
        pool = POOLS[a]
        if a in ORDERED:
            start = self.rng.randrange(len(pool) - k + 1)
            vals = pool[start:start + k]
            return vals if self.rng.random() < 0.6 else vals[::-1]
        return self.rng.sample(pool, k)

    def _gen2(self, vary, const):
        vals = {a: self._values(a, 2) for a in vary}
        # first varying attribute changes across columns, second down rows
        axis = {a: ("col" if i % 2 == 0 else "row") for i, a in enumerate(vary)}
        grid = []
        for y in range(2):
            row = []
            for x in range(2):
                cell = dict(const)
                for a in vary:
                    cell[a] = vals[a][x if axis[a] == "col" else y]
                row.append(cell)
            grid.append(row)
        return grid

    def _gen3(self, vary, const, rule_pool):
        r = self.rng
        vals = {a: self._values(a, 3) for a in vary}
        rules = {}
        for a in vary:
            rule = r.choice(rule_pool)
            rules[a] = (rule, r.choice([1, 2]))
        grid = []
        for y in range(3):
            row = []
            for x in range(3):
                cell = dict(const)
                for a in vary:
                    rule, shift = rules[a]
                    i = x if rule == "col" else y if rule == "row" else (x + shift * y) % 3
                    cell[a] = vals[a][i]
                row.append(cell)
            grid.append(row)
        return grid

    def _distractors(self, answer, vary, grid):
        r = self.rng
        seen_vals = {a: sorted({c[a] for row in grid for c in row}, key=str) for a in answer}
        mutable = [a for a in answer if a != "rot" or answer["shape"] in shapes.ROTATABLE]

        def mutate(cell, a):
            pool = [v for v in seen_vals[a] if v != cell[a]] if a in vary else []
            if not pool or r.random() < 0.25:
                pool = [v for v in POOLS[a] if v != cell[a]]
            c = dict(cell)
            c[a] = r.choice(pool)
            return c

        out, keys = [], {_visible_key(answer)}

        def add(c):
            k = _visible_key(c)
            if k not in keys:
                keys.add(k)
                out.append(c)

        prefer = [a for a in vary if a in mutable] or mutable
        # one-attribute changes on the rule attributes, then two-attribute changes so that the
        # answer is not simply the "average" of the options
        for a in r.sample(prefer, len(prefer)):
            add(mutate(answer, a))
            if len(out) >= 2:
                break
        tries = 0
        while len(out) < 4 and tries < 200:
            tries += 1
            if out and r.random() < 0.6:
                base = r.choice(out)
                add(mutate(base, r.choice(mutable)))
            else:
                add(mutate(mutate(answer, r.choice(mutable)), r.choice(mutable)))
        return out[:4]

    # ---------------------------------------------------------- interaction
    def _opt_rect(self, i):
        if T.compact:   # right of the matrix, three over two
            s, gap = 124, 22
            row, col = divmod(i, 3)
            n = 3 if row == 0 else 2
            x0 = 910 - (n * s + (n - 1) * gap) // 2
            return pygame.Rect(x0 + col * (s + gap), 285 - s - gap // 2 + row * (s + gap), s, s)
        s = 108
        gap = 24
        x0 = T.W // 2 - (5 * s + 4 * gap) // 2
        return pygame.Rect(x0 + i * (s + gap), 560, s, s)

    def _cell_rect(self, y, x):
        size = self.item["size"]
        s = (128 if size == 2 else 116) if T.compact else (120 if size == 2 else 108)
        gap = 10
        total = size * s + (size - 1) * gap
        cx, cy = (350, 285) if T.compact else (T.W // 2, 318)
        return pygame.Rect(cx - total // 2 + x * (s + gap), cy - total // 2 + y * (s + gap), s, s)

    def choose(self, i):
        self.choice = i
        ok = i == self.item["answer"]
        self.submit(1 if ok else 0, "" if ok else i18n.f("The answer was option {option}.", option=self.item["answer"] + 1))

    def on_item_start(self):
        self.choice = None

    def handle_item(self, e):
        if e.type == pygame.KEYDOWN and e.key in KEYS:
            self.choose(KEYS[e.key])
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i in range(5):
                if self._opt_rect(i).collidepoint(e.pos):
                    self.choose(i)

    def draw_item(self, surf):
        it = self.item
        size = it["size"]
        frame = self._cell_rect(0, 0).union(self._cell_rect(size - 1, size - 1)).inflate(30, 30)
        gfx.glow(surf, frame.center, frame.w * 0.8, self.accent, 0.1)
        gfx.panel(surf, frame, T.PANEL, T.BORDER, radius=18)
        for y in range(size):
            for x in range(size):
                rect = self._cell_rect(y, x)
                last = (y, x) == (size - 1, size - 1)
                if last and not self.revealing:
                    gfx.panel(surf, rect, gfx.lerp_color(CELL_BG, self.accent, 0.08), self.accent, radius=10)
                    pulse = 0.5 + 0.5 * abs(((self.t * 0.7) % 2) - 1)
                    gfx.text(surf, "?", rect.center, 54, gfx.lerp_color(T.DIM, self.accent, pulse), bold=True,
                             anchor="center")
                    continue
                gfx.panel(surf, rect, CELL_BG, T.GOOD if last else T.BORDER, radius=10)
                draw_cell(surf, it["grid"][y][x], rect)
        mouse = mouse_pos()
        for i, cell in enumerate(it["options"]):
            rect = self._opt_rect(i)
            border = T.BORDER
            if self.state == "item" and rect.collidepoint(mouse):
                border = self.accent
                gfx.glow(surf, rect.center, 90, self.accent, 0.2)
            if self.state == "feedback":
                if self.revealing and i == it["answer"]:
                    border = T.GOOD
                elif i == self.choice:
                    border = T.BAD if self.revealing else self.accent
            gfx.panel(surf, rect, CELL_BG, border, radius=12, border_w=2 if border != T.BORDER else 1)
            draw_cell(surf, cell, rect)
            gfx.text(surf, str(i + 1), (rect.x + 12, rect.y + 8), 14, T.MUTED, bold=True)
