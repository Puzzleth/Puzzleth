// D1 stand-in on node:sqlite, for the tests and the local server (local/serve.js).
import { readFileSync } from "node:fs";
import { DatabaseSync } from "node:sqlite";

/** Just enough of D1's API: prepare().bind().first() / all() / run(), and batch(). */
export class FakeD1 {
  constructor(file = ":memory:") {
    this.db = new DatabaseSync(file);
    this.db.exec(readFileSync(new URL("../schema.sql", import.meta.url), "utf8"));
  }
  prepare(sql) {
    const db = this.db;
    const stmt = {
      args: [],
      bind(...args) { return { ...stmt, args }; },
      first() { return db.prepare(sql).get(...this.args) ?? null; },
      all() { return { results: db.prepare(sql).all(...this.args) }; },
      run() { db.prepare(sql).run(...this.args); return { success: true }; },
    };
    return stmt;
  }
  async batch(stmts) {
    this.db.exec("BEGIN");
    try {
      for (const s of stmts) s.run();
      this.db.exec("COMMIT");
    } catch (e) {
      this.db.exec("ROLLBACK");
      throw e;
    }
  }
}
