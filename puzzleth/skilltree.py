"""The skill-point constellation: FSIQ at the centre, four index nodes, ten subtest nodes.

Each subtest node is a ring of 19 skill points, one per scaled-score point (WAIS scaled
scores run 1-19, mean 10). Index and FSIQ nodes are progress rings over their score range.
"""
import math

import pygame

from . import gfx, i18n, scoring
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
        "VCI": (-300, -145), "IN": (-450, -270), "VC": (-565, -145), "SI": (-450, -20),
        "WMI": (-250, 145), "AR": (-525, 130), "DS": (-350, 255),
    }
    # the compact layout (see theme.py): about 450 tall instead of 600, the subtests staggered in
    # two columns that reach out to the edges of a phone, with larger nodes and names (``scale``);
    # each name is kept narrow enough to stay clear of its neighbours (``name_w``)
    _LEFT_COMPACT = {
        "VCI": (-200, -100), "IN": (-360, -170), "VC": (-520, -60), "SI": (-360, -10),
        "WMI": (-200, 100), "AR": (-520, 80), "DS": (-360, 150),
    }
    _NAME_W_COMPACT = {"IN": 180, "SI": 180, "DS": 300, "VC": 210, "AR": 210}
    # as compact, but only about 720 wide: there is no room for the names, the nodes show their codes
    _LEFT_NARROW = {
        "VCI": (-165, -105), "IN": (-255, -185), "VC": (-320, -95), "SI": (-280, -5),
        "WMI": (-165, 105), "AR": (-320, 95), "DS": (-255, 185),
    }
    _MIRROR = {"VCI": "PRI", "IN": "BD", "VC": "MR", "SI": "VP", "WMI": "PSI", "AR": "SS", "DS": "CD"}

    def __init__(self, center=None, sx=1.0, sy=1.0, layout="full"):
        cx, cy = center = center or (T.W // 2, 460)
        self.center = center
        self.names = layout != "narrow"
        self.scale = 1.2 if layout == "compact" else 1.0
        k = self.scale
        self.sub_r, self.sub_ring = SUB_R * k, SUB_RING * k
        self.idx_r, self.idx_ring = IDX_R * k, IDX_RING * k
        self.fs_r, self.fs_ring = FS_R * k, FS_RING * k
        name_w = self._NAME_W_COMPACT if layout == "compact" else {}
        self.name_w = {}
        left = {"full": self._LEFT, "compact": self._LEFT_COMPACT, "narrow": self._LEFT_NARROW}[layout]
        pos = {}
        for k, (ox, oy) in left.items():
            pos[k] = (cx + ox * sx, cy + oy * sy)
            pos[self._MIRROR[k]] = (cx - ox * sx, cy + oy * sy)
            if k in name_w:
                self.name_w[k] = self.name_w[self._MIRROR[k]] = name_w[k]
        self.index_pos = {k: pos[k] for k in scoring.INDEX_SUBTESTS}
        self.sub_pos = {k: v for k, v in pos.items() if k not in scoring.INDEX_SUBTESTS}
        self.order = [cls.code for cls in BY_CODE.values()]

    # -------------------------------------------------------------- hit testing
    def hit(self, pos):
        x, y = pos
        for code, (px, py) in self.sub_pos.items():
            if math.hypot(x - px, y - py) <= self.sub_ring + 6:
                return code
        for idx, (px, py) in self.index_pos.items():
            if math.hypot(x - px, y - py) <= self.idx_ring + 6:
                return idx
        if math.hypot(x - self.center[0], y - self.center[1]) <= self.fs_ring + 6:
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
            self._link(surf, self.center, ip, col, lit_idx and fs is not None and self._fs_frac(anim) > 0, t,
                       self.fs_r, self.idx_r)
            for code in codes:
                lit = code in scaled and self._sub_fill(code, 19 if hide else scaled[code], anim) > 0
                self._link(surf, ip, self.sub_pos[code], col, lit, t, self.idx_r, self.sub_r)

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
        k = self.scale
        if filled:
            gfx.glow(surf, pos, (70 + filled * 2) * k, col, 0.18 + 0.012 * filled + (0.1 if hover else 0))
        elif hover:
            gfx.glow(surf, pos, 70 * k, col, 0.15)
        gfx.circle(surf, pos, self.sub_r, gfx.lerp_color(T.PANEL, col, 0.12 if filled else 0.0))
        gfx.circle(surf, pos, self.sub_r, col if hover else T.BORDER, 1)
        gfx.pips(surf, pos, self.sub_ring, 6 * k, 19, filled, col, ghost=best)
        if scaled and hide:
            gfx.text(surf, i18n.abbr(code), (x, y), round(18 * k), col, bold=True, anchor="center")
        else:
            gap = 3 if T.large_text else 0   # large text would run the number into the code
            if scaled:
                gfx.text(surf, str(filled), (x, y - (3 + gap) * k), 24, T.TEXT, bold=True, anchor="center")
            else:
                gfx.text(surf, "–", (x, y - (3 + gap) * k), 22, T.DIM, bold=True, anchor="center")
            gfx.text(surf, i18n.abbr(code), (x, y + (15 + gap) * k), round(11 * k), col if scaled else T.DIM,
                     bold=True, anchor="center")
        if self.names:
            name, size, at = self._name(code)
            gfx.text(surf, name, at, size, T.TEXT if hover else T.MUTED, anchor="center")

    def _name(self, code):
        """A subtest's name under its node: (text, size, centre)."""
        x, y = self.sub_pos[code]
        name, size = BY_CODE[code].name, round(14 * self.scale)
        if code in self.name_w:
            size = gfx.fit_width(name, size, self.name_w[code])
        return name, size, (x, y + self.sub_ring + 16 * self.scale)

    def name_rect(self, code):
        name, size, at = self._name(code)
        r = pygame.Rect((0, 0), T.font(size).size(i18n._(name)))
        r.center = at
        return r

    def _index_node(self, surf, pos, idx, score, frac, hover, t, hide=False):
        x, y = pos
        k = self.scale
        col = T.INDEX_COLORS[idx]
        has = score is not None and frac > 0
        if has:
            gfx.glow(surf, pos, 130 * k, col, 0.28 + (0.1 if hover else 0))
        gfx.circle(surf, pos, self.idx_r, gfx.lerp_color(T.PANEL, col, 0.14 if has else 0.04))
        gfx.circle(surf, pos, self.idx_r, col if (hover or has) else T.BORDER, 1)
        target = 1.0 if hide else (score - 50) / 100 if score is not None else 0
        gfx.ring(surf, pos, self.idx_ring, 8 * k, target * frac if has else 0, gfx.scale_color(col, 0.6) if hide else col)
        # tick at the population mean (100)
        gfx.arc(surf, pos, self.idx_ring, 12 * k, math.pi - 0.02, math.pi + 0.02, T.MUTED)
        if has and hide:
            gfx.text(surf, i18n.abbr(idx), (x, y), round(20 * k), col, bold=True, anchor="center")
            return
        gap = 3 if T.large_text else 0
        if has:
            val = int(round(50 + (score - 50) * frac))
            gfx.text(surf, str(val), (x, y - (5 + gap) * k), round(30 * k), T.TEXT, bold=True, anchor="center")
        else:
            gfx.text(surf, "?", (x, y - (5 + gap) * k), round(28 * k), T.DIM, bold=True, anchor="center")
        gfx.text(surf, i18n.abbr(idx), (x, y + (20 + gap) * k), round(12 * k), col, bold=True, anchor="center")

    def _fsiq_node(self, surf, pos, score, frac, hover, t, hide=False):
        x, y = pos
        k = self.scale
        col = T.GOLD
        has = score is not None and frac > 0
        pulse = 0.5 + 0.5 * math.sin(t * 1.6)
        if has:
            gfx.glow(surf, pos, 210 * k, col, 0.3 + 0.08 * pulse)
        else:
            gfx.glow(surf, pos, 170 * k, T.ACCENT, 0.08 + 0.04 * pulse)
        r, ring = self.fs_r, self.fs_ring
        gfx.circle(surf, pos, r, gfx.lerp_color(T.PANEL, col, 0.12 if has else 0.03))
        gfx.circle(surf, pos, r, col if (has or hover) else T.BORDER, 1)
        target = 1.0 if hide else ((score - 40) / 120 if has else 0)
        gfx.ring(surf, pos, ring, 10 * k, target * frac if has else 0, gfx.scale_color(col, 0.6) if hide else col)
        gfx.pips(surf, pos, ring + 14 * k, 2, 60, 0, col, track=gfx.lerp_color(T.BG, T.TRACK, 0.7), gap=0.05)
        # tick at the population mean: (100 - 40) / 120 = half way round
        gfx.arc(surf, pos, ring, 14 * k, math.pi - 0.02, math.pi + 0.02, T.MUTED)
        small = round(11 * k)
        if has and hide:
            gfx.text(surf, "SCORE", (x, y - 6 * k), round(28 * k), col, bold=True, anchor="center")
            gfx.text(surf, "scores hidden", (x, y + 22 * k), gfx.fit_width("scores hidden", small, 2 * r - 24), T.MUTED,
                     anchor="center")
        elif has:
            val = int(round(40 + (score - 40) * frac))
            gfx.text(surf, str(val), (x, y - 8 * k), round(48 * k), T.TEXT, bold=True, anchor="center")
            gfx.text(surf, "FULL SCALE SCORE", (x, y + 26 * k),
                     gfx.fit_width("FULL SCALE SCORE", small, 2 * r - 24, True), col, bold=True, anchor="center")
        else:
            gfx.text(surf, "SCORE", (x, y - 6 * k), round(28 * k), T.DIM, bold=True, anchor="center")
            gfx.text(surf, "complete all 10", (x, y + 22 * k), gfx.fit_width("complete all 10", small, 2 * r - 24),
                     T.DIM, anchor="center")
