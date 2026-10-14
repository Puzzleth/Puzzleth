"""Shared machinery for subtests.

ItemSubtest implements the WAIS administration rules:
  * start point   - adults begin partway into the item list,
  * reversal      - if either of the first two items is not perfect, earlier items are given in
                    reverse order until two consecutive perfect scores; unadministered items
                    below that point receive full credit,
  * discontinue   - stop after N consecutive scores of 0,
  * time limits   - per item, where the real test has them.
"""
import random

import pygame

from .. import gfx
from .. import theme as T

CONTINUE_KEYS = (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE)


class Subtest:
    code = ""
    name = ""
    index = ""
    measures = ""
    rules = []
    controls = []
    max_raw = 0

    def __init__(self, app, feedback=True, seed=None):
        self.app = app
        self.feedback = feedback
        self.rng = random.Random(seed)
        self.t = 0.0
        self.done = False

    @property
    def accent(self):
        return T.INDEX_COLORS[self.index]

    def setup(self):
        """Called once (after rng exists) before the first item is generated."""

    def handle_event(self, e):
        pass

    def update(self, dt):
        self.t += dt

    def draw(self, surf):
        pass

    def finish(self, raw, details=None):
        if not self.done:
            self.done = True
            self.app.subtest_done(self, int(raw), details or {})

    # ------------------------------------------------------------ chrome

    def draw_header(self, surf, subtitle="", right=""):
        chip = pygame.Rect(40, 26, 58, 26)
        gfx.panel(surf, chip, gfx.lerp_color(T.PANEL, self.accent, 0.3), self.accent, radius=13)
        gfx.text(surf, self.index, chip.center, 14, self.accent, bold=True, anchor="center")
        r = gfx.text(surf, self.name, (chip.right + 14, chip.centery), 26, T.TEXT, bold=True, anchor="midleft")
        if subtitle:
            gfx.text(surf, subtitle, (r.right + 16, chip.centery + 2), 17, T.MUTED, anchor="midleft")
        if right:
            gfx.text(surf, right, (T.W - 120, chip.centery), 17, T.MUTED, anchor="midright")

    def draw_footer(self, surf, rule_text="", streak=None, streak_max=None):
        y = T.H - 30
        x = 40
        if streak_max:
            x = gfx.text(surf, "DISCONTINUE", (x, y), 13, T.DIM, bold=True, anchor="midleft").right + 14
            for i in range(streak_max):
                col = T.BAD if i < streak else T.TRACK
                gfx.circle(surf, (x + i * 16, y), 5, col)
            x += streak_max * 16 + 10
        if rule_text:
            gfx.text(surf, rule_text, (x, y), 14, T.DIM, anchor="midleft")
        gfx.text(surf, "Esc  pause", (T.W - 40, y), 14, T.DIM, anchor="midright")

    def draw_timer(self, surf, remaining, limit, center=(T.W - 70, 40), r=22):
        frac = max(0.0, remaining / limit) if limit else 0
        col = self.accent if frac > 0.25 else gfx.lerp_color(T.BAD, self.accent, frac * 4)
        if frac <= 0.25:
            gfx.glow(surf, center, r * 2.4, T.BAD, 0.25)
        gfx.ring(surf, center, r, 5, frac, col)
        gfx.text(surf, f"{max(0, remaining):.0f}", center, 17, T.TEXT, bold=True, mono=True, anchor="center")


