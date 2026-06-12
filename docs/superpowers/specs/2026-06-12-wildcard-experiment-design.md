# wildcard experiment: a pre-registered, blind, three-arm study - design

date: 2026-06-12
status: approved-pending-user-review
branch: experiment (new, off main)

## purpose

Replace the case study's honest-but-n=1 demonstration with a structured experiment that an
expert reviewer would accept as methodologically sound. Two claims, tested separately because
they demand different instruments:

- **H1 (divergence, objective):** when the model self-selects "a random unrelated field," its
  picks collapse onto a few attractors near the problem; the external draw does not. Measured
  with hard, embedding-free statistics. Expected: strong, clean effect.
- **H2 (quality, subjective):** connections produced under the external draw are at least as
  structurally genuine and useful as those produced under self-selection. Measured by a blind,
  multi-grader panel with a human anchor. Outcome genuinely uncertain; we pre-commit to
  publishing whatever lands, including a null.

The experiment's own honesty mechanics mirror the skill's: freeze before you draw
(pre-registration), dice outside the model (entropy with committed master seeds), and an
accept-test the searcher does not control (blind panel + pre-specified analysis).

## design summary

| | |
|---|---|
| arms | A self-pick control · B wildcard treatment · C plain baseline |
| problems | 10, entropy-drawn from a ~50-problem pool authored blind to the hypothesis |
| runs | 3 per problem per arm = 90 protocol passes |
| self-pick samples (H1) | K=20 per problem = 200 |
| graders | 4 independent blind LLM instances, every output graded by all 4 = 360 gradings |
| human anchor | user blind-grades a random ~15-output subset; report correlation with panel |
| subject model | claude-fable-5 (pinned, identical across all arms) |
| grader model | claude-opus-4-8 (pinned; cross-model judge separation from subjects) |
| primary endpoint | structural-genuineness, arm B vs arm A (paired by problem) |

## the arms (only the draw source varies between A and B)

- **arm A (self-pick control):** the full wildcard protocol - freeze the sketch, inhabit,
  structure-map, present seeds - except step 2: instead of running draw.sh, the model is asked
  to name its own "random expert from a completely unrelated field, or a random unrelated
  concept" and proceed with it. Same instructions otherwise, token for token.
- **arm B (wildcard treatment):** the shipped skill verbatim, draw from draw.sh with a
  pre-registered derived seed (see randomization).
- **arm C (plain baseline):** no scaffolding. "Here is a problem; brainstorm 2-4 creative
  angles or connections that could help." Anchors what no intervention looks like.

A vs B isolates the draw source. C vs both anchors the scaffolding's overall contribution.
Each pass runs in a fresh, isolated agent context: no run can see any other run, arm, or the
hypothesis.

## problem sourcing (anti-cherry-picking)

1. A fable-5 agent that is told nothing about wildcard, the hypothesis, or the arms generates
   ~50 realistic working problems: half code/engineering, half non-code (writing, planning,
   design, operations, personal projects), each 60-120 words with enough texture to support a
   structural sketch. Generator prompt is committed verbatim.
2. The pool is committed (experiment/problems-pool.json).
3. 10 problems are selected by the project's own rejection-sampled entropy mechanism using the
   committed master seed (below). Selection is therefore auditable and re-derivable by anyone.

## randomization (true entropy, fully auditable)

One **master seed M** is drawn from /dev/urandom at pre-registration time and committed
*before any problem pool, output, or grade exists*. Everything derives from it:

- problem selection: seed "M:problems"
- arm B draws: seed "M:draw:<problem-id>:r<run>"
- grader item order: seed "M:order:<grader-id>"
- human-anchor subset: seed "M:anchor"

Because M is committed before any data exists, it cannot have been chosen to steer results;
because everything is derived, the entire randomization replays byte-for-byte from the repo.
This reconciles "true randomization" with the project's reproducibility guarantee.

## grading protocol

**normalization.** Each protocol pass's final output is reformatted by a normalizer agent into
a fixed template (a list of seeds/angles: noticing, mapping, provocation - or plain ideas for
arm C), stripping persona introductions, mode markers, and any arm-identifying preamble. Each
normalized output gets an opaque id.

**blinding check (manipulation check).** One additional agent, shown only normalized outputs,
guesses which arm each came from. We report guess accuracy vs chance. If blinding leaks badly,
we say so and interpret accordingly - measured, not assumed.

**panel.** 4 independent grader instances (opus-4-8), each grading all 90 normalized outputs in
its own randomized order, no arm labels, no access to other graders. Rubric per output, each
item 1-7 with written anchors (committed verbatim in the pre-registration):

- **structural genuineness** (primary): do the connections map systems of relations, or share
  surface vocabulary/nouns?
- **usefulness:** would a practitioner plausibly act on at least one of these?
- **novelty:** does any angle depart from the problem's obvious neighborhood?
- **non-derailment:** does it respect the user's framing rather than substituting its own?
- **fabrication flag** (binary): does any connection assert a false mechanism or invented fact?

**human anchor.** ~15 outputs drawn by seed "M:anchor" are blind-graded by the user with the
same rubric. Report Spearman correlation between human scores and panel means. This bounds the
"LLM graders may not track human judgment" objection with data instead of hand-waving.

**reliability.** Krippendorff's alpha (ordinal) across the 4 graders, reported per rubric item.

## H1 instrumentation (objective, embedding-free)

