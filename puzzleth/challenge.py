"""Challenge modes: rated puzzle sets and the daily challenge.

Both run a subtest as a *ladder*: a fixed-length set of puzzles at chosen difficulty levels,
instead of the WAIS start/reversal/discontinue rules. Levels go past the real test's last item
(up to the subtest's ``max_level``), so the difficulty keeps climbing.

Puzzle rating works like a chess puzzle rating (Elo). Each level has a nominal rating and your
rating moves after every puzzle by how surprising the result was. It is relative to this game
only: it says how hard a puzzle you can solve here about half the time.
"""
import datetime
import random

SET_LENGTH = 10
START_RATING = 1000
FLOOR = 100
PROVISIONAL = 20       # puzzles before the rating settles
K_PROVISIONAL = 48
K_SETTLED = 28
DAILY_EPOCH = datetime.date(2026, 1, 1)


def level_rating(level, n_items):
    """Nominal rating of a difficulty level: item 1 ~ 650, the real test's last item = 1800."""
    return 600 + 1200 * level / n_items


def level_for(rating, n_items, max_level):
    return max(1, min(max_level, round((rating - 600) * n_items / 1200)))


def expected(rating, opp):
    return 1 / (1 + 10 ** ((opp - rating) / 400))


def update(rating, opp, solved, played):
    k = K_PROVISIONAL if played < PROVISIONAL else K_SETTLED
    return max(FLOOR, rating + k * ((1.0 if solved else 0.0) - expected(rating, opp)))


def challenge_codes():
    from .subtests import ORDER
    return [cls.code for cls in ORDER if getattr(cls, "challenge", False)]


def daily_number(day):
    return (day - DAILY_EPOCH).days + 1


def daily_code(day):
    codes = challenge_codes()
    return codes[daily_number(day) % len(codes)]


def daily_levels(n_items, max_level, length=SET_LENGTH):
    """An easy-to-brutal ramp from a quarter of the way into the real test to past its end."""
    return [max(1, min(max_level, round(n_items * (0.25 + 0.95 * i / (length - 1))))) for i in range(length)]


class Ladder:
    kind = ""

    def __init__(self, cls):
        self.cls = cls
        self.results = []    # [(level, solved)]
        self.length = SET_LENGTH

    @property
    def position(self):
        return len(self.results)

    def next_level(self):
        raise NotImplementedError

    def item_seed(self):
        return None

    def record(self, level, solved):
        self.results.append((level, solved))

    @property
    def solved(self):
        return sum(1 for _, s in self.results if s)

    def label(self):
        return ""


class RatedLadder(Ladder):
    kind = "rated"

    def __init__(self, cls, rating=START_RATING, played=0, rng=None):
        super().__init__(cls)
        self.start = self.rating = rating
        self.played = played
        self.rng = rng or random.Random()

    def next_level(self):
        if self.position >= self.length:
            return None
        base = level_for(self.rating, self.cls.n_items, self.cls.max_level)
        return max(1, min(self.cls.max_level, base + self.rng.choice((-1, 0, 0, 1))))

    def record(self, level, solved):
        super().record(level, solved)
        self.rating = update(self.rating, level_rating(level, self.cls.n_items), solved, self.played)
        self.played += 1

    def label(self):
        return "Rated set"


class DailyLadder(Ladder):
    kind = "daily"

    def __init__(self, day=None):
        from .subtests import BY_CODE
        self.day = day or datetime.date.today()
        super().__init__(BY_CODE[daily_code(self.day)])
        self.number = daily_number(self.day)
        self.levels = daily_levels(self.cls.n_items, self.cls.max_level, self.length)

    def next_level(self):
        return self.levels[self.position] if self.position < self.length else None

    def item_seed(self):
        # every puzzle has its own seed, so everyone gets the same puzzles whatever they answer
        return f"daily-{self.day.isoformat()}-{self.position}"

    def label(self):
        return f"Daily #{self.number}"

    def share_text(self):
        squares = "".join("\U0001F7E9" if s else "\U0001F7E5" for _, s in self.results)
        return f"Puzzleth Daily #{self.number} · {self.cls.name}\n{self.solved}/{self.length} {squares}"
