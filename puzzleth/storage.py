"""Profile persistence (JSON in the user's home directory)."""
import datetime
import json
import os
import time
from pathlib import Path

from . import web

WEB_KEY = "puzzleth.profile"


def _path():
    base = os.environ.get("PUZZLETH_HOME")
    return Path(base) if base else Path.home() / ".puzzleth" / "profile.json"


def _legacy_path():
    """Where the game saved progress before it was renamed from Brain Puzzlerer."""
    return None if os.environ.get("PUZZLETH_HOME") else Path.home() / ".brain_puzzlerer" / "profile.json"


def _default():
    return {"subtests": {}, "batteries": [], "ratings": {}, "daily": {},
            "settings": {"feedback": True, "show_scores": True}}


class Profile:
    def __init__(self):
        self.path = None if web.IS_WEB else _path()
        self.data = _default()
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
            self.data.update(loaded)
            for k, v in _default().items():   # profiles from older versions
                self.data.setdefault(k, v)
            for k, v in _default()["settings"].items():
                self.data["settings"].setdefault(k, v)
        except (OSError, ValueError):
            pass

    def save(self):
        if web.IS_WEB:
            web.save(WEB_KEY, json.dumps(self.data))
            return
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            with open(tmp, "w") as f:
                json.dump(self.data, f, indent=1)
            tmp.replace(self.path)
        except OSError:
            pass

    @property
    def settings(self):
        return self.data["settings"]

    def record_subtest(self, code, raw, scaled, details):
        entry = self.data["subtests"].setdefault(code, {"history": [], "best": 0})
        entry["history"].append({"ts": time.time(), "raw": raw, "scaled": scaled, **details})
        entry["history"] = entry["history"][-50:]
        entry["best"] = max(entry["best"], scaled)
        self.save()

    def record_battery(self, scaled_by_code, indexes, fsiq):
        self.data["batteries"].append({"ts": time.time(), "scaled": scaled_by_code, "indexes": indexes, "fsiq": fsiq})
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
