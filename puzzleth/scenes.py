"""Menu, subtest briefing, results, learn, settings and pause screens."""

import datetime

import pygame

from . import gfx, i18n, online, scoring, sound, version_label, web
from . import theme as T
from .challenge import FLOOR, SET_LENGTH, daily_number
from .content import learn
from .display import mouse_pos
from .skilltree import SkillTree
from .storage import CODE_CHARS, MAX_PLAYERS, NAME_CHARS, NAME_LEN
from .subtests import BY_CODE, ORDER
from .widgets import Button

# Your donation page, e.g. "https://ko-fi.com/yourname". The menu shows a Donate button once it's set.
DONATE_URL = "https://ko-fi.com/n0va"
# What the online leaderboard sends and keeps, published beside the web version (tools/web/privacy.html).
PRIVACY_URL = "https://puzzleth.github.io/Puzzleth/privacy.html"


def _tooltip(surf, pos, title, lines, color):
    w = 330
    # Wrap each line to the box width, keeping the first line's highlight colour.
    rows = [
        (part, T.TEXT if i == 0 else T.MUTED)
        for i, line in enumerate(lines)
        for part in gfx.wrap(line, 15, w - 32)
    ]
    lh = max(22, T.font(15).get_linesize())
    h = 46 + lh * len(rows)
    x = min(T.W - w - 16, pos[0] + 18)
    y = min(T.H - h - 16, pos[1] + 18)
    rect = pygame.Rect(x, y, w, h)
    gfx.panel(surf, rect, T.PANEL, color, radius=12, alpha=248)
    gfx.text(surf, title, (x + 16, y + 12), 17, color, bold=True)
    for i, (line, col) in enumerate(rows):
        gfx.text(surf, line, (x + 16, y + 40 + i * lh), 15, col)


def _grade_line(letter):
    return i18n.f("Grade {grade}  ·  {label}", grade=letter, label=i18n._(scoring.grade_name(letter)))


def tree_tooltip(
    surf, key, pos, scaled, raw, best, attempts, indexes, overall, hide=False, ratings=None
):
    ratings = ratings or {}
    if key in BY_CODE:
        cls = BY_CODE[key]
        col = T.INDEX_COLORS[cls.index]
        lines = [cls.measures]
        s = scaled.get(key)
        tries = i18n.n(attempts.get(key, 0), "{n} attempt", "{n} attempts")
        if s and hide:
            lines.append(i18n.f("Measured  ·  scores hidden  ·  {attempts}", attempts=tries))
        elif s:
            lines.append(_grade_line(scoring.grade(s)))
            lines.append(i18n.n(s, "{n} skill point of 19", "{n} skill points of 19") + (
                i18n.f("  ·  raw {raw} / {max}", raw=raw[key], max=cls.max_raw) if raw.get(key) is not None else ""
            ))
        else:
            lines.append("Not yet measured")
        if best.get(key) and not hide:
            lines.append(i18n.f("Personal best {grade}  ·  {attempts}", grade=scoring.grade(best[key]), attempts=tries))
        if getattr(cls, "challenge", False):
            r = ratings.get(key)
            lines.append(
                i18n.f("Puzzle rating {rating}  ·  peak {peak}", rating=round(r["rating"]), peak=round(r["peak"]))
                if r
                else "Rated puzzle sets available"
            )
        _tooltip(surf, pos, f"{i18n._(cls.name)}  ({i18n.abbr(cls.index)})", lines, col)
    elif key in scoring.INDEX_SUBTESTS:
        col = T.INDEX_COLORS[key]
        names = ", ".join(i18n._(BY_CODE[c].name) for c in scoring.INDEX_SUBTESTS[key])
        lines = [names]
        if key in indexes and hide:
            lines.append("Measured  ·  scores hidden")
        elif key in indexes:
            lines.append(_grade_line(scoring.composite_grade(indexes[key])))
        else:
            lines.append("Complete all of its subtests to grade it")
        _tooltip(surf, pos, T.INDEX_NAMES[key], lines, col)
    elif key == "GS":
        lines = ["Combines all ten subtests"]
        if overall and hide:
            lines.append("Measured  ·  scores hidden")
        elif overall:
            lines += [_grade_line(scoring.composite_grade(overall)), "Grades run from D up to S",
                      "A training estimate, not a clinical result"]
        else:
            lines.append("Take the full assessment to grade it")
        _tooltip(surf, pos, "Grade Score", lines, T.GOLD)


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
    "Puzzleth is a training game modelled on the structure and rules of real one-to-one cognitive "
    "assessments. It uses none of their items and is not affiliated with or endorsed by any test publisher.",
    "Its grades come from rough standards made up for this game, not from a standardised sample of people. "
    "They cannot be compared with the results of a real assessment.",
    "It cannot diagnose anything and must not be used for school, work, legal or medical decisions. "
    "Only a standardised assessment given by a qualified psychologist can do that.",
    "Practising test formats can raise scores on a real test. If you take a clinical assessment, tell "
    "the examiner you have practised.",
]


