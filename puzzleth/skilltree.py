"""The skill-point constellation: FSIQ at the centre, four index nodes, ten subtest nodes.

Each subtest node is a ring of 19 skill points, one per scaled-score point (WAIS scaled
scores run 1-19, mean 10). Index and FSIQ nodes are progress rings over their score range.
"""
import math

from . import gfx, scoring
from . import theme as T
from .subtests import BY_CODE

SUB_R = 30
SUB_RING = 41
IDX_R = 44
IDX_RING = 56
FS_R = 66
FS_RING = 82


class SkillTree:
    # offsets from the FSIQ node, left half; the right half is mirrored
    _LEFT = {
        "VCI": (-250, -145), "IN": (-365, -270), "VC": (-415, -145), "SI": (-365, -20),
        "WMI": (-250, 145), "AR": (-405, 130), "DS": (-350, 255),
    }
    _MIRROR = {"VCI": "PRI", "IN": "BD", "VC": "MR", "SI": "VP", "WMI": "PSI", "AR": "SS", "DS": "CD"}

    def __init__(self, center=(T.W // 2, 460), sx=1.0, sy=1.0):
        cx, cy = center
        self.center = center
        pos = {}
        for k, (ox, oy) in self._LEFT.items():
            pos[k] = (cx + ox * sx, cy + oy * sy)
            pos[self._MIRROR[k]] = (cx - ox * sx, cy + oy * sy)
        self.index_pos = {k: pos[k] for k in scoring.INDEX_SUBTESTS}
        self.sub_pos = {k: v for k, v in pos.items() if k not in scoring.INDEX_SUBTESTS}
        self.order = [cls.code for cls in BY_CODE.values()]

    # -------------------------------------------------------------- hit testing
    def hit(self, pos):
        x, y = pos
        for code, (px, py) in self.sub_pos.items():
            if math.hypot(x - px, y - py) <= SUB_RING + 6:
                return code
        for idx, (px, py) in self.index_pos.items():
            if math.hypot(x - px, y - py) <= IDX_RING + 6:
                return idx
        if math.hypot(x - self.center[0], y - self.center[1]) <= FS_RING + 6:
            return "FSIQ"
        return None

    # -------------------------------------------------------------- animation schedule
    def _sub_fill(self, code, scaled, anim):
        if anim is None:
            return scaled
        i = self.order.index(code)
        start = 0.3 + i * 0.16
        return int(gfx.clamp((anim - start) * 16, 0, scaled))

    def _idx_frac(self, idx, anim):
        if anim is None:
            return 1.0
        j = ["VCI", "PRI", "WMI", "PSI"].index(idx)
        return gfx.ease_out((anim - 2.9 - j * 0.22) / 0.9)

    def _fs_frac(self, anim):
        return 1.0 if anim is None else gfx.ease_out((anim - 4.3) / 1.3)

    def finished(self, anim):
        return anim is None or anim > 5.8

    # -------------------------------------------------------------- drawing
    def draw(self, surf, data, t, anim=None, hover=None):
        scaled = data.get("scaled", {})
        best = data.get("best", {})
        indexes = data.get("indexes", {})
        fs = data.get("fsiq")
        hide = data.get("hide", False)   # show what's been measured, but no numbers

        # connections
        for idx, codes in scoring.INDEX_SUBTESTS.items():
            col = T.INDEX_COLORS[idx]
            ip = self.index_pos[idx]
            lit_idx = idx in indexes and self._idx_frac(idx, anim) > 0
            self._link(surf, self.center, ip, col, lit_idx and fs is not None and self._fs_frac(anim) > 0, t, FS_R, IDX_R)
            for code in codes:
                lit = code in scaled and self._sub_fill(code, 19 if hide else scaled[code], anim) > 0
                self._link(surf, ip, self.sub_pos[code], col, lit, t, IDX_R, SUB_R)

        for code, pos in self.sub_pos.items():
            idx = BY_CODE[code].index
            s = scaled.get(code)
            filled = self._sub_fill(code, 19 if hide else s, anim) if s else 0
            ghost = 0 if hide else best.get(code, 0)
            self._sub_node(surf, pos, code, s, filled, ghost, T.INDEX_COLORS[idx], hover == code, t, hide)
        for idx, pos in self.index_pos.items():
            self._index_node(surf, pos, idx, indexes.get(idx), self._idx_frac(idx, anim), hover == idx, t, hide)
        self._fsiq_node(surf, self.center, fs, self._fs_frac(anim), hover == "FSIQ", t, hide)

    def _link(self, surf, a, b, col, lit, t, ra, rb):
        ax, ay = a
        bx, by = b
        d = math.hypot(bx - ax, by - ay) or 1
        ux, uy = (bx - ax) / d, (by - ay) / d
        p1 = (ax + ux * (ra + 14), ay + uy * (ra + 14))
        p2 = (bx - ux * (rb + 14), by - uy * (rb + 14))
        if lit:
            gfx.thick_line(surf, p1, p2, 3, gfx.scale_color(col, 0.55))
            for k in range(2):
                f = (t * 0.35 + k * 0.5 + (ax + by) * 0.001) % 1.0
                q = (p1[0] + (p2[0] - p1[0]) * f, p1[1] + (p2[1] - p1[1]) * f)
                gfx.glow(surf, q, 16, col, 0.7 * math.sin(f * math.pi))
        else:
            gfx.thick_line(surf, p1, p2, 2, T.TRACK)

    def _sub_node(self, surf, pos, code, scaled, filled, best, col, hover, t, hide=False):
        x, y = pos
        if filled:
            gfx.glow(surf, pos, 70 + filled * 2, col, 0.18 + 0.012 * filled + (0.1 if hover else 0))
        elif hover:
            gfx.glow(surf, pos, 70, col, 0.15)
        gfx.circle(surf, pos, SUB_R, gfx.lerp_color(T.PANEL, col, 0.12 if filled else 0.0))
        gfx.circle(surf, pos, SUB_R, col if hover else T.BORDER, 1)
        gfx.pips(surf, pos, SUB_RING, 6, 19, filled, col, ghost=best)
        if scaled and hide:
            gfx.text(surf, code, (x, y), 18, col, bold=True, anchor="center")
        else:
            if scaled:
                gfx.text(surf, str(filled), (x, y - 3), 24, T.TEXT, bold=True, anchor="center")
            else:
                gfx.text(surf, "–", (x, y - 3), 22, T.DIM, bold=True, anchor="center")
            gfx.text(surf, code, (x, y + 15), 11, col if scaled else T.DIM, bold=True, anchor="center")
        gfx.text(surf, BY_CODE[code].name, (x, y + SUB_RING + 16), 14, T.TEXT if hover else T.MUTED, anchor="center")

    def _index_node(self, surf, pos, idx, score, frac, hover, t, hide=False):
        x, y = pos
        col = T.INDEX_COLORS[idx]
        has = score is not None and frac > 0
        if has:
            gfx.glow(surf, pos, 130, col, 0.28 + (0.1 if hover else 0))
        gfx.circle(surf, pos, IDX_R, gfx.lerp_color(T.PANEL, col, 0.14 if has else 0.04))
        gfx.circle(surf, pos, IDX_R, col if (hover or has) else T.BORDER, 1)
        target = 1.0 if hide else (score - 50) / 100 if score is not None else 0
        gfx.ring(surf, pos, IDX_RING, 8, target * frac if has else 0, gfx.scale_color(col, 0.6) if hide else col)
        # tick at the population mean (100)
        gfx.arc(surf, pos, IDX_RING, 12, math.pi - 0.02, math.pi + 0.02, T.MUTED)
        if has and hide:
            gfx.text(surf, idx, (x, y), 20, col, bold=True, anchor="center")
            return
        if has:
            val = int(round(50 + (score - 50) * frac))
            gfx.text(surf, str(val), (x, y - 5), 30, T.TEXT, bold=True, anchor="center")
        else:
            gfx.text(surf, "?", (x, y - 5), 28, T.DIM, bold=True, anchor="center")
        gfx.text(surf, idx, (x, y + 20), 12, col, bold=True, anchor="center")

    def _fsiq_node(self, surf, pos, score, frac, hover, t, hide=False):
        x, y = pos
        col = T.GOLD
        has = score is not None and frac > 0
        pulse = 0.5 + 0.5 * math.sin(t * 1.6)
        if has:
            gfx.glow(surf, pos, 210, col, 0.3 + 0.08 * pulse)
        else:
            gfx.glow(surf, pos, 170, T.ACCENT, 0.08 + 0.04 * pulse)
        gfx.circle(surf, pos, FS_R, gfx.lerp_color(T.PANEL, col, 0.12 if has else 0.03))
        gfx.circle(surf, pos, FS_R, col if (has or hover) else T.BORDER, 1)
        target = 1.0 if hide else ((score - 40) / 120 if has else 0)
        gfx.ring(surf, pos, FS_RING, 10, target * frac if has else 0, gfx.scale_color(col, 0.6) if hide else col)
        gfx.pips(surf, pos, FS_RING + 14, 2, 60, 0, col, track=gfx.lerp_color(T.BG, T.TRACK, 0.7), gap=0.05)
        # tick at the population mean: (100 - 40) / 120 = half way round
        gfx.arc(surf, pos, FS_RING, 14, math.pi - 0.02, math.pi + 0.02, T.MUTED)
        if has and hide:
            gfx.text(surf, "SCORE", (x, y - 6), 28, col, bold=True, anchor="center")
            gfx.text(surf, "scores hidden", (x, y + 22), 11, T.MUTED, anchor="center")
        elif has:
            val = int(round(40 + (score - 40) * frac))
            gfx.text(surf, str(val), (x, y - 8), 48, T.TEXT, bold=True, anchor="center")
            gfx.text(surf, "FULL SCALE SCORE", (x, y + 26), 11, col, bold=True, anchor="center")
        else:
            gfx.text(surf, "SCORE", (x, y - 6), 28, T.DIM, bold=True, anchor="center")
            gfx.text(surf, "complete all 10", (x, y + 22), 11, T.DIM, anchor="center")
