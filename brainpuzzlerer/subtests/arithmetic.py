"""Arithmetic: timed mental word problems."""
import pygame

from .. import gfx
from .. import theme as T
from ..widgets import Button, DigitEntry
from .base import ItemSubtest

NAMES = ["Ava", "Ben", "Chloe", "Dev", "Elena", "Farid", "Grace", "Hugo", "Iris", "Jonah", "Kira", "Leo",
         "Maya", "Nico", "Omar", "Priya", "Quinn", "Rosa", "Sam", "Tara"]
ITEMS = [("apples", "apple"), ("pencils", "pencil"), ("stickers", "sticker"), ("books", "book"),
         ("marbles", "marble"), ("cookies", "cookie"), ("stamps", "stamp"), ("cards", "card")]


def _tier1(r):
    name = r.choice(NAMES)
    things, _ = r.choice(ITEMS)
    kind = r.randrange(3)
    if kind == 0:
        a, b = r.randint(2, 9), r.randint(2, 9)
        return f"{name} has {a} {things} and gets {b} more. How many {things} does {name} have now?", a + b
    if kind == 1:
        a = r.randint(8, 15)
        b = r.randint(2, a - 2)
        return f"{name} had {a} {things} and gave away {b}. How many are left?", a - b
    a, b = r.randint(2, 5), r.randint(2, 5)
    return f"There are {a} bags with {b} {things} in each bag. How many {things} are there in all?", a * b


