"""Vector shapes used by Matrix Reasoning."""
import math

from . import gfx

SHAPES = ["circle", "square", "triangle", "pentagon", "hexagon", "star", "cross", "arrow"]
ROTATABLE = ["triangle", "arrow"]


def _regular(n, start=-math.pi / 2):
    return [(math.cos(start + i * math.tau / n), math.sin(start + i * math.tau / n)) for i in range(n)]


def _unit(shape):
    if shape == "square":
        return [(-0.8, -0.8), (0.8, -0.8), (0.8, 0.8), (-0.8, 0.8)]
    if shape == "triangle":
        return [(x, y + 0.15) for x, y in _regular(3)]
    if shape == "pentagon":
        return _regular(5)
    if shape == "hexagon":
        return _regular(6, 0)
    if shape == "star":
        pts = []
        for i in range(10):
            r = 1.0 if i % 2 == 0 else 0.45
            a = -math.pi / 2 + i * math.pi / 5
            pts.append((r * math.cos(a), r * math.sin(a) + 0.05))
        return pts
    if shape == "cross":
        a, b = 0.3, 0.9
        return [(-a, -b), (a, -b), (a, -a), (b, -a), (b, a), (a, a), (a, b), (-a, b), (-a, a), (-b, a), (-b, -a),
                (-a, -a)]
    if shape == "arrow":
        return [(0, -1), (0.75, -0.15), (0.3, -0.15), (0.3, 0.95), (-0.3, 0.95), (-0.3, -0.15), (-0.75, -0.15)]
    raise ValueError(shape)


def _pts(shape, center, r, rot_deg, k=1.0):
    """Unit shape scaled by r, rotated, and optionally shrunk by k about its own vertex centroid."""
    a = math.radians(rot_deg)
    ca, sa = math.cos(a), math.sin(a)
    cx, cy = center
    unit = _unit(shape)
    mx = sum(x for x, _ in unit) / len(unit)
    my = sum(y for _, y in unit) / len(unit)
    unit = [(mx + (x - mx) * k, my + (y - my) * k) for x, y in unit]
    return [(cx + r * (x * ca - y * sa), cy + r * (x * sa + y * ca)) for x, y in unit]


def draw(surf, shape, center, r, color, fill="solid", rot=0, bg=(0, 0, 0)):
    """fill: 'solid', 'hollow' (outline) or 'dot' (outline with a centre dot)."""
    stroke = max(2.5, r * 0.2)
    if shape == "circle":
        gfx.circle(surf, center, r, color)
        if fill != "solid":
            gfx.circle(surf, center, r - stroke, bg)
    else:
        gfx.poly(surf, _pts(shape, center, r, rot), color)
        if fill != "solid":
            k = max(0.15, 1 - stroke * 1.6 / r) if shape in ("star", "cross", "arrow") else max(0.15, 1 - stroke / r)
            gfx.poly(surf, _pts(shape, center, r, rot, k), bg)
    if fill == "dot":
        gfx.circle(surf, center, max(2, r * 0.22), color)
