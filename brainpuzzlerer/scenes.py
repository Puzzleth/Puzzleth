"""Menu, subtest briefing, results and pause screens."""
import math

import pygame

from .display import mouse_pos
from . import gfx, scoring
from . import theme as T
from .skilltree import SkillTree
from .subtests import BY_CODE, ORDER
from .widgets import Button


def _tooltip(surf, pos, title, lines, color):
    w = 330
    h = 46 + 22 * len(lines)
    x = min(T.W - w - 16, pos[0] + 18)
    y = min(T.H - h - 16, pos[1] + 18)
    rect = pygame.Rect(x, y, w, h)
    gfx.panel(surf, rect, T.PANEL, color, radius=12, alpha=248)
    gfx.text(surf, title, (x + 16, y + 12), 17, color, bold=True)
    for i, line in enumerate(lines):
        gfx.text(surf, line, (x + 16, y + 40 + i * 22), 15, T.TEXT if i == 0 else T.MUTED)


def tree_tooltip(surf, key, pos, scaled, raw, best, attempts, indexes, fsiq):
    if key in BY_CODE:
        cls = BY_CODE[key]
        col = T.INDEX_COLORS[cls.index]
        lines = [cls.measures]
        s = scaled.get(key)
        if s:
            lines.append(f"Scaled score {s} / 19  ·  {scoring.scaled_label(s)}")
            lines.append(f"Percentile ≈ {scoring.scaled_percentile(s):.0f}" +
                         (f"  ·  raw {raw[key]} / {cls.max_raw}" if raw.get(key) is not None else ""))
        else:
            lines.append("Not yet measured")
        if best.get(key):
            lines.append(f"Personal best {best[key]}  ·  {attempts.get(key, 0)} attempt(s)")
        _tooltip(surf, pos, f"{cls.name}  ({cls.index})", lines, col)
    elif key in scoring.INDEX_SUBTESTS:
        col = T.INDEX_COLORS[key]
        names = ", ".join(BY_CODE[c].name for c in scoring.INDEX_SUBTESTS[key])
        lines = [names]
        if key in indexes:
            v = indexes[key]
            lines += [f"Index score {v}  ·  {scoring.classification(v)}", f"Percentile ≈ {scoring.percentile(v):.0f}"]
        else:
            lines.append("Complete all of its subtests to compute it")
        _tooltip(surf, pos, T.INDEX_NAMES[key], lines, col)
    elif key == "FSIQ":
        lines = ["Combines all ten core subtests"]
        if fsiq:
            lines += [f"{fsiq}  ·  {scoring.classification(fsiq)}", f"Percentile ≈ {scoring.percentile(fsiq):.0f}",
                      "Training estimate — not a clinical IQ"]
        else:
            lines.append("Take the full assessment to compute it")
        _tooltip(surf, pos, "Full Scale IQ", lines, T.GOLD)


