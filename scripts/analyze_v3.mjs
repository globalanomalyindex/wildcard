// Offline analysis of study 3: the shipped wildcard skill (arm W) against a plain
// brainstorm (arm P), paired by problem, on ten problems neither prior study touched.
// Implements exactly experiment/v3/preregistration.md. Primary endpoint is NOVELTY,
// with a pre-registered +0.30 prediction and a decision rule fixed before collection.
// Pure: analyzeV3(dir) -> results; CLI writes results.json + results.md.
import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import {
  cliffsDelta, bootstrapCI, mulberry32, wilcoxonExact, krippendorffAlphaOrdinal,
} from "../experiment/lib/stats.mjs";
import { cksum } from "../site/js/entropy.js";

const ITEMS = ["genuineness", "usefulness", "novelty", "nonDerailment"];
const PRIMARY = "novelty";
const PREDICTED_GAIN = 0.30; // pre-registered, experiment/v3/preregistration.md
const read = (dir, f) => JSON.parse(readFileSync(join(dir, f), "utf8"));
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;

export function analyzeV3(dir) {
  const selRaw = read(dir, "problems-selected.json");
  const selected = Array.isArray(selRaw) ? selRaw : selRaw.problems;
  const problems = selected.map((p) => p.id);
  const M = read(dir, "config.json").masterSeed;
  const manifest = read(dir, "raw/manifest.json");
  const gradesDoc = read(dir, "grades.json");
  const rowFor = new Map(manifest.map((m) => [m.outId, m]));

  // per output: mean across graders, per item
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
    outRows.push({
      outId, arm: row.arm, problemId: row.problemId, rep: row.rep,
      abstained: row.abstained === true,
      fabFlags: gs.filter((g) => g.fabrication).length,
      nGraders: gs.length,
      ...Object.fromEntries(ITEMS.map((it) => [it, mean(gs.map((g) => g[it]))])),
    });
  }

  // one cell per problem x arm: mean over the three reps. Abstentions are excluded from
  // the quality means (an abstention has no angles to score) and counted separately, so
  // an arm cannot win by abstaining its way out of hard problems.
  const cell = (arm, pid, it) => {
    const rows = outRows.filter((o) => o.arm === arm && o.problemId === pid && !o.abstained);
    return rows.length ? mean(rows.map((r) => r[it])) : null;
  };

  const contrast = (it) => {
    const pairs = problems
      .map((pid) => [cell("W", pid, it), cell("P", pid, it)])
      .filter(([w, p]) => w !== null && p !== null);
    const ws = pairs.map((x) => x[0]), ps = pairs.map((x) => x[1]);
    const diffs = pairs.map(([w, p]) => w - p);
    const rng = mulberry32(cksum("bootstrap:" + M + ":" + it));
    const ci = bootstrapCI(pairs, (s) => mean(s.map((x) => x[0] - x[1])), 10000, rng);
    return {
      item: it, nPairs: pairs.length,
      meanW: mean(ws), meanP: mean(ps), diff: mean(diffs),
      cliffsDelta: cliffsDelta(ws, ps),
      ci95: [ci.lo, ci.hi], p: wilcoxonExact(diffs).p,
    };
  };

  const results = Object.fromEntries(ITEMS.map((it) => [it, contrast(it)]));
  const primary = results[PRIMARY];

  // The decision rule, applied mechanically. It was fixed before any data existed and is
  // not re-read off the result: W wins only on BOTH a >= +0.30 gain and a CI clear of zero.
  const ciExcludesZero = primary.ci95[0] > 0 || primary.ci95[1] < 0;
  const verdict = !ciExcludesZero
    ? "null: no detectable difference on the primary endpoint"
    : primary.diff >= PREDICTED_GAIN
      ? "W wins: prediction met"
      : primary.diff > 0
        ? "W ahead but under the pre-registered +0.30 threshold: prediction NOT met"
        : "W loses: the plain brainstorm scores higher on the primary endpoint";

  const guardRails = {
    fabricationW: outRows.filter((o) => o.arm === "W").reduce((s, o) => s + o.fabFlags, 0),
    fabricationP: outRows.filter((o) => o.arm === "P").reduce((s, o) => s + o.fabFlags, 0),
    abstentionsW: outRows.filter((o) => o.arm === "W" && o.abstained).length,
    abstentionsP: outRows.filter((o) => o.arm === "P" && o.abstained).length,
    nonDerailmentW: results.nonDerailment.meanW,
  };

  // inter-rater agreement, per item, over all graded outputs
  const reliability = {};
  for (const it of ITEMS) {
    const units = [...byOut.values()].map((gs) => gs.map((g) => g[it]));
    reliability[it] = krippendorffAlphaOrdinal(units);
  }

  return {
    masterSeed: M, nOutputs: outRows.length, nProblems: problems.length,
    primaryEndpoint: PRIMARY, predictedGain: PREDICTED_GAIN,
    predictionMet: primary.diff >= PREDICTED_GAIN && ciExcludesZero,
    verdict, results, guardRails, reliability,
    perProblem: problems.map((pid) => ({
      problemId: pid,
      ...Object.fromEntries(ITEMS.flatMap((it) => [
        [it + "W", cell("W", pid, it)], [it + "P", cell("P", pid, it)],
      ])),
    })),
  };
}

function md(r) {
  const f = (n) => (n === null || n === undefined ? "n/a" : n.toFixed(2));
  const line = (c) =>
    `| ${c.item} | ${f(c.meanW)} | ${f(c.meanP)} | ${c.diff >= 0 ? "+" : ""}${f(c.diff)} | ` +
    `${f(c.ci95[0])} to ${f(c.ci95[1])} | ${f(c.cliffsDelta)} | ${c.p.toFixed(4)} |`;
  return `# study 3 results: shipped skill vs plain brainstorm

master seed \`${r.masterSeed}\`, ${r.nProblems} problems, ${r.nOutputs} graded outputs.
primary endpoint: **${r.primaryEndpoint}**, pre-registered prediction **>= +${r.predictedGain.toFixed(2)}**.

## verdict

**${r.verdict}**

prediction met: **${r.predictionMet ? "yes" : "no"}**

## paired contrasts (W = wildcard skill, P = plain brainstorm)

| item | mean W | mean P | diff | 95% CI | cliff's delta | exact wilcoxon p |
|---|---|---|---|---|---|---|
${ITEMS.map((it) => line(r.results[it])).join("\n")}

## guard rails

- fabrication flags: W ${r.guardRails.fabricationW}, P ${r.guardRails.fabricationP}
- abstentions: W ${r.guardRails.abstentionsW}, P ${r.guardRails.abstentionsP}
- non-derailment, W: ${f(r.guardRails.nonDerailmentW)}

## inter-rater agreement (krippendorff's alpha, ordinal)

${ITEMS.map((it) => `- ${it}: ${f(r.reliability[it])}`).join("\n")}

regenerate: \`node scripts/analyze_v3.mjs experiment/v3\`
`;
}

if (process.argv[1] && process.argv[1].endsWith("analyze_v3.mjs")) {
  const dir = process.argv[2] || "experiment/v3";
  const r = analyzeV3(dir);
  writeFileSync(join(dir, "results.json"), JSON.stringify(r, null, 2) + "\n");
  writeFileSync(join(dir, "results.md"), md(r));
  console.log(md(r));
}
