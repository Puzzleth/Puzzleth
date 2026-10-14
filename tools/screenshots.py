"""Regenerate the README screenshots headlessly:  python3 tools/screenshots.py

Uses a throwaway profile with made-up results, so your own progress is never touched.
"""
import datetime
import os
import random
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "screenshots")
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
os.environ["PUZZLETH_HOME"] = os.path.join(tempfile.mkdtemp(), "profile.json")
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
screen = pygame.display.set_mode((1280, 800))

from puzzleth import scenes, scoring  # noqa: E402
from puzzleth.app import App  # noqa: E402
from puzzleth.challenge import DailyLadder  # noqa: E402
from puzzleth.subtests import BY_CODE, ORDER  # noqa: E402


def main():
    os.makedirs(OUT, exist_ok=True)
    app = App(screen)
    app.profile.settings["disclaimer_seen"] = True

    def shot(name, frames=40):
        for _ in range(frames):
            app.step(1 / 60, [])
        app.render()
        pygame.image.save(screen, os.path.join(OUT, f"{name}.png"))

    sample = {c.code: s for c, s in zip(ORDER, [12, 11, 9, 14, 10, 8, 13, 12, 9, 11])}
    for code, s in sample.items():
        app.profile.record_subtest(code, 10, s, {})
    app.to_menu()
    shot("skill-tree")

    indexes, fsiq = scoring.compute_indexes(sample)
    app.goto(scenes.BatteryResultScene(app, sample, {c: 10 for c in sample}, indexes, fsiq))
    shot("assessment-result", 420)

    for code, level, name in [("MR", 20, "matrix-reasoning"), ("BD", 16, "block-design"),
                              ("VP", 22, "visual-puzzles")]:
        app.begin_subtest(BY_CODE[code], "rated")
        app.scene.rng = random.Random(7)
        app.scene._begin(level)
        shot(name)

    rng = random.Random(4)
    lad = DailyLadder(datetime.date(2026, 10, 14))
    app.goto(lad.cls(app, ladder=lad))
    sub = app.scene
    while not sub.done:
        sub.submit(1 if rng.random() < 0.7 else 0)
        sub._advance()
    shot("daily-result", 150)

    app.open_learn("expect")
    app.scene.page = 1
    shot("learn")
    print(f"saved to {OUT}")


if __name__ == "__main__":
    main()
