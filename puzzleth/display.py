"""Window management: the game draws on a fixed 1280x800 canvas which the GPU scales to fit the
window (any size, any aspect ratio, letterboxed), in both windowed and fullscreen modes."""
import os

import pygame

from . import theme as T

# smooth (bilinear) scaling instead of pixelated nearest-neighbour; must be set before textures exist
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY", "linear")

_active = None


def mouse_pos():
    """Mouse position in canvas coordinates."""
    pos = pygame.mouse.get_pos()
    return _active.to_canvas(pos) if _active else pos


def fit(w, h):
    """Largest canvas-shaped rectangle centred in a w x h area."""
    scale = min(w / T.W, h / T.H)
    dw, dh = max(1, round(T.W * scale)), max(1, round(T.H * scale))
    return pygame.Rect((w - dw) // 2, (h - dh) // 2, dw, dh)


class Display:
    def __init__(self, fullscreen=False):
        global _active
        from pygame._sdl2.video import Renderer, Texture, Window

        self.window = Window("Puzzleth", (T.W, T.H), resizable=True)
        self.window.minimum_size = (T.W // 2, T.H // 2)
        try:
            self.renderer = Renderer(self.window, vsync=True)
        except pygame.error:
            self.renderer = Renderer(self.window)
        self.canvas = pygame.Surface((T.W, T.H))
        self.texture = Texture(self.renderer, (T.W, T.H), streaming=True)
        self.fullscreen = False
        self.set_fullscreen(fullscreen)
        _active = self

    def set_fullscreen(self, on):
        if on:
            self.window.set_fullscreen(desktop=True)
        else:
            self.window.set_windowed()
        self.fullscreen = on

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)
        return self.fullscreen

    def to_canvas(self, pos):
        """Window coordinates -> canvas coordinates (inverse of the letterbox fit)."""
        r = fit(*self.window.size)
        return int((pos[0] - r.x) * T.W / r.w), int((pos[1] - r.y) * T.H / r.h)

    def map_event(self, e):
        if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            return pygame.event.Event(e.type, {**e.dict, "pos": self.to_canvas(e.pos)})
        return e

    def present(self):
        self.texture.update(self.canvas)
        self.renderer.draw_color = (*T.BG, 255)
        self.renderer.clear()
        # the viewport covers the whole output in real pixels, which may exceed the window
        # size on HiDPI screens
        out = self.renderer.get_viewport()
        self.texture.draw(dstrect=fit(out.w, out.h))
        self.renderer.present()
