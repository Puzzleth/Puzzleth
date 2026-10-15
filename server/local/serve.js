// The leaderboard on your own computer, without Cloudflare, to try the game against:
//   cd server && npm run local              (then, in another terminal)
//   PUZZLETH_SERVER=http://localhost:8787 ./puzzle
// The players and ratings are kept in local/leaderboard.sqlite. Needs Node 22.5 or newer.
import { createServer } from "node:http";

import worker from "../src/index.js";
import { FakeD1 } from "./fake-d1.js";

const port = Number(process.env.PORT || 8787);
const env = { DB: new FakeD1(new URL("./leaderboard.sqlite", import.meta.url).pathname) };

createServer(async (req, res) => {
  const chunks = [];
  for await (const chunk of req) chunks.push(chunk);
  const body = chunks.length ? Buffer.concat(chunks) : undefined;
  const request = new Request(`http://localhost:${port}${req.url}`, {
    method: req.method,
    headers: { ...req.headers, "CF-Connecting-IP": req.socket.remoteAddress },
    body: req.method === "GET" || req.method === "HEAD" ? undefined : body,
  });
  const response = await worker.fetch(request, env);
  res.writeHead(response.status, Object.fromEntries(response.headers));
  res.end(Buffer.from(await response.arrayBuffer()));
}).listen(port, () => console.log(`Puzzleth leaderboard on http://localhost:${port}`));
