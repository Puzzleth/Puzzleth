"""Window management. The game lays itself out on a fixed 1280x800 canvas, centred on a "stage" that
has the shape of the window (or browser page): the background fills the whole stage and the stage
fills the whole window, so there are no bars on any screen. A real window has the GPU scale the stage
to the window in both windowed and fullscreen modes; in a browser the page scales it."""
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


def fit(w, h, cw=T.W, ch=T.H):
    """Largest cw x ch-shaped rectangle centred in a w x h area."""
    scale = min(w / cw, h / ch)
    dw, dh = max(1, round(cw * scale)), max(1, round(ch * scale))
    return pygame.Rect((w - dw) // 2, (h - dh) // 2, dw, dh)


def stage_size(w, h):
    """Smallest w x h-shaped size that holds the whole canvas."""
    if w <= 0 or h <= 0:
        return T.W, T.H
    if w * T.H >= h * T.W:   # wider than the canvas: extend it sideways
        return max(T.W, round(T.H * w / h)), T.H
    return T.W, max(T.H, round(T.W * h / w))


class Stage:
    """The surface the game is drawn on: ``surface`` is the whole stage, ``canvas`` the centred
    1280x800 part that scenes lay themselves out on."""

    def __init__(self, surface=None):
        self.surface = None
        self.canvas = None
        self.offset = (0, 0)
        if surface is not None:
            self.use(surface)

    def use(self, surface):
        w, h = surface.get_size()
        self.surface = surface
        self.offset = ((w - T.W) // 2, (h - T.H) // 2)
        self.canvas = surface.subsurface((*self.offset, T.W, T.H))

    def activate(self):
        """Make mouse_pos() report canvas coordinates."""
        global _active
        _active = self

    def window_to_stage(self, pos):
        return pos

    def to_canvas(self, pos):
        """Window coordinates -> canvas coordinates."""
        x, y = self.window_to_stage(pos)
        return x - self.offset[0], y - self.offset[1]

    def map_event(self, e):
        if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            return pygame.event.Event(e.type, {**e.dict, "pos": self.to_canvas(e.pos)})
        return e


class Display(Stage):
    """A real window that the stage is scaled to by the GPU."""

    def __init__(self, fullscreen=False):
        super().__init__()
        from pygame._sdl2.video import Renderer, Window

        self.window = Window("Puzzleth", (T.W, T.H), resizable=True)
        self.window.minimum_size = (T.W // 2, T.H // 2)
        try:
            self.renderer = Renderer(self.window, vsync=True)
        except pygame.error:
            self.renderer = Renderer(self.window)
        self.texture = None
        self.fullscreen = False
        self.set_fullscreen(fullscreen)
        self.update_size()
        self.activate()

    def set_fullscreen(self, on):
        if on:
            self.window.set_fullscreen(desktop=True)
        else:
            self.window.set_windowed()
        self.fullscreen = on

    def toggle_fullscreen(self):
        self.set_fullscreen(not self.fullscreen)
        return self.fullscreen

    def update_size(self):
        """Give the stage the window's shape; True when it changed (the canvas is then a new surface)."""
        from pygame._sdl2.video import Texture

        size = stage_size(*self.window.size)
        if self.surface is not None and self.surface.get_size() == size:
            return False
        self.use(pygame.Surface(size))
        self.texture = Texture(self.renderer, size, streaming=True)
        return True

    def window_to_stage(self, pos):
        """Inverse of the fit in present()."""
        sw, sh = self.surface.get_size()
        r = fit(*self.window.size, sw, sh)
        return int((pos[0] - r.x) * sw / r.w), int((pos[1] - r.y) * sh / r.h)

    def present(self):
        self.texture.update(self.surface)
        self.renderer.draw_color = (*T.BG, 255)
        self.renderer.clear()
        # the viewport covers the whole output in real pixels, which may exceed the window
        # size on HiDPI screens
        out = self.renderer.get_viewport()
        self.texture.draw(dstrect=fit(out.w, out.h, *self.surface.get_size()))
        self.renderer.present()
