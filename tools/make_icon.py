"""Draw the app icon (a skill-point ring) to tools/web/favicon.png:  python3 tools/make_icon.py"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.environ["SDL_VIDEODRIVER"] = "dummy"
sys.path.insert(0, ROOT)

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((1, 1))

from puzzleth import gfx  # noqa: E402
from puzzleth import theme as T  # noqa: E402

S = 256
surf = pygame.Surface((S, S), pygame.SRCALPHA)
pygame.draw.rect(surf, T.BG, (0, 0, S, S), border_radius=56)
c = (S // 2, S // 2)
gfx.glow(surf, c, 120, T.GOLD, 0.35)
gfx.circle(surf, c, 70, gfx.lerp_color(T.PANEL, T.GOLD, 0.15))
gfx.pips(surf, c, 92, 16, 12, 9, T.GOLD)
gfx.text(surf, "P", (c[0], c[1] - 4), 96, T.TEXT, bold=True, anchor="center")
pygame.image.save(surf, os.path.join(ROOT, "tools", "web", "favicon.png"))
