"""Digit Span: Forward, Backward and Sequencing."""
import pygame

from .. import gfx, i18n, sound
from .. import theme as T
from ..widgets import DigitEntry, Keypad
from .base import CONTINUE_KEYS, Subtest

TASKS = [
    ("Forward", list(range(2, 10)), "Repeat the digits in the same order."),
    ("Backward", list(range(2, 9)), "Repeat the digits in reverse order."),
    ("Sequencing", list(range(2, 10)), "Repeat the digits in order from lowest to highest."),
]

SHOW = 0.75   # seconds each digit is visible
GAP = 0.25    # blank between digits -> one digit per second, as on the real test


class DigitSpan(Subtest):
    code = "DS"
    name = "Digit Span"
    index = "WMI"
    measures = "Auditory working memory, attention and mental manipulation"
    max_raw = 46
    rules = [
        "Three tasks: Forward (same order), Backward (reverse), Sequencing (lowest to highest).",
        "Digits are presented at a rate of one per second and never repeated.",
        "Each span length has two trials; each correct trial earns 1 point.",
        "A task stops when both trials of the same length are failed.",
        "Each task begins with a sample trial that isn't scored.",
    ]
    controls = ["Listen to the digits (they are also shown), then type your answer and press Enter.",
                "Backspace corrects. The answer submits automatically at full length."]

    def __init__(self, app, feedback=True, seed=None):
        super().__init__(app, feedback, seed)
        self.setup()

    def setup(self):
        self.task_i = 0
        self.score = 0
        self.task_scores = [0, 0, 0]
        self.longest = [0, 0, 0]
        self.entry = DigitEntry((T.W // 2, 286 if T.compact else 430), accent=self.accent)
        self.keypad = Keypad(400 if T.compact else 540, [str(d) for d in range(1, 10)] + ["Del"], self.accent,
                             key_w=90 if T.compact else 78, key_h=72 if T.compact else 64)
        self._task_intro()

    def _task_intro(self):
        self.state = "intro"
        self.item_i = -1        # -1 = sample
        self.trial = 0
        self.item_results = []

    @property
    def task(self):
        return TASKS[self.task_i]

    def _length(self):
        return 2 if self.item_i < 0 else self.task[1][self.item_i]

    def _new_trial(self):
        n = self._length()
        name = self.task[0]
        if name == "Sequencing":
            # real sequencing items may repeat digits
            seq = [self.rng.randint(1, 9) for _ in range(n)]
            for i in range(1, n):
                while seq[i] == seq[i - 1]:
                    seq[i] = self.rng.randint(1, 9)
        else:
            seq = self.rng.sample(range(1, 10), n)
        self.seq = seq
        self.target = {"Forward": seq, "Backward": seq[::-1], "Sequencing": sorted(seq)}[name]
        self.entry.value = ""
        self.state = "present"
        self.pt = -0.8
        self.spoken = -1
        self.fb = None

    def _submit(self):
        ok = [int(c) for c in self.entry.value] == self.target
        if self.item_i < 0:
            self.fb = {"ok": ok, "sample": True}
        else:
            self.item_results.append(ok)
            if ok:
                self.score += 1
                self.task_scores[self.task_i] += 1
                self.longest[self.task_i] = max(self.longest[self.task_i], self._length())
            self.fb = {"ok": ok, "sample": False}
        if self.feedback or self.fb["sample"]:
            sound.play("correct" if ok else "wrong")
        else:
            sound.play("submit")   # test conditions: no hint of how it went
        self.state = "feedback"
        self.ft = 0.0

    def _after_feedback(self):
        if self.item_i < 0:
            self.item_i, self.trial = 0, 0
            self.item_results = []
            self._new_trial()
            return
        if self.trial == 0:
            self.trial = 1
            self._new_trial()
            return
        both_failed = not any(self.item_results[-2:])
        self.item_i += 1
        self.trial = 0
        if both_failed or self.item_i >= len(self.task[1]):
            self.task_i += 1
            if self.task_i >= len(TASKS):
                self.finish(self.score, {"forward": self.task_scores[0], "backward": self.task_scores[1],
                                         "sequencing": self.task_scores[2], "longest": self.longest})
                return
            self._task_intro()
            return
        self._new_trial()

    def handle_event(self, e):
        if self.state == "intro":
            if e.type == pygame.KEYDOWN and e.key in CONTINUE_KEYS or e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                self._new_trial()
        elif self.state == "input":
            if self.touch:
                e = self.keypad.handle(e) or e
            r = self.entry.handle(e)
            if r == "submit" and self.entry.value:
                self._submit()
            elif r is True and len(self.entry.value) >= len(self.target):
                self.auto_t = 0.35
        elif self.state == "feedback":
            show = self.feedback or self.fb["sample"]
            if show and self.ft > 0.25 and (e.type == pygame.KEYDOWN and e.key in CONTINUE_KEYS or
                                            e.type == pygame.MOUSEBUTTONDOWN and e.button == 1):
                self._after_feedback()

    def update(self, dt):
        super().update(dt)
        self.entry.update(dt)
        self.keypad.update(dt)
        if self.state == "present":
            self.pt += dt
            i = int(self.pt // (SHOW + GAP)) if self.pt >= 0 else -1
            sound.duck(True)
            if self.spoken < i < len(self.seq):
                # read out as each digit appears, one per second like the examiner
                self.spoken = i
                sound.play(f"digit{self.seq[i]}")
            if self.pt >= len(self.seq) * (SHOW + GAP):
                self.state = "input"
                self.auto_t = None
                sound.duck(False)
        elif self.state == "input" and self.auto_t is not None:
            if len(self.entry.value) < len(self.target):
                self.auto_t = None
            else:
                self.auto_t -= dt
                if self.auto_t <= 0:
                    self._submit()
        elif self.state == "feedback":
            self.ft += dt
            if not (self.feedback or self.fb["sample"]) and self.ft > 0.45:
                self._after_feedback()

    def draw(self, surf):
        name, lengths, instr = self.task
        if self.state == "intro":
            sub = i18n._(name)
        elif self.item_i < 0:
            sub = i18n.f("{task}  ·  sample", task=i18n._(name))
        else:
            sub = i18n.f("{task}  ·  {length} digits  ·  trial {trial} of 2", task=i18n._(name),
                         length=self._length(), trial=self.trial + 1)
        self.draw_header(surf, sub, right=i18n.f("Score {score}", score=self.score) if self.feedback else "")
        self._draw_task_track(surf)
        cx, cy = T.W // 2, (266 if T.compact else 330)
        fb_y = 376 if T.compact else 540   # (the keypad's place)

        if self.state == "intro":
            gfx.glow(surf, (cx, cy), 260, self.accent, 0.2)
            gfx.text(surf, i18n.f("Digit Span {task}", task=i18n._(name)), (cx, cy - 60), 44, T.TEXT, bold=True,
                     anchor="center")
            gfx.text(surf, instr, (cx, cy), 22, T.MUTED, anchor="center")
            ex = i18n.f("e.g.  {example}", example={"Forward": "3 · 8 · 6   →   3 8 6", "Backward": "3 · 8 · 6   →   6 8 3",
                                                    "Sequencing": "3 · 8 · 1   →   1 3 8"}[name])
            gfx.text(surf, ex, (cx, cy + 50), 22, self.accent, mono=True, anchor="center")
            gfx.text(surf, self.prompt("Press Space when ready", "Tap anywhere when ready"), (cx, cy + 140), 20,
                     T.TEXT, bold=True, anchor="center")
        elif self.state == "present":
            per = SHOW + GAP
            i = int(self.pt // per) if self.pt >= 0 else -1
            local = self.pt - i * per
            n = len(self.seq)
            for k in range(n):
                col = self.accent if k <= i else T.TRACK
                gfx.circle(surf, (cx - (n - 1) * 11 + k * 22, cy + 130), 5, col)
            if i < 0:
                gfx.text(surf, "Listen…", (cx, cy), 26, T.MUTED, anchor="center")
            elif local < SHOW:
                a = gfx.ease_out(local / 0.15) * (1 - gfx.clamp((local - SHOW + 0.15) / 0.15, 0, 1))
                gfx.glow(surf, (cx, cy), 170, self.accent, 0.45 * a)
                gfx.text(surf, str(self.seq[i]), (cx, cy), 150, T.TEXT, bold=True, mono=True, anchor="center",
                         alpha=255 * a)
        elif self.state in ("input", "feedback"):
            gfx.text(surf, instr, (cx, cy - 60), 22, T.MUTED, anchor="center")
            self.entry.draw(surf, slots=len(self.target))
            if self.state == "input" and self.touch:
                self.keypad.draw(surf)
            if self.state == "feedback" and (self.feedback or self.fb["sample"]):
                ok = self.fb["ok"]
                col = T.GOOD if ok else T.BAD
                gfx.glow(surf, (cx, fb_y + 20), 260, col, 0.15)
                word = i18n._("Correct" if ok else "Incorrect")
                tag = i18n._("  (sample — not scored)") if self.fb["sample"] else ("  +1" if ok else "  +0")
                gfx.text(surf, word + tag, (cx, fb_y), 26, col, bold=True, anchor="center")
                shown = " ".join(map(str, self.seq))
                gfx.text(surf, i18n.f("Presented: {shown}     Answer: {answer}", shown=shown,
                                      answer=" ".join(map(str, self.target))), (cx, fb_y + 44),
                         19, T.TEXT, mono=True, anchor="center")
                gfx.text(surf, self.prompt("Enter to continue"), (cx, fb_y + 90), 16, T.MUTED, anchor="center")
        self.draw_footer(surf, "Each task stops when both trials of one length are failed")

    def _draw_task_track(self, surf):
        x0 = T.W // 2 - 240
        for i, (name, lengths, _) in enumerate(TASKS):
            x = x0 + i * 240
            active = i == self.task_i
            col = self.accent if active else (T.MUTED if i < self.task_i else T.DIM)
            gfx.text(surf, i18n.upper(name), (x, 92), 14, col, bold=True, anchor="center")
            n = len(lengths)
            for k in range(n):
                done = i < self.task_i and k < self.longest[i] - 1 or (active and k < self.item_i)
                c = self.accent if done else T.TRACK
                gfx.circle(surf, (x - (n - 1) * 7 + k * 14, 114), 4, c if active or done else T.TRACK)
