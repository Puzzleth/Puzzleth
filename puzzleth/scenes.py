"""Menu, subtest briefing, results, learn, settings and pause screens."""

import datetime

import pygame

from . import gfx, scoring, sound, web
from . import theme as T
from .challenge import FLOOR, daily_number
from .content.learn import TOPICS
from .display import mouse_pos
from .skilltree import SkillTree
from .subtests import BY_CODE, ORDER
from .widgets import Button

# Your donation page, e.g. "https://ko-fi.com/yourname". The menu shows a Donate button once it's set.
DONATE_URL = "https://ko-fi.com/n0va"


def _tooltip(surf, pos, title, lines, color):
    w = 330
    h = 46 + 22 * len(lines)
    x = min(T.W - w - 16, pos[0] + 18)
    y = min(T.H - h - 16, pos[1] + 18)
    rect = pygame.Rect(x, y, w, h)
    gfx.panel(surf, rect, T.PANEL, color, radius=12, alpha=248)
    gfx.text(surf, title, (x + 16, y + 12), 17, color, bold=True)
    for i, line in enumerate(lines):
        gfx.text(
            surf, line, (x + 16, y + 40 + i * 22), 15, T.TEXT if i == 0 else T.MUTED
        )


def tree_tooltip(
    surf, key, pos, scaled, raw, best, attempts, indexes, fsiq, hide=False, ratings=None
):
    ratings = ratings or {}
    if key in BY_CODE:
        cls = BY_CODE[key]
        col = T.INDEX_COLORS[cls.index]
        lines = [cls.measures]
        s = scaled.get(key)
        if s and hide:
            lines.append(
                f"Measured  ·  scores hidden  ·  {attempts.get(key, 0)} attempt(s)"
            )
        elif s:
            lines.append(f"Scaled score {s} / 19  ·  {scoring.scaled_label(s)}")
            lines.append(
                f"Percentile ≈ {scoring.scaled_percentile(s):.0f}"
                + (
                    f"  ·  raw {raw[key]} / {cls.max_raw}"
                    if raw.get(key) is not None
                    else ""
                )
            )
        else:
            lines.append("Not yet measured")
        if best.get(key) and not hide:
            lines.append(
                f"Personal best {best[key]}  ·  {attempts.get(key, 0)} attempt(s)"
            )
        if getattr(cls, "challenge", False):
            r = ratings.get(key)
            lines.append(
                f"Puzzle rating {r['rating']:.0f}  ·  peak {r['peak']:.0f}"
                if r
                else "Rated puzzle sets available"
            )
        _tooltip(surf, pos, f"{cls.name}  ({cls.index})", lines, col)
    elif key in scoring.INDEX_SUBTESTS:
        col = T.INDEX_COLORS[key]
        names = ", ".join(BY_CODE[c].name for c in scoring.INDEX_SUBTESTS[key])
        lines = [names]
        if key in indexes and hide:
            lines.append("Measured  ·  scores hidden")
        elif key in indexes:
            v = indexes[key]
            lines += [
                f"Index score {v}  ·  {scoring.classification(v)}",
                f"Percentile ≈ {scoring.percentile(v):.0f}",
            ]
        else:
            lines.append("Complete all of its subtests to compute it")
        _tooltip(surf, pos, T.INDEX_NAMES[key], lines, col)
    elif key == "FSIQ":
        lines = ["Combines all ten core subtests"]
        if fsiq and hide:
            lines.append("Measured  ·  scores hidden")
        elif fsiq:
            lines += [
                f"{fsiq}  ·  {scoring.classification(fsiq)}",
                f"Percentile ≈ {scoring.percentile(fsiq):.0f}",
                "Training estimate, not a real IQ",
            ]
        else:
            lines.append("Take the full assessment to compute it")
        _tooltip(surf, pos, "Full Scale Score", lines, T.GOLD)


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


DISCLAIMER = [
    "Puzzleth is a training game modelled on the structure and rules of the WAIS-IV. It is not "
    "the WAIS, uses none of its items, and is not affiliated with or endorsed by its publisher.",
    "Scores come from approximate norms made up for this game, not from a standardised sample of people. "
    "The scores shown here cannot be compared with a real IQ score.",
    "It cannot diagnose anything and must not be used for school, work, legal or medical decisions. "
    "Only a standardised test given by a qualified psychologist produces a real IQ.",
    "Practising test formats can raise scores on a real test. If you take a clinical assessment, tell "
    "the examiner you have practised.",
]


