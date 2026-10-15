"""Main loop and scene/flow management."""
import asyncio

import pygame

from . import gfx, scoring, sound, web
from . import theme as T
from .challenge import START_RATING, DailyLadder, RatedLadder
from .display import Display
from .scenes import (BatteryResultScene, DisclaimerScene, IntroScene, LadderResultScene, LearnScene, MenuScene,
                     PauseOverlay, SubtestResultScene)
from .storage import Profile
from .subtests import ORDER
from .subtests.base import PAUSE_RECT, Subtest


class App:
    def __init__(self, screen=None):
        pygame.mixer.pre_init(44100, -16, 2, 512)   # a small buffer keeps sound effects in time
        pygame.init()
        self.profile = Profile()
        sound.init(self.profile.settings["sfx_volume"], self.profile.settings["music_volume"])
        self.display = None
        if screen is None and web.IS_WEB:
            # the browser page scales the canvas to fit the screen
            screen = pygame.display.set_mode((T.W, T.H))
        elif screen is None:
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
        self.current_ladder = None
        self.touch = web.IS_WEB   # show on-screen keypads and buttons
        self.portrait = False
        self.scene = MenuScene(self) if self.profile.settings.get("disclaimer_seen") else DisclaimerScene(self)

    # ------------------------------------------------------------ flow
    def goto(self, scene):
        sound.duck(False)
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
        if not self.profile.settings.get("expect_seen"):
            # first full assessment: offer the "what to expect" walkthrough first
            self.profile.settings["expect_seen"] = True
            self.profile.save()
            self.goto(LearnScene(self, topic="expect", then=self.start_battery))
            return
        self.battery = {"pos": 0, "scaled": {}, "raw": {}}
        self.goto(IntroScene(self, ORDER[0], battery_pos=0))

    def start_daily(self):
        self.battery = None
        self.goto(IntroScene(self, DailyLadder().cls, ladder_kind="daily"))

    def open_learn(self, topic=None):
        self.goto(LearnScene(self, topic=topic))

    def new_ladder(self, kind, cls):
        if kind == "daily":
            return DailyLadder()
        r = self.profile.rating(cls.code) or {}
        return RatedLadder(cls, r.get("rating", START_RATING), r.get("played", 0))

    def begin_subtest(self, cls, ladder_kind=None):
        self.current_cls = cls
        self.current_ladder = ladder_kind
        if ladder_kind:
            ladder = self.new_ladder(ladder_kind, cls)
            self.goto(ladder.cls(self, ladder=ladder))
            return
        feedback = False if self.battery else self.profile.settings.get("feedback", True)
        self.goto(cls(self, feedback=feedback))

    def restart_subtest(self):
        if self.current_cls:
            self.begin_subtest(self.current_cls, self.current_ladder)

    def ladder_progress(self, sub):
        lad = sub.ladder
        if lad.kind == "rated":   # saved after every puzzle, like a chess puzzle rating
            self.profile.set_rating(lad.cls.code, lad.rating, lad.played)

    def ladder_done(self, sub):
        lad = sub.ladder
        counted = lad.kind == "daily" and self.profile.record_daily(lad.day, lad.cls.code, lad.results)
        self.goto(LadderResultScene(self, lad, counted))

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
            if e.type == pygame.FINGERDOWN:
                self.touch = True
            sound.handle_event(e)
            if e.type == pygame.QUIT:
                self.running = False
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_F11:
                self.toggle_fullscreen()
            elif self.pause:
                self.pause.handle_event(e)
            elif isinstance(self.scene, Subtest) and (
                    e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE or
                    e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and PAUSE_RECT.collidepoint(e.pos)):
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
        if self.portrait:
            self._draw_rotate_hint()

    def _draw_rotate_hint(self):
        gfx.overlay(self.screen, T.BG, 235)
        c = (T.W // 2, T.H // 2)
        phone = pygame.Rect(0, 0, 150, 250)
        phone.center = (c[0], c[1] - 110)
        k = gfx.ease_in_out(abs((self.t * 0.6) % 2 - 1))      # rock between upright and sideways
        r = pygame.Rect(0, 0, int(150 + 100 * k), int(250 - 100 * k))
        r.center = phone.center
        pygame.draw.rect(self.screen, T.ACCENT, r, 8, border_radius=24)
        gfx.text(self.screen, "Turn your phone sideways", (c[0], c[1] + 90), 64, T.TEXT, bold=True, anchor="center")
        gfx.text(self.screen, "Puzzleth is played in landscape", (c[0], c[1] + 160), 40, T.MUTED, anchor="center")

    async def run_async(self):
        # yielding to the event loop every frame is what lets the game run inside a browser
        frame = 0
        while self.running:
            dt = min(0.05, self.clock.tick(T.FPS) / 1000)
            self.step(dt, pygame.event.get())
            if web.IS_WEB and frame % 30 == 0:
                self.portrait = web.is_portrait()
            frame += 1
            self.render()
            if self.display:
                self.display.present()
            else:
                pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()

