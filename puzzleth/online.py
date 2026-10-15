"""The online leaderboard (its server is in server/). Players join it one by one; until they do, nothing
about them is sent anywhere. Requests never hold up the game: they run in the background (a thread
on the desktop, the page's fetch() in a browser), and ``poll()``, called every frame, hands their
answers back to the game."""
import json
import os
import threading

from . import web

# The leaderboard server's address, e.g. "https://puzzleth-leaderboard.you.workers.dev" (see
# server/README.md). The game shows the leaderboard once it's set. PUZZLETH_SERVER overrides it.
SERVER_URL = "https://puzzleth-leaderboard.huci.workers.dev"
TIMEOUT = 15


def server():
    return os.environ.get("PUZZLETH_SERVER", SERVER_URL).rstrip("/")


def enabled():
    return bool(server())


def valid():
    """Whether the server's address is a web address (and not, say, the database's id)."""
    return server().startswith(("https://", "http://"))


class Request:
    """One request to the server. ``status`` is the HTTP status (0 if the server couldn't be reached)
    and ``data`` the answer's JSON, once ``done``."""

    def __init__(self, method, path, body=None, token=None, then=None):
        self.then = then
        self.done = False
        self.status = 0
        self.data = None
        self._js = None
        self._answer = None
        url = server() + path
        payload = json.dumps(body) if body is not None else ""
        if not valid():
            self._answer = (0, "")
        elif web.IS_WEB:
            # see puzzleth_fetch in tools/web/puzzleth.tmpl
            self._js = web.fetch(method, url, payload, token or "")
            if self._js is None:
                self._answer = (0, "")
        else:
            threading.Thread(target=self._send, args=(method, url, payload, token), daemon=True).start()

    @property
    def ok(self):
        return 200 <= self.status < 300

    def _send(self, method, url, payload, token):
        import urllib.error
        import urllib.request
        # Cloudflare turns away Python's own User-Agent ("error code: 1010"), so the game names itself
        headers = {"User-Agent": "Puzzleth (+https://github.com/VN0V4/Puzzleth)"}
        if payload:
            headers["Content-Type"] = "application/json"
        if token:
            headers["Authorization"] = f"Bearer {token}"
        try:
            req = urllib.request.Request(url, data=payload.encode() if payload else None, method=method,
                                         headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
                self._answer = (r.status, r.read().decode())
        except urllib.error.HTTPError as e:
            with e:
                self._answer = (e.code, e.read().decode(errors="replace"))
        except Exception:
            self._answer = (0, "")

    def poll(self):
        """True once the answer is in (and ``then`` has been called with it)."""
        if self.done:
            return True
        if self._answer is None and self._js is not None:
            got = web.fetch_result(self._js)
            if got:
                try:
                    r = json.loads(got)
                    self._answer = (int(r["status"]), r["body"])
                except (ValueError, KeyError, TypeError):
                    self._answer = (0, "")
        if self._answer is None:
            return False
        self.status, text = self._answer
        try:
            self.data = json.loads(text) if text else None
        except ValueError:
            self.data = None
        self.done = True
        if self.then:
            self.then(self)
        return True


def describe(req):
    """What went wrong with a request, for the player."""
    if not valid():
        return f"The leaderboard's address, {server()!r}, isn't a web address (see server/README.md)."
    if req.status == 0:
        return "Couldn't reach the leaderboard. Check your connection and try again."
    if req.status == 429:
        return "Too many new players from here today. Try again tomorrow."
    error = req.data.get("error") if isinstance(req.data, dict) else None
    return f"The leaderboard said no ({error or req.status})."


class Online:
    """Each player's place on the leaderboard. A player who joined has ``data["online"]``: their
    ``id``, ``tag``, secret ``token``, and ``sent``, how many puzzles each posted rating was after."""

    def __init__(self, profile):
        self.profile = profile
        self.pending = []
        self.ranks = {}       # (player, code) -> {"rank", "total"}, from the last rating posted
        self.busy = set()     # (player, code) being posted
        self.joining = None   # the player whose join is under way
        self.error = None

    def enabled(self):
        return enabled()

    def request(self, method, path, body=None, token=None, then=None):
        req = Request(method, path, body, token, then)
        self.pending.append(req)
        return req

    def poll(self):
        if self.pending:
            self.pending = [r for r in self.pending if not r.poll()]

    def account(self, name=None):
        data = self.profile.player(name or self.profile.current)
        return data.get("online") if data else None

    # ------------------------------------------------------------ joining and leaving
    def join(self, then=None):
        """Put the current player on the leaderboard, with the ratings they already have."""
        name = self.profile.current
        if not self.enabled() or not name or self.account(name) or self.joining:
            return
        self.joining = name
        self.error = None

        def joined(req):
            self.joining = None
            data = self.profile.player(name)
            if req.ok and data is not None and isinstance(req.data, dict) and req.data.get("token"):
                data["online"] = {k: req.data[k] for k in ("id", "tag", "token")}
                data["online"]["sent"] = {}
                self.profile.save()
                self.push(name, then)
            else:
                self.error = describe(req)
                if then:
                    then()

        self.request("POST", "/players", {"name": name}, then=joined)

    def leave(self, name=None):
        """Take a player off the leaderboard. Their progress here stays as it is."""
        name = name or self.profile.current
        data = self.profile.player(name)
        if not data or not data.get("online"):
            return
        self.profile.forget_online(data["online"]["token"])
        data["online"] = None
        self.profile.save()
        for key in [k for k in self.ranks if k[0] == name]:
            del self.ranks[key]
        self.flush()

    def flush(self):
        """Delete, from the server, the players who left it (or were removed here) while it was out of reach."""
        if not self.enabled():
            return
        for token in list(self.profile.root.get("forget", [])):
            def gone(req, token=token):
                if req.ok or req.status == 401:   # 401: it was already gone
                    self.profile.unforget_online(token)
            self.request("DELETE", "/players/me", token=token, then=gone)

    # ------------------------------------------------------------ ratings
    def push(self, name=None, then=None):
        """Post a player's ratings that changed since they were last posted. ``then`` is called when
        they all have been (or failed to be)."""
        from .challenge import challenge_codes
        name = name or self.profile.current
        acct = self.account(name)
        if not self.enabled() or not acct:
            if then:
                then()
            return
        ratings = self.profile.player(name)["ratings"]
        todo = [c for c in challenge_codes()
                if c in ratings and acct["sent"].get(c) != ratings[c]["played"] and (name, c) not in self.busy]
        left = [len(todo)]
        if not todo and then:
            then()
        for code in todo:
            r = ratings[code]
            self.busy.add((name, code))

            def posted(req, code=code, played=r["played"]):
                self.busy.discard((name, code))
                acct = self.account(name)
                if acct is not None:
                    if req.ok:
                        acct["sent"][code] = played
                        if isinstance(req.data, dict):
                            self.ranks[(name, code)] = req.data
                    elif req.status == 409:   # refused for good: don't send it again
                        acct["sent"][code] = played
                    elif req.status == 401:   # the server no longer knows them
                        self.profile.player(name)["online"] = None
                    self.profile.save()
                left[0] -= 1
                if not left[0] and then:
                    then()

            self.request("PUT", f"/ratings/{code}", {"rating": r["rating"], "played": r["played"]},
                         token=acct["token"], then=posted)

    def rank(self, code, name=None):
        """{"rank", "total"} from the last time the player's rating for ``code`` was posted, if it was."""
        return self.ranks.get((name or self.profile.current, code))

    def board(self, code, then, limit=10):
        """Fetch the top of the leaderboard (and where the current player stands, if they joined)."""
        acct = self.account()
        return self.request("GET", f"/leaderboard/{code}?limit={limit}", token=acct["token"] if acct else None,
                            then=then)
