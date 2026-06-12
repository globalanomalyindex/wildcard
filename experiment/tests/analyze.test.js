import test from "node:test";
import assert from "node:assert/strict";
import { analyze } from "../../scripts/analyze_experiment.mjs";

test("analyze produces the pre-registered result fields from a tiny fixture", () => {
  const r = analyze(new URL("./fixtures/tiny/", import.meta.url).pathname);
  assert.ok(r.h1.perProblem.length >= 1);
  assert.ok(typeof r.h1.pooledTopShare === "number");
  assert.ok(typeof r.h2.primary.delta === "number");
  assert.ok(typeof r.h2.primary.p === "number");
  assert.ok(r.h2.primary.ci.lo <= r.h2.primary.ci.hi);
  assert.ok(typeof r.reliability.genuineness === "number");
  assert.ok(typeof r.blinding.accuracy === "number");
  assert.ok(["superiority", "no detected difference", "inferiority"].includes(r.h2.primary.band));
});
