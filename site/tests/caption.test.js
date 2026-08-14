// The live draw's caption used to interpolate the drawn string straight after an article:
// "a <domain> specialist" and "a professor of <concept>". Both inherit the pool's grammar.
// The first printed "a acid mine drainage..." on the 46 domains that begin with a vowel; the
// second invented experts who do not exist ("a professor of abrasive", "a professor of amber").
// The fix puts the drawn string after a colon, where no determiner agreement is possible.
// These tests hold that property against every one of the 378 domains and 461 concepts.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "../..");
const src = readFileSync(join(ROOT, "site/js/draw-demo.js"), "utf8");
const { DOMAINS, CONCEPTS } = await import(join(ROOT, "site/js/domains.js"));

// The two caption templates, lifted from the source so the test tracks the real strings.
const leads = [...src.matchAll(/`(now imagine[^`]*)`/g)].map((m) => m[1]);

test("both caption templates were found in draw-demo.js", () => {
  assert.equal(leads.length, 2, `expected 2 caption leads, got ${leads.length}`);
});

test("no drawn string is ever preceded by an article or preposition", () => {
  // Whatever sits immediately before the ${pick} slot must not require agreement with,
  // or impose a part of speech on, an arbitrary pool entry.
  const BAD_LEAD_IN = /\b(a|an|the|of|for|in|on|with|by|from)\s*(<b>)?\s*$/i;
  for (const lead of leads) {
    const before = lead.slice(0, lead.indexOf("${pick}"));
    assert.ok(
      !BAD_LEAD_IN.test(before.replace(/<b>\s*$/, "")),
      `caption puts a determiner or preposition before the drawn string: ...${before.slice(-40)}`
    );
  }
});

test("every domain and concept renders without an a/an agreement error", () => {
  const render = (lead, pick) => lead.replaceAll("${pick}", pick).replace(/<\/?b>/g, "");
  // Find any "a X" / "an X" in the rendered sentence and check the article against X.
  const vowelish = (w) => /^[aeiou]/i.test(w);
  const offenders = [];
  for (const lead of leads) {
    for (const pick of [...DOMAINS, ...CONCEPTS]) {
      const text = render(lead, pick);
      for (const m of text.matchAll(/\b(an?)\s+(\S+)/gi)) {
        const [, art, word] = m;
        const bare = word.replace(/[^a-z]/gi, "");
        if (!bare) continue;
        const wrong = art.toLowerCase() === "a" ? vowelish(bare) : !vowelish(bare);
        // "a university", "an hour" style exceptions are not in these pools; flag anything.
        if (wrong) offenders.push(`"${art} ${bare}" in: ${text.slice(0, 90)}`);
      }
    }
  }
  assert.deepEqual(offenders.slice(0, 5), [], `${offenders.length} article disagreements`);
});

test("no caption claims a title that only some concepts could have", () => {
  // "a professor of X" was the specific regression: it asserts a field exists for the draw.
  for (const lead of leads) {
    assert.ok(
      !/professor of\s*(<b>)?\s*\$\{pick\}/.test(lead),
      "caption names a professor of the drawn concept itself; most concepts have no such field"
    );
  }
});
