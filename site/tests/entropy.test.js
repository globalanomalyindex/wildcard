import { test } from "node:test";
import assert from "node:assert/strict";
import { cksum, pickIndex } from "../js/entropy.js";

// Anchors measured from the real `cksum` binary on this machine — if these pass, the JS
// implementation is byte-for-byte the POSIX algorithm, independent of any data file.
test("cksum matches POSIX cksum byte-for-byte", () => {
  assert.equal(cksum("abc"), 1219131554);
  assert.equal(cksum(""), 4294967295);
  assert.equal(cksum("domain:1"), 3264583362);
  assert.equal(cksum("lens:1"), 2936984613);
  assert.equal(cksum("domain:42"), 1314043712);
  assert.equal(cksum("layout:review-101"), 3636748815);
});

test("pickIndex mirrors draw.sh modulo (seed 1 lens -> index 5)", () => {
  assert.equal(pickIndex("lens", "1", 8), 5); // structure-and-form
});

test("pickIndex streams are independent (verified against shell for seed 7)", () => {
  assert.equal(pickIndex("domain", "7", 344), 60);
  assert.equal(pickIndex("lens", "7", 344), 275);
});