def _tier2(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        price, n = r.randint(2, 9), r.randint(3, 6)
        return f"Notebooks cost ${price} each. How much do {n} notebooks cost?", price * n
    if kind == 1:
        n, per = r.randint(3, 8), r.choice([4, 6, 8])
        total = n * per
        return f"{name} shares {total} cookies equally among {per} friends. How many does each friend get?", n
    if kind == 2:
        a, b = r.randint(12, 45), r.randint(11, 38)
        return f"A bus has {a} passengers. At the next stop, {b} more get on. How many passengers are on the bus?", a + b
    pay = r.choice([10, 20])
    cost = r.randint(3, pay - 2)
    return f"{name} buys a toy for ${cost} and pays with a ${pay} bill. How much change does {name} get?", pay - cost


def _tier3(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        n, price, pay = r.randint(2, 4), r.randint(3, 6), 20
        if n * price >= pay:
            n = 2
        return (f"{name} buys {n} sandwiches at ${price} each and pays with a ${pay} bill. "
                f"How much change does {name} receive?"), pay - n * price
    if kind == 1:
        speed, hours = r.choice([40, 50, 60]), r.randint(2, 5)
        return f"A car travels at {speed} miles per hour. How far does it travel in {hours} hours?", speed * hours
    if kind == 2:
        per_day, days = r.randint(4, 9), r.choice([7, 14])
        return f"{name} reads {per_day} pages every day. How many pages does {name} read in {days} days?", per_day * days
    total, kept = r.choice([24, 30, 36, 42]), r.choice([2, 3])
    return (f"{name} has {total} marbles and gives one-{'half' if kept == 2 else 'third'} of them to a friend. "
            f"How many marbles does {name} have left?"), total - total // kept


def _tier4(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        price = r.choice([40, 60, 80, 120, 200])
        pct = r.choice([10, 25, 50])
        return f"A jacket costs ${price}. It is on sale for {pct}% off. What is the sale price?", price * (100 - pct) // 100
    if kind == 1:
        workers, hours = r.choice([(4, 6), (3, 8), (6, 4), (2, 12)])
        new = r.choice([w for w in (2, 3, 4, 6, 8, 12) if (workers * hours) % w == 0 and w != workers])
        return (f"{workers} workers can paint a house in {hours} hours. At the same rate, how many hours "
                f"would it take {new} workers?"), workers * hours // new
    if kind == 2:
        a, b, c = r.randint(70, 95), r.randint(70, 95), 0
        c = 3 * r.randint(78, 90) - a - b
        if not 50 <= c <= 100:
            a, b, c = 80, 90, 85
        return f"{name} scores {a}, {b} and {c} on three tests. What is {name}'s average score?", (a + b + c) // 3
    rate, mins = r.choice([3, 4, 5]), r.choice([12, 15, 20])
    return f"A machine fills {rate} bottles every minute. How many bottles does it fill in {mins} minutes?", rate * mins


def _tier5(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        orig, inc = r.choice([(40, 20), (50, 20), (60, 20), (80, 20), (40, 25), (60, 25), (80, 25)])
        new = orig * (100 + inc) // 100
        return f"After a {inc}% price increase, a lamp costs ${new}. What did it cost before the increase?", orig
    if kind == 1:
        a, b = r.choice([(2, 3), (3, 5), (1, 4), (2, 5)])
        k = r.randint(3, 8)
        return (f"{name} and a friend split some money in the ratio {a} to {b}. "
                f"If {name} gets ${a * k}, how much money was there in total?"), (a + b) * k
    if kind == 2:
        s1, s2 = r.choice([(40, 60), (30, 60), (60, 90), (30, 45)])
        d = r.choice([120, 180, 240, 300])
        while d % s1 or d % s2:
            d += 60
        return (f"A train travels {d} miles at {s1} miles per hour, then returns at {s2} miles per hour. "
                f"How many hours does the round trip take?"), d // s1 + d // s2
    n = r.choice([5, 6, 8])
    avg = r.randint(10, 20)
    drop = r.randint(4, avg - 2)
    return (f"The average of {n} numbers is {avg}. When one number, {drop}, is removed, what is the sum of the "
            f"remaining numbers?"), n * avg - drop


TIERS = [_tier1, _tier2, _tier3, _tier4, _tier5]


class Arithmetic(ItemSubtest):
    code = "AR"
    name = "Arithmetic"
    index = "WMI"
    measures = "Mental manipulation, concentration and numerical reasoning"
    n_items = 22
    start_item = 6
    discontinue_n = 3
    max_raw = 22
    rules = [
        "Word problems are read aloud and solved in your head — no paper or pencil.",
        "30-second limit per item, timed from the end of the reading.",
        "You may ask for the problem to be repeated once; the timer keeps running.",
        "1 point for each correct answer.",
        "Adults start at item 6; reversal rule applies.",
        "Discontinue after 3 consecutive scores of 0.",
    ]
    controls = ["The problem is shown while it's 'read', then hidden.",
                "Type your answer and press Enter.  R repeats the problem once."]

    def setup(self):
        self.entry = DigitEntry((T.W // 2, 470), accent=self.accent)
        self.repeat_btn = Button((T.W // 2 - 110, 560, 220, 46), "Repeat  (R)", self._repeat, self.accent,
                                 hotkeys=(pygame.K_r,), size=17)

    def time_limit(self, n):
        return 30

    def make_item(self, n):
        tier = 0 if n == 0 else min(4, (n - 1) * 5 // self.n_items)
        q, ans = TIERS[tier](self.rng)
        words = len(q.split())
        return {"q": q, "ans": ans, "read": 1.5 + words * 0.3, "repeat_until": None, "repeated": False}

    def on_item_start(self):
        self.entry.value = ""
        self.repeat_btn.enabled = True

    def timer_elapsed(self):
        return max(0.0, self.item_t - self.item["read"])

    def _visible(self):
        it = self.item
        if self.revealing:
            return True
        return self.item_t < it["read"] or (it["repeat_until"] is not None and self.item_t < it["repeat_until"])

    def _repeat(self):
        it = self.item
        if it["repeated"] or self.item_t < it["read"]:
            return
        it["repeated"] = True
        it["repeat_until"] = self.item_t + it["read"]
        self.repeat_btn.enabled = False

    def handle_item(self, e):
        if self.repeat_btn.handle(e):
            return
        if self.entry.handle(e) == "submit" and self.entry.value:
            ok = int(self.entry.value) == self.item["ans"]
            self.submit(1 if ok else 0, "" if ok else f"Answer: {self.item['ans']}")

    def on_timeout(self):
        self.submit(0, f"Time limit reached. Answer: {self.item['ans']}")

    def update_item(self, dt):
        self.entry.update(dt)
        self.repeat_btn.update(dt)
        if self.item["repeated"]:
            self.repeat_btn.enabled = False

    def draw_item(self, surf):
        rect = pygame.Rect(0, 0, 900, 200)
        rect.center = (T.W // 2, 270)
        gfx.panel(surf, rect, T.PANEL, T.BORDER, radius=18)
        if self._visible():
            reading = self.item_t < self.item["read"] and self.state == "item"
            if reading:
                frac = self.item_t / self.item["read"]
                pygame.draw.rect(surf, self.accent, (rect.x + 20, rect.bottom - 14, (rect.w - 40) * frac, 3),
                                 border_radius=2)
            gfx.text_block(surf, self.item["q"], (rect.x + 40, rect.y + 36), rect.w - 80, 27, T.TEXT, align="center")
        else:
            gfx.text(surf, "Problem hidden — solve it in your head", rect.center, 22, T.DIM, anchor="center")
            gfx.text(surf, "(press R to hear it once more)" if not self.item["repeated"] else "(already repeated)",
                     (rect.centerx, rect.centery + 34), 16, T.DIM, anchor="center")
        self.entry.draw(surf, label="your answer")
        if self.state == "item" and not self.item["repeated"] and self.item_t >= self.item["read"]:
            self.repeat_btn.draw(surf)
