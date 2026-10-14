"""Procedurally generated abstract line symbols on a 3x3 point lattice."""
from .gfx import circle, thick_line

POINTS = [(x, y) for y in range(3) for x in range(3)]
EDGES = sorted({tuple(sorted((p, q))) for p in POINTS for q in POINTS
                if p != q and max(abs(p[0] - q[0]), abs(p[1] - q[1])) == 1})


def _norm(e):
    return tuple(sorted(e))


def normalize(g):
    """Translate so the symbol touches the lattice's top-left. Symbols are drawn centred, so two
    glyphs that differ only by position would look identical; normalising makes equality visual."""
    pts = [p for e in g for p in e]
    mx = min(x for x, _ in pts)
    my = min(y for _, y in pts)
    return frozenset(_norm(((a[0] - mx, a[1] - my), (b[0] - mx, b[1] - my))) for a, b in g)


def random_glyph(rng, n_edges=None):
    n_edges = n_edges or rng.choice([3, 4, 4])
    while True:
        p = rng.choice(POINTS)
        edges = set()
        tries = 0
        while len(edges) < n_edges and tries < 40:
            tries += 1
            nbrs = [q for q in POINTS if q != p and max(abs(p[0] - q[0]), abs(p[1] - q[1])) == 1]
            q = rng.choice(nbrs)
            e = _norm((p, q))
            if e in edges:
                continue
            edges.add(e)
            # occasionally branch from an existing point instead of continuing the stroke
            p = q if rng.random() < 0.75 else rng.choice([pt for ed in edges for pt in ed])
        if len(edges) == n_edges:
            return normalize(edges)


def transform(g, kind):
    f = {
        "mirror": lambda p: (2 - p[0], p[1]),
        "flip": lambda p: (p[0], 2 - p[1]),
        "rot": lambda p: (2 - p[1], p[0]),
    }[kind]
    return normalize([_norm((f(a), f(b))) for a, b in g])


def variant(rng, g):
    """A near-miss: one stroke moved, or the whole symbol mirrored/rotated."""
    for _ in range(30):
        if rng.random() < 0.35:
            h = transform(g, rng.choice(["mirror", "flip", "rot"]))
        else:
            edges = set(g)
            edges.remove(rng.choice(sorted(edges)))
            pts = {pt for e in edges for pt in e}
            cands = [e for e in EDGES if e not in g and (e[0] in pts or e[1] in pts)]
            edges.add(rng.choice(cands))
            h = normalize(edges)
        if h != g:
            return h
    return random_glyph(rng)


def distance(a, b):
    return len(a ^ b)


def distinct_set(rng, n, min_dist=3):
    out = []
    while len(out) < n:
        g = random_glyph(rng)
        if all(distance(g, h) >= min_dist and transform(g, "mirror") != h for h in out):
            out.append(g)
    return out


def draw(surf, g, center, size, color, width=None):
    k = size * 0.36
    pts = [p for e in g for p in e] or [(1, 1)]
    cx = center[0] - ((min(x for x, _ in pts) + max(x for x, _ in pts)) / 2 - 1) * k
    cy = center[1] - ((min(y for _, y in pts) + max(y for _, y in pts)) / 2 - 1) * k
    width = width or max(2, size * 0.075)
    for a, b in g:
        thick_line(surf, (cx + (a[0] - 1) * k, cy + (a[1] - 1) * k), (cx + (b[0] - 1) * k, cy + (b[1] - 1) * k),
                   width, color)
    if not g:
        circle(surf, center, width, color)
