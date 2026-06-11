// The figures panel: real, measured, regenerable results. Small-n is flagged where it
// applies. Every number here is reproducible from the repo's tests or the recorded
// session in the case study. Kept lowercase by intent.
export const FIGURES = [
  {
    k: "expert selection · blind a/b · single session, small n (illustrative)",
    v: "asked to self-pick an unrelated expert, the model collapsed <b>3 of 3</b> times onto the problem's neighbor professions. five real entropy draws spanned six unrelated crafts the model never reached on its own.",
    cmd: "raw draws + transcript: case study",
  },
  {
    k: "draw uniformity",
    v: "rejection-sampled, <b>exactly uniform</b> over the map. <b>152</b> distinct experts in <b>200</b> entropy draws over <b>378</b> leaves; no expert recurred more than 6 times.",
    cmd: "regenerate: bash tests/run_all.sh",
  },
  {
    k: "reproducibility",
    v: "every seeded draw on this page reproduces in your terminal, byte for byte. ci gates the live deploy on the parity test, so the page can't ship a claim the mechanism fails.",
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
