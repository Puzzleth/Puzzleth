"""Profile persistence (JSON in the user's home directory)."""
import json
import os
import time
from pathlib import Path


def _path():
    base = os.environ.get("BRAIN_PUZZLERER_HOME")
    return Path(base) if base else Path.home() / ".brain_puzzlerer" / "profile.json"


def _default():
    return {"subtests": {}, "batteries": [], "settings": {"feedback": True}}


class Profile:
    def __init__(self):
        self.path = _path()
        self.data = _default()
        try:
            with open(self.path) as f:
                loaded = json.load(f)
            self.data.update(loaded)
        except (OSError, ValueError):
            pass

    def save(self):
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
