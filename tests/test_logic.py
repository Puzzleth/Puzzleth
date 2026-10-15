"""Correctness tests: administration rules, scoring math and procedural generators.

Run with:  python -m unittest discover -s tests
"""
import datetime
import hashlib
import os
import random
import re
import subprocess
import sys
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ["PUZZLETH_HOME"] = os.path.join(tempfile.mkdtemp(), "profile.json")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1280, 800))

from puzzleth import challenge, glyphs, scoring  # noqa: E402
from puzzleth.storage import Profile  # noqa: E402
from puzzleth.content import verbal as bank  # noqa: E402
from puzzleth.subtests import ORDER, arithmetic, block_design as bd  # noqa: E402
from puzzleth.subtests.base import ItemSubtest  # noqa: E402
from puzzleth.subtests.digit_span import DigitSpan  # noqa: E402
from puzzleth.subtests.matrix_reasoning import MatrixReasoning, _visible_key  # noqa: E402
from puzzleth.subtests.speed import Coding, SymbolSearch  # noqa: E402
from puzzleth.subtests.visual_puzzles import VisualPuzzles, rotations, tiles  # noqa: E402


class FakeApp:
    def __init__(self):
        self.result = None

    def subtest_done(self, sub, raw, details):
        self.result = (raw, details)

    def ladder_done(self, sub):
        self.result = sub.ladder


class Scripted(ItemSubtest):
    """An item subtest whose answers come from a script {item: points}."""
    n_items = 14
    start_item = 5
    discontinue_n = 2
    has_sample = False

    def make_item(self, n):
        return n

    def item_max(self, n):
        return 2


def run_script(cls, script):
    app = FakeApp()
    s = cls(app, feedback=False, seed=1)
    order = []
    while app.result is None:
        order.append(s.cur)
        s.submit(script(s.cur))
        s._advance()
    return app.result[0], order, s


class Sounds(unittest.TestCase):
    def test_every_documented_sound_is_bundled(self):
        from puzzleth import sound
        with open(os.path.join(ROOT, "puzzleth", "sounds", "README.md")) as f:
            names = {n for line in f if line.startswith("| `") for n in
                     re.findall(r"`(\w+)`", line.split("|")[1])}
        names |= {f"digit{d}" for d in range(1, 10)}
        self.assertLessEqual(names, set(sound._sound_files()))

    def test_ticks_once_per_second_in_the_last_five(self):
        from puzzleth import sound
        from puzzleth.subtests import base
        played = []
        old = sound.play
        sound.play = played.append
        try:
            t = 8.0
            while t > 0:
                base.tick_last_seconds(t, t - 1 / 60)
                t -= 1 / 60
        finally:
            sound.play = old
        self.assertEqual(played, ["tick"] * 5)


class AdministrationRules(unittest.TestCase):
    def test_all_perfect_gets_full_credit_below_start(self):
        raw, order, _ = run_script(Scripted, lambda n: 2)
        self.assertEqual(order, list(range(5, 15)))
        self.assertEqual(raw, 28)

    def test_reversal_until_two_consecutive_perfect(self):
        raw, order, _ = run_script(Scripted, lambda n: 0 if n == 5 else 2)
        # 5 fails, 6 passes -> reverse: 4 (perfect but 5 isn't) -> 3 (3,4 perfect) -> resume at 7
        self.assertEqual(order[:4], [5, 6, 4, 3])
        self.assertEqual(order[4], 7)
        self.assertEqual(raw, 28 - 2)  # only item 5 lost; items 1-2 credited

    def test_reversal_to_item_one_gives_no_free_credit(self):
        raw, order, _ = run_script(Scripted, lambda n: 1)
        self.assertEqual(order[:6], [5, 6, 4, 3, 2, 1])
        self.assertEqual(raw, 14)  # 14 items * 1 point, nothing credited

    def test_discontinue_after_consecutive_zeros(self):
        raw, order, _ = run_script(Scripted, lambda n: 0 if n >= 8 else 2)
        self.assertEqual(order, [5, 6, 7, 8, 9])
        self.assertEqual(raw, 7 * 2)

    def test_zeros_at_start_reverse_then_discontinue(self):
        raw, order, _ = run_script(Scripted, lambda n: 0 if n >= 5 else 2)
        self.assertEqual(order, [5, 6, 4, 3])
        self.assertEqual(raw, 8)  # items 3-4 earned (4) + items 1-2 credited below the basal (4)

    def test_every_item_subtest_max_raw_is_reachable(self):
        for cls in ORDER:
            if not issubclass(cls, ItemSubtest):
                continue
            raw, _, _ = run_script(cls, lambda n, c=cls: c.item_max(c, n))
            self.assertEqual(raw, cls.max_raw, cls.code)
            raw0, _, _ = run_script(cls, lambda n: 0)
            self.assertEqual(raw0, 0, cls.code)


class Scoring(unittest.TestCase):
    def test_mean_raw_maps_to_scaled_ten(self):
        for code, (mean, _) in scoring.NORMS.items():
            self.assertEqual(scoring.scaled_score(code, mean), 10, code)

    def test_scaled_is_monotonic_and_clamped(self):
        for code, cls in ((c.code, c) for c in ORDER):
            vals = [scoring.scaled_score(code, r) for r in range(0, cls.max_raw + 1)]
            self.assertEqual(vals, sorted(vals), code)
            self.assertTrue(all(1 <= v <= 19 for v in vals))

    def test_composites(self):
        all10 = {c.code: 10 for c in ORDER}
        idx, fs = scoring.compute_indexes(all10)
        self.assertEqual(fs, 100)
        self.assertEqual(set(idx.values()), {100})
        # composites of several above-average subtests are more extreme than any single one
        all13 = {c.code: 13 for c in ORDER}
        idx, fs = scoring.compute_indexes(all13)
        self.assertTrue(115 < idx["VCI"] < 120)
        self.assertTrue(118 < fs < 124)
        self.assertEqual(scoring.compute_indexes({"SI": 10})[1], None)

    def test_percentile_and_labels(self):
        self.assertAlmostEqual(scoring.percentile(100), 50, places=6)
        self.assertAlmostEqual(scoring.percentile(115), 84.13, places=1)
        self.assertAlmostEqual(scoring.scaled_percentile(13), 84.13, places=1)
        self.assertEqual(scoring.classification(130), "Very Superior")
        self.assertEqual(scoring.classification(129), "Superior")
        self.assertEqual(scoring.classification(90), "Average")
        self.assertEqual(scoring.classification(89), "Low Average")
        self.assertEqual(scoring.classification(69), "Extremely Low")


