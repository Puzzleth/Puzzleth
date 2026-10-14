"""Main loop and scene/flow management."""
import sys

import pygame

from . import gfx, scoring
from . import theme as T
from .display import Display
from .scenes import BatteryResultScene, IntroScene, MenuScene, PauseOverlay, SubtestResultScene
from .storage import Profile
from .subtests import ORDER
from .subtests.base import Subtest


class App:
    def __init__(self, screen=None):
        pygame.init()
        self.profile = Profile()
        self.display = None
        if screen is None:
            # real window: draw on a fixed canvas that the GPU scales to whatever size the window is
            self.display = Display(fullscreen=self.profile.settings.get("fullscreen", False))
            screen = self.display.canvas
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.bg = gfx.Background()
        self.t = 0.0
        self.fade = 0.0
        self.running = True
        self.battery = None
        self.pause = None
        self.current_cls = None
        self.scene = MenuScene(self)

    # ------------------------------------------------------------ flow
    def goto(self, scene):
        self.scene = scene
        self.pause = None
        self.fade = 1.0

    def to_menu(self):
        self.battery = None
        self.goto(MenuScene(self))

    def quit(self):
        self.running = False

    def start_practice(self, cls):
        self.battery = None
        self.goto(IntroScene(self, cls))

    def start_battery(self):
        self.battery = {"pos": 0, "scaled": {}, "raw": {}}
        self.goto(IntroScene(self, ORDER[0], battery_pos=0))

    def begin_subtest(self, cls):
        self.current_cls = cls
        feedback = False if self.battery else self.profile.settings.get("feedback", True)
        self.goto(cls(self, feedback=feedback))

    def restart_subtest(self):
        if self.current_cls:
            self.begin_subtest(self.current_cls)

    def toggle_fullscreen(self):
        if self.display:
            self.profile.settings["fullscreen"] = self.display.toggle_fullscreen()
            self.profile.save()

    @property
    def fullscreen(self):
        return bool(self.display and self.display.fullscreen)

    def resume(self):
        self.pause = None

    def subtest_done(self, sub, raw, details):
        scaled = scoring.scaled_score(sub.code, raw)
        best_before = self.profile.best_scaled(sub.code)
        self.profile.record_subtest(sub.code, raw, scaled, details)
        if self.battery:
            b = self.battery
            b["scaled"][sub.code] = scaled
            b["raw"][sub.code] = raw
            b["pos"] += 1
            if b["pos"] < len(ORDER):
                self.goto(IntroScene(self, ORDER[b["pos"]], battery_pos=b["pos"]))
            else:
                indexes, fsiq = scoring.compute_indexes(b["scaled"])
                self.profile.record_battery(b["scaled"], indexes, fsiq)
                self.battery = None
                self.goto(BatteryResultScene(self, b["scaled"], b["raw"], indexes, fsiq))
        else:
            self.goto(SubtestResultScene(self, type(sub), raw, scaled, best_before, details))

    # ------------------------------------------------------------ loop
    def step(self, dt, events):
        for e in events:
            if self.display:
                e = self.display.map_event(e)
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif self.pause:
                self.pause.handle_event(e)
            elif isinstance(self.scene, Subtest) and e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                self.pause = PauseOverlay(self)
            else:
                self.scene.handle_event(e)
        self.t += dt
        self.fade = max(0.0, self.fade - dt * 4)
        if self.pause:
            self.pause.update(dt)
        else:
            self.scene.update(dt)

    def render(self):
        self.bg.draw(self.screen, self.t)
        self.scene.draw(self.screen)
        if self.pause:
            self.pause.draw(self.screen)
        if self.fade > 0:
            gfx.overlay(self.screen, T.BG, 255 * gfx.ease_in_out(self.fade))

    def run(self):
        while self.running:
            dt = min(0.05, self.clock.tick(T.FPS) / 1000)
            self.step(dt, pygame.event.get())
            self.render()
            if self.display:
                self.display.present()
            else:
                pygame.display.flip()
        pygame.quit()


def run():
    App().run()
    sys.exit(0)
