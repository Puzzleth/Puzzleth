// Puzzleth's online leaderboard: a Cloudflare Worker with a D1 database (see server/README.md).
//
//   POST   /players              {name}             join: returns {id, tag, token, code}
//   PUT    /ratings/:code        {rating, played}   post your rating: returns {rank, total}
//   GET    /leaderboard/:code    ?limit=10          the top players, and you (with your token)
//   DELETE /players/me                              leave: removes you, your ratings and your backup
//   PUT    /backup               {...}              back up your progress (the game's own JSON)
//   POST   /players/me/code                         a new recovery code: returns {code}
//   POST   /restore              {code}             move to this device: returns {id, name, tag, token,
//                                                   code, data, ratings}
//
// A player proves who they are with the token they got on joining ("Authorization: Bearer ...").
// Their recovery code lets them get a new token on another device, which retires the old one.
// Ratings are worked out by the game, so the server can't check every puzzle; it accepts only
// ratings the game's rules could have produced (see checkRating in rules.js).

import {
  CODE_LEN, CODES, MAX_BACKUP, MAX_RATING, NAME, RANKED_AFTER, RESTORE_FAILS_PER_DAY, SECONDS_PER_PUZZLE,
  SIGNUPS_PER_DAY, START_RATING, TAG_CHARS, checkRating,
} from "./rules.js";

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Authorization, Content-Type",
  "Access-Control-Max-Age": "86400",
};

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...CORS },
  });
}

const fail = (status, error) => json({ error }, status);

function randomString(n, chars) {
  const bytes = crypto.getRandomValues(new Uint8Array(n));
  return Array.from(bytes, (b) => chars[b % chars.length]).join("");
}

function randomToken() {
  const bytes = crypto.getRandomValues(new Uint8Array(32));
  return btoa(String.fromCharCode(...bytes)).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function sha256(text) {
  const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(text));
  return Array.from(new Uint8Array(digest), (b) => b.toString(16).padStart(2, "0")).join("");
}

async function readJson(request, max = 1000) {
  const text = await request.text();
  if (text.length > max) return null;
  try {
    const data = JSON.parse(text);
    return data && typeof data === "object" ? data : null;
  } catch {
    return null;
  }
}

async function player(request, db) {
  const m = /^Bearer (\S+)$/.exec(request.headers.get("Authorization") || "");
  if (!m) return null;
  return db
    .prepare("SELECT id, name, tag, created FROM players WHERE token_hash = ?")
    .bind(await sha256(m[1]))
    .first();
}

/** A recovery code as players see it, XXXX-XXXX-XXXX, and as it's hashed: without dashes or spaces. */
const newCode = () => randomString(CODE_LEN, TAG_CHARS).replace(/(.{4})(?=.)/g, "$1-");
const plainCode = (code) => String(code).toUpperCase().replace(/[^0-9A-Z]/g, "");
const codeHash = (code) => sha256("puzzleth-code:" + plainCode(code));

/**
 * An address keyed with the IP_HASH_KEY secret (HMAC-SHA-256). A plain hash of an address could be
 * undone by hashing every address there is; without the key, which only Cloudflare holds, it can't.
 */