class BlockDesignTests(unittest.TestCase):
    # red region of each face as the set of square corners it touches fully
    CORNERS = {bd.TL: {"tl", "tr", "bl"}, bd.TR: {"tl", "tr", "br"}, bd.BR: {"tr", "br", "bl"},
               bd.BL: {"tl", "bl", "br"}}
    CW = {"tl": "tr", "tr": "br", "br": "bl", "bl": "tl"}
    MH = {"tl": "tr", "tr": "tl", "bl": "br", "br": "bl"}
    MV = {"tl": "bl", "bl": "tl", "tr": "br", "br": "tr"}

    def _check_map(self, table, corner_map):
        for f, corners in self.CORNERS.items():
            self.assertEqual({corner_map[c] for c in corners}, self.CORNERS[table[f]])

    def test_4x4_rotational_designs_are_symmetric(self):
        app = FakeApp()
        found = 0
        for seed in range(300):
            s = bd.BlockDesign(app, seed=seed)
            g = s._gen4(15)
            # turning the whole design a quarter turn clockwise: cell (y, x) moves to (x, 3 - y)
            turned = [[None] * 4 for _ in range(4)]
            for y in range(4):
                for x in range(4):
                    turned[x][3 - y] = bd.rot(g[y][x])
            mirrored = [[bd.MIRROR_H.get(f, f) for f in reversed(row)] for row in g]
            self.assertTrue(turned == g or mirrored == g, g)
            found += turned == g
        self.assertGreater(found, 50)

    def test_face_transforms_are_geometric(self):
        self._check_map(bd.ROT, self.CW)
        self._check_map(bd.MIRROR_H, self.MH)
        self._check_map(bd.MIRROR_V, self.MV)

    def test_designs_are_nontrivial(self):
        app = FakeApp()
        for seed in range(150):
            s = bd.BlockDesign(app, seed=seed)
            for n in range(0, bd.BlockDesign.max_level + 1):
                it = s.make_item(n)
                flat = [f for row in it["design"] for f in row]
                self.assertGreaterEqual(len(set(flat)), 2)
                self.assertEqual(it["size"], 2 if n <= 8 else 3 if n <= 14 else 4)
                self.assertNotEqual(it["work"], it["design"])
                if n > 2:
                    self.assertTrue(any(f in bd.DIAG for f in flat))


class MatrixTests(unittest.TestCase):
    def test_answer_unique_and_follows_rules(self):
        app = FakeApp()
        for seed in range(120):
            s = MatrixReasoning(app, seed=seed)
            for n in range(0, MatrixReasoning.max_level + 1):
                it = s.make_item(n)
                opts = it["options"]
                self.assertEqual(len(opts), 5)
                keys = [_visible_key(o) for o in opts]
                self.assertEqual(len(set(keys)), 5, f"duplicate options seed={seed} n={n}")
                size = it["size"]
                self.assertEqual(opts[it["answer"]], it["grid"][size - 1][size - 1])
                self._check_rows(it["grid"])

    def _check_rows(self, grid):
        # every attribute is either constant, constant per row, constant per column, or a Latin square
        attrs = grid[0][0].keys()
        size = len(grid)
        for a in attrs:
            vals = [[c[a] for c in row] for row in grid]
            row_const = all(len(set(r)) == 1 for r in vals)
            col_const = all(len({vals[y][x] for y in range(size)}) == 1 for x in range(size))
            latin = size == 3 and all(len(set(r)) == 3 for r in vals) and \
                all(len({vals[y][x] for y in range(3)}) == 3 for x in range(3))
            self.assertTrue(row_const or col_const or latin, a)


class VisualPuzzleTests(unittest.TestCase):
    def test_tiling_solver(self):
        sq = frozenset({(0, 0), (1, 0), (0, 1), (1, 1)})
        dom = frozenset({(0, 0), (1, 0)})
        vdom = frozenset({(0, 0), (0, 1)})
        self.assertTrue(tiles(sq, [dom, vdom]))      # needs a rotation
        self.assertFalse(tiles(sq, [dom, frozenset({(0, 0)})]))
        L = frozenset({(0, 0), (0, 1), (1, 1)})
        S = frozenset({(1, 0), (2, 0), (0, 1), (1, 1)})
        self.assertEqual(len(rotations(L)), 4)
        self.assertEqual(len(rotations(S)), 2)
        # mirror image of an S can't be produced by rotation alone
        Z = frozenset({(0, 0), (1, 0), (1, 1), (2, 1)})
        self.assertNotIn(Z, rotations(S))

    def test_exactly_one_solution(self):
        from itertools import combinations
        app = FakeApp()
        for seed in range(40):
            s = VisualPuzzles(app, seed=seed)
            for n in list(range(0, 27, 2)) + list(range(27, VisualPuzzles.max_level + 1)):
                it = s.make_item(n)
                pcs = it["pieces"]
                sols = [set(c) for c in combinations(range(6), 3) if tiles(it["target"], [pcs[i] for i in c])]
                self.assertEqual(sols, [it["correct"]])