class LanguageScene(Scene):
    """First-run language choice, before any game content is shown."""

    def __init__(self, app, done=None):
        super().__init__(app)
        self.app = app
        self.done = done
        self.buttons = []
        y = T.H // 2 - 20
        for code, name in i18n.LANGUAGES:
            self.buttons.append(Button(
                (T.W // 2 - 200, y, 400, 56), name,
                lambda code=code: self._choose(code), T.ACCENT, size=20,
            ))
            y += 70

    def _choose(self, code):
        self.app.profile.settings["language"] = code
        self.app.profile.save()
        self.app._language_chosen(code, self.done)

    def draw(self, surf):
        # every language at once: nothing is chosen yet
        y = T.H // 2 - 250
        for code, _ in i18n.LANGUAGES:
            gfx.text(surf, i18n.translate("Choose your language", code), (T.W // 2, y), 28, T.TEXT, bold=True,
                     anchor="center", translate=False)
            y += 40
        if self.done:   # from Settings
            hint = "You can change it again any time in Settings."
        else:
            hint = "The game will use this language. You can change it later in Settings."
        gfx.text(surf, hint, (T.W // 2, T.H // 2 + 3 * 70), gfx.fit_width(hint, 16, T.W - 80), T.MUTED,
                 anchor="center")
        super().draw(surf)


class DisclaimerScene(Scene):
    """Shown on first launch (must be acknowledged) and from the menu's About button."""

    def __init__(self, app):
        super().__init__(app)
        self.first = not app.profile.settings.get("disclaimer_seen")
        label = "I understand" if self.first else "Back"
        self.ok = Button(
            (T.W // 2 - 125, T.H - 82 if T.compact else 620, 250, 54),
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
        if T.compact:
            p = pygame.Rect(0, 0, 1180, T.H - 120)
            p.midtop = (T.W // 2, 20)
        elif T.large_text:
            p = pygame.Rect(0, 0, 1040, 550)
            p.center = (T.W // 2, 335)
        else:
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
            "This is not a psychological test",
            (p.centerx, p.y + 78),
            34,
            T.TEXT,
            bold=True,
            anchor="center",
        )
        y = p.y + 130
        size = gfx.fit_size(
            17,
            lambda k: gfx.block_height(DISCLAIMER, p.w - 120, k, spacing=1.25, gap=16)
            <= p.bottom - 12 - y,
        )
        for para in DISCLAIMER:
            gfx.circle(surf, (p.x + 52, y + 11), 3, T.GOLD)
            y += (
                gfx.text_block(
                    surf, para, (p.x + 68, y), p.w - 120, size, T.TEXT, spacing=1.25
                )
                + 16
            )
        super().draw(surf)


def _spread(buttons, left, right, y, h, gap=10):
    """Lay buttons out in a row from ``left`` to ``right``, each as wide as its label needs, so that
    any shrinking to fit is shared out evenly."""
    widest = {"Daily": i18n.f("Daily  {solved}/10", solved=10)}   # its label grows once today's challenge is played
    need = [T.font(b.size, True).size(i18n._(widest.get(b.label, b.label)))[0] + 32 for b in buttons]
    room = right - left - gap * (len(buttons) - 1)
    x = left
    for b, n in zip(buttons, need):
        w = n * room // sum(need)
        b.rect.update(x, y, w, h)
        x += w + gap


class MenuScene(Scene):
    def __init__(self, app):
        super().__init__(app)
        self.tree = SkillTree((T.W // 2, 315), layout="compact") if T.compact else SkillTree()
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
        name = app.profile.current or ""
        title_w = T.font(34, True).size("PUZZLETH")[0]
        self.player_btn = Button(
            (40 + title_w + 28, 32, max(140, T.font(17, True).size(name)[0] + 48), 40),
            name,
            app.open_players,
            T.ACCENT,
            hotkeys=(pygame.K_p,),
            size=17,
            translate=False,
        )
        if T.compact:   # all in one row at the top, the small ones along the bottom
            self.begin.rect.update(T.W - 830, 12, 310, 48)
            for i, b in enumerate((self.daily_btn, self.learn_btn, self.settings_btn)):
                b.rect.update(T.W - 510 + i * 160, 12, 150, 48)
            for b in (self.about_btn, self.quit_btn):
                b.rect.y = T.H - 50
            self.player_btn.rect.y = 14
        elif T.large_text:   # room for the bigger labels
            self.begin.rect.update(T.W - 480, 30, 310, 54)
            self.learn_btn.rect.update(T.W - 480, 94, 210, 44)
            self.settings_btn.rect.update(T.W - 250, 94, 210, 44)
        self.buttons = [
            self.player_btn,
            self.begin,
            self.daily_btn,
            self.learn_btn,
            self.settings_btn,
            self.about_btn,
            self.quit_btn,
        ]
        if online.enabled():   # Leaderboard goes between Learn and Settings
            self.board_btn = Button((0, 0, 0, 0), "Leaderboard", app.open_leaderboard, T.GOLD,
                                    hotkeys=(pygame.K_b,), size=15)
            self.buttons.insert(4, self.board_btn)
            if T.compact:
                row = (self.begin, self.daily_btn, self.learn_btn, self.board_btn, self.settings_btn)
            else:
                row = (self.learn_btn, self.board_btn, self.settings_btn)
            _spread(row, row[0].rect.x, T.W - 40, row[0].rect.y, row[0].rect.h)
        if web.IS_WEB:  # a browser tab is closed, not quit
            self.buttons.remove(self.quit_btn)
            self.about_btn.rect.x = self.quit_btn.rect.right - self.about_btn.rect.w
        if DONATE_URL:
            self.donate_btn = Button(
                (40, T.H - (50 if T.compact else 58), 190 if T.large_text else 170, 36),
                "Support Development",
                lambda: web.open_url(DONATE_URL),
                T.GOLD,
                size=14,
            )
            self.buttons.append(self.donate_btn)
        corner = max(b.rect.right for b in (self.about_btn, self.quit_btn) if b in self.buttons)
        self.update_btn = Button((corner - 190, self.about_btn.rect.y - 48, 190, 38), "Update available",
                                 web.load_update, T.GOLD, primary=True, size=15)
        if web.update_ready():
            self.buttons.append(self.update_btn)
        self._refresh()

    def _refresh(self):
        p = self.app.profile
        self.scaled = {c: p.last_scaled(c) for c in BY_CODE if p.last_scaled(c)}
        self.raw = {c: p.last_raw(c) for c in BY_CODE}
        self.best = {c: p.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: p.attempts(c) for c in BY_CODE}
        self.indexes, self.overall = scoring.compute_indexes(self.scaled)
        self.ratings = {c: p.rating(c) for c in BY_CODE if p.rating(c)}
        today = datetime.date.today()
        done = p.daily_result(today)
        self.daily_btn.label = i18n.f("Daily  {solved}/10", solved=done["solved"]) if done else "Daily"
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
        if self.update_btn not in self.buttons and int(self.t + dt) != int(self.t) and web.update_ready():
            self.buttons.append(self.update_btn)   # a newer web build is out: offer it instead of the version
        super().update(dt)
        self.hover = self.tree.hit(mouse_pos())

    def draw(self, surf):
        n = len(self.scaled)
        if self.app.touch:
            line = i18n.f("{n} / 10 skills measured  ·  tap any node to train it", n=n)
        else:
            line = i18n.f("{n} / 10 skills measured  ·  click any node to train it", n=n)
        if self.streak:
            line += i18n.f("  ·  daily streak {streak}", streak=self.streak)
        if T.compact:   # the tree needs the room of the subtitle
            gfx.text(surf, "PUZZLETH", (40, 14), 34, T.TEXT, bold=True)
            gfx.text(surf, line, (42, 64), gfx.fit_width(line, 15, self.begin.rect.x - 60), T.DIM)
        else:
            gfx.text(surf, "PUZZLETH", (40, 30), 34, T.TEXT, bold=True)
            gfx.text(surf, "Cognitive puzzle training", (42, 74), 17, T.MUTED)
            gfx.text(surf, line, (42, 100), 15, T.DIM)
        hide = not self.app.profile.settings.get("show_scores", True)
        data = {
            "scaled": self.scaled,
            "best": self.best,
            "indexes": self.indexes,
            "overall": self.overall,
            "hide": hide,
        }
        self.tree.draw(surf, data, self.t, None, self.hover)
        footer = "Not a psychological test. Grades are training estimates, not clinical results."
        gfx.text(
            surf,
            footer,
            (T.W // 2, T.H - 22 if T.compact else T.H - 26),
            gfx.fit_width(footer, 14, 560),   # clear of the Digit Span and Coding labels
            T.DIM,
            anchor="center",
        )
        if self.update_btn not in self.buttons:
            gfx.text(surf, version_label(), (self.update_btn.rect.right, self.about_btn.rect.y - 8), 13, T.DIM,
                     bold=True, anchor="bottomright")
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
                self.overall,
                hide,
                self.ratings,
            )


class NameEntryScene(Scene):
    """Arcade-style name entry: type, tap the letter board, or pick each letter with Up/Down and
    lock it in with Right. Shown before the first game and for each new player."""

    CHARS = NAME_CHARS
    LENGTH = NAME_LEN
    GROUP = None   # slots are drawn in groups of this many
    BOARD = [NAME_CHARS[i:i + 10] for i in range(0, 30, 10)] + [list(NAME_CHARS[30:]) + ["Del", "OK"]]

    def __init__(self, app):
        super().__init__(app)
        self.first = app.profile.current is None
        self.value = ""
        self.pick = None   # index into CHARS of the letter being picked with Up/Down
        self.error = None
        self.flash = {}
        self.slots_y = 158 if T.compact else 250
        key_w, key_h, gap = 76, 58, 10
        top = 250 if T.compact else 360
        x0 = T.W // 2 - (10 * key_w + 9 * gap) // 2
        self.keys = []
        for r, row in enumerate(self.BOARD):
            x = x0
            for label in row:
                w = key_w if len(label) == 1 else 2 * key_w + gap
                self.keys.append((label, pygame.Rect(x, top + r * (key_h + gap), w, key_h)))
                x += w + gap
        self._add_buttons()

    def _add_buttons(self):
        if online.enabled():   # bring a player over from another device instead
            self.buttons.append(Button((40, 14, 240, 52), "Restore a player", self.app.open_restore, T.ACCENT))
        if not self.first:
            self.buttons.append(Button((T.W - 260, 14, 220, 52), "Cancel", self.app.open_players, T.MUTED,
                                       hotkeys=(pygame.K_ESCAPE,)))
        if not T.compact:   # side by side under the letter board
            w = sum(b.rect.w for b in self.buttons) + 20 * (len(self.buttons) - 1)
            x = T.W // 2 - w // 2
            for b in self.buttons:
                b.rect.topleft = (x, T.H - 112)
                x += b.rect.w + 20

    def _type(self, ch):
        if len(self.value) < self.LENGTH:
            self.value += ch
            sound.play("key")
        self.pick = None
        self.error = None

    def _delete(self):
        if self.pick is not None:
            self.pick = None
        elif self.value:
            self.value = self.value[:-1]
            sound.play("key")
        self.error = None

    def _cycle(self, step):
        if len(self.value) >= self.LENGTH:
            return
        if self.pick is None:   # step on from the letter before (from A on an empty name)
            self.pick = self.CHARS.find(self.value[-1]) if self.value else -1 if step > 0 else 0
        self.pick = (self.pick + step) % len(self.CHARS)
        sound.play("tick")
        self.error = None

    def _submit(self):
        if self.pick is not None:
            self._type(self.CHARS[self.pick])
        self.error = self.app.profile.can_add(self.value)
        if self.error:
            sound.play("wrong")
            return
        self.app.profile.add_player(self.value)
        sound.play("submit")
        self.app.to_menu()

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for label, r in self.keys:
                if r.collidepoint(e.pos):
                    self.flash[label] = 1.0
                    if label == "OK":
                        self._submit()
                    elif label == "Del":
                        self._delete()
                    else:
                        self._type(label)
                    return True
        if e.type != pygame.KEYDOWN:
            return False
        if e.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit()
        elif e.key in (pygame.K_BACKSPACE, pygame.K_LEFT):
            self._delete()
        elif e.key == pygame.K_UP:
            self._cycle(1)
        elif e.key == pygame.K_DOWN:
            self._cycle(-1)
        elif e.key in (pygame.K_RIGHT, pygame.K_SPACE):
            if self.pick is not None:
                self._type(self.CHARS[self.pick])
        elif e.unicode and e.unicode.upper() in self.CHARS:
            self._type(e.unicode.upper())
        else:
            return False
        return True

    def update(self, dt):
        super().update(dt)
        for k in list(self.flash):
            self.flash[k] -= dt * 5
            if self.flash[k] <= 0:
                del self.flash[k]

    def _texts(self):
        """The heading, the line under it, and the hint under the slots."""
        if not self.first:
            sub = "A new player starts with fresh progress and their own settings."
        elif self.app.profile.data["subtests"] or self.app.profile.data["daily"]:
            sub = "Your progress so far will be kept under this name."
        else:
            sub = "Your progress is saved under this name. Everyone else can add their own."
        if self.app.touch:
            hint = "Tap the letters, then OK"
        else:
            hint = "Type your name, or pick each letter with Up/Down and lock it in with Right"
        return "ENTER YOUR NAME", sub, hint

    def draw(self, surf):
        cx = T.W // 2
        heading_y, sub_y = (40, 84) if T.compact else (90, 146)
        heading, sub, hint = self._texts()
        gfx.text(surf, heading, (cx, heading_y), 40, T.TEXT, bold=True, anchor="center")
        gfx.text(surf, sub, (cx, sub_y), gfx.fit_width(sub, 17, 1100), T.MUTED, anchor="center")

        slot_w, slot_h, gap = 72, 88, 14
        group_gap = 24 if self.GROUP else 0
        groups = (self.LENGTH - 1) // self.GROUP if self.GROUP else 0
        x0 = cx - (self.LENGTH * slot_w + (self.LENGTH - 1) * gap + groups * group_gap) // 2
        for i in range(self.LENGTH):
            x = x0 + i * (slot_w + gap) + (i // self.GROUP * group_gap if self.GROUP else 0)
            r = pygame.Rect(x, self.slots_y - slot_h // 2, slot_w, slot_h)
            filled = i < len(self.value)
            active = i == len(self.value)
            border = T.ACCENT if filled or active else T.BORDER
            if active:
                gfx.glow(surf, r.center, slot_w, T.ACCENT, 0.18)
            gfx.panel(surf, r, gfx.lerp_color(T.PANEL, T.ACCENT, 0.12 if filled else 0), border, radius=12,
                      border_w=2 if active else 1)
            if filled:
                gfx.text(surf, self.value[i], r.center, 52, T.TEXT, bold=True, mono=True, anchor="center",
                         translate=False)
            elif active and self.pick is not None:
                gfx.text(surf, self.CHARS[self.pick], r.center, 52, T.ACCENT, bold=True, mono=True, anchor="center")
            elif active and int(self.t * 2) % 2 == 0:
                pygame.draw.rect(surf, T.ACCENT, (r.centerx - 16, r.bottom - 18, 32, 4), border_radius=2)
        line, col = (self.error, T.BAD) if self.error else (hint, T.DIM)
        gfx.text(surf, line, (cx, self.slots_y + slot_h // 2 + 26), gfx.fit_width(line, 15, 1000), col,
                 bold=self.error is not None, anchor="center")

        hover = mouse_pos()
        for label, r in self.keys:
            f = self.flash.get(label, 0)
            ok = label == "OK"
            h = 0.12 if r.collidepoint(hover) else 0
            fill = gfx.lerp_color(gfx.lerp_color(T.PANEL, T.ACCENT, (0.25 if ok else 0.06) + h), T.ACCENT, 0.5 * f)
            gfx.panel(surf, r, fill, T.ACCENT if ok else T.BORDER, radius=12)
            gfx.text(surf, label, r.center, 26 if len(label) == 1 else 19, T.TEXT, bold=True,
                     mono=len(label) == 1, anchor="center")
        super().draw(surf)


class RestoreScene(NameEntryScene):
    """Bring a player over from another device: enter their recovery code (see RecoveryCodeScene)."""

    CHARS = CODE_CHARS
    LENGTH = 12
    GROUP = 4
    BOARD = [CODE_CHARS[i:i + 10] for i in range(0, 30, 10)] + [list(CODE_CHARS[30:]) + ["Del", "OK"]]

    def __init__(self, app):
        self.busy = False
        super().__init__(app)

    def _add_buttons(self):
        back = self.app.open_players if self.app.profile.current else self.app.to_menu
        rect = (T.W - 260, 14, 220, 52) if T.compact else (T.W // 2 - 110, T.H - 112, 220, 52)
        self.buttons = [Button(rect, "Back", back, T.MUTED, hotkeys=(pygame.K_ESCAPE,))]

    def handle_event(self, e):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_v and e.mod & (pygame.KMOD_CTRL | pygame.KMOD_META):
            self._paste()
            return True
        return super().handle_event(e)

    def _paste(self):
        try:
            text = pygame.scrap.get_text() if not web.IS_WEB else ""
        except (pygame.error, AttributeError):
            text = ""
        code = "".join(c for c in (text or "").upper() if c in self.CHARS)[:self.LENGTH]
        if code:
            self.value, self.pick, self.error = code, None, None
            sound.play("key")

    def _submit(self):
        if self.busy:
            return
        if self.pick is not None:
            self._type(self.CHARS[self.pick])
        if len(self.value) < self.LENGTH:
            self.error = i18n.f("Enter all {n} characters of the code", n=self.LENGTH)
            sound.play("wrong")
            return
        self.busy = True
        self.error = None

        def done(why):
            self.busy = False
            if why:
                self.error = why
                sound.play("wrong")
            else:
                sound.play("submit")
                if self.app.scene is self:
                    self.app.to_menu()

        code = "-".join(self.value[i:i + self.GROUP] for i in range(0, self.LENGTH, self.GROUP))
        self.app.online.restore(code, done)

    def _texts(self):
        sub = "Enter the recovery code from Leaderboard > Move to another device on your other device."
        if self.busy:
            hint = "Restoring…"
        elif self.app.touch:
            hint = "Tap the characters, then OK"
        else:
            hint = "Type or paste the code, then press Enter"
        return "RESTORE A PLAYER", sub, hint


def _last_played(ts):
    if not ts:
        return "Not played yet"
    days = (datetime.date.today() - datetime.date.fromtimestamp(ts)).days
    if days <= 0:
        return "Last played today"
    if days == 1:
        return "Last played yesterday"
    return i18n.n(days, "Last played {n} day ago", "Last played {n} days ago")


class PlayersScene(Scene):
    """Who's playing: pick your name, add a new player, or remove one."""

    def __init__(self, app):
        super().__init__(app)
        self.removing = False
        self.armed = None   # the player a second tap removes
        p = app.profile
        self.names = p.players()
        card_w, card_h, step, top = (560, 82, 96, 102) if T.compact else (560, 96, 112, 140)
        self.cards = []
        for i, name in enumerate(self.names):
            col, row = i % 2, i // 2
            r = pygame.Rect(T.W // 2 - card_w - 10 + col * (card_w + 20), top + row * step, card_w, card_h)
            self.cards.append((name, r))
        y = (T.H - 86) if T.compact else 620
        self.new_btn = Button((T.W // 2 - 350, y, 220, 52), "New player", app.new_player, T.ACCENT,
                              hotkeys=(pygame.K_n,), primary=True)
        self.new_btn.enabled = len(self.names) < MAX_PLAYERS
        self.remove_btn = Button((T.W // 2 - 110, y, 220, 52), "Remove…", self._toggle_remove, T.BAD)
        self.remove_btn.enabled = bool(self.names)
        back = (T.W - 260, 14, 220, 52) if T.compact else (T.W // 2 + 130, y, 220, 52)
        self.back_btn = Button(back, "Back", app.to_menu, T.ACCENT, hotkeys=(pygame.K_ESCAPE,))
        self.back_btn.enabled = p.current is not None
        self.buttons = [self.new_btn, self.remove_btn, self.back_btn]
        if online.enabled():   # a player from another device
            self.restore_btn = Button((0, 0, 0, 0), "Restore…", app.open_restore, T.ACCENT, hotkeys=(pygame.K_r,))
            self.restore_btn.enabled = self.new_btn.enabled
            self.buttons.insert(1, self.restore_btn)
            row = [b for b in self.buttons if b is not self.back_btn or not T.compact]
            w = 220 if T.compact else 200
            x = T.W // 2 - (len(row) * (w + 20) - 20) // 2
            for b in row:
                b.rect.update(x, y, w, 52)
                x += w + 20

    def _toggle_remove(self):
        self.removing = not self.removing
        self.armed = None
        self.remove_btn.label = "Done removing" if self.removing else "Remove…"
        self.remove_btn.primary = self.removing

    def _choose(self, name):
        if not self.removing:
            sound.play("select")
            self.app.profile.switch(name)
            self.app.player_changed()
            self.app.to_menu()
        elif self.armed != name:
            sound.play("tap")
            self.armed = name
        else:
            sound.play("wrong")
            self.app.profile.remove_player(name)
            self.app.player_changed()
            if self.app.profile.players():
                self.app.goto(PlayersScene(self.app))
            else:
                self.app.to_menu()   # nobody left: enter a new name

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for name, r in self.cards:
                if r.collidepoint(e.pos):
                    self._choose(name)
                    return True
            if self.removing:
                self.armed = None
        elif e.type == pygame.KEYDOWN and e.key == pygame.K_RETURN and self.app.profile.current and not self.removing:
            self.app.to_menu()
            return True
        elif e.type == pygame.KEYDOWN and pygame.K_1 <= e.key < pygame.K_1 + len(self.cards):
            self._choose(self.cards[e.key - pygame.K_1][0])
            return True
        return False

    def draw(self, surf):
        p = self.app.profile
        gfx.text(surf, "WHO'S PLAYING?", (40, 16 if T.compact else 30), 34, T.TEXT, bold=True)
        if self.removing:
            sub, col = "Tap a player twice to remove them and all their progress.", T.BAD
        else:
            sub, col = "Choose your name. Each player keeps their own progress and settings.", T.MUTED
        gfx.text(surf, sub, (42, 60 if T.compact else 76), gfx.fit_width(sub, 17, 800), col)
        hover = mouse_pos()
        for i, (name, r) in enumerate(self.cards):
            accent = T.BAD if self.removing else T.ACCENT
            current = name == p.current and not self.removing
            h = r.collidepoint(hover)
            if current or name == self.armed:
                gfx.glow(surf, r.center, r.w * 0.4, accent, 0.15)
            fill = gfx.lerp_color(T.PANEL, accent, 0.22 if name == self.armed else 0.12 if current else 0.06 if h else 0)
            border = accent if (current or h or name == self.armed) else T.BORDER
            gfx.panel(surf, r, fill, border, radius=16, border_w=2 if current else 1)
            if not self.app.touch:
                gfx.text(surf, str(i + 1), (r.x + 22, r.centery), 15, T.DIM, bold=True, anchor="center")
            gfx.text(surf, name, (r.x + 44, r.centery), 34, T.TEXT, bold=True, mono=True, anchor="midleft",
                     translate=False)
            data = p.player(name)
            if name == self.armed:
                lines = ["Tap again to remove", "all of this player's progress"]
                cols = (T.BAD, T.MUTED)
            else:
                measured = sum(1 for e in data["subtests"].values() if e["history"])
                lines = [i18n.f("{n} / 10 skills measured", n=measured),
                         "Playing now" if name == p.current else _last_played(data.get("seen"))]
                cols = (T.TEXT, T.ACCENT if name == p.current else T.MUTED)
            lh = T.font(15).get_linesize()
            for k, (line, c) in enumerate(zip(lines, cols)):
                gfx.text(surf, line, (r.right - 24, r.centery + (k - 1) * lh + 2), gfx.fit_width(line, 15, 270), c,
                         anchor="topright")
        super().draw(surf)


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
            label = i18n.f("Rated set  ·  {rating}", rating=round(r["rating"])) if r else "Rated set"
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
        # with large text the rules and the how-to-play panels don't fit side by side
        self.show_rules = False
        self.rules_btn = Button(
            (290, T.H - 104, 280, 44), "Rules of the real test", self._toggle_rules, col, size=16
        )
        self.large = T.large_text   # fixed for the scene, so the toggle can't go missing
        if self.large:
            self.buttons.append(self.rules_btn)

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        a = gfx.ease_out(self.t / 0.5)
        top = 24 if T.compact else 40   # of the mode line above the title
        dots_y = top + (36 if T.compact else 30)
        if self.ladder_kind == "daily":
            n = daily_number(datetime.date.today())
            gfx.text(
                surf,
                i18n.f("DAILY CHALLENGE #{n}  ·  SAME PUZZLES FOR EVERYONE TODAY", n=n),
                (50, top),
                14,
                T.GOLD,
                bold=True,
            )
        if self.battery_pos is not None:
            i = self.battery_pos
            gfx.text(
                surf,
                i18n.f("FULL ASSESSMENT  ·  SUBTEST {n} OF {total}", n=i + 1, total=len(ORDER)),
                (50, top),
                14,
                T.GOLD,
                bold=True,
            )
            for k, c in enumerate(ORDER):
                cc = T.INDEX_COLORS[c.index]
                x = 50 + k * 30
                gfx.circle(
                    surf,
                    (x + 8, dots_y),
                    7,
                    cc
                    if k < i
                    else (gfx.lerp_color(T.TRACK, cc, 0.6) if k == i else T.TRACK),
                )
                if k == i:
                    gfx.circle(surf, (x + 8, dots_y), 11, cc, 2)
        if not T.compact:
            y0 = 110
        elif self.battery_pos is not None:
            y0 = top + 62
        else:
            y0 = top + (36 if self.ladder_kind == "daily" else 0)
        gfx.glow(surf, (220, y0 + 60), 300, col, 0.18 * a)
        index_name = i18n.upper(T.INDEX_NAMES[cls.index])
        chip = pygame.Rect(50, y0, max(230, T.font(13, True).size(index_name)[0] + 30), 28)
        gfx.panel(surf, chip, gfx.lerp_color(T.PANEL, col, 0.25), col, radius=14)
        gfx.text(
            surf,
            index_name,
            chip.center,
            13,
            col,
            bold=True,
            anchor="center",
        )
        if T.compact:   # a smaller title, and the panels take what is left above the buttons
            gfx.text(surf, cls.name, (50, y0 + 36), 44, T.TEXT, bold=True)
            if self.show_rules:   # the long list of rules needs the room of the line under the title
                py = y0 + 104
            else:
                gfx.text(surf, cls.measures, (52, y0 + 96), 20, T.MUTED)
                py = y0 + 146
            ph = T.H - 124 - py
        else:
            gfx.text(surf, cls.name, (50, y0 + 44), 54, T.TEXT, bold=True)
            gfx.text(surf, cls.measures, (52, y0 + 112), 20, T.MUTED)
            py, ph = 290, 360

        side_w = T.W - 50 - 780   # the column on the right takes the rest of the width
        if not self.large:
            how_h = ph * 5 // 9
            self._panel(surf, (50, py, 700, ph), "RULES OF THE REAL TEST", cls.rules, 17, T.TEXT, col, True)
            self._panel(surf, (780, py, side_w, how_h), "HOW TO PLAY HERE", cls.controls, 17, T.TEXT, col)
            self._panel(surf, (780, py + how_h + 16, side_w, ph - how_h - 16), "MODE", [self._mode()], 16, T.MUTED,
                        col, top=30)
        elif self.show_rules:   # large text: the rules get the whole width, behind a toggle
            self._panel(surf, (50, py, T.W - 100, ph), "RULES OF THE REAL TEST", cls.rules, 17, T.TEXT, col, True)
        else:
            self._panel(surf, (50, py, 700, ph), "HOW TO PLAY HERE", cls.controls, 17, T.TEXT, col)
            self._panel(surf, (780, py, side_w, ph), "MODE", [self._mode()], 16, T.MUTED, col, top=30)
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

    @staticmethod
    def _panel(surf, rect, heading, paras, size, color, col, bullets=False, top=34):
        p = pygame.Rect(rect)
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=18)
        gfx.text(surf, heading, (p.x + 26, p.y + 22), 14, col, bold=True)
        x = p.x + (46 if bullets else 26)
        w = p.w - (76 if bullets else 52)
        y = p.y + 22 + max(top, T.font(14, True).get_linesize() + 12)
        size = gfx.fit_size(
            size,
            lambda k: gfx.block_height(paras, w, k, spacing=1.25, gap=8) <= p.bottom - 4 - y,
        )
        for para in paras:
            if bullets:
                gfx.circle(surf, (p.x + 32, y + round(T.text_px(size) * 0.65)), 3, col)
            y += gfx.text_block(surf, para, (x, y), w, size, color, spacing=1.25) + 8

    def _mode(self):
        if self.ladder_kind == "daily":
            if self.daily_done:
                return i18n.f("You've already played today ({solved}/10). This run is practice and won't change "
                              "your result.", solved=self.daily_done["solved"])
            return (
                "Daily challenge: 10 puzzles from easy to beyond the real test's hardest item, with feedback "
                "after each. Only your first completed try today counts."
            )
        if self.battery_pos is not None:
            return (
                "Test conditions: no feedback, exactly like the real assessment. Your result stays hidden "
                "until all ten subtests are complete."
            )
        if self.app.profile.settings.get("feedback", True):
            return "Training: after every item you'll see the score it earned and the best answer."
        return "Test conditions: no feedback after items. Sample items are still explained."

    def _toggle_rules(self):
        self.show_rules = not self.show_rules
        self.rules_btn.label = "How to play" if self.show_rules else "Rules of the real test"


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
        # compact: the score on the left, what it means and the buttons on the right
        bx, by = (self.INFO_X, 440) if T.compact else (T.W // 2, T.H - 120)
        self.buttons = [
            Button(
                (bx - 260, by, 240, 54),
                "Train again",
                lambda: app.start_practice(cls),
                col,
                hotkeys=(pygame.K_r,),
                primary=True,
            ),
            Button(
                (bx + 20, by, 240, 54),
                "Skill tree",
                app.to_menu,
                T.ACCENT,
                hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
            ),
        ]

    INFO_X = 880   # compact: centre of the column right of the score

    def draw(self, surf):
        cls = self.cls
        col = T.INDEX_COLORS[cls.index]
        c = (360, 320) if T.compact else (T.W // 2, 330)
        info = (self.INFO_X, 180) if T.compact else (c[0], c[1] + 190)   # where the words start
        gfx.text(
            surf, i18n.upper(cls.name), (T.W // 2, 40 if T.compact else 70), 16, col, bold=True, anchor="center"
        )
        if not self.app.profile.settings.get("show_scores", True):
            self._draw_hidden(surf, c, col, info)
            super().draw(surf)
            return
        filled = int(gfx.clamp((self.t - 0.4) * 14, 0, self.scaled))
        gfx.glow(surf, c, 260, col, 0.2 + 0.02 * filled)
        gfx.circle(surf, c, 112, gfx.lerp_color(T.PANEL, col, 0.12))
        gfx.pips(surf, c, 140, 18, 19, filled, col, ghost=self.best_before)
        letter = scoring.grade(self.scaled)
        done = self.t > 0.4 + self.scaled / 14   # the ring has filled
        if done:
            appear = gfx.ease_out((self.t - 0.4 - self.scaled / 14) / 0.3)
            gfx.grade_badge(surf, letter, (c[0], c[1] - 14), 96, self.t, alpha=255 * appear)
        gfx.text(
            surf, "GRADE", (c[0], c[1] + 52), 13, col, bold=True, anchor="center"
        )
        if done:
            x, y = info
            dy = (50, 94, 134) if T.compact else (42, 78, 106)   # (large text needs the room)
            gfx.text(surf, scoring.grade_name(letter), (x, y), 28, T.TEXT, bold=True, anchor="center")
            line = i18n.f("Raw {raw} / {max}", raw=self.raw, max=cls.max_raw) + "   ·   " + \
                i18n.n(self.scaled, "{n} skill point of 19", "{n} skill points of 19")
            gfx.text(surf, line, (x, y + dy[0]), 18, T.MUTED, anchor="center")
            if self.scaled > self.best_before > 0:
                gfx.text(
                    surf,
                    "NEW PERSONAL BEST",
                    (x, y + dy[1]),
                    16,
                    T.GOLD,
                    bold=True,
                    anchor="center",
                )
            self._draw_extra(surf, (x, y + dy[2]))
        super().draw(surf)

    def _draw_extra(self, surf, pos):
        extra = self._extra()
        if extra and T.compact:   # the column is narrower than the screen
            w = 640
            gfx.text_block(surf, extra, (pos[0] - w // 2, pos[1] - 10), w, 16, T.DIM, align="center")
        elif extra:
            gfx.text(surf, extra, pos, 16, T.DIM, anchor="center")

    def _draw_hidden(self, surf, c, col, info):
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
        x, y = info
        gfx.text(
            surf,
            "Scores are hidden. You can show them in Settings.",
            (x, y + 10),
            18,
            T.MUTED,
            anchor="center",
        )
        self._draw_extra(surf, (x, y + 46))

    def _extra(self):
        d = self.details
        if "forward" in d:
            return i18n.f("Forward {forward}  ·  Backward {backward}  ·  Sequencing {sequencing}", **d)
        if "attempted" in d:
            return i18n.f("{correct} correct  ·  {wrong} incorrect  ·  {attempted} attempted", **d)
        if d.get("discontinued"):
            return i18n.n(d["items"], "Stopped after {n} item. Every subtest ends after a run of misses, so everyone "
                          "reaches that point.", "Stopped after {n} items. Every subtest ends after a run of "
                          "misses, so everyone reaches that point.")
        if "items" in d:
            return i18n.n(d["items"], "{n} item given, right to the end of the subtest",
                          "{n} items given, right to the end of the subtest")
        return ""


class BatteryResultScene(Scene):
    def __init__(self, app, scaled, raw, indexes, overall):
        super().__init__(app)
        sound.play("complete")
        # compact: a tree without names, so that it fits beside the panel
        self.tree = SkillTree((460, 326), layout="narrow") if T.compact else SkillTree(center=((T.W - 340) // 2, 460), sx=0.68)
        self.scaled = scaled
        self.raw = raw
        self.indexes = indexes
        self.overall = overall
        self.best = {c: app.profile.best_scaled(c) for c in BY_CODE}
        self.attempts = {c: app.profile.attempts(c) for c in BY_CODE}
        self.hover = None
        self.buttons = [
            Button(
                # compact: at the top, so the panel can take the full height
                (T.W - 290, 14, 250, 50) if T.compact else (T.W - 290, T.H - 100, 250, 54),
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
        top = 18 if T.compact else 30
        gfx.text(surf, "ASSESSMENT COMPLETE", (40, top), 30, T.TEXT, bold=True)
        gfx.text(surf, "Your skill constellation", (42, top + 40), 17, T.MUTED)
        hide = not self.app.profile.settings.get("show_scores", True)
        data = {
            "scaled": self.scaled,
            "best": self.best,
            "indexes": self.indexes,
            "overall": self.overall,
            "hide": hide,
        }
        self.tree.draw(surf, data, self.t, self.t, self.hover)

        p = pygame.Rect(T.W - 370, 120, 330, 520) if T.large_text else pygame.Rect(T.W - 330, 120, 290, 520)
        if T.compact:
            p.update(p.x, 76, p.w, T.H - 88)
        row = 50 if T.compact else 52   # per index
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
                surf, "GRADE SCORE", (x, y), 13, T.GOLD, bold=True, alpha=255 * a
            )
            letter = scoring.composite_grade(self.overall)
            badge = gfx.grade_badge(surf, letter, (x + 44, y + 62), 76, self.t, alpha=255 * a)
            name = scoring.grade_name(letter)
            gfx.text(
                surf,
                name,
                (badge.right + 12, y + 62),
                gfx.fit_width(name, 20, p.right - 24 - badge.right - 12, bold=True),
                T.GRADE_COLORS[letter],
                bold=True,
                anchor="midleft",
                alpha=255 * a,
            )
            gfx.text(
                surf,
                "Grades run from D up to S",
                (x, y + 120),
                gfx.fit_width("Grades run from D up to S", 15, p.w - 48),
                T.MUTED,
                alpha=255 * a,
            )
            y += 170
            for idx in ("VCI", "PRI", "WMI", "PSI"):
                v = self.indexes[idx]
                col = T.INDEX_COLORS[idx]
                name = T.INDEX_NAMES[idx]
                gfx.text(
                    surf, name, (x, y), gfx.fit_width(name, 15, p.w - 108), T.TEXT, alpha=255 * a
                )
                gfx.grade_badge(surf, scoring.composite_grade(v), (p.right - 40, y + 18), 24, self.t,
                                alpha=255 * a)
                bar = pygame.Rect(x, y + max(24, T.font(17, True).get_linesize()), p.w - 90, 6)   # clear of the grade
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
                y += row
            gfx.text(
                surf,
                "NOT A PSYCHOLOGICAL TEST",
                (x, y + 6),
                13,
                T.PARTIAL,
                bold=True,
                alpha=255 * a,
            )
            note = (
                "Grades use rough standards made up for this game. They show trends in your "
                "training, nothing more."
            )
            note_y = y + 6 + max(22, T.font(13, True).get_linesize())
            gfx.text_block(
                surf,
                note,
                (x, note_y),
                p.w - 48,
                gfx.fit_size(13, lambda k: gfx.block_height([note], p.w - 48, k) <= p.bottom - 12 - note_y),
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
                self.overall,
                hide,
            )
        if not self.tree.finished(self.t):
            skip = "tap to skip" if self.app.touch else "click to skip"
            gfx.text(surf, skip, (self.tree.center[0], 100), 13, T.DIM, anchor="center")


class PauseOverlay:
    def __init__(self, app):
        self.app = app
        cx = T.W // 2
        self.top = 260 - (T.FULL_H - T.H) // 2   # of the title: centred on any canvas
        y = self.top + 70
        self.buttons = [
            Button(
                (cx - 140, y, 280, 52),
                "Resume",
                app.resume,
                T.ACCENT,
                hotkeys=(pygame.K_ESCAPE,),
                primary=True,
            ),
            Button(
                (cx - 140, y + 64, 280, 52),
                "Restart subtest",
                app.restart_subtest,
                T.PARTIAL,
            ),
            Button((cx - 140, y + 128, 280, 52), "Quit to skill tree", app.to_menu, T.BAD),
        ]

    def handle_event(self, e):
        for b in self.buttons:
            if b.handle(e):
                return

    def update(self, dt):
        for b in self.buttons:
            b.update(dt)

    def draw(self, surf):
        # Opaque cover: the puzzle underneath must not remain readable while paused
        gfx.overlay(surf, T.BG, 255)
        gfx.text(
            surf, "Paused", (T.W // 2, self.top), 44, T.TEXT, bold=True, anchor="center"
        )
        gfx.text(
            surf,
            "Timers are stopped (the real test can't be paused!)  ·  F11 toggles fullscreen",
            (T.W // 2, self.top + 40),
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
        # compact: the result on the left, the details and the buttons on the right
        bx, by = (self.INFO_X, 430) if T.compact else (T.W // 2, T.H - 110)
        home = Button(
            (bx + 20, by, 240, 54),
            "Skill tree",
            app.to_menu,
            T.ACCENT,
            hotkeys=(pygame.K_RETURN, pygame.K_ESCAPE),
        )
        if ladder.kind == "rated":
            again = Button(
                (bx - 260, by, 240, 54),
                "Another set",
                lambda: app.begin_subtest(cls, "rated"),
                col,
                hotkeys=(pygame.K_r,),
                primary=True,
            )
        else:
            again = Button(
                (bx - 260, by, 240, 54),
                "Copy result",
                self._copy,
                col,
                hotkeys=(pygame.K_c,),
                primary=True,
            )
        self.buttons = [again, home]
        if ladder.kind == "rated" and online.enabled():   # three narrower buttons
            board = Button((0, 0, 0, 0), "Leaderboard", lambda: app.open_leaderboard(cls.code), T.GOLD,
                           hotkeys=(pygame.K_b,))
            self.buttons.insert(1, board)
            for i, b in enumerate(self.buttons):
                b.rect.update(bx - 304 + i * 206, by, 196, 54)
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

    INFO_X = 880   # compact: centre of the column right of the result

    def draw(self, surf):
        lad = self.ladder
        cls = lad.cls
        col = T.INDEX_COLORS[cls.index]
        c = (360, 310) if T.compact else (T.W // 2, 290)
        info_x, info_y = (self.INFO_X, 150) if T.compact else (c[0], c[1] + 172)   # where the details start
        title = f"{lad.label()}  ·  {i18n._(cls.name)}".upper()
        gfx.text(surf, title, (T.W // 2, 40 if T.compact else 64), 16, col, bold=True, anchor="center")
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
                    (info_x, info_y),
                    30,
                    dcol,
                    bold=True,
                    anchor="center",
                )
                peak = self.app.profile.rating(cls.code)
                info = i18n.f("{solved} of {length} solved", solved=lad.solved, length=lad.length) + "  ·  " + \
                    i18n.n(lad.played, "{n} puzzle played", "{n} puzzles played")
                if peak:
                    info += i18n.f("  ·  peak {peak}", peak=round(peak["peak"]))
                online_rank = self.app.online.rank(cls.code)
                if online_rank and online_rank.get("rank"):
                    info += i18n.f("  ·  #{rank} of {total} online", rank=online_rank["rank"],
                                   total=online_rank["total"])
                width = 2 * min(info_x, T.W - info_x) - 40
                gfx.text(surf, info, (info_x, info_y + 40), gfx.fit_width(info, 17, width), T.MUTED, anchor="center")
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
                info = i18n.n(self.streak, "Daily streak: {n} day", "Daily streak: {n} days")
            else:
                info = (
                    i18n.f("Practice replay  ·  today's result was {solved}/10", solved=self.first["solved"])
                    if self.first
                    else ""
                )
            gfx.text(surf, info, (info_x, info_y + 8), 18, T.MUTED, anchor="center")
            if self.status:
                gfx.text(
                    surf, self.status, (info_x, info_y + 40), 16, T.GOOD, anchor="center"
                )
        # one square per puzzle, with its level underneath
        n = lad.length
        x0 = info_x - (n * 46 - 10) / 2
        sq_y = 250 if T.compact else 548
        for i, (level, solved) in enumerate(lad.results):
            if self.t < 0.3 + i * 0.08:
                break
            r = pygame.Rect(x0 + i * 46, sq_y, 36, 36)
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
            (info_x, sq_y + 72),
            12,
            T.DIM,
            anchor="center",
        )
        super().draw(surf)


class LeaderboardScene(Scene):
    """The online leaderboard: the top puzzle ratings of each subtest with rated sets, where the
    current player stands, and joining or leaving it."""

    ROWS = 10

    def __init__(self, app, code=None):
        super().__init__(app)
        from .challenge import challenge_codes
        self.codes = challenge_codes()
        self.code = code if code in self.codes else self.codes[0]
        self.boards = {}      # code -> the server's answer
        self.errors = {}      # code -> why it couldn't be fetched
        self.loading = set()
        self.armed = False    # a second tap on Leave leaves
        top = 76 if T.compact else 120
        tab_w = 230 if T.compact else 200
        self.tabs = []
        for i, c in enumerate(self.codes):
            cls = BY_CODE[c]
            b = Button((40 + i * (tab_w + 12), top, tab_w, 46), cls.name, lambda c=c: self._show(c),
                       T.INDEX_COLORS[cls.index], hotkeys=(pygame.K_1 + i,), size=16)
            self.tabs.append(b)
        y = top + 62
        self.table = pygame.Rect(40, y, 780, T.H - y - (16 if T.compact else 40))
        self.side = pygame.Rect(840, y, T.W - 880, self.table.h)
        bw = self.side.w - 60
        self.join_btn = Button((self.side.x + 30, self.side.bottom - 76, bw, 52), "", self._join, T.GOLD,
                               primary=True, size=18)
        self.play_btn = Button((self.side.x + 30, self.side.bottom - 140, bw, 52), "Play a rated set",
                               lambda: app.start_practice(BY_CODE[self.code]), T.GOLD, primary=True, size=17)
        self.leave_btn = Button((self.side.x + 30, self.side.bottom - 76, bw, 52), "", self._leave, T.BAD, size=16)
        self.code_btn = Button((self.side.x + 30, self.side.bottom - 204, bw, 52), "Move to another device",
                               app.open_recovery_code, T.ACCENT, size=16)
        if T.compact:   # three buttons need a little less room each
            for i, b in enumerate((self.leave_btn, self.play_btn, self.code_btn)):
                b.rect.update(b.rect.x, self.side.bottom - 70 - i * 58, bw, 48)
        back = (T.W - 260, 14, 220, 52) if T.compact else (T.W - 260, 30, 220, 52)
        self.back_btn = Button(back, "Back", app.to_menu, T.ACCENT, hotkeys=(pygame.K_ESCAPE,))
        self.privacy_btn = Button((back[0] - 160, back[1], 148, back[3]), "Privacy",
                                  lambda: web.open_url(PRIVACY_URL), T.ACCENT, size=16)
        self._sync_buttons()
        self._show(self.code)

    def _show(self, code):
        self.code = code
        self.armed = False
        if code in self.loading:
            return
        self.loading.add(code)

        def got(req):
            self.loading.discard(code)
            if req.ok and isinstance(req.data, dict):
                self.boards[code] = req.data
                self.errors.pop(code, None)
            else:
                self.errors[code] = online.describe(req)

        self.app.online.board(code, got, limit=self.ROWS)

    def _refresh(self):
        self.boards.clear()
        self._show(self.code)

    def _join(self):
        self.app.online.join(then=self._refresh)

    def _leave(self):
        if not self.armed:
            self.armed = True
            return
        sound.play("wrong")
        self.app.online.leave()
        self._refresh()

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_LEFT, pygame.K_RIGHT):
            i = self.codes.index(self.code) + (1 if e.key == pygame.K_RIGHT else -1)
            self._show(self.codes[i % len(self.codes)])
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and not self.leave_btn.rect.collidepoint(e.pos):
            self.armed = False
        return False

    def _sync_buttons(self):
        """Join, or play and leave, depending on whether the player has joined."""
        on = self.app.online
        acct = on.account()
        self.buttons = self.tabs + [self.privacy_btn, self.back_btn]
        if acct:
            self.buttons += [self.code_btn, self.play_btn, self.leave_btn]
            self.leave_btn.label = "Tap again to leave" if self.armed else "Leave the leaderboard"
            self.leave_btn.primary = self.armed
        elif self.app.profile.current:
            self.buttons.append(self.join_btn)
            joining = on.joining is not None
            self.join_btn.label = "Joining…" if joining else i18n.f("Join as {name}", name=self.app.profile.current)
            self.join_btn.enabled = not joining
        for b in self.tabs:
            b.primary = b.label == BY_CODE[self.code].name

    def update(self, dt):
        self._sync_buttons()
        super().update(dt)

    def draw(self, surf):
        gfx.text(surf, "LEADERBOARD", (40, 16 if T.compact else 30), 34, T.TEXT, bold=True)
        if not T.compact:   # the tabs need its room
            sub = "Puzzle ratings from rated sets, from players everywhere. You're ranked after your first set."
            gfx.text(surf, sub, (42, 76), gfx.fit_width(sub, 17, 900), T.MUTED)
        self._draw_table(surf)
        self._draw_side(surf)
        super().draw(surf)

    def _draw_table(self, surf):
        p = self.table
        cls = BY_CODE[self.code]
        col = T.INDEX_COLORS[cls.index]
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        board = self.boards.get(self.code)
        cols = (p.x + 70, p.x + 100, p.right - 190, p.right - 36)   # rank (right), name, rating (right), puzzles (right)
        head_y = p.y + 18
        for label, x, anchor in (("#", cols[0], "topright"), ("PLAYER", cols[1], "topleft"),
                                 ("RATING", cols[2], "topright"), ("PUZZLES", cols[3], "topright")):
            gfx.text(surf, label, (x, head_y), 13, T.DIM, bold=True, anchor=anchor)
        top = head_y + max(28, T.font(13, True).get_linesize() + 8)
        row_h = (p.bottom - 12 - top) // (self.ROWS + 1)
        if board is None:
            msg = self.errors.get(self.code) or "Loading…"
            gfx.text_block(surf, msg, (p.x + 60, p.centery - 20), p.w - 120, 17,
                           T.BAD if self.code in self.errors else T.MUTED, align="center")
            return
        rows = list(board["top"])
        me = board.get("me")
        mine = me["id"] if me else None
        if me and me.get("rank") and all(r["id"] != mine for r in rows):
            rows = rows[:self.ROWS] + [None, me]   # None: the gap before you
        if not rows:
            msg = "Nobody is ranked yet. Play a rated set to be the first!"
            gfx.text_block(surf, msg, (p.x + 60, p.centery - 20), p.w - 120, 17, T.MUTED, align="center")
            return
        size = gfx.fit_size(17, lambda k: T.font(k, True, True).get_linesize() <= row_h - 4)
        for i, r in enumerate(rows):
            y = top + i * row_h
            if r is None:
                gfx.text(surf, "···", (p.centerx, y + row_h // 2), 17, T.DIM, anchor="center")
                continue
            you = r["id"] == mine
            row = pygame.Rect(p.x + 14, y + 2, p.w - 28, row_h - 4)
            if you:
                gfx.panel(surf, row, gfx.lerp_color(T.PANEL, col, 0.18), col, radius=10)
            elif i % 2 == 0:
                gfx.panel(surf, row, gfx.lerp_color(T.PANEL, T.PANEL_HI, 0.5), T.PANEL, radius=10)
            cy = row.centery
            rank_col = T.GOLD if r["rank"] == 1 else T.TEXT if r["rank"] <= 3 else T.MUTED
            gfx.text(surf, str(r["rank"]), (cols[0], cy), size, rank_col, bold=True, anchor="midright")
            name = gfx.text(surf, r["name"], (cols[1], cy), size, T.TEXT, bold=True, mono=True, anchor="midleft",
                            translate=False)
            gfx.text(surf, f"#{r['tag']}", (name.right + 10, cy), max(11, size - 4), T.DIM, mono=True,
                     anchor="midleft")
            gfx.text(surf, f"{r['rating']:.0f}", (cols[2], cy), size, col if you else T.TEXT, bold=True,
                     anchor="midright")
            gfx.text(surf, str(r["played"]), (cols[3], cy), size, T.MUTED, anchor="midright")

    def _draw_side(self, surf):
        p = self.side
        on = self.app.online
        acct = on.account()
        cls = BY_CODE[self.code]
        col = T.INDEX_COLORS[cls.index]
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        x, y, w = p.x + 30, p.y + 24, p.w - 60
        name = self.app.profile.current or ""
        if not acct:
            gfx.text(surf, "COMPETE ONLINE", (x, y), 14, T.GOLD, bold=True)
            paras = [i18n.f("Put {name}'s puzzle ratings on the leaderboard.", name=name),
                     "Your name, ratings and progress are sent. The progress is a backup that lets you move "
                     "to another device with a recovery code. Leave any time to delete it all from the server."]
            if on.error:
                paras.append(on.error)
            bottom = self.join_btn.rect.y - 16
            top = y + 34
            size = gfx.fit_size(16, lambda k: gfx.block_height(paras, w, k, spacing=1.3, gap=12) <= bottom - top)
            for k, para in enumerate(paras):
                c = T.BAD if on.error and k == len(paras) - 1 else T.TEXT if k == 0 else T.MUTED
                top += gfx.text_block(surf, para, (x, top), w, size, c, spacing=1.3) + 12
            return
        gfx.text(surf, "YOU", (x, y), 14, col, bold=True)
        n = gfx.text(surf, name, (x, y + 28), gfx.fit_width(name, 30, w - 90, bold=True, mono=True, translate=False),
                     T.TEXT, bold=True, mono=True, translate=False)
        gfx.text(surf, f"#{acct['tag']}", (n.right + 10, n.centery), 16, T.DIM, mono=True, anchor="midleft")
        y = n.bottom + 16
        board = self.boards.get(self.code)
        me = board.get("me") if board else None
        local = self.app.profile.rating(self.code)
        if me and me.get("rank"):
            big = f"#{me['rank']}"
            line = i18n.f("of {total} ranked in {subtest}", total=board["total"], subtest=i18n._(cls.name))
        elif me and me.get("played"):
            left = max(0, SET_LENGTH - me["played"])
            big, line = "Unranked", i18n.n(left, "{n} more puzzle to be ranked", "{n} more puzzles to be ranked")
        elif local:
            big, line = "…", "Your rating is on its way"
        else:
            big, line = "Unrated", i18n.f("Play a {subtest} rated set to get a rating", subtest=i18n._(cls.name))
        r = gfx.text(surf, big, (x, y), 56 if big.startswith("#") else 34, col, bold=True)
        y = r.bottom + 6
        bottom = self.code_btn.rect.y - 12
        lines = [line]
        if me and me.get("rating") is not None:
            lines.append(i18n.f("Rating {rating}  ·  peak {peak}", rating=round(me["rating"]), peak=round(me["peak"])))
        size = gfx.fit_size(16, lambda k: gfx.block_height(lines, w, k, spacing=1.3, gap=6) <= bottom - y)
        for k, ln in enumerate(lines):
            y += gfx.text_block(surf, ln, (x, y), w, size, T.MUTED if k == 0 else T.TEXT, spacing=1.3) + 6


class RecoveryCodeScene(Scene):
    """The current player's recovery code, which moves them to another device (see RestoreScene)."""

    def __init__(self, app):
        super().__init__(app)
        self.armed = False   # a second tap on New code gets one
        self.busy = False
        self.status = None
        self.panel = pygame.Rect(0, 0, 1000, T.H - 200 if T.compact else 470)
        self.panel.midtop = (T.W // 2, 84 if T.compact else 120)
        y = self.panel.bottom + (16 if T.compact else 30)
        self.copy_btn = Button((T.W // 2 - 350, y, 220, 52), "Copy", self._copy, T.ACCENT, hotkeys=(pygame.K_c,))
        self.new_btn = Button((T.W // 2 - 110, y, 220, 52), "New code", self._new, T.BAD)
        back = (T.W - 260, 14, 220, 52) if T.compact else (T.W // 2 + 130, y, 220, 52)
        back_btn = Button(back, "Back", app.open_leaderboard, T.ACCENT, hotkeys=(pygame.K_ESCAPE,), primary=True)
        if T.compact:
            self.copy_btn.rect.x, self.new_btn.rect.x = T.W // 2 - 230, T.W // 2 + 10
        self.buttons = [self.copy_btn, self.new_btn, back_btn]
        acct = app.online.account()
        if acct and not acct.get("code"):   # joined before there were codes
            self._fetch()

    def _code(self):
        acct = self.app.online.account()
        return acct.get("code") if acct else None

    def _fetch(self):
        self.busy = True

        def got(req):
            self.busy = False
            self.status = None if req.ok else online.describe(req)

        self.app.online.new_code(got)

    def _new(self):
        if not self.armed:
            self.armed = True
            return
        self.armed = False
        self._fetch()

    def _copy(self):
        code = self._code()
        if not code:
            return
        try:
            ok = web.copy_text(code) if web.IS_WEB else (pygame.scrap.put_text(code) or True)
        except (pygame.error, AttributeError):
            ok = False
        self.status = "Copied!" if ok else "Couldn't reach the clipboard. Write the code down instead."

    def handle_event(self, e):
        if super().handle_event(e):
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.armed = False
        return False

    def update(self, dt):
        code = self._code()
        self.copy_btn.enabled = bool(code) and not self.busy
        self.new_btn.enabled = self.app.online.account() is not None and not self.busy
        self.new_btn.label = "Tap again" if self.armed else "New code"
        self.new_btn.primary = self.armed
        super().update(dt)

    def draw(self, surf):
        gfx.text(surf, "MOVE TO ANOTHER DEVICE", (40, 16 if T.compact else 30), 34, T.TEXT, bold=True)
        p = self.panel
        gfx.glow(surf, p.center, 480, T.ACCENT, 0.06)
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        name = self.app.profile.current or ""
        code = self._code()
        y = p.y + (24 if T.compact else 36)
        gfx.text(surf, i18n.f("{name}'S RECOVERY CODE", name=name), (p.centerx, y), 14, T.ACCENT, bold=True,
                 anchor="midtop")
        y += 30
        if code and not self.busy:
            r = gfx.text(surf, code, (p.centerx, y), 60 if T.compact else 72, T.TEXT, bold=True, mono=True,
                         anchor="midtop")
        else:
            r = gfx.text(surf, "Getting your code…" if self.busy else "No code yet", (p.centerx, y + 20), 30,
                         T.MUTED, bold=True, anchor="midtop")
        if self.status:
            bad = self.status != "Copied!"
            gfx.text(surf, self.status, (p.centerx, r.bottom + 10), gfx.fit_width(self.status, 15, p.w - 80),
                     T.BAD if bad else T.GOOD, bold=True, anchor="midtop")
        elif self.armed:
            line = "Your current code will stop working."
            gfx.text(surf, line, (p.centerx, r.bottom + 10), 15, T.BAD, bold=True, anchor="midtop")
        paras = [
            "On your other device, choose Restore a player when it asks for a name (or on the Who's playing "
            "screen) and enter this code.",
            i18n.f("{name}'s progress, settings and leaderboard place move there. This device keeps its copy of "
                   "the progress but stops posting to the leaderboard.", name=name),
            "Keep the code private: anyone who has it can take over this player. If someone else has seen "
            "it, get a new code.",
        ]
        top = r.bottom + 50
        w = p.w - 120
        size = gfx.fit_size(17, lambda k: gfx.block_height(paras, w, k, spacing=1.3, gap=12) <= p.bottom - 20 - top)
        for k, para in enumerate(paras):
            top += gfx.text_block(surf, para, (p.x + 60, top), w, size, T.TEXT if k == 0 else T.MUTED,
                                  spacing=1.3) + 12
        super().draw(surf)


class LearnScene(Scene):
    """How cognitive assessments work, what a session is like, how to read scores. With ``then`` it shows one
    topic as a walkthrough whose last page continues to ``then``."""

    def __init__(self, app, topic=None, then=None):
        super().__init__(app)
        self.then = then
        self.topics = learn.topics(i18n.language())
        keys = [k for k, _, _ in self.topics]
        self.ti = keys.index(topic) if topic in keys else 0
        self.page = 0
        self.nav = []
        if then is None:
            for i, (_, title, _) in enumerate(self.topics):
                b = Button(
                    (40, 84 + i * 56, 250, 46) if T.compact else (40, 150 + i * 58, 250, 46),
                    title,
                    lambda i=i: self._select(i),
                    T.ACCENT,
                    size=16,
                )
                self.nav.append(b)
        self.panel = pygame.Rect(320, 130, T.W - 360, 560)
        if then:
            self.panel = pygame.Rect(180, 130, T.W - 360, 560)
        if T.compact:   # under a shorter heading, down to the bottom
            self.panel.update(self.panel.x, 104 if then else 84, self.panel.w, T.H - (120 if then else 104))
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
        if T.compact and then:   # top right, clear of the panel
            back_rect = (T.W - 200, 24, 160, 46)
        else:
            back_rect = (40, T.H - (66 if T.compact else 84), 200, 46)
        back = Button(
            back_rect,
            "Skip" if then else "Back",
            self._leave,
            T.MUTED,
            hotkeys=(pygame.K_ESCAPE,),
            size=16,
        )
        self.buttons = self.nav + [self.prev_btn, self.next_btn, back]
        self._split = {}

    @property
    def pages(self):
        """The topic's pages; large text splits the longer ones over more pages."""
        key = (self.ti, T.large_text)
        if key not in self._split:
            self._split[key] = [
                part for title, paras in self.topics[self.ti][2] for part in self._paginate(title, paras)
            ]
        return self._split[key]

    def _paginate(self, title, paras):
        limit = self.panel.bottom - 80
        if self.layout_page(paras, self.panel) <= limit:
            return [(title, paras)]
        # keep each "## " heading with the paragraph after it
        units = []
        for para in paras:
            if units and units[-1][-1].startswith("## "):
                units[-1].append(para)
            else:
                units.append([para])
        pages = [[]]
        for unit in units:
            if pages[-1] and self.layout_page(pages[-1] + unit, self.panel) > limit:
                pages.append([])
            pages[-1] += unit
        return [(title, page) for page in pages]

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
        elif self.ti < len(self.topics) - 1:
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
                (self.ti + (1 if e.key == pygame.K_DOWN else -1)) % len(self.topics)
            )
            return True
        return False

    def update(self, dt):
        super().update(dt)
        self.page = min(self.page, len(self.pages) - 1)
        for i, b in enumerate(self.nav):
            b.primary = i == self.ti
        last = self.page == len(self.pages) - 1
        self.prev_btn.enabled = self.page > 0 or (self.then is None and self.ti > 0)
        if self.then:
            self.next_btn.label = "Start the assessment" if last else "Next"
            self.next_btn.accent = T.GOLD if last else T.ACCENT
        else:
            self.next_btn.label = "Next topic" if last else "Next"
            self.next_btn.enabled = not (last and self.ti == len(self.topics) - 1)

    @staticmethod
    def layout_page(paras, p, surf=None, size=17):
        """Draw (or, without a surface, just measure) a page's paragraphs; returns the bottom y.
        Must stay above ``p.bottom - 80``, where the page buttons are."""
        y = p.y + 84
        w = p.w - 80
        lh = int(T.font(size).get_linesize() * 1.3)
        head = size - 2
        for para in paras:
            if para.startswith("## "):
                y += 4
                if surf:
                    gfx.text(surf, para[3:], (p.x + 40, y), head, T.ACCENT, bold=True)
                y += max(24, T.font(head, True).get_linesize() + 2)
            elif surf:
                y += (
                    gfx.text_block(
                        surf, para, (p.x + 40, y), w, size, T.TEXT, spacing=1.3
                    )
                    + 12
                )
            else:
                y += lh * len(gfx.wrap(para, size, w)) + 12
        return y

    def draw(self, surf):
        top = 16 if T.compact else 30
        if self.then:
            gfx.text(
                surf,
                "BEFORE YOUR FIRST FULL ASSESSMENT",
                (180, top + 4),
                30,
                T.TEXT,
                bold=True,
            )
            gfx.text(
                surf,
                "A quick look at what a real session is like. Skip whenever you like.",
                (182, top + 46),
                17,
                T.MUTED,
            )
        elif T.compact:   # no room for the subtitle
            gfx.text(surf, "LEARN", (40, top), 34, T.TEXT, bold=True)
        else:
            gfx.text(surf, "LEARN", (40, top), 34, T.TEXT, bold=True)
            gfx.text(
                surf,
                "How assessments work, what a session is like, and how to read the scores",
                (42, top + 44),
                17,
                T.MUTED,
            )
        p = self.panel
        gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        title, paras = self.pages[self.page]
        gfx.text(surf, title, (p.x + 40, p.y + 30), 28, T.TEXT, bold=True)
        size = gfx.fit_size(
            17, lambda k: self.layout_page(paras, p, size=k) <= p.bottom - 80
        )
        self.layout_page(paras, p, surf, size)
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
    def __init__(self, app):
        super().__init__(app)
        self.ROW = 160 if T.compact else 114 if T.large_text else 100
        s = app.profile.settings
        n = len(sound.tracks())
        if not sound.available():
            music_desc = "No audio device was found."
        elif n:
            music_desc = i18n.n(n, "Plays the {n} track in your music folder on a shuffled loop. It turns down "
                                   "while digits are read out.",
                                "Plays the {n} tracks in your music folder on a shuffled loop. It turns down "
                                "while digits are read out.")
        elif web.IS_WEB:
            music_desc = "Put your own mp3, ogg or wav files in the puzzleth/music folder. None found yet."
        else:
            music_desc = ("Put your own mp3, ogg or wav files in the puzzleth/music folder or ~/.puzzleth/music. "
                          "None found yet.")
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
                "Grades",
                "Show the D to S grades of subtests, areas and the overall Grade Score. Hide them to practise "
                "without a grade. Puzzle ratings and daily results still show.",
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
        if T.compact:   # two columns, the descriptions under the titles
            self.panels = [pygame.Rect(40, 84, 590, 16 + 3 * self.ROW), pygame.Rect(650, 84, 590, 16 + 2 * self.ROW)]
            self.slots = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1)]   # (panel, row in it) of each setting
        else:
            # large text needs the room of a wider panel
            w = 1120 if T.large_text else 840
            self.panels = [pygame.Rect(
                T.W // 2 - w // 2, 96 if T.large_text else 118, w, 16 + len(self.rows) * self.ROW
            )]
            self.slots = [(0, i) for i in range(len(self.rows))]
        self.toggles = []
        for (k, i), row in zip(self.slots, self.rows):
            p = self.panels[k]
            b = Button(
                (p.right - 190, p.y + 28 + i * self.ROW, 150, 44) if T.compact else
                (p.right - 190, p.y + 30 + i * self.ROW, 150, 48),
                "",
                row[3],
                T.ACCENT,
                size=17,
            )
            self.toggles.append(b)
        self.toggles[2].enabled = self.toggles[3].enabled = sound.available()
        self.toggles[4].enabled = app.display is not None
        if T.compact:
            done = (T.W - 260, 14, 220, 52)
        else:
            done = (T.W // 2 - 110, max(T.H - 120, self.panels[0].bottom + 18), 220, 52)
        back = Button(
            done,
            "Done",
            app.to_menu,
            T.ACCENT,
            hotkeys=(pygame.K_ESCAPE, pygame.K_RETURN),
            primary=True,
        )
        language = Button(
            (40, T.H - 74, 180, 48),
            "Language",
            app.choose_language,
            T.ACCENT,
            size=16,
        )
        self.buttons = self.toggles + [language, back]

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
        gfx.text(surf, "SETTINGS", (40, 16 if T.compact else 30), 34, T.TEXT, bold=True)
        for p in self.panels:
            gfx.panel(surf, p, T.PANEL, T.BORDER, radius=20)
        top = max(30, T.font(20, True).get_linesize())
        desc_w = self.panels[0].w - 300
        if T.compact:   # below the toggle button rather than beside it
            top = 52
            desc_w = self.panels[0].w - 70
        size = gfx.fit_size(
            15,
            lambda k: all(
                gfx.block_height([row[1]], desc_w, k, spacing=1.3) <= self.ROW - 26 - top
                for row in self.rows
            ),
        )
        for (k, i), (title, desc, *_rest) in zip(self.slots, self.rows):
            p = self.panels[k]
            y = p.y + 26 + i * self.ROW
            if i:
                pygame.draw.line(
                    surf, T.BORDER, (p.x + 30, y - 18), (p.right - 30, y - 18), 1
                )
            gfx.text(surf, title, (p.x + 40, y), gfx.fit_width(title, 20, p.w - 250, bold=True), T.TEXT, bold=True)
            gfx.text_block(
                surf, desc, (p.x + 40, y + top), desc_w, size, T.MUTED, spacing=1.3
            )
        super().draw(surf)


def _volume_label(v):
    return f"{round(v * 100)}\u00a0%" if v > 0 and i18n.language() == "fr" else f"{round(v * 100)}%" if v > 0 else "Off"
