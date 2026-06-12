// Offline analysis of the v1-vs-v2 re-test (head-to-head, identical draws per matched run).
// Pure: analyzeRetest(dir) -> results; CLI writes results.json + results.md.
// Implements exactly experiment/v2/preregistration.md - paired v2 vs v1, primary = genuineness.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import {
  cliffsDelta, bootstrapCI, mulberry32, wilcoxonExact, krippendorffAlphaOrdinal,
} from "../experiment/lib/stats.mjs";
import { cksum } from "../site/js/entropy.js";

const ITEMS = ["genuineness", "usefulness", "novelty", "nonDerailment"];
const read = (dir, f) => JSON.parse(readFileSync(join(dir, f), "utf8"));
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;

export function analyzeRetest(dir) {
  const selected = read(dir, "problems-selected.json");
  const M = selected.masterSeed ?? read(dir, "config.json").masterSeed;
  const problems = selected.problems.map((p) => p.id);
  const manifest = read(dir, "raw/manifest.json");
  const gradesDoc = read(dir, "grades.json");
  const rowFor = new Map(manifest.map((m) => [m.outId, m]));

  // per output: mean across graders per item
  const byOut = new Map();
  for (const g of gradesDoc.graders) {
    if (!g.grades) continue;
    for (const gr of g.grades) {
      if (!byOut.has(gr.id)) byOut.set(gr.id, []);
      byOut.get(gr.id).push(gr);
    }
  }
  const outRows = [];
  for (const [outId, gs] of byOut) {
    const row = rowFor.get(outId);
    if (!row) continue;
    const means = Object.fromEntries(ITEMS.map((it) => [it, mean(gs.map((g) => g[it]))]));
    outRows.push({
      outId, arm: row.arm, problemId: row.problemId, abstained: row.abstained === true,
      fabFlags: gs.filter((g) => g.fabrication).length,
      removFlags: gs.filter((g) => g.removabilityCompliant).length,
      nGraders: gs.length, ...means,
    });
  }

  // per problem x arm cell (mean over runs, abstained excluded from quality means)
  const cell = (arm, pid, it) => {
    const rows = outRows.filter((o) => o.arm === arm && o.problemId === pid && !o.abstained);
    return rows.length ? mean(rows.map((r) => r[it])) : null;
  };
  const contrast = (it) => {
    const pairs = problems
      .map((pid) => [cell("v2", pid, it), cell("v1", pid, it)])
      .filter(([x, y]) => x !== null && y !== null);
    const xs = pairs.map((p) => p[0]), ys = pairs.map((p) => p[1]);
    const diffs = pairs.map(([x, y]) => x - y);
    const delta = cliffsDelta(xs, ys);
    const rng = mulberry32(cksum("bootstrap:" + M));
    const ci = bootstrapCI(pairs, (s) => mean(s.map((p) => p[0] - p[1])), 10000, rng);
    const w = wilcoxonExact(diffs);
    return { item: it, nPairs: pairs.length, meanV2: mean(xs), meanV1: mean(ys),
      meanDiff: mean(diffs), delta, ci, p: w.p };
  };
  const primary = contrast("genuineness");
  // pre-registered band: prediction is v2 - v1 >= +0.5
  primary.metGE05 = primary.meanDiff >= 0.5;
  primary.band = primary.ci.lo > 0 ? "v2 > v1" : primary.ci.hi < 0 ? "v1 > v2" : "no detected difference";
  const secondary = ITEMS.filter((it) => it !== "genuineness").map(contrast);

  // guard rails
  const armAgg = (arm) => {
    const rows = outRows.filter((o) => o.arm === arm);
    return {
      n: rows.length,
      fabricationOutputs: rows.filter((r) => r.fabFlags >= 1).length,
      abstentions: rows.filter((r) => r.abstained).length,
      removabilityRate: mean(rows.map((r) => r.removFlags / Math.max(1, r.nGraders))),
    };
  };
  const guardRails = { v1: armAgg("v1"), v2: armAgg("v2") };

  const reliability = Object.fromEntries(ITEMS.map((it) => [it,
    krippendorffAlphaOrdinal([...byOut.values()].filter((gs) => gs.length >= 2).map((gs) => gs.map((g) => g[it])))]));

  const missing = manifest.filter((m) => m.ok === false).map((m) => m.outId ?? m.id);
  return { primary, secondary, guardRails, reliability, missing, counts: { outputs: outRows.length } };
}

if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const dir = process.argv[2] ?? "experiment/v2";
  const r = analyzeRetest(dir);
  writeFileSync(join(dir, "results.json"), JSON.stringify(r, null, 2) + "\n");
  const f = (x, d = 2) => (typeof x === "number" ? x.toFixed(d) : String(x));
  const md = [];
  md.push("# re-test results: v1 (mapping-gated) vs v2 (seeding) - generated, do not edit\n");
  md.push("identical draws per matched run, so distance is controlled by design; the only variable is skill text.\n");
  const p = r.primary;
  md.push("## primary: structural genuineness, v2 vs v1 (paired by problem)\n");
  md.push(`mean v2 ${f(p.meanV2)} vs v1 ${f(p.meanV1)}; paired mean diff **${f(p.meanDiff)}** (95% ci ${f(p.ci.lo)} to ${f(p.ci.hi)}); exact wilcoxon p = ${f(p.p, 4)}; band: **${p.band}**; pre-registered prediction (diff >= +0.5): **${p.metGE05 ? "met" : "not met"}** (n pairs = ${p.nPairs}).\n`);
  md.push("## secondary (paired v2 vs v1)\n");
  md.push("| item | mean v2 | mean v1 | diff | 95% ci | p |");
  md.push("|---|---|---|---|---|---|");
  for (const s of r.secondary) md.push(`| ${s.item} | ${f(s.meanV2)} | ${f(s.meanV1)} | ${f(s.meanDiff)} | ${f(s.ci.lo)} to ${f(s.ci.hi)} | ${f(s.p, 4)} |`);
  md.push("");
  md.push("## guard rails\n");
  md.push(`fabrication (outputs with >=1 flag): v1 ${r.guardRails.v1.fabricationOutputs}/${r.guardRails.v1.n}, v2 ${r.guardRails.v2.fabricationOutputs}/${r.guardRails.v2.n} (must stay flat or fall).`);
  md.push(`removability compliance rate: v1 ${f(r.guardRails.v1.removabilityRate)}, v2 ${f(r.guardRails.v2.removabilityRate)} (v2 expected higher).`);
  md.push(`abstentions: v1 ${r.guardRails.v1.abstentions}, v2 ${r.guardRails.v2.abstentions}.`);
  md.push(`draw distance: controlled by design (v1 and v2 received identical wildcards per matched run).\n`);
  md.push("## reliability\n");
  md.push(`krippendorff alpha (ordinal): ${ITEMS.map((it) => `${it} ${f(r.reliability[it])}`).join(", ")}.`);
  md.push(`missing cells: ${r.missing.length ? r.missing.join(", ") : "none"}.`);
  writeFileSync(join(dir, "results.md"), md.join("\n") + "\n");
  console.log("wrote re-test results.json + results.md");
}