class ArithmeticTests(unittest.TestCase):
    def test_answers_are_positive_integers(self):
        for seed in range(3000):
            r = random.Random(seed)
            for tier in arithmetic.TIERS:
                q, ans = tier(r)
                self.assertIsInstance(ans, int, q)
                self.assertGreater(ans, 0, q)

    def test_specific_templates(self):
        # brute-force check a few templates against an independent calculation
        for seed in range(500):
            r = random.Random(seed)
            q, ans = arithmetic._tier5(r)
            if "price increase" in q:
                pct = int(q.split("%")[0].split()[-1])
                new = int(q.split("$")[1].split(".")[0])
                self.assertEqual(ans * (100 + pct), new * 100, q)
            if "round trip" in q:
                nums = [int(w) for w in q.replace(",", "").split() if w.isdigit()]
                d, s1, s2 = nums
                self.assertEqual(ans, d / s1 + d / s2, q)

    def test_challenge_templates(self):
        for seed in range(500):
            q, ans = arithmetic._tier6(random.Random(seed))
            nums = [int(w.strip("$%,.?")) for w in q.split() if w.strip("$%,.?").isdigit()]
            if "bike" in q:
                self.assertEqual(ans * 100, nums[0] * 110 * 90 // 100, q)
            elif "pipe" in q:
                a, b = nums
                self.assertAlmostEqual(ans, 1 / (1 / a + 1 / b), msg=q)
            elif "cousin" in q:
                k = nums[0]
                self.assertEqual(3 * ans + k, 2 * (ans + k), q)
            elif "Half of" in q:
                self.assertEqual(ans / 2 + ans / 3, nums[0], q)
            else:
                d, a, b = nums
                self.assertEqual(ans * (a + b), d, q)


class SpeedTests(unittest.TestCase):
    def test_symbol_search_items(self):
        app = FakeApp()
        s = SymbolSearch(app, seed=3)
        for _ in range(2000):
            s.new_item()
            it = s.item
            hits = sum(g in it["targets"] for g in it["group"])
            self.assertEqual(hits, 1 if it["present"] else 0)
            self.assertEqual(len(set(it["group"])), 5)

    def test_symbol_search_score(self):
        app = FakeApp()
        s = SymbolSearch(app, seed=3)
        s.state = "run"
        for ok in [True] * 10 + [False] * 4:
            s.answer(ok)
        self.assertEqual(s.score(), 6)

    def test_coding_key_and_sequence(self):
        app = FakeApp()
        s = Coding(app, seed=5)
        self.assertEqual(len(s.key), 9)
        for i in range(9):
            for j in range(i + 1, 9):
                self.assertGreaterEqual(glyphs.distance(s.key[i], s.key[j]), 3)
        self.assertEqual(len(s.seq), 135)
        self.assertTrue(all(a != b for a, b in zip(s.seq, s.seq[1:])))

    def test_glyph_variants_differ(self):
        r = random.Random(0)
        for _ in range(2000):
            g = glyphs.random_glyph(r)
            v = glyphs.variant(r, g)
            self.assertNotEqual(v, g)
            # glyphs are drawn centred, so they must be stored translation-normalised:
            # equal data <=> identical appearance
            self.assertEqual(glyphs.normalize(v), v)
            self.assertEqual(glyphs.normalize(g), g)


class DigitSpanTests(unittest.TestCase):
    def test_targets(self):
        app = FakeApp()
        s = DigitSpan(app, seed=2)
        for task_i in range(3):
            s.task_i = task_i
            s.item_i = 3
            for _ in range(50):
                s._new_trial()
                name = s.task[0]
                expect = {"Forward": s.seq, "Backward": s.seq[::-1], "Sequencing": sorted(s.seq)}[name]
                self.assertEqual(s.target, expect)
                self.assertEqual(len(s.seq), s.task[1][3])
                self.assertTrue(all(a != b for a, b in zip(s.seq, s.seq[1:])))

    def test_perfect_run_scores_max(self):
        app = FakeApp()
        s = DigitSpan(app, seed=4)
        while app.result is None:
            if s.state in ("intro",):
                s._new_trial()
            s.entry.value = "".join(map(str, s.target))
            s._submit()
            s._after_feedback()
        self.assertEqual(app.result[0], DigitSpan.max_raw)


class ContentTests(unittest.TestCase):
    def test_banks_are_large_enough(self):
        for tier in range(1, 7):
            self.assertGreaterEqual(len(bank.SIMILARITIES[tier]), 3)
            self.assertGreaterEqual(len(bank.VOCABULARY[tier]), 5)
            self.assertGreaterEqual(len(bank.INFORMATION[tier]), 5)
            for members, two, one, zero in bank.SIMILARITIES[tier]:
                self.assertGreaterEqual(len(members), 2)
                self.assertEqual(len({two, one, zero}), 3)
            for q, ans, wrong in bank.INFORMATION[tier]:
                self.assertNotIn(ans, wrong)
                self.assertEqual(len(set(wrong)), 3)

    def test_choice_items_have_one_best_answer(self):
        app = FakeApp()
        for cls in [c for c in ORDER if c.code in ("SI", "VC", "IN")]:
            for seed in range(30):
                s = cls(app, seed=seed)
                for n in range(0, cls.n_items + 1):
                    it = s.make_item(n)
                    pts = [p for _, p in it["options"]]
                    texts = [t for t, _ in it["options"]]
                    self.assertEqual(len(set(texts)), 4)
                    self.assertEqual(max(pts), s.item_max(n))
                    self.assertEqual(pts.count(max(pts)), 1)


class ChallengeTests(unittest.TestCase):
    def test_rating_math(self):
        self.assertAlmostEqual(challenge.expected(1200, 1200), 0.5)
        self.assertAlmostEqual(challenge.expected(1400, 1200) + challenge.expected(1200, 1400), 1.0)
        self.assertGreater(challenge.update(1000, 1000, True, 0), 1000)
        self.assertLess(challenge.update(1000, 1000, False, 0), 1000)
        # beating a much harder puzzle is worth more than beating an easy one
        self.assertGreater(challenge.update(1000, 1400, True, 50) - 1000, challenge.update(1000, 600, True, 50) - 1000)
        self.assertEqual(challenge.update(challenge.FLOOR, 2000, False, 50), challenge.FLOOR)
        for n_items in (14, 22, 26):
            for level in range(1, n_items + 1):
                self.assertEqual(challenge.level_for(challenge.level_rating(level, n_items), n_items, 99), level)
            self.assertEqual(challenge.level_rating(n_items, n_items), 1800)

    def test_rated_set_runs_ten_puzzles_and_adapts(self):
        for cls in (MatrixReasoning, VisualPuzzles, bd.BlockDesign, arithmetic.Arithmetic):
            for solve in (True, False):
                app = FakeApp()
                lad = challenge.RatedLadder(cls, 1000, 0, random.Random(1))
                s = cls(app, ladder=lad)
                levels = []
                while app.result is None:
                    levels.append(s.cur)
                    self.assertTrue(1 <= s.cur <= cls.max_level)
                    s.submit(1 if solve else 0)
                    s._advance()
                self.assertEqual(len(lad.results), challenge.SET_LENGTH)
                self.assertEqual(s.scores, {})   # WAIS scoring is untouched by ladders
                self.assertIsNone(app.result.next_level())
                if solve:
                    self.assertGreater(lad.rating, 1000)
                    self.assertGreater(levels[-1], levels[0])
                else:
                    self.assertLess(lad.rating, 1000)
                    self.assertLessEqual(levels[-1], levels[0])

    def test_rating_converges_on_ability(self):
        # a player who solves everything up to level 15 and nothing above settles near level 15
        lad = challenge.RatedLadder(MatrixReasoning, 1000, 0, random.Random(2))
        lad.length = 400
        while (lv := lad.next_level()) is not None:
            lad.record(lv, lv <= 15)
        self.assertAlmostEqual(challenge.level_for(lad.rating, 26, 32), 15.5, delta=1.5)

    def test_daily_rotates_through_challenge_subtests(self):
        day = datetime.date(2026, 3, 1)
        codes = {challenge.daily_code(day + datetime.timedelta(days=i)) for i in range(4)}
        self.assertEqual(codes, set(challenge.challenge_codes()))
        self.assertEqual(challenge.daily_number(challenge.DAILY_EPOCH), 1)
        for cls in (MatrixReasoning, VisualPuzzles, bd.BlockDesign, arithmetic.Arithmetic):
            lv = challenge.daily_levels(cls.n_items, cls.max_level)
            self.assertEqual(lv, sorted(lv))
            self.assertGreater(lv[-1], cls.n_items)

    def _daily_fingerprint(self, day, answers):
        app = FakeApp()
        lad = challenge.DailyLadder(day)
        s = lad.cls(app, ladder=lad)
        items = []
        while app.result is None:
            items.append(repr(_item_signature(s.item)))
            s.submit(answers.pop(0))
            s._advance()
        return items

    def test_daily_puzzles_are_the_same_whatever_you_answer(self):
        for i in range(4):
            day = datetime.date(2026, 5, 1) + datetime.timedelta(days=i)
            a = self._daily_fingerprint(day, [1] * 10)
            b = self._daily_fingerprint(day, [0, 1] * 5)
            self.assertEqual(a, b)
            self.assertNotEqual(a, self._daily_fingerprint(day + datetime.timedelta(days=4), [1] * 10))

    def test_daily_puzzles_do_not_depend_on_hash_seed(self):
        code = ("import sys, os, datetime, hashlib; sys.path.insert(0, %r); sys.path.insert(0, %r);"
                "os.environ['SDL_VIDEODRIVER'] = 'dummy';"
                "import pygame; pygame.init(); pygame.display.set_mode((10, 10));"
                "import test_logic as t;"
                "fp = [t.ChallengeTests()._daily_fingerprint(datetime.date(2026, 5, 1) + datetime.timedelta(days=i),"
                " [1] * 10) for i in range(4)];"
                "print(hashlib.sha256(repr(fp).encode()).hexdigest())") % (ROOT, os.path.dirname(__file__))
        out = set()
        for hs in ("1", "2"):
            env = dict(os.environ, PYTHONHASHSEED=hs, PYGAME_HIDE_SUPPORT_PROMPT="1")
            out.add(subprocess.run([sys.executable, "-c", code], env=env, capture_output=True, text=True,
                                   check=True).stdout.strip())
        self.assertEqual(len(out), 1)


def _item_signature(item):
    """A hash-order-independent description of a generated item."""
    def norm(v):
        if isinstance(v, (set, frozenset)):
            return sorted(norm(x) for x in v)
        if isinstance(v, dict):
            return sorted((k, norm(x)) for k, x in v.items())
        if isinstance(v, (list, tuple)):
            return [norm(x) for x in v]
        return v
    return hashlib.sha256(repr(norm(item)).encode()).hexdigest()


class ProfileTests(unittest.TestCase):
    def setUp(self):
        self.path = os.path.join(tempfile.mkdtemp(), "profile.json")
        os.environ["PUZZLETH_HOME"] = self.path

    def test_daily_first_try_counts_and_streak(self):
        p = Profile()
        d = datetime.date(2026, 6, 10)
        self.assertTrue(p.record_daily(d, "MR", [(5, True), (6, False)]))
        self.assertFalse(p.record_daily(d, "MR", [(5, True), (6, True)]))
        self.assertEqual(p.daily_result(d)["solved"], 1)
        p.record_daily(d - datetime.timedelta(days=1), "VP", [(5, True)])
        p.record_daily(d - datetime.timedelta(days=3), "VP", [(5, True)])
        self.assertEqual(p.daily_streak(d), 2)
        self.assertEqual(p.daily_streak(d + datetime.timedelta(days=1)), 2)   # today not played yet
        self.assertEqual(p.daily_streak(d + datetime.timedelta(days=2)), 0)
        self.assertEqual(Profile().daily_streak(d), 2)                          # persisted

    def test_rating_peak_and_old_profiles(self):
        with open(self.path, "w") as f:
            f.write('{"subtests": {}, "batteries": [], "settings": {"feedback": false}}')
        p = Profile()
        self.assertEqual(p.settings["feedback"], False)
        self.assertTrue(p.settings["show_scores"])
        p.set_rating("MR", 1100, 10)
        p.set_rating("MR", 1050, 11)
        self.assertEqual(p.rating("MR"), {"rating": 1050, "played": 11, "peak": 1100})

    def test_first_player_keeps_progress_from_before_names(self):
        with open(self.path, "w") as f:
            f.write('{"subtests": {"MR": {"history": [], "best": 9}}, "batteries": [],'
                    ' "settings": {"feedback": false, "music_volume": 0.25}}')
        p = Profile()
        self.assertIsNone(p.current)
        self.assertTrue(p.add_player("lu ca!"))
        self.assertEqual(p.current, "LUCA")
        self.assertEqual(p.best_scaled("MR"), 9)
        self.assertFalse(p.settings["feedback"])
        p.add_player("ALEX")                       # a fresh start, with the device's volume
        self.assertEqual(p.best_scaled("MR"), 0)
        self.assertTrue(p.settings["feedback"])
        self.assertEqual(p.settings["music_volume"], 0.25)
        p.settings["show_scores"] = False
        p.switch("LUCA")
        self.assertTrue(p.settings["show_scores"])
        q = Profile()                              # persisted, with the last player chosen
        self.assertEqual((q.current, q.players()), ("LUCA", ["LUCA", "ALEX"]))
        self.assertFalse(q.player("ALEX")["settings"]["show_scores"])

    def test_names_and_removing_players(self):
        p = Profile()
        self.assertEqual(p.can_add(""), "Enter at least one letter")
        p.add_player("SAM")
        self.assertFalse(p.add_player("sam"))      # names are capitals, so this is SAM again
        p.add_player("ALEX")
        p.remove_player("ALEX")                    # the current player: back to whoever played last
        self.assertEqual((p.current, p.players()), ("SAM", ["SAM"]))
        p.remove_player("SAM")
        self.assertIsNone(p.current)
        self.assertEqual(p.best_scaled("MR"), 0)

    def test_arcade_name_entry(self):
        from puzzleth.app import App
        from puzzleth.scenes import MenuScene, NameEntryScene
        app = App(pygame.display.get_surface())
        scene = NameEntryScene(app)

        def key(k, ch=""):
            scene.handle_event(pygame.event.Event(pygame.KEYDOWN, key=k, unicode=ch, mod=0, scancode=0))
        key(pygame.K_b, "b")
        for k in (pygame.K_UP, pygame.K_UP, pygame.K_RIGHT, pygame.K_DOWN):   # C, D, locked; then C
            key(k)
        key(pygame.K_RETURN)
        self.assertEqual(app.profile.current, "BDC")
        self.assertIsInstance(app.scene, MenuScene)


class FakeLeaderboard:
    """A stand-in for the leaderboard server (server/src/index.js) on a local port."""

    def __init__(self):
        import http.server
        import json
        import threading
        board = self
        self.players = {}   # token -> name
        self.joined = 0
        self.agents = set()
        self.ratings = {}   # (token, code) -> {"rating", "played"}
        self.refuse = None  # an HTTP status to answer rating posts with
        self.log = []

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def _answer(self, status, data=None):
                body = json.dumps(data).encode() if data is not None else b""
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def _handle(self):
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(n)) if n else None
                token = (self.headers.get("Authorization") or "").removeprefix("Bearer ")
                board.log.append((self.command, self.path))
                board.agents.add(self.headers.get("User-Agent", ""))
                if self.command == "POST" and self.path == "/players":
                    board.joined += 1
                    tok = f"tok{board.joined}"
                    board.players[tok] = body["name"]
                    return self._answer(201, {"id": tok, "name": body["name"], "tag": "AB23", "token": tok})
                if token not in board.players:
                    return self._answer(401, {"error": "unknown player"})
                if self.command == "DELETE":
                    del board.players[token]
                    return self._answer(204)
                code = self.path.split("/")[2][:2]
                if self.command == "PUT":
                    if board.refuse:
                        return self._answer(board.refuse, {"error": "no"})
                    board.ratings[(token, code)] = body
                    return self._answer(200, {"rank": 1, "total": 1})
                me = board.ratings.get((token, code))
                return self._answer(200, {"code": code, "total": 1, "top": [], "me": me})

            do_GET = do_POST = do_PUT = do_DELETE = _handle

        self.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        self.url = f"http://127.0.0.1:{self.server.server_port}"

    def close(self):
        self.server.shutdown()
        self.server.server_close()