class DisclaimerScene(Scene):
    """Shown on first launch (must be acknowledged) and from the menu's About button."""

    def __init__(self, app):
        super().__init__(app)
        self.first = not app.profile.settings.get("disclaimer_seen")
        label = "I understand" if self.first else "Back"
        self.ok = Button(
            (T.W // 2 - 125, 620, 250, 54),
            label,
            self._ok,
            T.GOLD,
            hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
            primary=True,
            size=19,
        )
        self.buttons = [self.ok]

    def _ok(self):
        if self.first:
            self.app.profile.settings["disclaimer_seen"] = True
            self.app.profile.save()
        self.app.to_menu()

    def draw(self, surf):
        p = pygame.Rect(0, 0, 820, 470)
        p.center = (T.W // 2, 350)
        gfx.glow(surf, p.center, 520, T.GOLD, 0.08)
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        gfx.text(
            surf,
            "PUZZLETH",
            (p.centerx, p.y + 36),
            14,
            T.GOLD,
            bold=True,
            anchor="center",
        )
        gfx.text(
            surf,
            "This is not an actual IQ test",
            (p.centerx, p.y + 78),
            34,
            T.TEXT,
            bold=True,
            anchor="center",
        )
        y = p.y + 130
        for para in DISCLAIMER:
            gfx.circle(surf, (p.x + 52, y + 11), 3, T.GOLD)
            y += (
                gfx.text_block(
                    surf, para, (p.x + 68, y), p.w - 120, 17, T.TEXT, spacing=1.25
                )
                + 16
            )
        super().draw(surf)


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.tree = SkillTree()
        self.hover = None
        self.begin = Button(
            (T.W - 410, 30, 240, 54),
            "Begin Full Assessment",
            app.start_battery,
            T.GOLD,
            hotkeys=(pygame.K_RETURN,),
            primary=True,
            size=18,
        )
        self.daily_btn = Button(
            (T.W - 160, 30, 120, 54),
            "Daily",
            app.start_daily,
            T.ACCENT,
            hotkeys=(pygame.K_d,),
            size=17,
        )
        self.learn_btn = Button(
            (T.W - 410, 94, 180, 40),
            "Learn",
            app.open_learn,
            T.ACCENT,
            hotkeys=(pygame.K_l,),
            size=15,
        )
        self.settings_btn = Button(
            (T.W - 220, 94, 180, 40),
            "Settings",
            lambda: app.goto(SettingsScene(app)),
            T.ACCENT,
            hotkeys=(pygame.K_s,),
            size=15,
        )
        self.about_btn = Button(
            (T.W - 260, T.H - 58, 100, 36),
            "About",
            lambda: app.goto(DisclaimerScene(app)),
            T.MUTED,
            size=14,
        )
        self.quit_btn = Button(
            (T.W - 150, T.H - 58, 110, 36), "Quit", app.quit, T.BAD, size=14
        )
        self.buttons = [
            self.begin,
            self.daily_btn,
            self.learn_btn,
            self.settings_btn,
            self.about_btn,
            self.quit_btn,
        ]
        if web.IS_WEB:  # a browser tab is closed, not quit
            self.buttons.remove(self.quit_btn)
            self.about_btn.rect.x = self.quit_btn.rect.right - self.about_btn.rect.w
        if DONATE_URL:
            self.donate_btn = Button(
                (40, T.H - 58, 110, 36),
                "Donate",
                lambda: web.open_url(DONATE_URL),
                T.GOLD,
                size=14,
            )
            self.buttons.append(self.donate_btn)
        self._refresh()

    def _refresh(self):
        p = self.app.profile
        self.scaled = {c: p.last_scaled(c) for c in BY_CODE if p.last_scaled(c)}
        self.raw = {c: p.last_raw(c) for c in BY_CODE}
        self.best = {c: p.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: p.attempts(c) for c in BY_CODE}
        self.indexes, self.fsiq = scoring.compute_indexes(self.scaled)
        self.ratings = {c: p.rating(c) for c in BY_CODE if p.rating(c)}
        today = datetime.date.today()
        done = p.daily_result(today)
        self.daily_btn.label = f"Daily  {done['solved']}/10" if done else "Daily"
        self.streak = p.daily_streak(today)

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
        self.hover = self.tree.hit(mouse_pos())

    def draw(self, surf):
        gfx.text(surf, "PUZZLETH", (40, 30), 34, T.TEXT, bold=True)
        gfx.text(surf, "WAIS-style cognitive training", (42, 74), 17, T.MUTED)
        n = len(self.scaled)
        line = f"{n} / 10 skills measured  ·  click any node to train it"
        if self.streak:
            line += f"  ·  daily streak {self.streak}"
        gfx.text(surf, line, (42, 100), 15, T.DIM)
        hide = not self.app.profile.settings.get("show_scores", True)
        data = {
            "scaled": self.scaled,
            "best": self.best,
            "indexes": self.indexes,
            "fsiq": self.fsiq,
            "hide": hide,
        }
        self.tree.draw(surf, data, self.t, None, self.hover)
        gfx.text(
            surf,
            "Not an actual IQ test. Scores are training estimates, not clinical results.",
            (T.W // 2, T.H - 26),
            14,
            T.DIM,
            anchor="center",
        )
        super().draw(surf)
        if self.hover:
            tree_tooltip(
                surf,
                self.hover,
                mouse_pos(),
                self.scaled,
                self.raw,
                self.best,
                self.attempts,
                self.indexes,
                self.fsiq,
                hide,
                self.ratings,
            )


class IntroScene(Scene):
    """Briefing shown before each subtest: what it measures and the real test's rules."""

    def __init__(self, app, cls, battery_pos=None, ladder_kind=None):
        super().__init__(app)
        self.cls = cls
        self.battery_pos = battery_pos
        self.ladder_kind = ladder_kind
        col = T.INDEX_COLORS[cls.index]
        self.start = Button(
            (T.W - 300, T.H - 110, 250, 56),
            "Begin",
            lambda: app.begin_subtest(cls, ladder_kind),
            col,
            hotkeys=(pygame.K_RETURN, pygame.K_SPACE),
            primary=True,
            size=20,
        )
        back_label = "Abandon assessment" if battery_pos else "Back"
        self.back = Button(
            (50, T.H - 104, 220, 44),
            back_label,
            app.to_menu,
            T.MUTED,
            hotkeys=(pygame.K_ESCAPE,),
            size=16,
        )
        self.buttons = [self.start, self.back]
        self.rated = None
        if (
            battery_pos is None
            and ladder_kind is None
            and getattr(cls, "challenge", False)
        ):
            r = app.profile.rating(cls.code)
            label = f"Rated set  ·  {r['rating']:.0f}" if r else "Rated set"
            self.rated = Button(
                (T.W - 570, T.H - 110, 250, 56),
                label,
                lambda: app.begin_subtest(cls, "rated"),
                T.GOLD,
                hotkeys=(pygame.K_r,),
                size=19,
            )
            self.buttons.append(self.rated)
        self.daily_done = (
            app.profile.daily_result(datetime.date.today())
            if ladder_kind == "daily"
            else None
        )

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        a = gfx.ease_out(self.t / 0.5)
        if self.ladder_kind == "daily":
            n = daily_number(datetime.date.today())
            gfx.text(
                surf,
                f"DAILY CHALLENGE #{n}  ·  SAME PUZZLES FOR EVERYONE TODAY",
                (50, 40),
                14,
                T.GOLD,
                bold=True,
            )
        if self.battery_pos is not None:
            i = self.battery_pos
            gfx.text(
                surf,
                f"FULL ASSESSMENT  ·  SUBTEST {i + 1} OF {len(ORDER)}",
                (50, 40),
                14,
                T.GOLD,
                bold=True,
            )
            for k, c in enumerate(ORDER):
                cc = T.INDEX_COLORS[c.index]
                x = 50 + k * 30
                gfx.circle(
                    surf,
                    (x + 8, 70),
                    7,
                    cc
                    if k < i
                    else (gfx.lerp_color(T.TRACK, cc, 0.6) if k == i else T.TRACK),
                )
                if k == i:
                    gfx.circle(surf, (x + 8, 70), 11, cc, 2)
        y0 = 110
        gfx.glow(surf, (220, y0 + 60), 300, col, 0.18 * a)
        chip = pygame.Rect(50, y0, 230, 28)
        gfx.panel(surf, chip, gfx.lerp_color(T.PANEL, col, 0.25), col, radius=14)
        gfx.text(
            surf,
            T.INDEX_NAMES[cls.index].upper(),
            chip.center,
            13,
            col,
            bold=True,
            anchor="center",
        )
        gfx.text(surf, cls.name, (50, y0 + 44), 54, T.TEXT, bold=True)
        gfx.text(surf, cls.measures, (52, y0 + 112), 20, T.MUTED)

        rp = pygame.Rect(50, 290, 700, 360)
        gfx.panel(surf, rp, T.PANEL, T.BORDER, radius=18)
        gfx.text(
            surf, "RULES OF THE REAL TEST", (rp.x + 26, rp.y + 22), 14, col, bold=True
        )
        y = rp.y + 56
        for rule in cls.rules:
            gfx.circle(surf, (rp.x + 32, y + 11), 3, col)
            y += (
                gfx.text_block(
                    surf, rule, (rp.x + 46, y), rp.w - 76, 17, T.TEXT, spacing=1.25
                )
                + 8
            )

        cp = pygame.Rect(780, 290, 450, 200)
        gfx.panel(surf, cp, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "HOW TO PLAY HERE", (cp.x + 26, cp.y + 22), 14, col, bold=True)
        y = cp.y + 56
        for c in cls.controls:
            y += (
                gfx.text_block(
                    surf, c, (cp.x + 26, y), cp.w - 52, 17, T.TEXT, spacing=1.25
                )
                + 8
            )

        mp = pygame.Rect(780, 506, 450, 144)
        gfx.panel(surf, mp, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, "MODE", (mp.x + 26, mp.y + 22), 14, col, bold=True)
        if self.ladder_kind == "daily":
            mode = (
                "Daily challenge: 10 puzzles from easy to beyond the real test's hardest item, with feedback "
                "after each. Only your first completed try today counts."
            )
            if self.daily_done:
                mode = (
                    f"You've already played today ({self.daily_done['solved']}/10). This run is practice "
                    "and won't change your result."
                )
        elif self.battery_pos is not None:
            mode = (
                "Test conditions: no feedback, exactly like the real assessment. Your result stays hidden "
                "until all ten subtests are complete."
            )
        elif self.app.profile.settings.get("feedback", True):
            mode = "Training: after every item you'll see the score it earned and the best answer."
        else:
            mode = "Test conditions: no feedback after items. Sample items are still explained."
        gfx.text_block(
            surf, mode, (mp.x + 26, mp.y + 52), mp.w - 52, 16, T.MUTED, spacing=1.25
        )
        if self.rated:
            gfx.text(
                surf,
                "10 puzzles matched to your rating",
                (self.rated.rect.centerx, self.rated.rect.bottom + 16),
                13,
                T.DIM,
                anchor="center",
            )
        super().draw(surf)


class SubtestResultScene(Scene):
    def __init__(self, app, cls, raw, scaled, best_before, details):
        super().__init__(app)
        sound.play("complete")
        self.cls = cls
        self.raw = raw
        self.scaled = scaled
        self.best_before = best_before
        self.details = details
        col = T.INDEX_COLORS[cls.index]
        self.buttons = [
            Button(
                (T.W // 2 - 260, T.H - 120, 240, 54),
                "Train again",
                lambda: app.start_practice(cls),
                col,
                hotkeys=(pygame.K_r,),
                primary=True,
            ),
            Button(
                (T.W // 2 + 20, T.H - 120, 240, 54),
                "Skill tree",
                app.to_menu,
                T.ACCENT,
                hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
            ),
        ]

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        c = (T.W // 2, 330)
        gfx.text(
            surf, cls.name.upper(), (c[0], 70), 16, col, bold=True, anchor="center"
        )
        if not self.app.profile.settings.get("show_scores", True):
            self._draw_hidden(surf, c, col)
            super().draw(surf)
            return
        filled = int(gfx.clamp((self.t - 0.4) * 14, 0, self.scaled))
        gfx.glow(surf, c, 260, col, 0.2 + 0.02 * filled)
        gfx.circle(surf, c, 112, gfx.lerp_color(T.PANEL, col, 0.12))
        gfx.pips(surf, c, 140, 18, 19, filled, col, ghost=self.best_before)
        gfx.text(
            surf, str(filled), (c[0], c[1] - 14), 92, T.TEXT, bold=True, anchor="center"
        )
        gfx.text(
            surf, "SCALED SCORE", (c[0], c[1] + 48), 13, col, bold=True, anchor="center"
        )
        if self.t > 0.4 + self.scaled / 14:
            label = scoring.scaled_label(self.scaled)
            gfx.text(
                surf, label, (c[0], c[1] + 190), 28, T.TEXT, bold=True, anchor="center"
            )
            pct = scoring.scaled_percentile(self.scaled)
            line = f"Raw {self.raw} / {cls.max_raw}   ·   ≈ {pct:.0f}th percentile   ·   mean is 10, SD 3"
            gfx.text(surf, line, (c[0], c[1] + 232), 18, T.MUTED, anchor="center")
            if self.scaled > self.best_before > 0:
                gfx.text(
                    surf,
                    "NEW PERSONAL BEST",
                    (c[0], c[1] + 268),
                    16,
                    T.GOLD,
                    bold=True,
                    anchor="center",
                )
            extra = self._extra()
            if extra:
                gfx.text(surf, extra, (c[0], c[1] + 296), 16, T.DIM, anchor="center")
        super().draw(surf)

    def _draw_hidden(self, surf, c, col):
        a = gfx.ease_out(self.t / 0.8)
        gfx.glow(surf, c, 240, col, 0.2 * a)
        gfx.circle(surf, c, 112, gfx.lerp_color(T.PANEL, col, 0.12))
        gfx.ring(surf, c, 140, 10, a, gfx.scale_color(col, 0.7))
        gfx.text(surf, "Done", (c[0], c[1] - 8), 56, T.TEXT, bold=True, anchor="center")
        gfx.text(
            surf,
            "SUBTEST COMPLETE",
            (c[0], c[1] + 40),
            13,
            col,
            bold=True,
            anchor="center",
        )
        gfx.text(
            surf,
            "Scores are hidden. You can show them in Settings.",
            (c[0], c[1] + 200),
            18,
            T.MUTED,
            anchor="center",
        )
        extra = self._extra()
        if extra:
            gfx.text(surf, extra, (c[0], c[1] + 236), 16, T.DIM, anchor="center")

    def _extra(self):
        d = self.details
        if "forward" in d:
            return f"Forward {d['forward']}  ·  Backward {d['backward']}  ·  Sequencing {d['sequencing']}"
        if "attempted" in d:
            return f"{d['correct']} correct  ·  {d['wrong']} incorrect  ·  {d['attempted']} attempted"
        if d.get("discontinued"):
            return (
                f"Stopped after {d['items']} items. Every subtest ends after a run of misses, "
                f"so everyone reaches that point."
            )
        if "items" in d:
            return f"{d['items']} items given, right to the end of the subtest"
        return ""


class BatteryResultScene(Scene):
    def __init__(self, app, scaled, raw, indexes, fsiq):
        super().__init__(app)
        sound.play("complete")
        self.tree = SkillTree(center=(475, 460), sx=0.82)
        self.scaled = scaled
        self.raw = raw
        self.indexes = indexes
        self.fsiq = fsiq
        self.best = {c: app.profile.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: app.profile.attempts(c) for c in BY_CODE}
        self.hover = None
        self.buttons = [
            Button(
                (T.W - 290, T.H - 100, 250, 54),
                "Skill tree",
                app.to_menu,
                T.GOLD,
                hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
                primary=True,
            )
        ]

    def update(self, dt):
        super().update(dt)
        self.hover = self.tree.hit(mouse_pos()) if self.tree.finished(self.t) else None

    def handle_event(self, e):
        if not self.tree.finished(self.t) and (
            e.type == pygame.MOUSEBUTTONDOWN or e.type == pygame.KEYDOWN
        ):
            self.t = 6.0  # skip the animation
            return True
        return super().handle_event(e)

    def draw(self, surf):
        gfx.text(surf, "ASSESSMENT COMPLETE", (40, 30), 30, T.TEXT, bold=True)
        gfx.text(surf, "Your skill constellation", (42, 70), 17, T.MUTED)
        hide = not self.app.profile.settings.get("show_scores", True)
        data = {
            "scaled": self.scaled,
            "best": self.best,
            "indexes": self.indexes,
            "fsiq": self.fsiq,
            "hide": hide,
        }
        self.tree.draw(surf, data, self.t, self.t, self.hover)

        p = pygame.Rect(T.W - 330, 120, 290, 520)
        a = gfx.ease_out((self.t - 5.0) / 0.8)
        if a > 0 and hide:
            gfx.panel(surf, p, T.PANEL, T.BORDER, radius=18, alpha=int(235 * a))
            x, y = p.x + 24, p.y + 22
            gfx.text(
                surf,
                "ALL TEN SUBTESTS DONE",
                (x, y),
                13,
                T.GOLD,
                bold=True,
                alpha=255 * a,
            )
            gfx.text_block(
                surf,
                "You finished a full assessment under real test conditions: no feedback, real "
                "time limits, real stopping rules. That's the whole experience.",
                (x, y + 30),
                p.w - 48,
                17,
                T.TEXT,
                spacing=1.3,
                alpha=255 * a,
            )
            gfx.text_block(
                surf,
                "Scores are hidden. Your results are saved, and you can show them any time in "
                "Settings.",
                (x, y + 210),
                p.w - 48,
                16,
                T.MUTED,
                spacing=1.3,
                alpha=255 * a,
            )
        elif a > 0:
            gfx.panel(surf, p, T.PANEL, T.BORDER, radius=18, alpha=int(235 * a))
            x, y = p.x + 24, p.y + 22
            gfx.text(
                surf, "FULL SCALE SCORE", (x, y), 13, T.GOLD, bold=True, alpha=255 * a
            )
            gfx.text(
                surf, str(self.fsiq), (x, y + 18), 64, T.TEXT, bold=True, alpha=255 * a
            )
            gfx.text(
                surf,
                scoring.classification(self.fsiq),
                (x, y + 96),
                20,
                T.GOLD,
                bold=True,
                alpha=255 * a,
            )
            gfx.text(
                surf,
                f"≈ {scoring.percentile(self.fsiq):.1f}th percentile",
                (x, y + 124),
                16,
                T.MUTED,
                alpha=255 * a,
            )
            y += 170
            for idx in ("VCI", "PRI", "WMI", "PSI"):
                v = self.indexes[idx]
                col = T.INDEX_COLORS[idx]
                gfx.text(surf, T.INDEX_NAMES[idx], (x, y), 15, T.TEXT, alpha=255 * a)
                gfx.text(
                    surf,
                    str(v),
                    (p.right - 24, y),
                    17,
                    col,
                    bold=True,
                    anchor="topright",
                    alpha=255 * a,
                )
                bar = pygame.Rect(x, y + 24, p.w - 48, 6)
                pygame.draw.rect(surf, T.TRACK, bar, border_radius=3)
                pygame.draw.rect(
                    surf,
                    col,
                    (bar.x, bar.y, bar.w * (v - 50) / 100 * a, 6),
                    border_radius=3,
                )
                mid = bar.x + bar.w // 2
                pygame.draw.line(
                    surf, T.MUTED, (mid, bar.y - 3), (mid, bar.bottom + 2), 1
                )
                y += 52
            gfx.text(
                surf,
                "NOT AN ACTUAL IQ TEST",
                (x, y + 6),
                13,
                T.PARTIAL,
                bold=True,
                alpha=255 * a,
            )
            gfx.text_block(
                surf,
                "Estimates use approximate norms made up for this game. They show trends in "
                "your training, not a real IQ.",
                (x, y + 28),
                p.w - 48,
                13,
                T.MUTED,
                alpha=255 * a,
            )
        super().draw(surf)
        if self.hover:
            tree_tooltip(
                surf,
                self.hover,
                mouse_pos(),
                self.scaled,
                self.raw,
                self.best,
                self.attempts,
                self.indexes,
                self.fsiq,
                hide,
            )
        if not self.tree.finished(self.t):
            gfx.text(surf, "click to skip", (475, 100), 13, T.DIM, anchor="center")


class PauseOverlay:
    def __init__(self, app):
        self.app = app
        cx = T.W // 2
        self.buttons = [
            Button(
                (cx - 140, 330, 280, 52),
                "Resume",
                app.resume,
                T.ACCENT,
                hotkeys=(pygame.K_ESCAPE,),
                primary=True,
            ),
            Button(
                (cx - 140, 394, 280, 52),
                "Restart subtest",
                app.restart_subtest,
                T.PARTIAL,
            ),
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
        gfx.text(
            surf, "Paused", (T.W // 2, 260), 44, T.TEXT, bold=True, anchor="center"
        )
        gfx.text(
            surf,
            "Timers are stopped (the real test can't be paused!)  ·  F11 toggles fullscreen",
            (T.W // 2, 300),
            16,
            T.MUTED,
            anchor="center",
        )
        for b in self.buttons:
            b.draw(surf)


class LadderResultScene(Scene):
    """End of a rated set or daily challenge."""

    def __init__(self, app, ladder, counted=False):
        super().__init__(app)
        sound.play("complete")
        self.ladder = ladder
        self.counted = counted
        self.status = ""
        cls = ladder.cls
        col = T.INDEX_COLORS[cls.index]
        home = Button(
            (T.W // 2 + 20, T.H - 110, 240, 54),
            "Skill tree",
            app.to_menu,
            T.ACCENT,
            hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
        )
        if ladder.kind == "rated":
            again = Button(
                (T.W // 2 - 260, T.H - 110, 240, 54),
                "Another set",
                lambda: app.begin_subtest(cls, "rated"),
                col,
                hotkeys=(pygame.K_r,),
                primary=True,
            )
        else:
            again = Button(
                (T.W // 2 - 260, T.H - 110, 240, 54),
                "Copy result",
                self._copy,
                col,
                hotkeys=(pygame.K_c,),
                primary=True,
            )
        self.buttons = [again, home]
        today = ladder.day if ladder.kind == "daily" else datetime.date.today()
        self.streak = app.profile.daily_streak(today)
        self.first = app.profile.daily_result(today) if ladder.kind == "daily" else None

    def _copy(self):
        text = self.ladder.share_text()
        try:
            ok = (
                web.copy_text(text)
                if web.IS_WEB
                else (pygame.scrap.put_text(text) or True)
            )
        except (pygame.error, AttributeError):
            ok = False
        self.status = (
            "Copied! Paste it anywhere to share."
            if ok
            else "Couldn't reach the clipboard."
        )

    def draw(self, surf):
        lad = self.ladder
        cls = lad.cls
        col = T.INDEX_COLORS[cls.index]
        c = (T.W // 2, 290)
        title = f"{lad.label()}  ·  {cls.name}".upper()
        gfx.text(surf, title, (c[0], 64), 16, col, bold=True, anchor="center")
        a = gfx.ease_out((self.t - 0.2) / 1.2)
        gfx.glow(surf, c, 250, col, 0.2)
        gfx.circle(surf, c, 104, gfx.lerp_color(T.PANEL, col, 0.12))
        if lad.kind == "rated":
            shown = lad.start + (lad.rating - lad.start) * a
            gfx.ring(
                surf, c, 132, 10, gfx.clamp((shown - FLOOR) / (2200 - FLOOR), 0, 1), col
            )
            gfx.text(
                surf,
                f"{shown:.0f}",
                (c[0], c[1] - 10),
                72,
                T.TEXT,
                bold=True,
                anchor="center",
            )
            gfx.text(
                surf,
                "PUZZLE RATING",
                (c[0], c[1] + 40),
                13,
                col,
                bold=True,
                anchor="center",
            )
            delta = round(lad.rating) - round(lad.start)
            if self.t > 1.4:
                dcol = T.GOOD if delta > 0 else T.BAD if delta < 0 else T.MUTED
                gfx.text(
                    surf,
                    f"{delta:+d}",
                    (c[0], c[1] + 172),
                    30,
                    dcol,
                    bold=True,
                    anchor="center",
                )
                peak = self.app.profile.rating(cls.code)
                info = f"{lad.solved} of {lad.length} solved  ·  {lad.played} puzzles played"
                if peak:
                    info += f"  ·  peak {peak['peak']:.0f}"
                gfx.text(surf, info, (c[0], c[1] + 212), 17, T.MUTED, anchor="center")
        else:
            filled = int(gfx.clamp(self.t * 8, 0, lad.solved))
            gfx.pips(surf, c, 132, 14, lad.length, filled, col)
            gfx.text(
                surf,
                f"{filled}/{lad.length}",
                (c[0], c[1] - 10),
                66,
                T.TEXT,
                bold=True,
                anchor="center",
            )
            gfx.text(
                surf, "SOLVED", (c[0], c[1] + 40), 13, col, bold=True, anchor="center"
            )
            if self.counted:
                info = (
                    f"Daily streak: {self.streak} day{'s' if self.streak != 1 else ''}"
                )
            else:
                info = (
                    f"Practice replay  ·  today's result was {self.first['solved']}/10"
                    if self.first
                    else ""
                )
            gfx.text(surf, info, (c[0], c[1] + 180), 18, T.MUTED, anchor="center")
            if self.status:
                gfx.text(
                    surf, self.status, (c[0], c[1] + 212), 16, T.GOOD, anchor="center"
                )
        # one square per puzzle, with its level underneath
        n = lad.length
        x0 = c[0] - (n * 46 - 10) / 2
        for i, (level, solved) in enumerate(lad.results):
            if self.t < 0.3 + i * 0.08:
                break
            r = pygame.Rect(x0 + i * 46, 548, 36, 36)
            gfx.panel(
                surf,
                r,
                gfx.lerp_color(T.PANEL, T.GOOD if solved else T.BAD, 0.7),
                T.GOOD if solved else T.BAD,
                radius=8,
            )
            gfx.text(
                surf, str(level), (r.centerx, r.bottom + 14), 13, T.DIM, anchor="center"
            )
        gfx.text(
            surf,
            "difficulty level of each puzzle",
            (c[0], 620),
            12,
            T.DIM,
            anchor="center",
        )
        super().draw(surf)


class LearnScene(Scene):
    """How the WAIS works, what a session is like, how to read scores. With ``then`` it shows one
    topic as a walkthrough whose last page continues to ``then``."""

    def __init__(self, app, topic=None, then=None):
        super().__init__(app)
        self.then = then
        keys = [k for k, _, _ in TOPICS]
        self.ti = keys.index(topic) if topic in keys else 0
        self.page = 0
        self.nav = []
        if then is None:
            for i, (_, title, _) in enumerate(TOPICS):
                b = Button(
                    (40, 150 + i * 58, 250, 46),
                    title,
                    lambda i=i: self._select(i),
                    T.ACCENT,
                    size=16,
                )
                self.nav.append(b)
        self.panel = pygame.Rect(320, 130, T.W - 360, 560)
        if then:
            self.panel = pygame.Rect(180, 130, T.W - 360, 560)
        pr = self.panel
        self.prev_btn = Button(
            (pr.x + 30, pr.bottom - 70, 150, 46),
            "Previous",
            self._prev,
            T.ACCENT,
            hotkeys=(pygame.K_LEFT,),
            size=16,
        )
        self.next_btn = Button(
            (pr.right - 260, pr.bottom - 70, 230, 46),
            "Next",
            self._next,
            T.ACCENT,
            hotkeys=(pygame.K_RIGHT, pygame.K_RETURN),
            primary=True,
            size=16,
        )
        back = Button(
            (40, T.H - 84, 200, 46),
            "Skip" if then else "Back",
            self._leave,
            T.MUTED,
            hotkeys=(pygame.K_ESCAPE,),
            size=16,
        )
        self.buttons = self.nav + [self.prev_btn, self.next_btn, back]

    @property
    def pages(self):
        return TOPICS[self.ti][2]

    def _select(self, i):
        self.ti, self.page = i, 0

    def _prev(self):
        if self.page > 0:
            self.page -= 1
        elif self.then is None and self.ti > 0:
            self.ti -= 1
            self.page = len(self.pages) - 1

    def _next(self):
        if self.page < len(self.pages) - 1:
            self.page += 1
        elif self.then:
            self.then()
        elif self.ti < len(TOPICS) - 1:
            self._select(self.ti + 1)

    def _leave(self):
        if self.then:
            self.then()
        else:
            self.app.to_menu()

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if (
            self.then is None
            and e.type == pygame.KEYDOWN
            and e.key in (pygame.K_UP, pygame.K_DOWN)
        ):
            self._select(
                (self.ti + (1 if e.key == pygame.K_DOWN else -1)) % len(TOPICS)
            )
            return True
        return False

    def update(self, dt):
        super().update(dt)
        for i, b in enumerate(self.nav):
            b.primary = i == self.ti
        last = self.page == len(self.pages) - 1
        self.prev_btn.enabled = self.page > 0 or (self.then is None and self.ti > 0)
        if self.then:
            self.next_btn.label = "Start the assessment" if last else "Next"
            self.next_btn.accent = T.GOLD if last else T.ACCENT
        else:
            self.next_btn.label = "Next topic" if last else "Next"
            self.next_btn.enabled = not (last and self.ti == len(TOPICS) - 1)

    @staticmethod
    def layout_page(paras, p, surf=None):
        """Draw (or, without a surface, just measure) a page's paragraphs; returns the bottom y.
        Must stay above ``p.bottom - 80``, where the page buttons are."""
        y = p.y + 84
        w = p.w - 80
        lh = int(T.font(17).get_linesize() * 1.3)
        for para in paras:
            if para.startswith("## "):
                y += 4
                if surf:
                    gfx.text(surf, para[3:], (p.x + 40, y), 15, T.ACCENT, bold=True)
                y += 24
            elif surf:
                y += (
                    gfx.text_block(
                        surf, para, (p.x + 40, y), w, 17, T.TEXT, spacing=1.3
                    )
                    + 12
                )
            else:
                y += lh * len(gfx.wrap(para, 17, w)) + 12
        return y

    def draw(self, surf):
        if self.then:
            gfx.text(
                surf,
                "BEFORE YOUR FIRST FULL ASSESSMENT",
                (180, 34),
                30,
                T.TEXT,
                bold=True,
            )
            gfx.text(
                surf,
                "A quick look at what a real session is like. Skip whenever you like.",
                (182, 76),
                17,
                T.MUTED,
            )
        else:
            gfx.text(surf, "LEARN", (40, 30), 34, T.TEXT, bold=True)
            gfx.text(
                surf,
                "How the WAIS works, what a session is like, and how to read the scores",
                (42, 74),
                17,
                T.MUTED,
            )
        p = self.panel
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        title, paras = self.pages[self.page]
        gfx.text(surf, title, (p.x + 40, p.y + 30), 28, T.TEXT, bold=True)
        self.layout_page(paras, p, surf)
        n = len(self.pages)
        if n > 1:
            for i in range(n):
                gfx.circle(
                    surf,
                    (p.centerx - (n - 1) * 9 + i * 18, p.bottom - 47),
                    4,
                    T.ACCENT if i == self.page else T.TRACK,
                )
        super().draw(surf)


VOLUMES = (0.0, 0.25, 0.5, 0.75, 1.0)


class SettingsScene(Scene):
    ROW = 100

    def __init__(self, app):
        super().__init__(app)
        s = app.profile.settings
        n = len(sound.tracks())
        if not sound.available():
            music_desc = "No audio device was found."
        elif n:
            music_desc = (
                f"Plays the {n} track{'s' if n != 1 else ''} in your music folder on a shuffled loop. "
                "It turns down while digits are read out."
            )
        else:
            music_desc = (
                "Put your own mp3, ogg or wav files in the puzzleth/music folder"
                + ("." if web.IS_WEB else " or ~/.puzzleth/music.")
                + " None found yet."
            )
        self.rows = [
            (
                "Feedback while training",
                "After each item, show how it was scored and the best answer. The full assessment never gives "
                "feedback, just like the real test.",
                lambda: s.get("feedback", True),
                lambda: self._flip("feedback"),
                ("On", "Off"),
            ),
            (
                "Test-style scores",
                "Show scaled scores, index scores and the Full Scale Score. Hide them to practise without a number. "
                "Puzzle ratings and daily results still show.",
                lambda: s.get("show_scores", True),
                lambda: self._flip("show_scores"),
                ("Shown", "Hidden"),
            ),
            (
                "Sound effects",
                "Clicks, timer ticks and the spoken digits in Digit Span. Right/wrong chimes only play when "
                "feedback is shown."
                if sound.available()
                else "No audio device was found.",
                lambda: s["sfx_volume"],
                lambda: self._volume("sfx_volume"),
                _volume_label,
            ),
            (
                "Music",
                music_desc,
                lambda: s["music_volume"],
                lambda: self._volume("music_volume"),
                _volume_label,
            ),
            (
                "Fullscreen  (F11)",
                "Use your browser's menu to go fullscreen, or add Puzzleth to your home screen."
                if web.IS_WEB
                else "Fill the whole screen. In a window, the game scales to any size you like.",
                lambda: app.fullscreen,
                app.toggle_fullscreen,
                ("On", "Off"),
            ),
        ]
        self.panel = pygame.Rect(
            T.W // 2 - 420, 118, 840, 16 + len(self.rows) * self.ROW
        )
        self.toggles = []
        for i, row in enumerate(self.rows):
            b = Button(
                (self.panel.right - 190, self.panel.y + 30 + i * self.ROW, 150, 48),
                "",
                row[3],
                T.ACCENT,
                size=17,
            )
            self.toggles.append(b)
        self.toggles[2].enabled = self.toggles[3].enabled = sound.available()
        self.toggles[4].enabled = app.display is not None
        back = Button(
            (T.W // 2 - 110, T.H - 120, 220, 52),
            "Done",
            app.to_menu,
            T.ACCENT,
            hotkeys=(pygame.K_ESCAPE, pygame.K_RETURN),
            primary=True,
        )
        self.buttons = self.toggles + [back]

    def _flip(self, key):
        s = self.app.profile.settings
        s[key] = not s.get(key, True)
        self.app.profile.save()

    def _volume(self, key):
        s = self.app.profile.settings
        s[key] = next((v for v in VOLUMES if v > s[key] + 0.01), 0.0)
        sound.set_volumes(s["sfx_volume"], s["music_volume"])
        self.app.profile.save()

    def update(self, dt):
        super().update(dt)
        for b, row in zip(self.toggles, self.rows):
            on = row[2]()
            labels = row[4]
            b.label = labels(on) if callable(labels) else labels[0] if on else labels[1]
            b.primary = bool(on)

    def draw(self, surf):
        gfx.text(surf, "SETTINGS", (40, 30), 34, T.TEXT, bold=True)
        p = self.panel
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        for i, (title, desc, *_rest) in enumerate(self.rows):
            y = p.y + 26 + i * self.ROW
            if i:
                pygame.draw.line(
                    surf, T.BORDER, (p.x + 30, y - 18), (p.right - 30, y - 18), 1
                )
            gfx.text(surf, title, (p.x + 40, y), 20, T.TEXT, bold=True)
            gfx.text_block(
                surf, desc, (p.x + 40, y + 30), p.w - 300, 15, T.MUTED, spacing=1.3
            )
        super().draw(surf)


def _volume_label(v):
    return f"{round(v * 100)}%" if v > 0 else "Off"
