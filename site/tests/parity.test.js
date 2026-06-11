import { test } from "node:test";
import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, LENSES } from "../js/domains.js";
import { pickIndex } from "../js/entropy.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

function shellDraw(seed) {
  const out = execFileSync(
    "bash",
    ["plugin/scripts/draw.sh", "--seed", seed, "--file", "plugin/references/domains.txt"],
    { cwd: repo, encoding: "utf8" }
  );
  const domain = out.match(/^domain=(.*)$/m)[1];
  const lens = out.match(/^lens=(.*)$/m)[1];
  return { domain, lens };
}

test("browser pick equals draw.sh pick for many seeds", () => {
  for (const seed of ["1", "42", "7", "review-101", "wildcard", "999"]) {
    const shell = shellDraw(seed);
    const jsDomain = DOMAINS[pickIndex("domain", seed, DOMAINS.length)];
    const jsLens = LENSES[pickIndex("lens", seed, LENSES.length)];
    assert.equal(jsDomain, shell.domain, `domain parity for seed ${seed}`);
    assert.equal(jsLens, shell.lens, `lens parity for seed ${seed}`);
  }
});