class OnlineTests(unittest.TestCase):
    def setUp(self):
        os.environ["PUZZLETH_HOME"] = os.path.join(tempfile.mkdtemp(), "profile.json")
        self.board = FakeLeaderboard()
        os.environ["PUZZLETH_SERVER"] = self.board.url
        from puzzleth.online import Online
        self.profile = Profile()
        self.profile.add_player("ANA")
        self.online = Online(self.profile)

    def tearDown(self):
        os.environ.pop("PUZZLETH_SERVER", None)
        self.board.close()

    def settle(self):
        """Wait for every request to be answered."""
        import time
        for _ in range(500):
            self.online.poll()
            if not self.online.pending:
                return
            time.sleep(0.01)
        self.fail("requests never finished")

    def test_nothing_is_sent_until_a_player_joins(self):
        self.profile.set_rating("MR", 1100, 10)
        self.online.push()
        self.online.flush()
        self.settle()
        self.assertEqual(self.board.log, [])
        self.assertIsNone(self.online.account())

    def test_joining_posts_ratings_once(self):
        self.profile.set_rating("MR", 1100, 10)
        self.profile.set_rating("VP", 950, 12)
        done = []
        self.online.join(then=lambda: done.append(True))
        self.settle()
        self.assertEqual(done, [True])
        acct = self.online.account()
        self.assertEqual((acct["tag"], acct["sent"]), ("AB23", {"MR": 10, "VP": 12}))
        self.assertEqual(self.board.ratings[("tok1", "MR")], {"rating": 1100, "played": 10})
        self.assertEqual(self.online.rank("MR"), {"rank": 1, "total": 1})
        n = len(self.board.log)
        self.online.push()                 # nothing new
        self.settle()
        self.assertEqual(len(self.board.log), n)
        self.profile.set_rating("MR", 1120, 11)
        self.online.push()
        self.settle()
        self.assertEqual(self.board.ratings[("tok1", "MR")]["played"], 11)
        self.assertEqual(Profile().player("ANA")["online"]["sent"]["MR"], 11)   # saved
        # Cloudflare refuses Python's default User-Agent with a 403
        self.assertTrue(all(ua.startswith("Puzzleth") for ua in self.board.agents), self.board.agents)

    def test_refused_and_forgotten_ratings(self):
        self.online.join()
        self.settle()
        self.profile.set_rating("MR", 1100, 10)
        self.board.refuse = 409            # refused for good: not sent again
        self.online.push()
        self.settle()
        self.assertEqual(self.online.account()["sent"], {"MR": 10})
        self.profile.set_rating("MR", 1110, 11)
        self.board.refuse = 401            # the server lost them: they're no longer on it
        self.online.push()
        self.settle()
        self.assertIsNone(self.online.account())

    def test_leaving_and_removing_delete_from_the_server(self):
        self.online.join()
        self.settle()
        self.online.leave()
        self.assertIsNone(self.online.account())
        self.settle()
        self.assertEqual((self.board.players, self.profile.root["forget"]), ({}, []))
        self.profile.add_player("BO")
        self.online.join()
        self.settle()
        self.profile.remove_player("BO")
        self.assertEqual(self.profile.root["forget"], ["tok2"])
        self.online.flush()
        self.settle()
        self.assertEqual((self.board.players, Profile().root["forget"]), ({}, []))

    def test_unreachable_server(self):
        self.board.close()
        self.profile.set_rating("MR", 1100, 10)
        self.online.join()
        self.settle()
        self.assertIsNone(self.online.account())
        self.assertIn("Couldn't reach", self.online.error)
        got = []
        self.online.board("MR", got.append)
        self.settle()
        self.assertEqual(got[0].status, 0)

    def test_an_address_that_isnt_a_web_address(self):
        from puzzleth import online
        os.environ["PUZZLETH_SERVER"] = "22961002-afbb-44a9-951f-5d5190bfab3f"   # a D1 database id
        got = []
        self.online.board("MR", got.append)
        self.settle()
        self.assertEqual(got[0].status, 0)
        self.assertIn("isn't a web address", online.describe(got[0]))
        self.assertEqual(self.board.log, [])

    def test_leaderboard_scene(self):
        from puzzleth import theme
        from puzzleth.app import App
        from puzzleth.scenes import LeaderboardScene, MenuScene
        app = App(pygame.display.get_surface())
        app.online = self.online
        app.profile = self.profile
        rows = [{"rank": i + 1, "id": f"p{i}", "name": f"P{i}", "tag": "XY23", "rating": 1500 - 10 * i,
                 "played": 40} for i in range(10)]
        me = {"id": "tok1", "name": "ANA", "tag": "AB23", "rank": 42, "rating": 1100, "played": 30, "peak": 1150}
        for compact in (False, True):
            theme.set_compact(compact)
            try:
                menu = MenuScene(app)
                self.assertIn("Leaderboard", [b.label for b in menu.buttons])
                labels = [b for b in menu.buttons if b.label]
                for i, b in enumerate(labels):
                    self.assertTrue(pygame.Rect(0, 0, theme.W, theme.H).contains(b.rect), b.label)
                    for other in labels[i + 1:]:
                        self.assertFalse(b.rect.colliderect(other.rect), (b.label, other.label))
                scene = LeaderboardScene(app, "VP")
                self.assertEqual(scene.code, "VP")
                surf = pygame.Surface((theme.W, theme.H))
                scene.draw(surf)                                      # loading
                self.settle()
                scene.update(0.1)
                self.assertIn(scene.join_btn, scene.buttons)
                scene.boards["VP"] = {"code": "VP", "total": 50, "top": rows, "me": None}
                scene.draw(surf)
                self.online.join()
                self.settle()
                scene.update(0.1)
                self.assertIn(scene.leave_btn, scene.buttons)
                scene.boards["VP"] = {"code": "VP", "total": 50, "top": rows, "me": me}
                scene.draw(surf)
                scene.errors["MR"] = "nope"
                scene.code = "MR"
                scene.draw(surf)
                for b in scene.buttons:
                    self.assertTrue(pygame.Rect(0, 0, theme.W, theme.H).contains(b.rect), b.label)
                scene._leave()
                self.assertIsNotNone(self.online.account())           # the first tap only asks
                scene._leave()
                self.assertIsNone(self.online.account())
                self.settle()
            finally:
                theme.set_compact(False)


