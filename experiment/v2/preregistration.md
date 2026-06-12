# Re-test pre-registration freeze: wildcard v2 (seeding) vs v1 (mapping-gated)

Committed before any v2 output or re-run v1 output exists. Master seed
M2 = `b6443153e1e18f11`, drawn from /dev/urandom at freeze time.

## skill versions under test (identical draw.sh, identical draws)

- **v1** = the mapping-gated skill as merged to main (commit `76f3252`): plugin/SKILL.md + references.
- **v2** = the seeding-not-forcing revision on branch skill-v2-seeding (commit `30fe03b`): the
  removability-gated skill. The only thing that differs between arms is the skill text the subject reads.

## design

10 fresh problems (experiment/v2/problems-selected.json), drawn from the committed 50-problem pool with
M2, excluding the 10 v1-study problems (zero overlap, verified). Each problem is run 3 times per arm;
arm = {v1 skill, v2 skill}. The draw for a matched run is fixed via
`draw.sh --seed "b6443153e1e18f11:draw:<pid>:r<run>"`, identical for v1 and v2, so the two arms receive the SAME
wildcards and differ only in skill text. 60 protocol passes (10 x 3 x 2). Subjects pinned
claude-sonnet-4-6 (as in the v1 study). Normalizers claude-haiku; 4 blind graders claude-opus-4-8.
Raw outputs quarantined outside the repo until grading completes.

## derivations from M2 (via the parity-tested cksum stream)

- arm draw seeds: `M2:draw:<pid>:r<run>` (shared by v1 and v2 for the same pid + run).
- opaque output ids: seededShuffle of the 60 manifest rows, tag "ids", seed M2.
- grader presentation order: seededShuffle(out-ids, "order:<grader-id>", M2).

## rubric

Same four 1-7 scales as the v1 study (structural genuineness [primary], usefulness, novelty,
non-derailment) plus the fabrication flag, with one addition committed here before any scoring: graders
score an offering on the quality of its **distinct executable moves**, not on the number of strands (v2
ships fewer by design). Plus, per the guard rails: a removability-compliance judgment (does each
shipped strand's final move survive deleting the donor sentence?) and the v1 adjacency judgment (is the
donor surface-adjacent to the problem?), so a v2 win can be re-checked conditioned on distance.

---

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
