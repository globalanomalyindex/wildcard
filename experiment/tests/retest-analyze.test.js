import test from "node:test";
import assert from "node:assert/strict";
import { analyzeRetest } from "../../scripts/analyze_retest.mjs";

test("analyzeRetest produces the pre-registered head-to-head fields from a tiny fixture", () => {
  const r = analyzeRetest(new URL("./fixtures/retest-tiny/", import.meta.url).pathname);
  assert.ok(typeof r.primary.meanDiff === "number");
  assert.ok(r.primary.ci.lo <= r.primary.ci.hi);
  assert.ok(["v2 > v1", "v1 > v2", "no detected difference"].includes(r.primary.band));
  assert.ok(typeof r.primary.metGE05 === "boolean");
  assert.ok(r.guardRails.v1 && r.guardRails.v2);
  assert.ok(typeof r.guardRails.v2.removabilityRate === "number");
  assert.ok(typeof r.reliability.genuineness === "number");
});
