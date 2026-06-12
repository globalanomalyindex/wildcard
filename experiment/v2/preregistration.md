# Pre-registration: wildcard v2 (seeding) vs v1 (mapping-gated), blind head-to-head

Registered before any v2 output is generated or scored.

## Design

10 fresh problems, none reused from the v1 study, spanning code and non-code domains as before. Each problem is run 3 times per arm (v1 skill text vs v2 skill text), with the draw fixed per matched run via `draw.sh --seed` so both arms receive identical wildcards: 30 outputs per arm, 60 total, differing only in the skill text. Outputs are de-identified, order-randomized, and scored by the same blind panel rubric as the v1 study.

## Primary endpoint

Mean judged genuineness (1-7): is each offered idea a genuinely good, novel, useful move in the user's domain, rather than a decorated analogy? Scored per output, averaged per arm. Because v2 deliberately ships fewer strands, the rubric scores an offering on its distinct executable moves, not on volume; this rubric fix is committed before any scoring.

## Directional prediction

v2 mean genuineness exceeds v1 mean genuineness by at least +0.5 points, paired per problem-and-seed, one-sided. Mechanism claimed: the v1 deficit was located at the emit stage (real connections shipped undischarged, in donor vocabulary, terminating in metaphor), and v2 forces the translation step (removability gate, concrete-move third beat, routine per-strand release, saturation in user particulars) without touching the draw. v1's own best outputs (6.25 to 6.50) already behave as v2 prescribes on equally distant draws, so the predicted ceiling is demonstrated, not hoped for.

## Honest bounds

1. We do not predict v2 will exceed the v1 study's near-pick arms (A/C). Some genuine distance costs a gloss clause that judges may still mildly discount; the claim is that v2 closes most of the gap, not all of it.
2. Strand count per output will fall by design (about 3, redundancy collapsed). If the panel rewards bulk despite the rubric fix, the comparison is invalid as registered and is re-run with per-strand scoring.
3. Whole-task abstention may rise in v2, since strands that cannot be cashed out are released rather than force-shipped. Abstentions are excluded from the genuineness mean but counted; an abstention rate above 15% in v2 is reported as a real cost even if genuineness rises.

## Guard rails (secondary endpoints; any break invalidates a win)

- Fabrication count (invented facts, mechanisms, or connections): must stay flat or fall vs v1.
- Draw distance: judged surface-adjacency of donor to problem must not shrink; v2 must win by discharging distance, not by avoiding it. Checked with the v1 adjacency rubric, and the primary comparison is re-checked conditioned on judged distance.
- Removability compliance: fraction of shipped strands whose final move survives deletion of the donor sentence (target near 100% in v2; measured in v1 for contrast).
- Over-correction watch: judges flag strands that read as bare to-dos with no visible cross-domain insight; a collapse in v2's insight-visible rate is reported as a calibration failure of the one-clause gloss.

## Falsification

The hypothesis is falsified if v2 does not beat v1 on mean genuineness by at least +0.5 (one-sided, paired), or if any guard rail breaks: fabrication rises, draw distance shrinks, or the gain disappears once conditioned on distance. A null result with intact guard rails means the emit-stage diagnosis was wrong or insufficient, and seeding-not-forcing does not by itself buy genuineness. That result gets reported as plainly as a positive one.