const hmacKeys = new Map();
async function ipHashOf(request, env, what) {
  const secret = env.IP_HASH_KEY;
  if (!secret) throw new Error("IP_HASH_KEY is not set: run `npx wrangler secret put IP_HASH_KEY`");
  if (!hmacKeys.has(secret)) {
    hmacKeys.set(secret, crypto.subtle.importKey(
      "raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]));
  }
  const text = `puzzleth${what}:` + (request.headers.get("CF-Connecting-IP") || "");
  const mac = await crypto.subtle.sign("HMAC", await hmacKeys.get(secret), new TextEncoder().encode(text));
  return Array.from(new Uint8Array(mac), (b) => b.toString(16).padStart(2, "0")).join("");
}

/** How many times this address did ``what`` in the last day (signups doubles as the log of both). */
async function recently(request, env, what, now) {
  const ipHash = await ipHashOf(request, env, what);
  await env.DB.prepare("DELETE FROM signups WHERE ts < ?").bind(now - 86400).run();
  const row = await env.DB.prepare("SELECT COUNT(*) AS n FROM signups WHERE ip_hash = ?").bind(ipHash).first();
  return { n: row.n, log: env.DB.prepare("INSERT INTO signups (ip_hash, ts) VALUES (?, ?)").bind(ipHash, now) };
}

async function rankOf(db, code, rating) {
  const row = await db
    .prepare(
      "SELECT COUNT(*) AS total, SUM(CASE WHEN rating > ? THEN 1 ELSE 0 END) AS above " +
        "FROM ratings WHERE code = ? AND played >= ?",
    )
    .bind(rating, code, RANKED_AFTER)
    .first();
  return { rank: (row.above || 0) + 1, total: row.total || 0 };
}

async function join(request, env) {
  const body = await readJson(request);
  const name = body && typeof body.name === "string" ? body.name : "";
  if (!NAME.test(name)) return fail(400, "names are 1 to 8 capital letters and digits");
  const now = Math.floor(Date.now() / 1000);
  const recent = await recently(request, env, "", now);
  if (recent.n >= SIGNUPS_PER_DAY) return fail(429, "too many new players from here today");
  const id = randomString(12, "0123456789abcdef");
  const tag = randomString(4, TAG_CHARS);
  const token = randomToken();
  const code = newCode();
  await env.DB.batch([
    env.DB.prepare("INSERT INTO players (id, name, tag, token_hash, created) VALUES (?, ?, ?, ?, ?)").bind(
      id, name, tag, await sha256(token), now),
    env.DB.prepare("INSERT INTO backups (player_id, code_hash) VALUES (?, ?)").bind(id, await codeHash(code)),
    recent.log,
  ]);
  return json({ id, name, tag, token, code }, 201);
}

async function postRating(request, env, code) {
  const me = await player(request, env.DB);
  if (!me) return fail(401, "unknown player");
  const body = await readJson(request);
  if (!body) return fail(400, "expected {rating, played}");
  const rating = Math.round(body.rating * 10) / 10;
  const played = body.played;
  const now = Math.floor(Date.now() / 1000);
  const old = await env.DB
    .prepare("SELECT rating, played, peak, updated FROM ratings WHERE player_id = ? AND code = ?")
    .bind(me.id, code)
    .first();
  // Apply the time-based cap to first posts too, using when the player joined.
  const effectiveOld = old || {
    rating: START_RATING,
    played: 0,
    // Give slack for the set being played at join time, same as later posts
    updated: me.created - RANKED_AFTER * SECONDS_PER_PUZZLE,
  };
  const why = checkRating(effectiveOld, rating, played, now);
  if (why) return json({ error: why, rating: old ? old.rating : null, played: old ? old.played : 0 }, 409);
  await env.DB
    .prepare(
      "INSERT INTO ratings (player_id, code, rating, played, peak, updated) VALUES (?, ?, ?, ?, ?, ?) " +
        "ON CONFLICT (player_id, code) DO UPDATE SET rating = ?, played = ?, peak = MAX(peak, ?), updated = ?",
    )
    .bind(
      // VALUES
      me.id, code, rating, played, rating, now,
      // DO UPDATE SET ...
      rating, played, rating, now,
    )
    .run();
  const ranked = played >= RANKED_AFTER;
  const { rank, total } = await rankOf(env.DB, code, rating);
  return json({ rank: ranked ? rank : null, total });
}

async function leaderboard(request, env, code, url) {
  const limit = Math.max(1, Math.min(50, parseInt(url.searchParams.get("limit"), 10) || 10));
  const { results } = await env.DB
    .prepare(
      "SELECT p.id, p.name, p.tag, r.rating, r.played, r.peak FROM ratings r JOIN players p ON p.id = r.player_id " +
        "WHERE r.code = ? AND r.played >= ? ORDER BY r.rating DESC, r.played DESC, r.updated ASC LIMIT ?",
    )
    .bind(code, RANKED_AFTER, limit)
    .all();
  // tied ratings share a rank
  const top = [];
  for (const [i, r] of results.entries()) {
    const rank = i && r.rating === results[i - 1].rating ? top[i - 1].rank : i + 1;
    top.push({ rank, id: r.id, name: r.name, tag: r.tag, rating: r.rating, played: r.played, peak: r.peak });
  }
  let me = null;
  const who = await player(request, env.DB);
  if (who) {
    const mine = await env.DB
      .prepare("SELECT rating, played, peak FROM ratings WHERE player_id = ? AND code = ?")
      .bind(who.id, code)
      .first();
    me = { id: who.id, name: who.name, tag: who.tag, rank: null, rating: null, played: 0, peak: null };
    if (mine) {
      Object.assign(me, mine);
      if (mine.played >= RANKED_AFTER) me.rank = (await rankOf(env.DB, code, mine.rating)).rank;
    }
  }
  const { total } = await rankOf(env.DB, code, MAX_RATING);
  return json({ code, total, top, me });
}

async function leave(request, env) {
  const me = await player(request, env.DB);
  if (!me) return fail(401, "unknown player");
  await env.DB.batch([
    env.DB.prepare("DELETE FROM ratings WHERE player_id = ?").bind(me.id),
    env.DB.prepare("DELETE FROM backups WHERE player_id = ?").bind(me.id),
    env.DB.prepare("DELETE FROM players WHERE id = ?").bind(me.id),
  ]);
  return new Response(null, { status: 204, headers: CORS });
}

async function backup(request, env) {
  const me = await player(request, env.DB);
  if (!me) return fail(401, "unknown player");
  const data = await readJson(request, MAX_BACKUP);
  if (!data || Array.isArray(data)) return fail(400, `expected a JSON object of at most ${MAX_BACKUP} characters`);
  const now = Math.floor(Date.now() / 1000);
  await env.DB
    .prepare(
      "INSERT INTO backups (player_id, data, updated) VALUES (?, ?, ?) " +
        "ON CONFLICT (player_id) DO UPDATE SET data = ?, updated = ?",
    )
    .bind(me.id, JSON.stringify(data), now, JSON.stringify(data), now)
    .run();
  return json({ updated: now });
}

async function renewCode(request, env) {
  const me = await player(request, env.DB);
  if (!me) return fail(401, "unknown player");
  const code = newCode();
  await env.DB
    .prepare(
      "INSERT INTO backups (player_id, code_hash) VALUES (?, ?) " +
        "ON CONFLICT (player_id) DO UPDATE SET code_hash = ?",
    )
    .bind(me.id, await codeHash(code), await codeHash(code))
    .run();
  return json({ code });
}

async function restore(request, env) {
  const body = await readJson(request);
  const code = body && typeof body.code === "string" ? body.code : "";
  const now = Math.floor(Date.now() / 1000);
  const recent = await recently(request, env, "-restore", now);
  if (recent.n >= RESTORE_FAILS_PER_DAY) return fail(429, "too many wrong codes from here today");
  const found = plainCode(code).length === CODE_LEN && await env.DB
    .prepare(
      "SELECT p.id, p.name, p.tag, b.data FROM backups b JOIN players p ON p.id = b.player_id WHERE b.code_hash = ?",
    )
    .bind(await codeHash(code))
    .first();
  if (!found) {
    await recent.log.run();
    return fail(404, "no player has that code");
  }
  // a new token for this device; the old device's stops working
  const token = randomToken();
  await env.DB.prepare("UPDATE players SET token_hash = ? WHERE id = ?").bind(await sha256(token), found.id).run();
  const { results } = await env.DB
    .prepare("SELECT code, rating, played, peak FROM ratings WHERE player_id = ?")
    .bind(found.id)
    .all();
  return json({
    id: found.id, name: found.name, tag: found.tag, token, code: plainCode(code).replace(/(.{4})(?=.)/g, "$1-"),
    data: found.data ? JSON.parse(found.data) : null, ratings: results,
  });
}

async function handle(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "");
  const method = request.method;
  if (method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (path === "/players" && method === "POST") return join(request, env);
  if (path === "/players/me" && method === "DELETE") return leave(request, env);
  if (path === "/players/me/code" && method === "POST") return renewCode(request, env);
  if (path === "/backup" && method === "PUT") return backup(request, env);
  if (path === "/restore" && method === "POST") return restore(request, env);
  const m = /^\/(ratings|leaderboard)\/([A-Z]{2})$/.exec(path);
  if (m && CODES.includes(m[2])) {
    if (m[1] === "ratings" && method === "PUT") return postRating(request, env, m[2]);
    if (m[1] === "leaderboard" && method === "GET") return leaderboard(request, env, m[2], url);
  }
  if (path === "" && method === "GET") return json({ name: "Puzzleth leaderboard", codes: CODES });
  return fail(404, "not found");
}

export default {
  async fetch(request, env) {
    try {
      return await handle(request, env);
    } catch (e) {
      console.error(e);
      return fail(500, "server error");
    }
  },
};