class TouchTests(unittest.TestCase):
    def _tap(self, rect):
        return pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=rect.center)

    def test_keypad_types_into_entry_and_submits(self):
        from puzzleth.widgets import DigitEntry, Keypad
        pad = Keypad(600, [str(d) for d in range(10)] + ["Del", "OK"])
        entry = DigitEntry((640, 400))
        for i in (4, 2, 7, 10):           # 4, 2, 7, Del
            entry.handle(pad.handle(self._tap(pad.rects[i])))
        self.assertEqual(entry.value, "42")
        self.assertEqual(entry.handle(pad.handle(self._tap(pad.rects[11]))), "submit")
        self.assertIsNone(pad.handle(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))))

    def test_coding_accepts_taps_on_the_key(self):
        app = FakeApp()
        s = Coding(app, seed=3)
        before = s.practice_left
        s.handle_event(self._tap(s._key_rect(s.current - 1)))
        self.assertEqual(s.practice_left, before - 1)

    def test_arithmetic_keypad_answers(self):
        app = FakeApp()
        app.touch = True
        s = arithmetic.Arithmetic(app, seed=5)
        s.item_t = s.item["read"] + 0.1
        for ch in str(s.item["ans"]):
            s.handle_event(self._tap(s.keypad.rects[int(ch)]))
        s.handle_event(self._tap(s.keypad.rects[11]))
        self.assertEqual(s.state, "feedback")
        self.assertEqual(s.fb["points"], 1)


