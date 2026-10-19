"""Arithmetic: timed mental word problems."""
import pygame

from .. import gfx, i18n
from .. import theme as T
from ..widgets import Button, DigitEntry, Keypad
from .base import ItemSubtest

NAMES = ["Ava", "Ben", "Chloe", "Dev", "Elena", "Farid", "Grace", "Hugo", "Iris", "Jonah", "Kira", "Leo",
         "Maya", "Nico", "Omar", "Priya", "Quinn", "Rosa", "Sam", "Tara"]
ITEMS = ["apples", "pencils", "stickers", "books", "marbles", "cookies", "stamps", "cards"]

# Problems are written in English and translated whole (see puzzleth/locales). Amounts with a unit are
# filled in already worded, as each language writes money, distances and counts differently.


def _count(n, noun):
    """"12 apples": Romanian adds "de" from 20 on ("20 de mere")."""
    return f"{n} {i18n.de(n) if i18n.language() == 'ro' else ''}{i18n._(noun)}"


def _money(n):
    return {"ro": f"{n} {i18n.de(n)}lei", "fr": f"{n}\u00a0€"}.get(i18n.language(), f"${n}")


def _distance(n):
    """Miles in English; the other languages use kilometres (the sums are the same)."""
    return {"ro": f"{n} {i18n.de(n)}kilometri", "fr": f"{n}\u00a0km"}.get(i18n.language(), f"{n} miles")


def _speed(n):
    return {"ro": f"{n}\u00a0km/h", "fr": f"{n}\u00a0km/h"}.get(i18n.language(), f"{n} miles per hour")


def _tier1(r):
    name = r.choice(NAMES)
    things = i18n._(r.choice(ITEMS))
    kind = r.randrange(3)
    if kind == 0:
        a, b = r.randint(2, 9), r.randint(2, 9)
        return i18n.f("{name} has {a} {things} and gets {b} more. How many {things} does {name} have now?",
                      name=name, a=a, b=b, things=things), a + b
    if kind == 1:
        a = r.randint(8, 15)
        b = r.randint(2, a - 2)
        return i18n.f("{name} had {a} {things} and gave away {b}. How many are left?",
                      name=name, a=a, b=b, things=things), a - b
    a, b = r.randint(2, 5), r.randint(2, 5)
    return i18n.f("There are {a} bags with {b} {things} in each bag. How many {things} are there in all?",
                  a=a, b=b, things=things), a * b


