// The leaderboard Worker against a real SQLite database (node:sqlite standing in for D1).
//   cd server && npm test
import assert from "node:assert/strict";
import { beforeEach, test } from "node:test";

import { FakeD1 } from "../local/fake-d1.js";
import worker from "../src/index.js";
import { MAX_STEP, RANKED_AFTER, RESTORE_FAILS_PER_DAY, SIGNUPS_PER_DAY, checkRating } from "../src/rules.js";

let env;
let ip;
beforeEach(() => {
  env = { DB: new FakeD1(), IP_HASH_KEY: "test-key" };
  ip = 0;
});

async function call(method, path, { body, token, from } = {}) {
  const headers = { "CF-Connecting-IP": from || `10.0.0.${++ip}` };
  if (token) headers.Authorization = `Bearer ${token}`;
  const res = await worker.fetch(
    new Request(`https://board.test${path}`, { method, headers, body: body && JSON.stringify(body) }), env);
  const text = await res.text();
  return { status: res.status, data: text ? JSON.parse(text) : null, headers: res.headers };
}

const join = async (name) => (await call("POST", "/players", { body: { name } })).data;

async function post(token, code, rating, played) {
  return call("PUT", `/ratings/${code}`, { token, body: { rating, played } });
}

test("joining hands out a token and a tag", async () => {
  const r = await call("POST", "/players", { body: { name: "ANA" } });
  assert.equal(r.status, 201);
  assert.equal(r.data.name, "ANA");
  assert.match(r.data.tag, /^[2-9A-Z]{4}$/);
  assert.ok(r.data.token.length >= 40);
  assert.equal(r.headers.get("Access-Control-Allow-Origin"), "*");
  // only the token's hash is stored
  const row = env.DB.db.prepare("SELECT token_hash FROM players").get();
  assert.notEqual(row.token_hash, r.data.token);
});

test("names follow the game's rules", async () => {
  for (const name of ["", "toolongname", "ana", "A B", 7, null])
    assert.equal((await call("POST", "/players", { body: { name } })).status, 400, String(name));
  assert.equal((await call("POST", "/players", { body: "nonsense" })).status, 400);
});

test("sign-ups are limited per address", async () => {
  for (let i = 0; i < SIGNUPS_PER_DAY; i++)
    assert.equal((await call("POST", "/players", { body: { name: "BOT" }, from: "1.2.3.4" })).status, 201);
  assert.equal((await call("POST", "/players", { body: { name: "BOT" }, from: "1.2.3.4" })).status, 429);
  assert.equal((await call("POST", "/players", { body: { name: "ANA" }, from: "5.6.7.8" })).status, 201);
});

test("addresses are stored only keyed with IP_HASH_KEY", async () => {
  await call("POST", "/players", { body: { name: "ANA" }, from: "1.2.3.4" });
  const { createHash } = await import("node:crypto");
  const { ip_hash } = env.DB.db.prepare("SELECT ip_hash FROM signups").get();
  assert.match(ip_hash, /^[0-9a-f]{64}$/);
  assert.notEqual(ip_hash, createHash("sha256").update("puzzleth:1.2.3.4").digest("hex"));
  env.IP_HASH_KEY = undefined;
  assert.equal((await call("POST", "/players", { body: { name: "ANA" } })).status, 500);
});

test("ratings need a known token and a rated subtest", async () => {
  const ana = await join("ANA");
  assert.equal((await post("nope", "MR", 1100, 10)).status, 401);
  assert.equal((await post(undefined, "MR", 1100, 10)).status, 401);
  assert.equal((await post(ana.token, "DS", 1100, 10)).status, 404);
  assert.equal((await post(ana.token, "MR", 1100, 10)).status, 200);
});

test("the leaderboard ranks players after a rated set", async () => {
  const ana = await join("ANA");
  const bo = await join("BO");
  const cy = await join("CY");
  assert.deepEqual((await post(ana.token, "MR", 1200, 12)).data, { rank: 1, total: 1 });
  assert.deepEqual((await post(bo.token, "MR", 1300, 10)).data, { rank: 1, total: 2 });
  assert.deepEqual((await post(cy.token, "MR", 1100, RANKED_AFTER - 1)).data, { rank: null, total: 2 });
  const board = (await call("GET", "/leaderboard/MR", { token: ana.token })).data;
  assert.equal(board.total, 2);
  assert.deepEqual(board.top.map((r) => [r.rank, r.name, r.rating]), [[1, "BO", 1300], [2, "ANA", 1200]]);
  assert.equal(board.me.rank, 2);
  assert.equal(board.me.tag, ana.tag);
  // not ranked yet, but still told who they are
  const mine = (await call("GET", "/leaderboard/MR", { token: cy.token })).data.me;
  assert.equal(mine.rank, null);
  assert.equal(mine.played, RANKED_AFTER - 1);
  // anyone can look, with or without a token
  const anon = (await call("GET", "/leaderboard/MR")).data;
  assert.equal(anon.me, null);
  assert.equal(anon.top.length, 2);
  assert.equal((await call("GET", "/leaderboard/BD")).data.total, 0);
});

test("tied ratings share a rank and the limit is respected", async () => {
  for (const [name, rating] of [["A", 1200], ["B", 1200], ["C", 1100]]) {
    const p = await join(name);
    await post(p.token, "VP", rating, 10);
  }
  const top = (await call("GET", "/leaderboard/VP?limit=2")).data.top;
  assert.deepEqual(top.map((r) => r.rank), [1, 1]);
  const all = (await call("GET", "/leaderboard/VP?limit=500")).data.top;
  assert.deepEqual(all.map((r) => r.rank), [1, 1, 3]);
});