class WebStorageTests(unittest.TestCase):
    def test_profile_uses_browser_storage(self):
        from puzzleth import storage, web
        store = {}
        saved = (web.IS_WEB, web.load, web.save)
        web.IS_WEB, web.load, web.save = True, store.get, store.__setitem__
        try:
            p = storage.Profile()
            self.assertIsNone(p.path)
            p.settings["feedback"] = False
            p.save()
            self.assertIn(storage.WEB_KEY, store)
            self.assertFalse(storage.Profile().settings["feedback"])
        finally:
            web.IS_WEB, web.load, web.save = saved


class LearnTests(unittest.TestCase):
    def test_every_page_fits(self):
        from puzzleth.content.learn import TOPICS
        from puzzleth.scenes import LearnScene
        panel = pygame.Rect(320, 130, 920, 560)
        for _, _, pages in TOPICS:
            for title, paras in pages:
                self.assertLessEqual(LearnScene.layout_page(paras, panel), panel.bottom - 80, title)

    def test_large_text_splits_long_pages(self):
        from puzzleth import gfx
        from puzzleth.app import App
        from puzzleth.content.learn import TOPICS
        from puzzleth.scenes import LearnScene
        gfx.set_large_text(True)
        try:
            scene = LearnScene(App(pygame.display.get_surface()))
            p = scene.panel
            for ti, (_, _, pages) in enumerate(TOPICS):
                scene._select(ti)
                self.assertGreaterEqual(len(scene.pages), len(pages))
                originals = [para for _, paras in pages for para in paras]
                self.assertEqual([para for _, paras in scene.pages for para in paras], originals)
                for title, paras in scene.pages:
                    self.assertLessEqual(LearnScene.layout_page(paras, p), p.bottom - 80, title)
        finally:
            gfx.set_large_text(False)


