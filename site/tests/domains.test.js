import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { DOMAINS, LENSES, PROVENANCE } from "../js/domains.js";

const here = dirname(fileURLToPath(import.meta.url));
const repo = join(here, "..", "..");

test("domains.js count matches the source map exactly", () => {
  const src = readFileSync(join(repo, "plugin/references/domains.txt"), "utf8");
  const lines = src.split("\n").filter((l) => l.trim() && !l.trim().startsWith("#"));
  assert.equal(DOMAINS.length, lines.length);
  assert.equal(DOMAINS.length, PROVENANCE.count);
});

test("domains are tag-stripped and ordered (index parity with draw.sh)", () => {
  assert.equal(DOMAINS[0], "drilling-mud rheology testing with Marsh funnel and rotational viscometer");
  assert.ok(DOMAINS.every((d) => !d.includes("|")));
});

test("lenses parsed from draw.sh (8, includes structure-and-form)", () => {
  assert.equal(LENSES.length, 8);
  assert.equal(LENSES[5], "structure-and-form");
});
