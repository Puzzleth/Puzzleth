"""Verbal Comprehension subtests: Similarities, Vocabulary, Information.

The real subtests are free-response; here they are multiple choice, but the options are
written to mirror how a real examiner awards 2, 1 or 0 points.
"""
import pygame

from .. import gfx, i18n
from .. import theme as T
from ..content import verbal
from ..widgets import OptionCard
from .base import ItemSubtest

KEYS = {pygame.K_1: 0, pygame.K_2: 1, pygame.K_3: 2, pygame.K_4: 3,
        pygame.K_KP1: 0, pygame.K_KP2: 1, pygame.K_KP3: 2, pygame.K_KP4: 3}


class ChoiceSubtest(ItemSubtest):
    tiers = 6

    def setup(self):
        self.bank = verbal.bank(i18n.language())
        self.used = set()
        self.cards = []
        self.choice = None

    def tier(self, n):
        return 1 if n == 0 else 1 + (n - 1) * self.tiers // self.n_items

    def pick(self, pool, key=lambda x: x):
        fresh = [x for x in pool if key(x) not in self.used] or pool
        x = self.rng.choice(fresh)
        self.used.add(key(x))
        return x

    def generate(self, n):
        """Return dict with 'options' [(text, points)] plus prompt fields."""
        raise NotImplementedError

    def make_item(self, n):
        item = self.generate(n)
        self.rng.shuffle(item["options"])
        self.choice = None
        self.cards = [OptionCard(self._card_rect(i), str(i + 1), txt, self.accent)
                      for i, (txt, _) in enumerate(item["options"])]
        return item

    @staticmethod
    def _card_rect(i):
        if T.compact:   # two by two under the prompt
            w, h, gap = 590, 112, 16
            row, col = divmod(i, 2)
            return pygame.Rect(T.W // 2 - w - gap // 2 + col * (w + gap), 252 + row * (h + gap), w, h)
        w, h, gap = 800, 68, 14
        return pygame.Rect((T.W - w) // 2, 316 + i * (h + gap), w, h)

    def choose(self, i):
        self.choice = i
        pts = self.item["options"][i][1]
        best = max(p for _, p in self.item["options"])
        best_txt = next(t for t, p in self.item["options"] if p == best)
        explain = self.explain(pts, best_txt)
        if self.revealing_after_submit():
            for j, card in enumerate(self.cards):
                p = self.item["options"][j][1]
                card.tag = i18n.n(p, "{n} pt", "{n} pts") if best > 1 else (i18n._("correct") if p else "")
                if j == i:
                    card.state = "good" if p == best else ("partial" if p > 0 else "bad")
                elif p == best:
                    card.state = "good"
                else:
                    card.state = "dim"
        else:
            self.cards[i].state = "selected"
        self.submit(pts, explain)

    def revealing_after_submit(self):
        return self.feedback or self.is_sample

    def explain(self, pts, best_txt):
        return "" if pts == self.item_max(self.cur) else i18n.f("Best answer: {answer}", answer=best_txt)

    def handle_item(self, e):
        if e.type == pygame.KEYDOWN and e.key in KEYS and KEYS[e.key] < len(self.cards):
            self.choose(KEYS[e.key])
        elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            for i, c in enumerate(self.cards):
                if c.hit(e.pos):
                    self.choose(i)
                    break

    def update_item(self, dt):
        for c in self.cards:
            c.update(dt)

    def draw_prompt(self, surf):
        pass

    @staticmethod
    def prompt_y():
        return 148 if T.compact else 190

    def draw_item(self, surf):
        self.draw_prompt(surf)
        for c in self.cards:
            if self.state != "item":
                c.hover = 0
            c.draw(surf)


class Similarities(ChoiceSubtest):
    code = "SI"
    name = "Similarities"
    index = "VCI"
    measures = "Verbal concept formation and abstract reasoning"
    n_items = 18
    start_item = 4
    discontinue_n = 3
    max_raw = 36
    rules = [
        "Two words are read aloud; you explain how they are alike.",
        "2 points: the abstract, general category the two belong to.",
        "1 point: a concrete, specific property they share.",
        "0 points: a difference, something only one has, or a vague/wrong answer.",
        "Adults start at item 4. If either of the first two isn't perfect, earlier items are given in reverse.",
        "Discontinue after 3 consecutive scores of 0. No time limit.",
    ]
    controls = ["Pick the answer an examiner would score highest.", "Click an answer or press 1–4."]

    def item_max(self, n):
        return 2

    def generate(self, n):
        tier = self.tier(n)
        cats = self.bank.SIMILARITIES[tier]
        members, two, one, near = self.pick(cats, key=lambda c: c[1])
        a, b = self.rng.sample(members, 2)
        generic = self.rng.choice(self.bank.SIMILARITIES_GENERIC_ZERO)
        return {"a": a, "b": b,
                "options": [(two, 2), (one, 1), (near, 0), (generic, 0)]}

    def explain(self, pts, best_txt):
        if pts == 2:
            return i18n._("Abstract category — exactly what earns full credit.")
        if pts == 1:
            return i18n.f("True, but concrete. 2-point answer: {answer}", answer=best_txt)
        return i18n.f("A 2-point answer: {answer}", answer=best_txt)

    def draw_prompt(self, surf):
        cy = self.prompt_y()
        gfx.glow(surf, (T.W // 2, cy), 300, self.accent, 0.15)
        a = self.item["a"].capitalize()
        b = self.item["b"].capitalize()
        gfx.text(surf, a, (T.W // 2 - 46, cy), 54, T.TEXT, bold=True, anchor="midright")
        gfx.text(surf, "&", (T.W // 2, cy), 40, self.accent, anchor="center")
        gfx.text(surf, b, (T.W // 2 + 46, cy), 54, T.TEXT, bold=True, anchor="midleft")
        gfx.text(surf, "In what way are they alike?", (T.W // 2, cy + 64), 20, T.MUTED, anchor="center")


class Vocabulary(ChoiceSubtest):
    code = "VC"
    name = "Vocabulary"
    index = "VCI"
    measures = "Word knowledge and verbal concept formation"
    n_items = 30
    start_item = 5
    discontinue_n = 3
    max_raw = 60
    rules = [
        "You are asked \"What does ___ mean?\" and give a definition.",
        "2 points: a precise definition capturing the word's central meaning.",
        "1 point: a vague, partial, or overly narrow definition (e.g. one example use).",
        "0 points: a wrong or unrelated meaning.",
        "Adults start at item 5; reversal rule applies.",
        "Discontinue after 3 consecutive scores of 0. No time limit.",
    ]
    controls = ["Choose the definition that would earn the most credit.", "Click an answer or press 1–4."]

    def item_max(self, n):
        return 2

    def generate(self, n):
        tier = self.tier(n)
        words = self.bank.VOCABULARY[tier]
        word, precise, partial = self.pick(words, key=lambda w: w[0])
        others = [w for w in words if w[0] != word]
        distract = self.rng.sample(others, 2)
        return {"word": word, "options": [(precise, 2), (partial, 1), (distract[0][1], 0), (distract[1][1], 0)]}

    def explain(self, pts, best_txt):
        if pts == 2:
            return i18n._("Precise definition — full credit.")
        if pts == 1:
            return i18n.f("Vague or partial. Precise: {answer}", answer=best_txt)
        return i18n.f("Meaning: {answer}", answer=best_txt)

    def draw_prompt(self, surf):
        cy = self.prompt_y()
        gfx.glow(surf, (T.W // 2, cy), 300, self.accent, 0.15)
        gfx.text(surf, "What does", (T.W // 2, cy - 54), 20, T.MUTED, anchor="center")
        gfx.text(surf, self.item["word"].upper(), (T.W // 2, cy + 4), 58, T.TEXT, bold=True, anchor="center")
        gfx.text(surf, "mean?", (T.W // 2, cy + 62), 20, T.MUTED, anchor="center")


class Information(ChoiceSubtest):
    code = "IN"
    name = "Information"
    index = "VCI"
    measures = "General knowledge acquired from culture and education"
    n_items = 26
    start_item = 3
    discontinue_n = 3
    max_raw = 26
    rules = [
        "General-knowledge questions on a wide range of topics.",
        "1 point for each correct answer.",
        "Adults start at item 3; reversal rule applies.",
        "Discontinue after 3 consecutive scores of 0. No time limit.",
    ]
    controls = ["Click an answer or press 1–4."]

    def generate(self, n):
        q, ans, wrong = self.pick(self.bank.INFORMATION[self.tier(n)], key=lambda x: x[0])
        return {"q": q, "options": [(ans, 1)] + [(w, 0) for w in wrong]}

    def explain(self, pts, best_txt):
        return "" if pts else i18n.f("Answer: {answer}", answer=best_txt)

    def draw_prompt(self, surf):
        cy = self.prompt_y()
        gfx.glow(surf, (T.W // 2, cy), 300, self.accent, 0.12)
        lines = gfx.wrap(self.item["q"], 36, 1000 if T.compact else 900, bold=True)
        lh = T.font(36, True).get_linesize()
        y0 = cy - lh * len(lines) / 2
        for i, line in enumerate(lines):
            gfx.text(surf, line, (T.W // 2, y0 + i * lh), 36, T.TEXT, bold=True, anchor="midtop")