class LargeTextTests(unittest.TestCase):
    def test_sizes(self):
        from puzzleth import gfx, theme
        self.assertEqual(theme.text_px(14), 14)
        gfx.set_large_text(True)
        try:
            self.assertEqual(theme.text_px(14), 20)
            self.assertEqual(theme.text_px(20), 28)
            self.assertEqual(theme.text_px(54), 54)
            sizes = [theme.text_px(k) for k in range(8, 60)]
            self.assertEqual(sizes, sorted(sizes))
            # fitting never goes below the desktop size
            self.assertEqual(theme.text_px(gfx.fit_size(17, lambda k: False)), 17)
            self.assertEqual(gfx.fit_size(17, lambda k: True), 17)
        finally:
            gfx.set_large_text(False)
        self.assertEqual(gfx.fit_size(17, lambda k: False), 17)


class StageTests(unittest.TestCase):
    def test_stage_fills_any_screen(self):
        from puzzleth.display import Stage, stage_size
        self.assertEqual(stage_size(1280, 800), (1280, 800))
        for w, h in [(844, 390), (1024, 768), (390, 844), (2560, 1080), (1, 1)]:
            sw, sh = stage_size(w, h)
            self.assertGreaterEqual(sw, 1280)
            self.assertGreaterEqual(sh, 800)
            self.assertTrue(sw == 1280 or sh == 800)                # as small as it can be
            self.assertAlmostEqual(sw / sh, w / h, delta=0.01)    # with the screen's shape
        stage = Stage(pygame.Surface((1731, 800)))
        self.assertEqual(stage.canvas.get_size(), (1280, 800))
        self.assertEqual(stage.to_canvas((225, 10)), (0, 10))
        e = stage.map_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(865, 400), button=1))
        self.assertEqual(e.pos, (640, 400))


