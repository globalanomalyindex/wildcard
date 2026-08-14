// Fixture test for the study-3 analyzer. The fixture is hand-built so every number is
// checkable by eye: W scores exactly 1.00 above P on all three quality scales, the two
// graders agree perfectly (alpha 1), and one P run is an abstention that must NOT drag
// P's quality mean down. Written before the real grades existed, and it caught a real
// bug: bootstrapCI returns {lo,hi}, not a tuple, so reading ci95[0] gave undefined and
// the decision rule silently fell through to "null" for every possible result.
import { test } from "node:test";
import assert from "node:assert/strict";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";
import { analyzeV3 } from "../../scripts/analyze_v3.mjs";

const FIX = join(dirname(fileURLToPath(import.meta.url)), "fixtures/v3-tiny");
const r = analyzeV3(FIX);

test("paired means and difference are exact", () => {
  assert.equal(r.results.novelty.meanW, 5);
  assert.equal(r.results.novelty.meanP, 4);
  assert.equal(r.results.novelty.diff, 1);
  assert.equal(r.results.novelty.nPairs, 3);
});

test("an abstention is excluded from the quality mean, not scored as a zero", () => {
  // P-q3b abstained with a 1 on every scale. If it were counted, P's mean would be 3.25.
  assert.equal(r.results.novelty.meanP, 4);
  assert.equal(r.guardRails.abstentionsP, 1);
  assert.equal(r.guardRails.abstentionsW, 0);
});

test("the confidence interval is a real numeric pair, not undefined", () => {
  const [lo, hi] = r.results.novelty.ci95;
  assert.equal(typeof lo, "number");
  assert.equal(typeof hi, "number");
  assert.ok(Number.isFinite(lo) && Number.isFinite(hi));
  assert.ok(lo <= r.results.novelty.diff && r.results.novelty.diff <= hi);
});

test("the decision rule fires on the primary endpoint only", () => {
  assert.equal(r.primaryEndpoint, "novelty");
  assert.equal(r.predictedGain, 0.3);
  // +1.00 with a CI clear of zero clears the +0.30 bar
  assert.equal(r.predictionMet, true);
  assert.match(r.verdict, /W wins/);
});

test("perfect grader agreement gives alpha 1", () => {
  assert.equal(r.reliability.novelty, 1);
});

test("guard rails are counted per arm", () => {
  assert.equal(r.guardRails.fabricationW, 0);
  assert.equal(r.guardRails.fabricationP, 0);
  assert.equal(r.guardRails.nonDerailmentW, 6);
});
