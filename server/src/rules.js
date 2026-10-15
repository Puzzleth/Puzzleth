// What the leaderboard accepts. Kept apart from index.js, whose only export must be the Worker.

// these match puzzleth/challenge.py and puzzleth/storage.py
export const CODES = ["BD", "MR", "AR", "VP"];   // the subtests with rated puzzle sets
export const START_RATING = 1000;
export const FLOOR = 100;
export const MAX_RATING = 3000;   // the hardest puzzles are rated about 2150
export const MAX_STEP = 48;       // the most one puzzle can move a rating (K_PROVISIONAL)
export const RANKED_AFTER = 10;   // one rated set
export const NAME = /^[A-Z0-9]{1,8}$/;

export const SECONDS_PER_PUZZLE = 2;   // nobody solves puzzles faster than this, on average
export const SIGNUPS_PER_DAY = 20;     // per address
export const TAG_CHARS = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ";

/** Why a new rating can't be accepted, or null if it can. ``old`` is the stored row, if any. */
export function checkRating(old, rating, played, now) {
  if (typeof rating !== "number" || !Number.isFinite(rating) || rating < FLOOR || rating > MAX_RATING)
    return "rating out of range";
  if (!Number.isInteger(played) || played < 1 || played > 1e6) return "played out of range";
  const from = old ? old.rating : START_RATING;
  const before = old ? old.played : 0;
  if (played < before) return "fewer puzzles than before";
  // each puzzle moves the rating by less than MAX_STEP (0.5 for rounding)
  if (Math.abs(rating - from) > MAX_STEP * (played - before) + 0.5) return "rating moved too far";
  // and puzzles take time (a set's worth of slack for the one being played)
  if (old && played - before > RANKED_AFTER + (now - old.updated) / SECONDS_PER_PUZZLE)
    return "too many puzzles too quickly";
  return null;
}
