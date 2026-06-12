// Offline analysis over the frozen experiment artifacts. Pure: analyze(dir) -> results
// object; the CLI entry writes results.json and results.md. Implements exactly the
// pre-registered plan in experiment/preregistration.md - nothing more is confirmatory.
import { readFileSync, writeFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import {
  shannonEntropy, cliffsDelta, bootstrapCI, mulberry32, wilcoxonExact,
  krippendorffAlphaOrdinal, spearman,
} from "../experiment/lib/stats.mjs";
import { cksum } from "../site/js/entropy.js";

const ITEMS = ["genuineness", "usefulness", "novelty", "nonDerailment"];
const read = (dir, f) => JSON.parse(readFileSync(join(dir, f), "utf8"));
const mean = (a) => a.reduce((s, v) => s + v, 0) / a.length;

function histogram(labels) {
  const m = new Map();
  for (const l of labels) m.set(l, (m.get(l) || 0) + 1);
  return [...m.values()].sort((a, b) => b - a);
}

export function analyze(dir) {
  const selected = read(dir, "problems-selected.json");
  const M = selected.masterSeed ?? read(dir, "config.json").masterSeed;
  const problems = selected.problems.map((p) => p.id);
  const manifest = read(dir, "raw/manifest.json");
  const gradesDoc = read(dir, "grades.json");
  const selfpicks = read(dir, "h1/selfpicks.json");
  const externals = read(dir, "h1/externals.json");
  const anchor = existsSync(join(dir, "human-anchor.json")) ? read(dir, "human-anchor.json") : [];

  // ---- H1: divergence ----
  const perProblem = problems.map((pid) => {
    const self = selfpicks.filter((s) => s.problemId === pid && s.canonical);
    const ext = externals.filter((e) => e.problemId === pid);
    const sh = histogram(self.map((s) => s.canonical));
    const eh = histogram(ext.map((e) => e.pick));
    return {
      problemId: pid,
      self: { k: self.length, distinct: sh.length, entropy: shannonEntropy(sh),
        top1Share: sh.length ? sh[0] / self.length : 0 },
      external: { k: ext.length, distinct: eh.length, entropy: shannonEntropy(eh),
        top1Share: eh.length ? eh[0] / ext.length : 0 },
    };
  });
  const pooled = histogram(selfpicks.filter((s) => s.canonical).map((s) => s.canonical));
  const pooledTopShare = pooled.slice(0, 10).reduce((a, b) => a + b, 0) /
    Math.max(1, pooled.reduce((a, b) => a + b, 0));
  const adjRate = (rows) => rows.length
    ? rows.filter((r) => r.adjacent === true).length / rows.length : 0;
  const h1 = {
    perProblem, pooledDistinct: pooled.length, pooledTopShare,
    selfAdjacency: adjRate(selfpicks), externalAdjacency: adjRate(externals),
    meanSelfEntropy: perProblem.reduce((s, p) => s + p.self.entropy, 0) / perProblem.length,
    meanExternalEntropy: perProblem.reduce((s, p) => s + p.external.entropy, 0) / perProblem.length,
  };

  // ---- H2: quality ----
  // per output: mean across graders per item; abstained excluded from quality means.
  const byOut = new Map();
  for (const g of gradesDoc.graders) {
    if (!g.grades) continue;
    for (const gr of g.grades) {
      if (!byOut.has(gr.id)) byOut.set(gr.id, []);
      byOut.get(gr.id).push(gr);
    }
  }
  const rowFor = new Map(manifest.map((m) => [m.outId, m]));
  const outMeans = [];
  for (const [outId, gs] of byOut) {
    const row = rowFor.get(outId);
    if (!row) continue;
    const abstained = row.abstained === true;
    const fabFlags = gs.filter((g) => g.fabrication).length;
    const means = Object.fromEntries(ITEMS.map((it) =>
      [it, gs.reduce((s, g) => s + g[it], 0) / gs.length]));
    outMeans.push({ outId, arm: row.arm, problemId: row.problemId, abstained, fabFlags,
      nGraders: gs.length, ...means });
  }
  const cell = (arm, pid, it) => {
    const rows = outMeans.filter((o) => o.arm === arm && o.problemId === pid && !o.abstained);
    return rows.length ? rows.reduce((s, r) => s + r[it], 0) / rows.length : null;
  };
  const contrast = (armX, armY, it) => {
    const pairs = problems
      .map((pid) => [cell(armX, pid, it), cell(armY, pid, it)])
      .filter(([x, y]) => x !== null && y !== null);
    const xs = pairs.map((p) => p[0]), ys = pairs.map((p) => p[1]);
    const delta = cliffsDelta(xs, ys);
    const rng = mulberry32(cksum("bootstrap:" + M));
    const ci = bootstrapCI(pairs, (sample) =>
      cliffsDelta(sample.map((p) => p[0]), sample.map((p) => p[1])), 10000, rng);
    const w = wilcoxonExact(pairs.map(([x, y]) => x - y));
    const band = ci.lo > 0 ? "superiority" : ci.hi < 0 ? "inferiority" : "no detected difference";
    return { item: it, nPairs: pairs.length, meanX: mean(xs), meanY: mean(ys),
      delta, ci, p: w.p, band };
  };
  const primary = contrast("B", "A", "genuineness");
  const secondary = [];
  for (const it of ITEMS) for (const [x, y] of [["B", "A"], ["B", "C"], ["A", "C"]]) {
    if (it === "genuineness" && x === "B" && y === "A") continue;
    secondary.push({ contrast: `${x} vs ${y}`, ...contrast(x, y, it) });
  }
  const fabrication = {}; const abstention = {};
  for (const arm of ["A", "B", "C"]) {
    const rows = outMeans.filter((o) => o.arm === arm);
    fabrication[arm] = Object.fromEntries([1, 2, 3, 4].map((t) =>
      [`>=${t}`, rows.filter((r) => r.fabFlags >= t).length]));
    abstention[arm] = rows.filter((r) => r.abstained).length;
  }

  // ---- reliability, anchor, blinding ----
  const reliability = Object.fromEntries(ITEMS.map((it) => [it,
    krippendorffAlphaOrdinal([...byOut.values()]
      .filter((gs) => gs.length >= 2).map((gs) => gs.map((g) => g[it])))]));
  let anchorStats = null;
  if (anchor.length >= 3) {
    const perItem = Object.fromEntries(ITEMS.map((it) => {
      const pairs = anchor
        .map((h) => [h[it], outMeans.find((o) => o.outId === h.outId)?.[it]])
        .filter(([, p]) => p !== undefined);
      return [it, spearman(pairs.map((p) => p[0]), pairs.map((p) => p[1]))];
    }));
    const all = anchor.flatMap((h) => ITEMS
      .map((it) => [h[it], outMeans.find((o) => o.outId === h.outId)?.[it]])
      .filter(([, p]) => p !== undefined));
    anchorStats = { perItem, pooled: spearman(all.map((p) => p[0]), all.map((p) => p[1])),
      n: anchor.length };
  }
  const guesses = gradesDoc.blinding?.guesses ?? gradesDoc.blinding ?? [];
  const correct = guesses.filter((g) => rowFor.get(g.id)?.arm === g.arm).length;
  const blinding = { n: guesses.length, correct,
    accuracy: guesses.length ? correct / guesses.length : 0, chance: 1 / 3 };

  const missing = manifest.filter((m) => m.ok === false).map((m) => m.outId ?? m.id);
  return { h1, h2: { primary, secondary, fabrication, abstention }, reliability,
    anchor: anchorStats, blinding, missing, counts: { outputs: outMeans.length } };
}

// ---- CLI: node scripts/analyze_experiment.mjs [dir] ----
if (process.argv[1] && import.meta.url.endsWith(process.argv[1].split("/").pop())) {
  const dir = process.argv[2] ?? "experiment";
  const r = analyze(dir);
  writeFileSync(join(dir, "results.json"), JSON.stringify(r, null, 2) + "\n");
  const f = (x, d = 2) => (typeof x === "number" ? x.toFixed(d) : String(x));
  const md = [];
  md.push("# results (generated by scripts/analyze_experiment.mjs - do not edit)\n");
  md.push("## h1: divergence\n");
  md.push("| problem | self distinct/20 | self entropy | self top1 | ext distinct/20 | ext entropy |");
  md.push("|---|---|---|---|---|---|");
  for (const p of r.h1.perProblem)
    md.push(`| ${p.problemId} | ${p.self.distinct} | ${f(p.self.entropy)} | ${f(p.self.top1Share)} | ${p.external.distinct} | ${f(p.external.entropy)} |`);
  md.push("");
  md.push(`mean entropy: self ${f(r.h1.meanSelfEntropy)} bits vs external ${f(r.h1.meanExternalEntropy)} bits.`);
  md.push(`pooled self-picks: ${r.h1.pooledDistinct} distinct labels over all problems; top-10 labels cover ${f(r.h1.pooledTopShare * 100, 1)}%.`);
  md.push(`adjacency to the problem: self ${f(r.h1.selfAdjacency * 100, 1)}% vs external ${f(r.h1.externalAdjacency * 100, 1)}%.\n`);
  md.push("## h2: quality (primary: structural genuineness, B vs A)\n");
  const pr = r.h2.primary;
  md.push(`mean B ${f(pr.meanX)} vs mean A ${f(pr.meanY)}; cliff's delta ${f(pr.delta)} (95% ci ${f(pr.ci.lo)} to ${f(pr.ci.hi)}); exact wilcoxon p = ${f(pr.p, 4)}; pre-registered band: **${pr.band}** (n pairs = ${pr.nPairs}).\n`);
  md.push("### secondary (exploratory)\n");
  md.push("| contrast | item | mean X | mean Y | delta | 95% ci | p |");
  md.push("|---|---|---|---|---|---|---|");
  for (const s of r.h2.secondary)
    md.push(`| ${s.contrast} | ${s.item} | ${f(s.meanX)} | ${f(s.meanY)} | ${f(s.delta)} | ${f(s.ci.lo)} to ${f(s.ci.hi)} | ${f(s.p, 4)} |`);
  md.push("");
  md.push(`fabrication flags per arm (output counts at grader-flag thresholds): ${JSON.stringify(r.h2.fabrication)}`);
  md.push(`abstentions per arm: ${JSON.stringify(r.h2.abstention)}\n`);
  md.push("## reliability and checks\n");
  md.push(`krippendorff alpha (ordinal): ${ITEMS.map((it) => `${it} ${f(r.reliability[it])}`).join(", ")}.`);
  if (r.anchor) md.push(`human anchor (n=${r.anchor.n}): pooled spearman ${f(r.anchor.pooled)}; per item ${ITEMS.map((it) => `${it} ${f(r.anchor.perItem[it])}`).join(", ")}.`);
  md.push(`blinding check: ${r.blinding.correct}/${r.blinding.n} (${f(r.blinding.accuracy * 100, 1)}%) vs chance 33.3%.`);
  md.push(`missing cells: ${r.missing.length ? r.missing.join(", ") : "none"}.`);
  writeFileSync(join(dir, "results.md"), md.join("\n") + "\n");
  console.log("wrote results.json + results.md");
}