class ItemSubtest(Subtest):
    n_items = 10
    start_item = 1
    discontinue_n = 3
    has_sample = True

    def __init__(self, app, feedback=True, seed=None):
        super().__init__(app, feedback, seed)
        self.scores = {}
        self.order = []
        self.phase = "forward"
        self.reversal_checked = False
        self.state = "item"
        self.fb = None
        self.fb_t = 0.0
        self.item_t = 0.0
        self.setup()
        self._begin(0 if self.has_sample else self.start_item)

    # --- hooks for subclasses
    def make_item(self, n):
        raise NotImplementedError

    def item_max(self, n):
        return 1

    def time_limit(self, n):
        return None

    def timer_elapsed(self):
        return self.item_t

    def on_item_start(self):
        pass

    def handle_item(self, e):
        pass

    def update_item(self, dt):
        pass

    def draw_item(self, surf):
        pass

    def on_timeout(self):
        self.submit(0, "Time limit reached.")

    # --- flow
    @property
    def is_sample(self):
        return self.cur == 0

    @property
    def revealing(self):
        """True while showing feedback that may reveal the correct answer."""
        return self.state == "feedback" and self.fb and self.fb["show"]

    def _begin(self, n):
        self.cur = n
        self.item = self.make_item(n)
        self.item_t = 0.0
        self.state = "item"
        self.fb = None
        self.on_item_start()

    def submit(self, points, explain=""):
        if self.state != "item":
            return
        mx = self.item_max(self.cur)
        if self.cur != 0:
            self.scores[self.cur] = points
            self.order.append(self.cur)
        show = self.feedback or self.cur == 0
        self.fb = {"points": points, "max": mx, "explain": explain, "show": show}
        self.state = "feedback"
        self.fb_t = 0.0

    def _perfect(self, n):
        return n in self.scores and self.scores[n] == self.item_max(n)

    def _zero_run(self):
        best = run = 0
        for n in range(1, self.n_items + 1):
            if n in self.scores and self.scores[n] == 0:
                run += 1
                best = max(best, run)
            else:
                run = 0
        return best

    def admin_zero_streak(self):
        k = 0
        for n in reversed(self.order):
            if self.scores[n] != 0:
                break
            k += 1
        return k

    def next_item(self):
        s = self.scores
        if not s:
            return self.start_item
        if not self.reversal_checked and self.start_item > 1 and len(self.order) >= 2:
            self.reversal_checked = True
            if not (self._perfect(self.order[0]) and self._perfect(self.order[1])):
                self.phase = "reverse"
        if self.phase == "reverse":
            low = min(s)
            if low == 1 or (self._perfect(low) and self._perfect(low + 1)):
                self.phase = "forward"
            else:
                return low - 1
        if self._zero_run() >= self.discontinue_n:
            return None
        nxt = max(s) + 1
        return nxt if nxt <= self.n_items else None

    def raw_score(self):
        raw = sum(self.scores.values())
        if self.scores:
            low = min(self.scores)
            if low > 1 and self._perfect(low) and self._perfect(low + 1):
                raw += sum(self.item_max(i) for i in range(1, low))
        return raw

    def _advance(self):
        nxt = self.next_item()
        if nxt is None:
            self.finish(self.raw_score(), {"items": len(self.order), "discontinued": self._zero_run() >= self.discontinue_n})
        else:
            self._begin(nxt)

    # --- scene interface
    def handle_event(self, e):
        if self.state == "feedback":
            if self.fb["show"] and self.fb_t > 0.25 and (
                    (e.type == pygame.KEYDOWN and e.key in CONTINUE_KEYS) or
                    (e.type == pygame.MOUSEBUTTONDOWN and e.button == 1)):
                self._advance()
            return
        self.handle_item(e)

    def update(self, dt):
        super().update(dt)
        if self.state == "item":
            self.item_t += dt
            lim = self.time_limit(self.cur)
            if lim and self.timer_elapsed() >= lim:
                self.on_timeout()
            self.update_item(dt)
        elif self.state == "feedback":
            self.fb_t += dt
            if not self.fb["show"] and self.fb_t >= 0.35:
                self._advance()

    def item_label(self):
        if self.is_sample:
            return "Sample item"
        tag = f"Item {self.cur} of {self.n_items}"
        if self.phase == "reverse":
            tag += "  ·  reverse order"
        return tag

    def footer_rule(self):
        return f"Stops after {self.discontinue_n} consecutive scores of 0"

    def draw(self, surf):
        self.draw_header(surf, self.item_label())
        lim = self.time_limit(self.cur)
        if lim:
            remaining = lim - self.timer_elapsed() if self.state == "item" else lim - min(lim, self.timer_elapsed())
            self.draw_timer(surf, remaining, lim)
        self.draw_item(surf)
        if self.state == "feedback":
            if self.fb["show"]:
                self.draw_feedback(surf)
            else:
                gfx.overlay(surf, T.BG, 160 * gfx.ease_out(self.fb_t / 0.35))
        self.draw_footer(surf, self.footer_rule(), self.admin_zero_streak(), self.discontinue_n)

    def draw_feedback(self, surf):
        p, mx = self.fb["points"], self.fb["max"]
        col = T.GOOD if p == mx else (T.PARTIAL if p > 0 else T.BAD)
        word = "Perfect" if p == mx else ("Partial credit" if p > 0 else "No credit")
        rect = pygame.Rect(0, 0, 760, 74)
        rect.midbottom = (T.W // 2, T.H - 52)
        a = gfx.ease_out(self.fb_t / 0.25)
        rect.y += int((1 - a) * 20)
        gfx.glow(surf, rect.center, 360, col, 0.18 * a)
        gfx.panel(surf, rect, gfx.lerp_color(T.PANEL, col, 0.16), col, radius=16)
        gfx.circle(surf, (rect.x + 40, rect.centery), 22, col)
        gfx.text(surf, f"+{p}", (rect.x + 40, rect.centery), 18, T.BG, bold=True, anchor="center")
        head = f"{word}  ·  {p} / {mx}" + ("   (sample, not scored)" if self.is_sample else "")
        gfx.text(surf, head, (rect.x + 76, rect.y + 14), 19, col, bold=True)
        if self.fb["explain"]:
            gfx.text(surf, self.fb["explain"], (rect.x + 76, rect.y + 42), 15, T.TEXT)
        gfx.text(surf, "Enter to continue", (rect.right - 20, rect.centery), 15, T.MUTED, anchor="midright")


class SpeedSubtest(Subtest):
    """Untimed practice with feedback, then a single fixed time limit (120 s on the WAIS)."""

    duration = 120
    practice_n = 3

    def __init__(self, app, feedback=True, seed=None):
        super().__init__(app, feedback, seed)
        self.state = "practice"
        self.practice_left = self.practice_n
        self.remaining = self.duration
        self.correct = 0
        self.wrong = 0
        self.attempted = 0
        self.flash = 0.0
        self.flash_col = T.GOOD
        self.practice_msg = ""
        self.setup()
        self.new_item(practice=True)

    def new_item(self, practice=False):
        raise NotImplementedError

    def answer(self, ok):
        if self.state == "practice":
            self.flash_col = T.GOOD if ok else T.BAD
            self.flash = 1.0
            self.practice_msg = "Correct!" if ok else "Not quite — " + self.explain_wrong()
            if ok:
                self.practice_left -= 1
                if self.practice_left <= 0:
                    self.state = "ready"
                    return
                self.new_item(practice=True)
            return
        if self.state != "run":
            return
        self.attempted += 1
        if ok:
            self.correct += 1
        else:
            self.wrong += 1
        self.flash_col = self.accent
        self.flash = 1.0
        if self.attempted >= self.max_raw:
            self.end()
        else:
            self.new_item()

    def explain_wrong(self):
        return "check the key and try again."

    def score(self):
        return self.correct

    def end(self):
        self.state = "over"
        self.finish(self.score(), {"correct": self.correct, "wrong": self.wrong, "attempted": self.attempted})

    def handle_event(self, e):
        if self.state == "ready":
            if e.type == pygame.KEYDOWN and e.key in CONTINUE_KEYS or \
                    e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self.state = "run"
                self.new_item()
            return
        if self.state in ("practice", "run"):
            self.handle_item(e)

    def handle_item(self, e):
        pass

    def update(self, dt):
        super().update(dt)
        self.flash = max(0.0, self.flash - dt * 4)
        if self.state == "run":
            self.remaining -= dt
            if self.remaining <= 0:
                self.remaining = 0
                self.end()

    def draw(self, surf):
        sub = {"practice": "Practice", "ready": "Ready", "run": f"{self.attempted} answered", "over": ""}[self.state]
        self.draw_header(surf, sub)
        self.draw_timer(surf, self.remaining, self.duration)
        if self.state == "ready":
            self.draw_ready(surf)
        else:
            self.draw_item(surf)
            if self.state == "practice":
                gfx.text(surf, f"Practice — {self.practice_left} correct answer(s) to go. Not timed.",
                         (T.W // 2, 92), 17, T.MUTED, anchor="center")
                if self.practice_msg:
                    col = T.GOOD if self.practice_msg.startswith("Correct") else T.BAD
                    gfx.text(surf, self.practice_msg, (T.W // 2, T.H - 80), 18, col, bold=True, anchor="center")
        self.draw_footer(surf, f"{self.duration}-second limit  ·  work fast, but accurately")

    def draw_ready(self, surf):
        c = (T.W // 2, T.H // 2 - 30)
        gfx.glow(surf, c, 220, self.accent, 0.25 + 0.1 * abs(((self.t * 0.8) % 2) - 1))
        gfx.text(surf, "Practice complete", (c[0], c[1] - 70), 34, T.TEXT, bold=True, anchor="center")
        gfx.text(surf, f"The {self.duration}-second timer starts as soon as you continue.", (c[0], c[1] - 20), 20,
                 T.MUTED, anchor="center")
        gfx.text(surf, "No feedback is given during the timed section.", (c[0], c[1] + 12), 20, T.MUTED,
                 anchor="center")
        gfx.text(surf, "Press Space to begin", (c[0], c[1] + 80), 24, self.accent, bold=True, anchor="center")

    def draw_item(self, surf):
        pass