class CompactLayoutTests(unittest.TestCase):
    """The 1280x600 layout phones get (see theme.py), drawn with large text as on a phone."""

    def setUp(self):
        from puzzleth import gfx, theme
        theme.set_compact(True)
        gfx.set_large_text(True)
        self.canvas = pygame.Rect(0, 0, theme.W, theme.H)

    def tearDown(self):
        from puzzleth import gfx, theme
        theme.set_compact(False)
        gfx.set_large_text(False)

    def surface(self):
        from puzzleth.display import Stage
        return Stage(pygame.Surface((1300, 600))).canvas

    def assert_inside(self, rects, bottom=None, name=""):
        """Every rect on the canvas (above ``bottom``) and none overlapping another."""
        area = self.canvas.copy()
        if bottom is not None:
            area.height = bottom
        for i, r in enumerate(rects):
            self.assertTrue(area.contains(r), f"{name}: {r} is outside {area}")
            for other in rects[i + 1:]:
                self.assertFalse(r.colliderect(other), f"{name}: {r} overlaps {other}")

    def test_stage(self):
        from puzzleth.display import Stage, stage_size
        self.assertEqual(stage_size(844, 390), (1298, 600))   # fills a phone with hardly any sides
        self.assertEqual(stage_size(390, 844), (1280, 2770))
        self.assertEqual(Stage(pygame.Surface((1298, 600))).canvas.get_size(), (1280, 600))

    def test_layout_follows_the_page(self):
        from unittest import mock
        from puzzleth import theme, web
        from puzzleth.app import App
        from puzzleth.scenes import MenuScene
        theme.set_compact(False)
        app = App(pygame.display.get_surface())
        app.scene, app.pause = MenuScene(app), None
        for size, compact in [((844, 390), True), ((390, 844), True), ((740, 340), True),
                              ((1024, 768), False), ((1366, 1024), False), ((1280, 800), False), ((900, 560), False)]:
            with mock.patch.object(web, "view_size", return_value=size), mock.patch.object(app, "_fit_page"):
                app._check_layout()
            self.assertEqual(theme.compact, compact, size)
            self.assertEqual(theme.H, 600 if compact else 800)
        self.assertIsInstance(app.scene, MenuScene)   # rebuilt for the new layout

    def test_layout_waits_for_a_subtest_to_end(self):
        from unittest import mock
        from puzzleth import theme, web
        from puzzleth.app import App
        app = App(pygame.display.get_surface())
        app.scene, app.pause = MatrixReasoning(app), None
        with mock.patch.object(web, "view_size", return_value=(1280, 800)):
            app._check_layout()
        self.assertTrue(theme.compact)

    def test_scenes_fit(self):
        from puzzleth import scenes as S
        from puzzleth.app import App
        from puzzleth.subtests import BY_CODE
        app = App(pygame.display.get_surface())
        app.touch = True
        surf = self.surface()
        sc = {c: 10 for c in BY_CODE}
        idx, fs = scoring.compute_indexes(sc)
        lad = challenge.RatedLadder(BY_CODE["MR"], rng=random.Random(1))
        while lad.next_level() is not None:
            lad.record(lad.next_level(), True)
        made = {
            "menu": S.MenuScene(app), "disclaimer": S.DisclaimerScene(app), "settings": S.SettingsScene(app),
            "learn": S.LearnScene(app), "walkthrough": S.LearnScene(app, "expect", then=lambda: None),
            "intro": S.IntroScene(app, BY_CODE["AR"]), "battery intro": S.IntroScene(app, BY_CODE["BD"], battery_pos=4),
            "result": S.SubtestResultScene(app, BY_CODE["MR"], 14, 12, 10, {"items": 12, "discontinued": True}),
            "assessment": S.BatteryResultScene(app, sc, sc, idx, fs), "rated": S.LadderResultScene(app, lad),
        }
        for name, scene in made.items():
            scene.t = 10.0
            scene.draw(surf)
            self.assert_inside([b.rect for b in scene.buttons], name=name)
        pause = S.PauseOverlay(app)
        self.assert_inside([b.rect for b in pause.buttons], name="pause")
        # the tree's nodes stay clear of the menu's buttons
        menu = made["menu"]
        for code, (x, y) in menu.tree.sub_pos.items():
            node = pygame.Rect(0, 0, 90, 90)
            node.center = (x, y)
            for b in menu.buttons:
                self.assertFalse(node.colliderect(b.rect), (code, b.label))

    def test_learn_pages_fit(self):
        from puzzleth.app import App
        from puzzleth.content.learn import TOPICS
        from puzzleth.scenes import LearnScene
        for then in (None, lambda: None):
            scene = LearnScene(App(pygame.display.get_surface()), then=then)
            self.assertLessEqual(scene.panel.bottom, self.canvas.bottom)
            for ti in range(len(TOPICS) if then is None else 1):
                scene._select(ti)
                for title, paras in scene.pages:
                    self.assertLessEqual(LearnScene.layout_page(paras, scene.panel), scene.panel.bottom - 80, title)

    def test_subtests_fit(self):
        from puzzleth.subtests.verbal import Information, Similarities, Vocabulary
        app = FakeApp()
        app.touch = True
        surf = self.surface()
        above_feedback = self.canvas.bottom - 94   # the feedback bar takes the bottom of the screen
        for level in (1, 12, 30):
            mr = MatrixReasoning(app, seed=1)
            mr._begin(level)
            size = mr.item["size"]
            frame = mr._cell_rect(0, 0).union(mr._cell_rect(size - 1, size - 1)).inflate(30, 30)
            self.assert_inside([frame] + [mr._opt_rect(i) for i in range(5)], above_feedback, "matrix")
        vp = VisualPuzzles(app, seed=1)
        self.assert_inside([vp._opt_rect(i) for i in range(6)] + [vp.confirm_btn.rect], above_feedback, "pieces")
        for level in (6, 12, 16):
            b = bd.BlockDesign(app, seed=1)
            b._begin(level)
            s = b.item["size"]
            cells = [b._cell_rect(y, x) for y in range(s) for x in range(s)]
            self.assert_inside(cells + [b.giveup_btn.rect], above_feedback, "blocks")
        for cls in (Similarities, Vocabulary, Information):
            sub = cls(app, seed=1)
            self.assert_inside([c.rect for c in sub.cards], above_feedback, cls.name)
        ar = arithmetic.Arithmetic(app, seed=1)
        self.assert_inside(ar.keypad.rects + [ar.repeat_btn.rect], above_feedback, "arithmetic")
        ds = DigitSpan(app, seed=1)
        self.assert_inside(ds.keypad.rects, above_feedback, "digit span")
        ss = SymbolSearch(app, seed=1)
        self.assert_inside([ss.yes_btn.rect, ss.no_btn.rect], above_feedback, "symbol search")
        cd = Coding(app, seed=1)
        self.assert_inside([cd._key_rect(i) for i in range(9)], name="coding")
        for sub in (mr, vp, b, sub, ar, ds, ss, cd):
            sub.draw(surf)


if __name__ == "__main__":
    unittest.main()