class Scene:
    def __init__(self, app):
        self.app = app
        self.t = 0.0
        self.buttons = []

    def handle_event(self, e):
        for b in self.buttons:
            if b.handle(e):
                return True
        return False

    def update(self, dt):
        self.t += dt
        for b in self.buttons:
            b.update(dt)

    def draw(self, surf):
        for b in self.buttons:
            b.draw(surf)


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.tree = SkillTree()
        self.hover = None
        self.begin = Button((T.W - 410, 30, 250, 54), "Begin Full Assessment", app.start_battery, T.GOLD,
                            hotkeys=(pygame.K_RETURN,), primary=True, size=19)
        self.quit_btn = Button((T.W - 150, 30, 110, 54), "Quit", app.quit, T.BAD, size=17)
        self.fb_btn = Button((T.W - 410, 94, 180, 40), "", self._toggle_fb, T.ACCENT, size=15)
        self.fs_btn = Button((T.W - 220, 94, 180, 40), "", app.toggle_fullscreen, T.ACCENT, size=15)
        self.buttons = [self.begin, self.fb_btn, self.fs_btn, self.quit_btn]
        self._refresh()

    def _toggle_fb(self):
        s = self.app.profile.settings
        s["feedback"] = not s.get("feedback", True)
        self.app.profile.save()

    def _refresh(self):
        p = self.app.profile
        self.scaled = {c: p.last_scaled(c) for c in BY_CODE if p.last_scaled(c)}
        self.raw = {c: p.last_raw(c) for c in BY_CODE}
        self.best = {c: p.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: p.attempts(c) for c in BY_CODE}
        self.indexes, self.fsiq = scoring.compute_indexes(self.scaled)

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            key = self.tree.hit(e.pos)
            if key in BY_CODE:
                self.app.start_practice(BY_CODE[key])
                return True
        if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
            self.app.quit()
        return False

    def update(self, dt):
        super().update(dt)
        self.fb_btn.label = "Feedback: " + ("ON" if self.app.profile.settings.get("feedback", True) else "OFF")
        self.fs_btn.label = ("Windowed" if self.app.fullscreen else "Fullscreen") + "  (F11)"
        self.fs_btn.enabled = self.app.display is not None
        self.hover = self.tree.hit(mouse_pos())

    def draw(self, surf):
        gfx.text(surf, "BRAIN PUZZLERER", (40, 30), 34, T.TEXT, bold=True)
        gfx.text(surf, "WAIS-style cognitive training", (42, 74), 17, T.MUTED)
        n = len(self.scaled)
        gfx.text(surf, f"{n} / 10 skills measured  ·  click any node to train that subtest alone", (42, 100), 15,
                 T.DIM)
        data = {"scaled": self.scaled, "best": self.best, "indexes": self.indexes, "fsiq": self.fsiq}
        self.tree.draw(surf, data, self.t, None, self.hover)
        super().draw(surf)
        if self.hover:
            tree_tooltip(surf, self.hover, mouse_pos(), self.scaled, self.raw, self.best, self.attempts,
                         self.indexes, self.fsiq)


class IntroScene(Scene):
    """Briefing shown before each subtest: what it measures and the real test's rules."""

    def __init__(self, app, cls, battery_pos=None):
        super().__init__(app)
        self.cls = cls
        self.battery_pos = battery_pos
        col = T.INDEX_COLORS[cls.index]
        self.start = Button((T.W - 300, T.H - 110, 250, 56), "Begin", lambda: app.begin_subtest(cls), col,
                            hotkeys=(pygame.K_RETURN, pygame.K_SPACE), primary=True, size=20)
        back_label = "Abandon assessment" if battery_pos else "Back"
        self.back = Button((50, T.H - 104, 220, 44), back_label, app.to_menu, T.MUTED, hotkeys=(pygame.K_ESCAPE,),
                           size=16)
        self.buttons = [self.start, self.back]

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        a = gfx.ease_out(self.t / 0.5)
        if self.battery_pos is not None:
            i = self.battery_pos
            gfx.text(surf, f"FULL ASSESSMENT  ·  SUBTEST {i + 1} OF {len(ORDER)}", (50, 40), 14, T.GOLD, bold=True)
            for k, c in enumerate(ORDER):
                cc = T.INDEX_COLORS[c.index]
                x = 50 + k * 30
                gfx.circle(surf, (x + 8, 70), 7, cc if k < i else (gfx.lerp_color(T.TRACK, cc, 0.6) if k == i else T.TRACK))
                if k == i:
                    gfx.circle(surf, (x + 8, 70), 11, cc, 2)
        y0 = 110
        gfx.glow(surf, (220, y0 + 60), 300, col, 0.18 * a)
        chip = pygame.Rect(50, y0, 230, 28)
        gfx.panel(surf, chip, gfx.lerp_color(T.PANEL, col, 0.25), col, radius=14)
        gfx.text(surf, T.INDEX_NAMES[cls.index].upper(), chip.center, 13, col, bold=True, anchor="center")
        gfx.text(surf, cls.name, (50, y0 + 44), 54, T.TEXT, bold=True)
        gfx.text(surf, cls.measures, (52, y0 + 112), 20, T.MUTED)

        rp = pygame.Rect(50, 290, 700, 360)
        gfx.panel(surf, rp, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "RULES OF THE REAL TEST", (rp.x + 26, rp.y + 22), 14, col, bold=True)
        y = rp.y + 56
        for rule in cls.rules:
            gfx.circle(surf, (rp.x + 32, y + 11), 3, col)
            y += gfx.text_block(surf, rule, (rp.x + 46, y), rp.w - 76, 17, T.TEXT, spacing=1.25) + 8

        cp = pygame.Rect(780, 290, 450, 200)
        gfx.panel(surf, cp, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "HOW TO PLAY HERE", (cp.x + 26, cp.y + 22), 14, col, bold=True)
        y = cp.y + 56
        for c in cls.controls:
            y += gfx.text_block(surf, c, (cp.x + 26, y), cp.w - 52, 17, T.TEXT, spacing=1.25) + 8

        mp = pygame.Rect(780, 506, 450, 144)
        gfx.panel(surf, mp, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "MODE", (mp.x + 26, mp.y + 22), 14, col, bold=True)
        if self.battery_pos is not None:
            mode = "Test conditions: no feedback, exactly like the real assessment. Your result stays hidden " \
                   "until all ten subtests are complete."
        elif self.app.profile.settings.get("feedback", True):
            mode = "Training: after every item you'll see the score it earned and the best answer."
        else:
            mode = "Test conditions: no feedback after items. Sample items are still explained."
        gfx.text_block(surf, mode, (mp.x + 26, mp.y + 52), mp.w - 52, 16, T.MUTED, spacing=1.25)
        super().draw(surf)


