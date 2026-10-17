"""Profile persistence (JSON in the user's home directory)."""
import datetime
import json
import os
import time
from pathlib import Path

from . import i18n, web

WEB_KEY = "puzzleth.profile"


def profile_path():
    base = os.environ.get("PUZZLETH_HOME")
    return Path(base) if base else Path.home() / ".puzzleth" / "profile.json"


def _legacy_path():
    """Where the game saved progress before it was renamed from Brain Puzzlerer."""
    return None if os.environ.get("PUZZLETH_HOME") else Path.home() / ".brain_puzzlerer" / "profile.json"


NAME_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
NAME_LEN = 8
CODE_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"   # recovery codes (no 0/O or 1/I to mix up), see online.py
MAX_PLAYERS = 8
# settings each player chooses for themselves; the rest (volumes, fullscreen, ...) belong to the device
PLAYER_SETTINGS = ("feedback", "show_scores", "expect_seen")


def _default_settings():
    return {"sfx_volume": 0.75, "music_volume": 0.5, "language": None}


def _default_player():
    # "online": their place on the online leaderboard, once they join it (see online.py)
    return {"subtests": {}, "batteries": [], "ratings": {}, "daily": {},
            "settings": {"feedback": True, "show_scores": True}, "seen": 0, "online": None}


def clean_name(name):
    """A player name as the arcade-style entry allows it: capitals and digits, at most NAME_LEN."""
    return "".join(c for c in str(name).upper() if c in NAME_CHARS)[:NAME_LEN]


class _Settings:
    """The device's settings, except PLAYER_SETTINGS, which are read from and written to the
    current player's own settings."""

    def __init__(self, device, profile):
        self.device = device
        self.profile = profile

    def _own(self, key):
        return self.profile.data["settings"] if key in PLAYER_SETTINGS else self.device

    def __getitem__(self, key):
        return self._own(key)[key]

    def __setitem__(self, key, value):
        self._own(key)[key] = value

    def __contains__(self, key):
        return key in self._own(key)

    def get(self, key, default=None):
        return self._own(key).get(key, default)


