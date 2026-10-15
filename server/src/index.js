// Puzzleth's online leaderboard: a Cloudflare Worker with a D1 database (see server/README.md).
//
//   POST   /players              {name}             join: returns {id, tag, token}
//   PUT    /ratings/:code        {rating, played}   post your rating: returns {rank, total}
//   GET    /leaderboard/:code    ?limit=10          the top players, and you (with your token)
//   DELETE /players/me                              leave: removes you and your ratings
//
// A player proves who they are with the token they got on joining ("Authorization: Bearer ...").
// Ratings are worked out by the game, so the server can't check every puzzle; it accepts only
// ratings the game's rules could have produced (see checkRating in rules.js).

import { CODES, MAX_RATING, NAME, RANKED_AFTER, SIGNUPS_PER_DAY, TAG_CHARS, checkRating } from "./rules.js";

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

async function readJson(request) {
  const text = await request.text();
  if (text.length > 1000) return null;
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
  return db.prepare("SELECT id, name, tag FROM players WHERE token_hash = ?").bind(await sha256(m[1])).first();
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
  const ipHash = await sha256("puzzleth:" + (request.headers.get("CF-Connecting-IP") || ""));
  await env.DB.prepare("DELETE FROM signups WHERE ts < ?").bind(now - 86400).run();
  const recent = await env.DB.prepare("SELECT COUNT(*) AS n FROM signups WHERE ip_hash = ?").bind(ipHash).first();
  if (recent.n >= SIGNUPS_PER_DAY) return fail(429, "too many new players from here today");
  const id = randomString(12, "0123456789abcdef");
  const tag = randomString(4, TAG_CHARS);
  const token = randomToken();
  await env.DB.batch([
    env.DB.prepare("INSERT INTO players (id, name, tag, token_hash, created) VALUES (?, ?, ?, ?, ?)").bind(
      id, name, tag, await sha256(token), now),
    env.DB.prepare("INSERT INTO signups (ip_hash, ts) VALUES (?, ?)").bind(ipHash, now),
  ]);
  return json({ id, name, tag, token }, 201);
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
  const why = checkRating(old, rating, played, now);
  if (why) return json({ error: why, rating: old ? old.rating : null, played: old ? old.played : 0 }, 409);
  await env.DB
    .prepare(
      "INSERT INTO ratings (player_id, code, rating, played, peak, updated) VALUES (?1, ?2, ?3, ?4, ?3, ?5) " +
        "ON CONFLICT (player_id, code) DO UPDATE SET rating = ?3, played = ?4, peak = MAX(peak, ?3), updated = ?5",
    )
    .bind(me.id, code, rating, played, now)
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
    env.DB.prepare("DELETE FROM players WHERE id = ?").bind(me.id),
  ]);
  return new Response(null, { status: 204, headers: CORS });
}

async function handle(request, env) {
  const url = new URL(request.url);
  const path = url.pathname.replace(/\/+$/, "");
  const method = request.method;
  if (method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });
  if (path === "/players" && method === "POST") return join(request, env);
  if (path === "/players/me" && method === "DELETE") return leave(request, env);
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