class SubtestResultScene(Scene):
    def __init__(self, app, cls, raw, scaled, best_before, details):
        super().__init__(app)
        self.cls = cls
        self.raw = raw
        self.scaled = scaled
        self.best_before = best_before
        self.details = details
        col = T.INDEX_COLORS[cls.index]
        self.buttons = [
            Button((T.W // 2 - 260, T.H - 120, 240, 54), "Train again", lambda: app.start_practice(cls), col,
                   hotkeys=(pygame.K_r,), primary=True),
            Button((T.W // 2 + 20, T.H - 120, 240, 54), "Skill tree", app.to_menu, T.ACCENT,
                   hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE)),
        ]

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        c = (T.W // 2, 330)
        filled = int(gfx.clamp((self.t - 0.4) * 14, 0, self.scaled))
        gfx.text(surf, cls.name.upper(), (c[0], 70), 16, col, bold=True, anchor="center")
        gfx.glow(surf, c, 260, col, 0.2 + 0.02 * filled)
        gfx.circle(surf, c, 112, gfx.lerp_color(T.PANEL, col, 0.12))
        gfx.pips(surf, c, 140, 18, 19, filled, col, ghost=self.best_before)
        gfx.text(surf, str(filled), (c[0], c[1] - 14), 92, T.TEXT, bold=True, anchor="center")
        gfx.text(surf, "SCALED SCORE", (c[0], c[1] + 48), 13, col, bold=True, anchor="center")
        if self.t > 0.4 + self.scaled / 14:
            label = scoring.scaled_label(self.scaled)
            gfx.text(surf, label, (c[0], c[1] + 190), 28, T.TEXT, bold=True, anchor="center")
            pct = scoring.scaled_percentile(self.scaled)
            line = f"Raw {self.raw} / {cls.max_raw}   ·   ≈ {pct:.0f}th percentile   ·   mean is 10, SD 3"
            gfx.text(surf, line, (c[0], c[1] + 232), 18, T.MUTED, anchor="center")
            if self.scaled > self.best_before > 0:
                gfx.text(surf, "NEW PERSONAL BEST", (c[0], c[1] + 268), 16, T.GOLD, bold=True, anchor="center")
            extra = self._extra()
            if extra:
                gfx.text(surf, extra, (c[0], c[1] + 296), 16, T.DIM, anchor="center")
        super().draw(surf)

    def _extra(self):
        d = self.details
        if "forward" in d:
            return f"Forward {d['forward']}  ·  Backward {d['backward']}  ·  Sequencing {d['sequencing']}"
        if "attempted" in d:
            return f"{d['correct']} correct  ·  {d['wrong']} incorrect  ·  {d['attempted']} attempted"
        if d.get("discontinued"):
            return f"Discontinued after {d['items']} items administered"
        if "items" in d:
            return f"{d['items']} items administered"
        return ""


class BatteryResultScene(Scene):
    def __init__(self, app, scaled, raw, indexes, fsiq):
        super().__init__(app)
        self.tree = SkillTree(center=(475, 460), sx=0.82)
        self.scaled = scaled
        self.raw = raw
        self.indexes = indexes
        self.fsiq = fsiq
        self.best = {c: app.profile.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: app.profile.attempts(c) for c in BY_CODE}
        self.hover = None
        self.buttons = [Button((T.W - 290, T.H - 100, 250, 54), "Skill tree", app.to_menu, T.GOLD,
                               hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE), primary=True)]

    def update(self, dt):
        super().update(dt)
        self.hover = self.tree.hit(mouse_pos()) if self.tree.finished(self.t) else None

    def handle_event(self, e):
        if not self.tree.finished(self.t) and (e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN):
            self.t = 6.0   # skip the animation
            return True
        return super().handle_event(e)

    def draw(self, surf):
        gfx.text(surf, "ASSESSMENT COMPLETE", (40, 30), 30, T.TEXT, bold=True)
        gfx.text(surf, "Your skill constellation", (42, 70), 17, T.MUTED)
        data = {"scaled": self.scaled, "best": self.best, "indexes": self.indexes, "fsiq": self.fsiq}
        self.tree.draw(surf, data, self.t, self.t, self.hover)

        p = pygame.Rect(T.W - 330, 120, 290, 520)
        a = gfx.ease_out((self.t - 5.0) / 0.8)
        if a > 0:
            gfx.panel(surf, p, T.PANEL, T.BORDER, radius=18, alpha=int(235 * a))
            x, y = p.x + 24, p.y + 22
            gfx.text(surf, "FULL SCALE IQ", (x, y), 13, T.GOLD, bold=True, alpha=255 * a)
            gfx.text(surf, str(self.fsiq), (x, y + 18), 64, T.TEXT, bold=True, alpha=255 * a)
            gfx.text(surf, scoring.classification(self.fsiq), (x, y + 96), 20, T.GOLD, bold=True, alpha=255 * a)
            gfx.text(surf, f"≈ {scoring.percentile(self.fsiq):.1f}th percentile", (x, y + 124), 16, T.MUTED,
                     alpha=255 * a)
            y += 170
            for idx in ("VCI", "PRI", "WMI", "PSI"):
                v = self.indexes[idx]
                col = T.INDEX_COLORS[idx]
                gfx.text(surf, T.INDEX_NAMES[idx], (x, y), 15, T.TEXT, alpha=255 * a)
                gfx.text(surf, str(v), (p.right - 24, y), 17, col, bold=True, anchor="topright", alpha=255 * a)
                bar = pygame.Rect(x, y + 24, p.w - 48, 6)
                pygame.draw.rect(surf, T.TRACK, bar, border_radius=3)
                pygame.draw.rect(surf, col, (bar.x, bar.y, bar.w * (v - 50) / 100 * a, 6), border_radius=3)
                mid = bar.x + bar.w // 2
                pygame.draw.line(surf, T.MUTED, (mid, bar.y - 3), (mid, bar.bottom + 2), 1)
                y += 52
            gfx.text_block(surf, "Estimates use approximate norms tuned to this game. They show trends in your "
                                 "training, not a clinical IQ.", (x, y + 8), p.w - 48, 13, T.DIM, alpha=255 * a)
        super().draw(surf)
        if self.hover:
            tree_tooltip(surf, self.hover, mouse_pos(), self.scaled, self.raw, self.best, self.attempts,
                         self.indexes, self.fsiq)
        if not self.tree.finished(self.t):
            gfx.text(surf, "click to skip", (475, 100), 13, T.DIM, anchor="center")


class PauseOverlay:
    def __init__(self, app):
        self.app = app
        cx = T.W // 2
        self.buttons = [
            Button((cx - 140, 330, 280, 52), "Resume", app.resume, T.ACCENT, hotkeys=(pygame.K_ESCAPE,), primary=True),
            Button((cx - 140, 394, 280, 52), "Restart subtest", app.restart_subtest, T.PARTIAL),
            Button((cx - 140, 458, 280, 52), "Quit to skill tree", app.to_menu, T.BAD),
        ]

    def handle_event(self, e):
        for b in self.buttons:
            if b.handle(e):
                return

    def update(self, dt):
        for b in self.buttons:
            b.update(dt)

    def draw(self, surf):
        gfx.overlay(surf, T.BG, 200)
        gfx.text(surf, "Paused", (T.W // 2, 260), 44, T.TEXT, bold=True, anchor="center")
        gfx.text(surf, "Timers are stopped (the real test can't be paused!)  ·  F11 toggles fullscreen", (T.W // 2, 300),
                 16, T.MUTED,
                 anchor="center")
        for b in self.buttons:
            b.draw(surf)
