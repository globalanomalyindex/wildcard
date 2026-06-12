// The figures panel: real, measured, regenerable results. Small-n is flagged where it
// applies. Every number here is reproducible from the repo's tests or the recorded
// session in the case study. Kept lowercase by intent.
export const FIGURES = [
  {
    k: "self-pick vs external draw · pre-registered blind study",
    v: "across <b>10</b> problems x <b>20</b> self-picks each, the model's own \"random unrelated expert\" averaged <b>1.48</b> bits of entropy vs the draw's <b>4.30</b>, and <b>47%</b> of self-picks were surface-adjacent to the problem vs <b>9%</b> for the draw. blind-graded by 4 graders + a human anchor: <b>0</b> fabrications. honestly, the distant connections scored <i>lower</i> on judged genuineness (delta -0.50, p=0.008), not higher: distance costs clean mapping. full writeup in the case study.",
    cmd: "regenerate: node scripts/analyze_experiment.mjs experiment",
  },
  {
    k: "draw uniformity",
    v: "rejection-sampled, <b>exactly uniform</b> over the map. <b>152</b> distinct experts in <b>200</b> entropy draws over <b>378</b> leaves; no expert recurred more than 6 times.",
    cmd: "regenerate: bash tests/run_all.sh",
  },
  {
    k: "two modes · one seeded coin-flip",
    v: "each draw first rolls a mode: a hyper-specific <b>specialist</b> (378 disciplines) or a general <b>concept</b> (461 concepts). the roll is <code>cksum(\"mode:\"+seed)%2</code>, so it is ~50/50 and reproducible. measured <b>296</b> specialist over <b>600</b> seeds (<b>49.3%</b>).",
    cmd: "regenerate: bash tests/test_mode_balance.sh",
  },
  {
    k: "concept pool · safety pipeline",
    v: "open scope without a live network call. <b>7291</b> concept-bearing candidates from wikipedia vital articles (people and history excluded at source) -> <b>7115</b> passed a mechanical, logged safety screen -> <b>176</b> rejected by rule (142 names, 15 person, 9 toolong, 6 ip, 4 meta) -> curated and adversarially reviewed to <b>461</b>. concept draws: <b>160</b> distinct in <b>200</b> seeds, max recurrence 3.",
    cmd: "screen: bash plugin/scripts/screen_concepts.sh",
  },
  {
    k: "reproducibility",
    v: "every seeded draw on this page reproduces in your terminal, byte for byte, now including the mode pick. ci gates the live deploy on the parity test, so the page can't ship a claim the mechanism fails.",
    cmd: "verify: draw.sh --seed <seed>",
  },
  {
    k: "honesty bar · adversarial review",
    v: "one cold review <b>failed</b> the no-derailment check on a run. it was fixed (an additive-not-prescriptive rule), re-tested, and passed clean. reported here rather than hidden.",
    cmd: "",
  },
  {
    k: "the map",
    v: "<b>378</b> niche disciplines, breadth-audited: all 22 axis buckets spanned, zero duplicates. selection is uniform over this curated span, not a claim to hold every field.",
    cmd: "audit: bash audit_domains.sh",
  },
];

export function renderFigures(el) {
  el.innerHTML = FIGURES.map((f) =>
    `<div class="fig"><span class="fig-k">${f.k}</span><span class="fig-v">${f.v}</span>` +
    (f.cmd ? `<span class="fig-cmd">${f.cmd}</span>` : "") + `</div>`
  ).join("");
}