def _tier2(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        price, n = r.randint(2, 9), r.randint(3, 6)
        return i18n.f("Notebooks cost {price} each. How much do {n} notebooks cost?", price=_money(price), n=n), \
            price * n
    if kind == 1:
        n, per = r.randint(3, 8), r.choice([4, 6, 8])
        total = n * per
        return i18n.f("{name} shares {cookies} equally among {per} friends. How many does each friend get?",
                      name=name, cookies=_count(total, "cookies"), per=per), n
    if kind == 2:
        a, b = r.randint(12, 45), r.randint(11, 38)
        return i18n.f("A bus has {passengers}. At the next stop, {b} more get on. How many passengers are on the bus?",
                      passengers=_count(a, "passengers"), b=b), a + b
    pay = r.choice([10, 20])
    cost = r.randint(3, pay - 2)
    return i18n.f("{name} buys a toy for {cost} and pays with a {pay} bill. How much change does {name} get?",
                  name=name, cost=_money(cost), pay=_money(pay)), pay - cost


def _tier3(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        n, price, pay = r.randint(2, 4), r.randint(3, 6), 20
        if n * price >= pay:
            n = 2
        return i18n.f("{name} buys {n} sandwiches at {price} each and pays with a {pay} bill. "
                      "How much change does {name} receive?", name=name, n=n, price=_money(price),
                      pay=_money(pay)), pay - n * price
    if kind == 1:
        speed, hours = r.choice([40, 50, 60]), r.randint(2, 5)
        return i18n.f("A car travels at {speed}. How far does it travel in {hours}?",
                      speed=_speed(speed), hours=_count(hours, "hours")), speed * hours
    if kind == 2:
        per_day, days = r.randint(4, 9), r.choice([7, 14])
        return i18n.f("{name} reads {per_day} pages every day. How many pages does {name} read in {days}?",
                      name=name, per_day=per_day, days=_count(days, "days")), per_day * days
    total, kept = r.choice([24, 30, 36, 42]), r.choice([2, 3])
    return i18n.f("{name} has {marbles} and gives {fraction} of them to a friend. "
                  "How many marbles does {name} have left?", name=name, marbles=_count(total, "marbles"),
                  fraction=i18n._("one-half" if kept == 2 else "one-third")), total - total // kept


def _tier4(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        price = r.choice([40, 60, 80, 120, 200])
        pct = r.choice([10, 25, 50])
        return i18n.f("A jacket costs {price}. It is on sale for {pct}% off. What is the sale price?",
                      price=_money(price), pct=pct), price * (100 - pct) // 100
    if kind == 1:
        workers, hours = r.choice([(4, 6), (3, 8), (6, 4), (2, 12)])
        new = r.choice([w for w in (2, 3, 4, 6, 8, 12) if (workers * hours) % w == 0 and w != workers])
        return i18n.f("{workers} workers can paint a house in {hours}. At the same rate, how many hours "
                      "would it take {new} workers?", workers=workers, hours=_count(hours, "hours"),
                      new=new), workers * hours // new
    if kind == 2:
        a, b, c = r.randint(70, 95), r.randint(70, 95), 0
        c = 3 * r.randint(78, 90) - a - b
        if not 50 <= c <= 100:
            a, b, c = 80, 90, 85
        return i18n.f("{name} scores {a}, {b} and {c} on three tests. What is {name}'s average score?",
                      name=name, a=a, b=b, c=c), (a + b + c) // 3
    rate, mins = r.choice([3, 4, 5]), r.choice([12, 15, 20])
    return i18n.f("A machine fills {rate} bottles every minute. How many bottles does it fill in {minutes}?",
                  rate=rate, minutes=_count(mins, "minutes")), rate * mins


def _tier5(r):
    name = r.choice(NAMES)
    kind = r.randrange(4)
    if kind == 0:
        orig, inc = r.choice([(40, 20), (50, 20), (60, 20), (80, 20), (40, 25), (60, 25), (80, 25)])
        new = orig * (100 + inc) // 100
        return i18n.f("After a {inc}% price increase, a lamp costs {price}. What did it cost before the increase?",
                      inc=inc, price=_money(new)), orig
    if kind == 1:
        a, b = r.choice([(2, 3), (3, 5), (1, 4), (2, 5)])
        k = r.randint(3, 8)
        return i18n.f("{name} and a friend split some money in the ratio {a} to {b}. "
                      "If {name} gets {share}, how much money was there in total?", name=name, a=a, b=b,
                      share=_money(a * k)), (a + b) * k
    if kind == 2:
        s1, s2 = r.choice([(40, 60), (30, 60), (60, 90), (30, 45)])
        d = r.choice([120, 180, 240, 300])
        while d % s1 or d % s2:
            d += 60
        return i18n.f("A train travels {distance} at {speed1}, then returns at {speed2}. "
                      "How many hours does the round trip take?", distance=_distance(d), speed1=_speed(s1),
                      speed2=_speed(s2)), d // s1 + d // s2
    n = r.choice([5, 6, 8])
    avg = r.randint(10, 20)
    drop = r.randint(4, avg - 2)
    return i18n.f("The average of {n} numbers is {avg}. When one number, {drop}, is removed, what is the sum of "
                  "the remaining numbers?", n=n, avg=avg, drop=drop), n * avg - drop


def _tier6(r):
    """Challenge levels only: multi-step problems harder than any real item."""
    name = r.choice(NAMES)
    kind = r.randrange(5)
    if kind == 0:
        price = r.choice([100, 200, 300, 400, 500])
        return i18n.f("A bike that costs {price} goes up in price by 10%, then the new price is cut by 10%. "
                      "What does it cost now?", price=_money(price)), price * 99 // 100
    if kind == 1:
        a, b = r.choice([(3, 6), (4, 12), (6, 12), (10, 15), (12, 24), (20, 30)])
        return i18n.f("One pipe fills a tank in {a}, another in {b}. How many hours do they take working together?",
                      a=_count(a, "hours"), b=_count(b, "hours")), a * b // (a + b)
    if kind == 2:
        k = r.randint(4, 12)
        return i18n.f("{name} is three times as old as a cousin. In {years}, {name} will be twice as old as the "
                      "cousin. How old is the cousin now?", name=name, years=_count(k, "years")), k
    if kind == 3:
        n = 6 * r.randint(4, 15)
        return i18n.f("Half of a number plus a third of the same number is {sum}. What is the number?",
                      sum=5 * n // 6), n
    a, b, t = r.choice([8, 10, 12, 15]), r.choice([10, 12, 15, 18, 20]), r.randint(2, 4)
    return i18n.f("Two cyclists start {distance} apart and ride towards each other at {speed1} and {speed2}. "
                  "After how many hours do they meet?", distance=_distance((a + b) * t), speed1=_speed(a),
                  speed2=_speed(b)), t


TIERS = [_tier1, _tier2, _tier3, _tier4, _tier5, _tier6]


class Arithmetic(ItemSubtest):
    code = "AR"
    name = "Arithmetic"
    index = "WMI"
    measures = "Mental manipulation, concentration and numerical reasoning"
    n_items = 22
    start_item = 6
    discontinue_n = 3
    max_raw = 22
    challenge = True
    max_level = 28
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
        # compact: the problem, then the answer with Repeat beside it, then the keypad
        self.entry = DigitEntry((T.W // 2, 300 if T.compact else 470), accent=self.accent)
        repeat = (T.W // 2 + 170, 277, 220, 46) if T.compact else (T.W // 2 - 110, 560, 220, 46)
        self.repeat_btn = Button(repeat, "Repeat", self._repeat, self.accent, hotkeys=(pygame.K_r,), size=17)
        self.keypad = Keypad(436 if T.compact else 660, [str(d) for d in range(10)] + ["Del", "OK"], self.accent,
                             key_w=84 if T.compact else 74, key_h=72 if T.compact else 64)

    def time_limit(self, n):
        return 30

    def make_item(self, n):
        tier = 0 if n == 0 else 5 if n > self.n_items else min(4, (n - 1) * 5 // self.n_items)
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
        if self.touch:
            e = self.keypad.handle(e) or e
        if self.entry.handle(e) == "submit" and self.entry.value:
            try:
                entered = int(self.entry.value)
            except ValueError:
                entered = None
            ok = (entered == self.item["ans"])
            self.submit(1 if ok else 0, "" if ok else i18n.f("Answer: {answer}", answer=self.item["ans"]))

    def on_timeout(self):
        self.submit(0, i18n.f("Time limit reached. Answer: {answer}", answer=self.item["ans"]))

    def update_item(self, dt):
        self.entry.update(dt)
        self.keypad.update(dt)
        self.repeat_btn.label = "Repeat" if self.touch else "Repeat  (R)"
        self.repeat_btn.update(dt)
        if self.item["repeated"]:
            self.repeat_btn.enabled = False

    def draw_item(self, surf):
        rect = pygame.Rect(0, 0, 1000, 180) if T.compact else pygame.Rect(0, 0, 900, 200)
        rect.center = (T.W // 2, 162 if T.compact else 270)
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
            again = "(tap Repeat to see it once more)" if self.touch else "(press R to hear it once more)"
            gfx.text(surf, again if not self.item["repeated"] else "(already repeated)",
                     (rect.centerx, rect.centery + 34), 16, T.DIM, anchor="center")
        self.entry.draw(surf, label="your answer")
        if self.touch and self.state == "item":
            self.keypad.draw(surf)
        if self.state == "item" and not self.item["repeated"] and self.item_t >= self.item["read"]:
            self.repeat_btn.draw(surf)
