import os
import tempfile
import unittest
import pygame

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
pygame.init()
pygame.display.set_mode((10, 10))


class RegressionTests(unittest.TestCase):
    def test_digit_entry_rejects_non_decimal_unicode(self):
        from puzzleth.widgets import DigitEntry
        entry = DigitEntry((100, 100))
        ev = pygame.event.Event(pygame.KEYDOWN, key=0, unicode="²", mod=0, scancode=0)
        self.assertFalse(entry.handle(ev))
        self.assertEqual(entry.value, "")

    def test_arithmetic_and_digit_span_ignore_bad_digits(self):
        from puzzleth.subtests.arithmetic import Arithmetic
        from puzzleth.subtests.digit_span import DigitSpan
        # Minimal fake app
        class App:
            def __init__(self):
                self.result = None

            def subtest_done(self, sub, raw, details):
                self.result = (raw, details)
        # Arithmetic: int() errors become a wrong answer, not a crash
        a = Arithmetic(App(), seed=1)
        a.item_t = a.item["read"] + 0.1
        a.entry.value = "²3"
        a.handle_item(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="\r", mod=0, scancode=0))
        # Digit Span: int() errors become a wrong answer, not a crash
        d = DigitSpan(App(), seed=1)
        d.state = "input"
        d.target = [1, 2, 3]
        d.entry.value = "1²3"
        # direct submit path
        d._submit()
        self.assertIsNotNone(d.fb)

    def test_profile_loads_with_malformed_file_and_keeps_corrupt_copy(self):
        from puzzleth.storage import Profile
        prev = os.environ.get("PUZZLETH_HOME")
        with tempfile.TemporaryDirectory() as directory:
            try:
                path = os.path.join(directory, "profile.json")
                os.environ["PUZZLETH_HOME"] = path
                with open(path, "w") as f:
                    f.write("[]")  # valid JSON, wrong shape
                p = Profile()
                # A fresh profile is created
                self.assertIn("settings", p.root)
                # The corrupt one is moved aside
                junk = [f for f in os.listdir(directory) if f.startswith("profile.json.corrupt-")]
                self.assertTrue(junk)
            finally:
                if prev is None:
                    os.environ.pop("PUZZLETH_HOME", None)
                else:
                    os.environ["PUZZLETH_HOME"] = prev

    def test_speed_timers_use_real_time(self):
        from puzzleth.subtests.speed import SymbolSearch
        # Fake app with timer_dt support
        class App:
            def __init__(self):
                self.result = None
                self.timer_dt = 0.1

            def subtest_done(self, sub, raw, details):
                self.result = (raw, details)
        s = SymbolSearch(App(), seed=1)
        s.state = "run"
        s.remaining = 1.0
        for _ in range(10):
            s.update(0.05)  # clamped animation delta
        self.assertAlmostEqual(s.remaining, 0.0, places=12)
        self.assertIsNotNone(s.app.result)

    def test_rated_quit_counts_as_miss(self):
        from puzzleth.app import App
        from puzzleth.subtests.visual_puzzles import VisualPuzzles
        from puzzleth.challenge import START_RATING
        app = App(pygame.display.get_surface())
        app.begin_subtest(VisualPuzzles, ladder_kind="rated")
        # Leave immediately: should count as a miss
        app.to_menu()
        r = app.profile.rating("VP")
        self.assertIsNotNone(r)
        self.assertEqual(r["played"], 1)
        self.assertLess(r["rating"], START_RATING)


if __name__ == "__main__":
    unittest.main()

