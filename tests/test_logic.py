"""Correctness tests: administration rules, scoring math and procedural generators.

Run with:  python -m unittest discover -s tests
"""
import os
import random
import sys
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ["BRAIN_PUZZLERER_HOME"] = os.path.join(tempfile.mkdtemp(), "profile.json")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1280, 800))

from brainpuzzlerer import glyphs, scoring  # noqa: E402
from brainpuzzlerer.content import verbal as bank  # noqa: E402
from brainpuzzlerer.subtests import ORDER, arithmetic, block_design as bd  # noqa: E402
from brainpuzzlerer.subtests.base import ItemSubtest  # noqa: E402
from brainpuzzlerer.subtests.digit_span import DigitSpan  # noqa: E402
from brainpuzzlerer.subtests.matrix_reasoning import MatrixReasoning, _visible_key  # noqa: E402
from brainpuzzlerer.subtests.speed import Coding, SymbolSearch  # noqa: E402
from brainpuzzlerer.subtests.visual_puzzles import VisualPuzzles, rotations, tiles  # noqa: E402


class FakeApp:
    def __init__(self):
        self.result = None

    def subtest_done(self, sub, raw, details):
        self.result = (raw, details)


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

    def test_face_transforms_are_geometric(self):
        self._check_map(bd.ROT, self.CW)
        self._check_map(bd.MIRROR_H, self.MH)
        self._check_map(bd.MIRROR_V, self.MV)

    def test_designs_are_nontrivial(self):
        app = FakeApp()
        for seed in range(150):
            s = bd.BlockDesign(app, seed=seed)
            for n in range(0, 15):
                it = s.make_item(n)
                flat = [f for row in it["design"] for f in row]
                self.assertGreaterEqual(len(set(flat)), 2)
                self.assertEqual(it["size"], 2 if n <= 8 else 3)
                self.assertNotEqual(it["work"], it["design"])
                if n > 2:
                    self.assertTrue(any(f in bd.DIAG for f in flat))


class MatrixTests(unittest.TestCase):
    def test_answer_unique_and_follows_rules(self):
        app = FakeApp()
        for seed in range(120):
            s = MatrixReasoning(app, seed=seed)
            for n in range(0, 27):
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
            for n in range(0, 27, 2):
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


if __name__ == "__main__":
    unittest.main()