test("ratings the game's rules can't produce are refused", async () => {
  const ana = await join("ANA");
  assert.equal((await post(ana.token, "MR", 1000 + MAX_STEP * 10 + 5, 10)).status, 409);   // too far
  assert.equal((await post(ana.token, "MR", 5000, 1000)).status, 409);                      // out of range
  assert.equal((await post(ana.token, "MR", "high", 10)).status, 409);
  assert.equal((await post(ana.token, "MR", 1300, 10)).status, 200);
  const r = await post(ana.token, "MR", 1290, 9);                                            // played went down
  assert.equal(r.status, 409);
  assert.deepEqual([r.data.rating, r.data.played], [1300, 10]);   // tells the game what it has
  // a few more puzzles are fine, thousands of them in a moment aren't
  assert.equal((await post(ana.token, "MR", 1350, 15)).status, 200);
  assert.equal((await post(ana.token, "MR", 2900, 5000)).status, 409);
  // the peak is kept
  await post(ana.token, "MR", 1320, 16);
  assert.equal((await call("GET", "/leaderboard/MR", { token: ana.token })).data.me.peak, 1350);
});

test("checkRating allows the time puzzles take", () => {
  const old = { rating: 1000, played: 10, updated: 0 };
  assert.equal(checkRating(old, 1000, 20, 0), null);                 // a set's worth of slack
  assert.ok(checkRating(old, 1000, 40, 0));
  // Time allows more puzzles, but a single post is capped
  assert.ok(checkRating(old, 1000, 40, 3600));
  assert.equal(checkRating(null, 1400, 20, 0), null);                 // first post after joining
  assert.ok(checkRating(null, 99, 20, 0));
});

test("leaving removes the player and their ratings", async () => {
  const ana = await join("ANA");
  await post(ana.token, "AR", 1100, 10);
  assert.equal((await call("DELETE", "/players/me", { token: ana.token })).status, 204);
  assert.equal((await call("DELETE", "/players/me", { token: ana.token })).status, 401);
  assert.equal((await call("GET", "/leaderboard/AR")).data.total, 0);
  assert.equal(env.DB.db.prepare("SELECT COUNT(*) AS n FROM ratings").get().n, 0);
});

test("browsers' preflight requests are answered", async () => {
  const r = await worker.fetch(new Request("https://board.test/ratings/MR", { method: "OPTIONS" }), env);
  assert.equal(r.status, 204);
  assert.match(r.headers.get("Access-Control-Allow-Headers"), /Authorization/);
});

test("progress is backed up and restored with the recovery code", async () => {
  const ana = await join("ANA");
  assert.match(ana.code, /^[2-9A-Z]{4}-[2-9A-Z]{4}-[2-9A-Z]{4}$/);
  await post(ana.token, "MR", 1200, 12);
  const progress = { subtests: { MR: { history: [], best: 12 } }, daily: {} };
  assert.equal((await call("PUT", "/backup", { token: ana.token, body: progress })).status, 200);
  assert.equal((await call("PUT", "/backup", { token: "nope", body: progress })).status, 401);
  assert.equal((await call("PUT", "/backup", { token: ana.token, body: [1, 2] })).status, 400);
  // codes are typed in any case, with or without dashes
  const r = await call("POST", "/restore", { body: { code: ana.code.replace(/-/g, "").toLowerCase() } });
  assert.equal(r.status, 200);
  assert.deepEqual([r.data.id, r.data.name, r.data.tag, r.data.code], [ana.id, "ANA", ana.tag, ana.code]);
  assert.deepEqual(r.data.data, progress);
  assert.deepEqual(r.data.ratings, [{ code: "MR", rating: 1200, played: 12, peak: 1200 }]);
  // the new device takes over: the old token no longer works, the new one does
  assert.equal((await post(ana.token, "MR", 1210, 13)).status, 401);
  assert.equal((await post(r.data.token, "MR", 1210, 13)).status, 200);
  // only the code's hash is kept
  assert.equal(env.DB.db.prepare("SELECT COUNT(*) AS n FROM backups WHERE code_hash LIKE ?").get(
    `%${ana.code.slice(0, 4)}%`).n, 0);
});

test("a player who joined before backups can get a code, and a new code retires the old", async () => {
  const ana = await join("ANA");
  env.DB.db.prepare("DELETE FROM backups").run();
  const first = await call("POST", "/players/me/code", { token: ana.token });
  assert.equal(first.status, 200);
  const r = await call("POST", "/restore", { body: { code: first.data.code } });
  assert.equal(r.data.data, null);   // nothing backed up yet
  const second = (await call("POST", "/players/me/code", { token: r.data.token })).data.code;
  assert.notEqual(second, first.data.code);
  assert.equal((await call("POST", "/restore", { body: { code: first.data.code } })).status, 404);
  assert.equal((await call("POST", "/restore", { body: { code: second } })).status, 200);
});

test("wrong recovery codes are limited per address, and leaving deletes the backup", async () => {
  for (let i = 0; i < RESTORE_FAILS_PER_DAY; i++)
    assert.equal((await call("POST", "/restore", { body: { code: "ABCD-EFGH-JKLM" }, from: "1.2.3.4" })).status, 404);
  assert.equal((await call("POST", "/restore", { body: { code: "ABCD-EFGH-JKLM" }, from: "1.2.3.4" })).status, 429);
  const ana = await join("ANA");
  await call("PUT", "/backup", { token: ana.token, body: { daily: {} } });
  assert.equal((await call("DELETE", "/players/me", { token: ana.token })).status, 204);
  assert.equal(env.DB.db.prepare("SELECT COUNT(*) AS n FROM backups").get().n, 0);
  assert.equal((await call("POST", "/restore", { body: { code: ana.code } })).status, 404);
});
