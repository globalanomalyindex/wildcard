import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, CONCEPTS, LENSES } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

function shellDraw(seed) {
  const out = execFileSync("bash", [
    "plugin/scripts/draw.sh", "--seed", seed,
    "--domains-file", "plugin/references/domains.txt",
    "--concepts-file", "plugin/references/concepts.txt",
  ], { cwd: repo, encoding: "utf8" });
  const mode = out.match(/^mode=(.*)$/m)[1];
  const pick = out.match(/^(?:domain|concept)=(.*)$/m)[1];
  const lens = out.match(/^lens=(.*)$/m)[1];
  return { mode, pick, lens };
}

test("browser reproduces shell mode + pick + lens for many seeds", () => {
  for (const seed of ["1", "42", "7", "wildcard", "review-101", "999"]) {
    const s = shellDraw(seed);
    const mode = pickIndex("mode", seed, 2) === 0 ? "specialist" : "concept";
    const pool = mode === "specialist" ? DOMAINS : CONCEPTS;
    const tag = mode === "specialist" ? "domain" : "concept";
    const pick = pool[pickIndex(tag, seed, pool.length)];
    const lens = LENSES[pickIndex("lens", seed, LENSES.length)];
    assert.equal(mode, s.mode, `mode for ${seed}`);
    assert.equal(pick, s.pick, `pick for ${seed}`);
    assert.equal(lens, s.lens, `lens for ${seed}`);
  }
});
