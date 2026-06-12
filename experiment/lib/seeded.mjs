// Derived-seed utilities for the experiment. Every random choice in the study derives
// from the master seed M (drawn from /dev/urandom at pre-registration, committed before
// any data existed) through the SAME parity-tested cksum stream the draw uses.
// Honest note (disclosed in the pre-registration): seeded picks are cksum % n, the
// parity path, not the rejection-sampled entropy path; modulo bias over a 2^32 hash is
// < 1.2e-8 for n <= 1000, negligible at this scale.
import { pickIndex } from "../../site/js/entropy.js";

// count distinct indices in [0, poolSize), derived from `${tag}:${i}` streams of M.
export function selectDistinct(tag, masterSeed, poolSize, count) {
  if (count > poolSize) throw new Error("count exceeds pool");
  const chosen = [];
  for (let i = 0; chosen.length < count; i++) {
    const idx = pickIndex(`${tag}:${i}`, masterSeed, poolSize);
    if (!chosen.includes(idx)) chosen.push(idx);
  }
  return chosen;
}

// Fisher-Yates with each swap index drawn from its own derived stream. Pure: returns a copy.
export function seededShuffle(arr, tag, masterSeed) {
  const out = arr.slice();
  for (let i = out.length - 1; i > 0; i--) {
    const j = pickIndex(`${tag}:${i}`, masterSeed, i + 1);
    [out[i], out[j]] = [out[j], out[i]];
  }
  return out;
}