For each problem, K=20 independent fresh-context self-picks ("name a random expert from a
completely unrelated field..."), one pick per call. Metrics:

- distinct-count and top-1 share per problem
- Shannon entropy (bits) per problem vs the external draw's same-K expectation (uniform over
  378+461; at K=20, expected near-perfect distinctness, entropy near log2(20))
- cross-problem attractor analysis: pooled top-10 share across all 200 self-picks (does the
  model return to the same favorite fields across different problems?)
- problem-adjacency: a blind classifier agent judges, for each pick (and for matched external
  draws), "does this field share surface vocabulary with the problem's domain?" - reported as
  adjacency rate per arm. Embedding-free by design: no new dependency, no embedding-model
  freshness questions.

## analysis plan (pre-specified)

- aggregation: per problem x arm, mean across runs and graders -> 10 paired values per contrast.
- primary contrast: structural genuineness, B vs A. Wilcoxon signed-rank (paired by problem),
  Cliff's delta with bootstrap 95% CI (10k resamples, seeded).
- secondary contrasts (labelled exploratory): all other rubric items B vs A; B vs C; A vs C;
  fabrication rates per arm; abstention rates per arm (count of honest abstentions, reported
  descriptively - abstaining is the skill working, so it is not scored as failure).
- H1: descriptive statistics + the entropy gap; no significance theater on a near-certain
  effect - the numbers speak.
- interpretation bands, pre-committed: CI excluding 0 in B's favor = superiority; CI spanning 0
  = no detected difference (reported as exactly that); CI excluding 0 against B = inferiority,
  reported plainly. No post-hoc re-slicing to rescue a result; anything not in this plan is
  labelled exploratory.
- all analysis in pure, tested scripts (node, zero-dependency like the rest of the repo),
  running offline from frozen artifacts, gated in CI.

## artifacts (all committed)

```
experiment/preregistration.md      hypotheses, rubric verbatim, prompts verbatim, master seed,
                                   analysis plan - committed before any data
experiment/problems-pool.json      the blind-authored pool
experiment/problems-selected.json  the 10 drawn problems + derivation
experiment/raw/                    every protocol-pass transcript (90) + self-picks (200)
experiment/normalized/             anonymized outputs + id map (map committed after grading)
experiment/grades.json             all 360 panel gradings + blinding-check guesses
experiment/human-anchor.json       the user's blind gradings
experiment/results.md              generated by the analysis scripts
scripts/analyze_experiment.mjs     tested, CI-gated analysis
docs/methods-colophon.md           the autonomous-process record (below)
```

## the methods colophon (the trust document)

A standalone document recording, with the real run details, why this pipeline earns trust -
argued from architecture, not assertion. Core argument: **blinding and isolation are enforced
by construction, not by promise.** A human-run study asks readers to trust that graders were
blind, raters did not confer, and problems were not steered. Here: the problem author is a
process that never saw the hypothesis; each grader is a fresh context with no channel to learn
an output's arm and no ability to confer; randomization came from OS entropy with the master
seed committed before any data existed (even the experimenters could not steer it); every
transcript is committed, so the chain of custody is a git history; and the scale (90 passes,
360 independent gradings) exceeds what a solo human evaluation can deliver, while the human
anchor keeps the panel honest. Names the real stack truthfully: design and orchestration by
claude (opus 4.8 with 1M context, and fable 5), subjects pinned to fable 5, graders pinned to
opus 4.8, fan-out via the workflow orchestrator. Honest about residual limits (LLM graders,
same-vendor models, n=10 problems) - the credibility comes from the architecture plus the
disclosures, never from overclaiming.

## what gets rewritten when the data lands

- **case study:** the "does it actually work?" section is replaced by the real study: methods,
  pre-registration pointer, H1 numbers, H2 effect sizes + CIs, alpha, human-anchor correlation,
  blinding-check result, limitations. The old n=1 A/B survives as a clearly labelled
  "illustrative walkthrough" subsection. The html mirror is synced.
- **skill:** measured divergence numbers replace the qualitative "poor RNG over its own
  distribution" claim in SKILL.md (cite the experiment); any failure mode surfaced in the 90
  transcripts becomes a guidance line (same route as the vellum derailment fix). The skill is
  never tuned toward the test problems.
- **site:** figures panel gains the headline experiment numbers; run-note updated.

## run plan

Phased workflows (user has approved workflow usage), subjects pinned fable-5, graders pinned
opus-4-8, all agents receive only their need-to-know slice:

1. pre-registration freeze (no agents: write, draw M, commit)
2. blind pool generation -> commit -> entropy-draw 10 -> commit
3. collection: 90 protocol passes + 200 self-picks, parallel, fresh contexts
4. normalization + blinding check
5. panel: 4 graders x 90 outputs (pipeline), freeze grades
6. human anchor: present 15 outputs to the user, record gradings
7. offline analysis -> results.md; update case study, skill, site, colophon
8. full verify + merge + deploy (same gates as v2)

Rough budget: ~700 agent calls, heavily parallel, one-time. Analysis re-runs forever for free.

## risks and honest limits

- **H2 may be null or unfavorable.** Pre-committed to publishing as-is; a null with honest
  reporting is more impressive to the target audience than a polished win.
- **blinding leakage:** wildcard outputs may have a recognizable flavor even normalized. The
  blinding check measures this instead of assuming it away.
- **LLM graders:** may not track human judgment; bounded by the human anchor correlation.
- **same vendor:** subjects and graders are both anthropic models (different families); noted
  in limitations.
- **n=10 problems:** supports effect sizes and CIs, not grand generalization; stated plainly.
