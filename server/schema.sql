-- The online leaderboard's database (Cloudflare D1, which is SQLite). See server/README.md.

-- Everyone who has joined the leaderboard. The token that proves who a player is stays on their
-- device; only its SHA-256 hash is kept here.
CREATE TABLE IF NOT EXISTS players (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  tag TEXT NOT NULL,              -- four characters that tell players with the same name apart
  token_hash TEXT NOT NULL UNIQUE,
  created INTEGER NOT NULL        -- unix seconds
);

-- One puzzle rating per player and subtest.
CREATE TABLE IF NOT EXISTS ratings (
  player_id TEXT NOT NULL REFERENCES players(id) ON DELETE CASCADE,
  code TEXT NOT NULL,
  rating REAL NOT NULL,
  played INTEGER NOT NULL,
  peak REAL NOT NULL,
  updated INTEGER NOT NULL,       -- unix seconds
  PRIMARY KEY (player_id, code)
);
CREATE INDEX IF NOT EXISTS ratings_board ON ratings (code, rating DESC);

-- Recent sign-ups by (hashed) address, to limit how fast new players can be made.
CREATE TABLE IF NOT EXISTS signups (
  ip_hash TEXT NOT NULL,
  ts INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS signups_ip ON signups (ip_hash, ts);
