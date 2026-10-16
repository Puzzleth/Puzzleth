# Puzzleth leaderboard server

The online leaderboard is a [Cloudflare Worker](https://developers.cloudflare.com/workers/) with a
[D1](https://developers.cloudflare.com/d1/) database. Both fit easily in Cloudflare's free plan.
The game finds the server through `SERVER_URL` in `puzzleth/online.py`, and shows the
Leaderboard button only once that's set.

## Deploy it

You need a free Cloudflare account and Node.js.

```sh
cd server
npx wrangler login
npx wrangler d1 create puzzleth-leaderboard        # prints a database_id: put it in wrangler.toml
npx wrangler d1 execute puzzleth-leaderboard --remote --file=schema.sql
npx wrangler deploy                                # prints the Worker's address
```

`SERVER_URL` takes the Worker's web address, not the database id. Put the address `wrangler deploy` printed (for example
`https://puzzleth-leaderboard.yourname.workers.dev`) into `SERVER_URL` in `puzzleth/online.py`,
then push. The next web build shows the leaderboard.

**Updating it.** When the server's code changes, run the schema again (it only adds what's
missing, and keeps every player) and redeploy:

```sh
npx wrangler d1 execute puzzleth-leaderboard --remote --file=schema.sql
npx wrangler deploy
```

No secrets are involved. The repository holds the server's code and address, but no keys or
passwords. Each player's token is created by the server when they join, kept only on their
device, and stored on the server only as a hash.

## What it stores and checks

Only players who choose **Join** in the game are sent anywhere. For each of them the server keeps
their name, a four-character tag (so two players called ANA can be told apart), and for each
subtest their puzzle rating, peak and number of puzzles played. It also keeps a backup of their
progress and settings as the game sends it, and the hash of their recovery code, which moves them
to another device. **Leave the leaderboard**, or removing the player in the game, deletes all of it.

Restoring with the recovery code gives the new device a new token, and the old token stops
working. Wrong codes are limited to 20 a day per address. Codes are 12 characters, about 60
random bits, so they can't be guessed in that many tries.

The game works out ratings itself, so the server can't check each puzzle. Instead it accepts only
ratings the game's rules could have produced (`src/rules.js`):

- ratings between 100 and 3000, for the four subtests with rated sets;
- the number of puzzles played never goes down;
- each puzzle moves the rating by at most 48 points, the game's largest step;
- puzzles can't be played faster than one every two seconds (plus a set's worth of slack);
- at most 20 new players a day from one address.

That stops typos and casual tampering, not a determined cheater who plays by those rules. Players
are ranked once they've played a full set of 10 puzzles.

## Try it locally

```sh
cd server
npm test           # the Worker against a real SQLite database (Node 22.5 or newer)
npm run local      # the leaderboard on http://localhost:8787, without Cloudflare
PUZZLETH_SERVER=http://localhost:8787 ../puzzle   # in another terminal: the game, using it
```

`npx wrangler dev` runs it in Cloudflare's own local runtime instead (first run
`npx wrangler d1 execute puzzleth-leaderboard --local --file=schema.sql`).

## API

| Request | Body | Answer |
|---|---|---|
| `POST /players` | `{"name": "ANA"}` | `{"id", "name", "tag", "token", "code"}` |
| `PUT /ratings/MR` | `{"rating": 1234.5, "played": 40}` | `{"rank", "total"}` (`rank` is null until 10 puzzles) |
| `GET /leaderboard/MR?limit=10` | | `{"code", "total", "top": [...], "me"}` |
| `DELETE /players/me` | | 204 |
| `PUT /backup` | the player's progress, a JSON object | `{"updated"}` |
| `POST /players/me/code` | | `{"code"}`, a new recovery code (the old one stops working) |
| `POST /restore` | `{"code": "K3QX-7HMP-W2ZA"}` | `{"id", "name", "tag", "token", "code", "data", "ratings"}` |

Send the token as `Authorization: Bearer <token>` to post ratings, back up, get a new code, leave,
or get `me` in the leaderboard. The subtest codes are `BD`, `MR`, `AR` and `VP`.