class Profile:
    """Everyone who plays on this device, each under the name they chose. ``data`` is the current
    player's progress; until somebody has entered a name it belongs to no one (and progress saved
    by versions without players lands there, to be adopted by the first name entered)."""

    def __init__(self):
        self.path = None if web.IS_WEB else profile_path()
        # "forget": leaderboard tokens of players who left it, until the server has deleted them
        self.root = {"current": None, "settings": _default_settings(), "players": {}, "unnamed": _default_player(),
                     "forget": []}
        try:
            if web.IS_WEB:
                # browsers: the page's localStorage survives reloads; the virtual file system doesn't
                loaded = json.loads(web.load(WEB_KEY) or "{}")
            else:
                src = self.path
                legacy = _legacy_path()
                if not src.exists() and legacy and legacy.exists():
                    src = legacy   # carried over on the next save
                with open(src) as f:
                    loaded = json.load(f)
            self._load(loaded)
        except (OSError, ValueError):
            pass
        self.settings = _Settings(self.root["settings"], self)
        self.data = self._player_data()

    def _load(self, loaded):
        if "players" not in loaded:   # saved before there were players: all of it was one person's
            settings = loaded.pop("settings", {})
            own = {k: settings.pop(k) for k in PLAYER_SETTINGS if k in settings}
            loaded = {"settings": settings, "unnamed": {**loaded, "settings": own}}
        self.root.update(loaded)
        for k, v in _default_settings().items():   # profiles from older versions
            self.root["settings"].setdefault(k, v)
        for data in [*self.root["players"].values(), self.root.get("unnamed") or {}]:
            for k, v in _default_player().items():
                data.setdefault(k, v)
            for k, v in _default_player()["settings"].items():
                data["settings"].setdefault(k, v)
        if self.root["current"] not in self.root["players"]:
            self.root["current"] = None

    def _player_data(self):
        cur = self.root["current"]
        if cur:
            return self.root["players"][cur]
        if not self.root.get("unnamed"):
            self.root["unnamed"] = _default_player()
        return self.root["unnamed"]

    def save(self):
        if web.IS_WEB:
            web.save(WEB_KEY, json.dumps(self.root))
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w") as f:
                json.dump(self.root, f, indent=1)
            tmp.replace(self.path)
        except OSError:
            pass

    # ------------------------------------------------------------ players
    @property
    def current(self):
        """The current player's name, or None before anyone has entered one."""
        return self.root["current"]

    def players(self):
        """Every player's name, the most recently chosen first."""
        ps = self.root["players"]
        return sorted(ps, key=lambda n: -ps[n].get("seen", 0))

    def player(self, name):
        return self.root["players"].get(name)

    def can_add(self, name):
        """None if ``name`` can be added as a new player, else why not."""
        name = clean_name(name)
        if not name:
            return "Enter at least one letter"
        if name in self.root["players"]:
            return i18n.f("{name} is already a player here", name=name)
        if len(self.root["players"]) >= MAX_PLAYERS:
            return i18n.f("There can be at most {n} players", n=MAX_PLAYERS)
        return None

    def add_player(self, name):
        """Add a player and switch to them. The first one takes over any progress made before names."""
        name = clean_name(name)
        if self.can_add(name):
            return False
        unnamed = self.root.get("unnamed")
        self.root["players"][name] = unnamed if unnamed else _default_player()
        self.root["unnamed"] = None
        self.switch(name)
        return True

    def switch(self, name):
        if name not in self.root["players"]:
            return
        self.root["current"] = name
        self.data = self.root["players"][name]
        self.data["seen"] = time.time()
        self.save()

    def remove_player(self, name):
        """Delete a player and all of their progress (and their place on the online leaderboard); switches
        to whoever played last if it was the current one."""
        data = self.root["players"].pop(name, None)
        if data is None:
            return
        if data.get("online"):
            self.forget_online(data["online"]["token"])
        if self.root["current"] == name:
            rest = self.players()
            self.root["current"] = None
            if rest:
                self.switch(rest[0])
            else:
                self.data = self._player_data()
        self.save()

    def backup_data(self, name):
        """What a player's online backup holds: their progress and settings, without their token."""
        data = self.root["players"][name]
        return {k: v for k, v in data.items() if k not in ("online", "seen")}

    def restore_player(self, name, data, account):
        """Add a player restored from their online backup (``data``, None if nothing was backed up yet)
        and switch to them. Returns why not, if they can't be added."""
        name = clean_name(name)
        mine = self.root["players"].get(name)
        if mine is not None and (mine.get("online") or {}).get("id") != account["id"]:
            return i18n.f("There's already a player called {name} here. Remove them first.", name=name)
        if mine is None and len(self.root["players"]) >= MAX_PLAYERS:
            return i18n.f("There can be at most {n} players", n=MAX_PLAYERS)
        player = _default_player()
        for k, v in (data or {}).items():
            if k in player and isinstance(v, type(player[k])):
                player[k] = v
        player["settings"] = {**_default_player()["settings"], **player["settings"]}
        player["online"] = account
        self.root["players"][name] = player
        self.switch(name)
        return None

    def forget_online(self, token):
        """Remember to delete a leaderboard player from the server (see online.Online.flush)."""
        if token not in self.root["forget"]:
            self.root["forget"].append(token)
        self.save()

    def unforget_online(self, token):
        if token in self.root["forget"]:
            self.root["forget"].remove(token)
            self.save()

    def record_subtest(self, code, raw, scaled, details):
        entry = self.data["subtests"].setdefault(code, {"history": [], "best": 0})
        entry["history"].append({"ts": time.time(), "raw": raw, "scaled": scaled, **details})
        entry["history"] = entry["history"][-50:]
        entry["best"] = max(entry["best"], scaled)
        self.save()

    def record_battery(self, scaled_by_code, indexes, overall):
        # (older entries kept the overall points under "fsiq")
        self.data["batteries"].append({"ts": time.time(), "scaled": scaled_by_code, "indexes": indexes,
                                       "overall": overall})
        self.save()

    def last_scaled(self, code):
        e = self.data["subtests"].get(code)
        return e["history"][-1]["scaled"] if e and e["history"] else None

    def last_raw(self, code):
        e = self.data["subtests"].get(code)
        return e["history"][-1]["raw"] if e and e["history"] else None

    def best_scaled(self, code):
        e = self.data["subtests"].get(code)
        return e["best"] if e else 0

    def attempts(self, code):
        e = self.data["subtests"].get(code)
        return len(e["history"]) if e else 0

    # ------------------------------------------------------------ challenge modes
    def rating(self, code):
        """{"rating", "played", "peak"} for a subtest's puzzle rating (None if never played)."""
        return self.data["ratings"].get(code)

    def set_rating(self, code, rating, played):
        e = self.data["ratings"].setdefault(code, {"rating": rating, "played": 0, "peak": rating})
        e["rating"] = round(rating, 1)
        e["played"] = played
        e["peak"] = max(e["peak"], e["rating"])
        self.save()

    def daily_result(self, day):
        return self.data["daily"].get(day.isoformat())

    def record_daily(self, day, code, results):
        """Only the first completed attempt of each day counts. Returns True if this one did."""
        key = day.isoformat()
        if key in self.data["daily"]:
            return False
        self.data["daily"][key] = {"code": code, "results": [bool(s) for _, s in results],
                                   "solved": sum(1 for _, s in results if s)}
        self.save()
        return True

    def daily_streak(self, today):
        """Consecutive days played, ending today (or yesterday, if today isn't played yet)."""
        day = today if today.isoformat() in self.data["daily"] else today - datetime.timedelta(days=1)
        n = 0
        while day.isoformat() in self.data["daily"]:
            n += 1
            day -= datetime.timedelta(days=1)
        return n
