"""Main loop and scene/flow management."""
import asyncio
import os

import pygame

from . import gfx, i18n, online, scoring, sound, web
from . import theme as T
from .challenge import START_RATING, DailyLadder, RatedLadder
from .display import Display, Stage, stage_size
from .scenes import (BatteryResultScene, DisclaimerScene, IntroScene, LadderResultScene, LanguageScene, LeaderboardScene, LearnScene,
                     MenuScene, NameEntryScene, PauseOverlay, PlayersScene, RecoveryCodeScene, RestoreScene,
                     SettingsScene, SubtestResultScene)
from .storage import Profile
from .subtests import ORDER
from .subtests.base import Subtest, pause_rect


class App:
    def __init__(self, screen=None):
        pygame.mixer.pre_init(44100, -16, 2, 512)   # a small buffer keeps sound effects in time
        pygame.init()
        self.profile = Profile()
        self.online = online.Online(self.profile)
        self.online.flush()   # players who left the leaderboard while it was out of reach
        self.online.sync()    # ratings and progress earned while it was
        sound.init(self.profile.settings["sfx_volume"], self.profile.settings["music_volume"])
        if screen is not None:
            self.stage = Stage(screen)
        elif web.IS_WEB:
            # the browser page scales the stage to fit the page, which has the page's shape
            self.stage = Stage()
            self._check_layout()
            self._fit_page()
        else:
            # real window: the GPU scales the stage to whatever size the window is
            self.stage = Display(fullscreen=self.profile.settings.get("fullscreen", False))
        self.display = self.stage if isinstance(self.stage, Display) else None
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
        if web.IS_WEB:   # before the first scene lays itself out
            self._check_large_text()
            web.mark_started()
        language = self.profile.settings.get("language")
        if language not in {code for code, _ in i18n.LANGUAGES}:
            self.scene = LanguageScene(self)
        else:
            self._set_language(language)
            self._show_initial_scene()

    @staticmethod
    def _set_language(language):
        i18n.set_language(language)
        sound.set_language(language)   # the spoken digits

    def _language_chosen(self, language, done=None):
        self._set_language(language)
        if done:
            done()
        else:
            self._show_initial_scene()

    def choose_language(self):
        self.goto(LanguageScene(self, done=lambda: self.goto(SettingsScene(self))))

    def _show_initial_scene(self):
        if not self.profile.settings.get("disclaimer_seen"):
            self.scene = DisclaimerScene(self)
        elif len(self.profile.players()) > 1:   # make sure the right person is playing
            self.scene = PlayersScene(self)
        else:
            self.scene = self._menu()

    # ------------------------------------------------------------ flow
    def goto(self, scene):
        sound.duck(False)
        self.scene = scene
        self.pause = None
        self.fade = 1.0

    def _menu(self):
        # nothing can be played until the player has entered a name
        return MenuScene(self) if self.profile.current else NameEntryScene(self)

    def to_menu(self):
        self.battery = None
        self.goto(self._menu())

    def open_players(self):
        self.goto(PlayersScene(self))

    def new_player(self):
        self.goto(NameEntryScene(self))

    def open_leaderboard(self, code=None):
        self.goto(LeaderboardScene(self, code))

    def open_restore(self):
        self.goto(RestoreScene(self))

    def open_recovery_code(self):
        self.goto(RecoveryCodeScene(self))

    def player_changed(self):
        """After switching or removing players: catch the leaderboard up."""
        self.online.flush()
        self.online.sync()

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
        self.online.sync()
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
        self.online.backup()

    @property
    def screen(self):
        """The 1280x800 canvas every scene is laid out on (the centre of the stage)."""
        return self.stage.canvas

    def _fit_page(self):
        size = stage_size(*web.view_size())
        if self.stage.surface is None or self.stage.surface.get_size() != size or self.screen.get_height() != T.H:
            self.stage.use(pygame.display.set_mode(size))
            self.stage.activate()
            web.refit_canvas()

    # ------------------------------------------------------------ loop
    def step(self, dt, events):
        for e in events:
            e = self.stage.map_event(e)
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
                    e.type == pygame.MOUSEBUTTONDOWN and e.button == 1 and pause_rect().collidepoint(e.pos)):
                self.pause = PauseOverlay(self)
            else:
                self.scene.handle_event(e)
        sound.update(dt)
        self.online.poll()
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

    @staticmethod
    def _check_large_text():
        # phones show the canvas at about half size: draw the small print larger there. Screens
        # opened from then on make room for it; the open one fits it in as best it can.
        gfx.set_large_text(web.view_scale(T.W, T.FULL_H) < 0.75)

    def _check_layout(self):
        """Use the compact layout (see theme.py) on pages too small for the full one and about the shape
        of a phone. Which way round the phone is held doesn't matter, so turning it never switches
        layouts; a page resized past the limit switches once the open screen can simply be rebuilt."""
        w, h = web.view_size()
        short, long = min(w, h), max(w, h)
        want = short < 0.75 * T.FULL_H and long >= 1.7 * short
        if want == T.compact:
            return
        scene = getattr(self, "scene", None)
        if scene is not None and (self.pause or type(scene) not in (MenuScene, DisclaimerScene, SettingsScene, PlayersScene)):
            return
        T.set_compact(want)
        if scene is not None:
            self._fit_page()
            self.scene = type(scene)(self)

    async def run_async(self):
        # yielding to the event loop every frame is what lets the game run inside a browser
        frame = 0
        # PUZZLETH_QUIT_AFTER=N: close after N frames (a smoke test of a packaged build)
        quit_after = int(os.environ.get("PUZZLETH_QUIT_AFTER") or 0)
        while self.running:
            if quit_after and frame >= quit_after:
                break
            dt = min(0.05, self.clock.tick(T.FPS) / 1000)
            self.step(dt, pygame.event.get())
            if web.IS_WEB and frame % 30 == 0:
                self.portrait = web.is_portrait()
                self._check_large_text()
                self._check_layout()
                self._fit_page()
            frame += 1
            if self.display:
                self.display.update_size()
            self.render()
            if self.display:
                self.display.present()
            else:
                pygame.display.flip()
            await asyncio.sleep(0)
        pygame.quit()
