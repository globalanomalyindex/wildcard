# Historical evidence audit — 20 September 2026

This is a newly executed audit and post-hoc reanalysis of existing observations. It is not a new model experiment, a human evaluation, or evidence that an independently sampled replacement treatment works. All 478 historical research and analyzer files remain byte-for-byte identical to commit `04ff0a546d4e55038fa75881ec245662ac5765e9`.

## What reproduced

Calling the three pure historical analyzers reproduced each committed `results.json` exactly. The original 22 experiment tests passed. Those tests do not validate completeness or establish scientific validity.

| Study | Stored grading rows | Unique grader/output pairs | Scheduled pairs | Integrity |
|---|---:|---:|---:|---|
| 1 | 360 | 360 | 360 | Complete grading matrix |
| 2 | 240 | 239 | 240 | One duplicated pair and one missing pair |
| 3 | 238 | 238 | 240 | Two missing pairs |

The generalization unit for each arm contrast is the problem: ten units, with three outputs per arm per problem. Grader calls are repeated measurements of those outputs, not 240 independent tasks.

## New finding: Study 2 contains a duplicate and a missing judgment

`experiment/v2/grades.json` contains **two identical g3/out-35 rows** and no g3/out-48 row. The manifest maps out-35 to `v2-p26-r1` and out-48 to `v2-p14-r3`. Counting 240 rows concealed the defect. The original analyzer averages five grading rows for out-35 and three for out-48; it reports no missing cells because all problem/arm means remain present.

There is no evidence that the repeated row belongs to the missing output. The source is unchanged. A separate sensitivity analysis removes the repeated pair once and leaves the missing pair absent. This gives a genuineness difference of **+0.805556**, compared with the original **+0.808889**; the exact conditional signed-rank p remains **0.001953125**. All seven hypothetical 1–7 values for the missing genuineness rating give differences from **+0.766667 to +0.816667** and retain the original +0.50 point prediction. These are hypothetical bounds, not recovered scores.

This defect was not identified in the supplied audit package. It does not reverse the reported primary direction. It does invalidate a claim that Study 2's grader/output matrix is complete.

## Study 3 result and limits

| Metric | Wildcard mean | Plain mean | Difference | Original paired bootstrap 95% interval | Original signed-rank p |
|---|---:|---:|---:|---|---:|
| Genuineness | 5.208333 | 5.438889 | −0.230556 | −0.552778 to +0.072222 | 0.312500 |
| Usefulness | 6.216667 | 6.450000 | −0.233333 | −0.447222 to −0.025000 | 0.140625 |
| Novelty, primary | 5.433333 | 4.708333 | +0.725000 | +0.216667 to +1.208333 | 0.037109 |
| Non-derailment | 6.658333 | 6.547222 | +0.111111 | +0.011111 to +0.227778 | 0.097656 |

The original decision rule required a novelty **point estimate ≥ +0.30** and a 95% interval excluding zero. It was met. It did not require the lower confidence limit to exceed +0.30, and the data do not establish a minimum +0.30 gain with 95% confidence. The protocol also named a signed-rank primary test; the recorded result meets p < .05, but a p threshold is not part of the written decision rule.

The missing judgments are g4/P-p48-r3 and g3/P-p47-r2. Eight of ten problem means favor Wildcard in novelty. All 49 hypothetical combinations of the two missing novelty ratings give differences **+0.675 to +0.775**. The original seeded-bootstrap rule survives every combination. Signed-rank p ranges from **0.021484 to 0.058594**; this sensitivity does not authorize replacing the original CI-based decision rule with a p-only rule.

Usefulness has a negative percentile interval but a signed-rank p above .05. This is not a computational contradiction: the bootstrap interval concerns a mean difference, whereas the signed-rank test uses ranks under sign-symmetry assumptions. The two procedures are not inversions of one another. Neither non-significance nor a CI spanning zero establishes equality. Cliff's delta in the original outputs compares all cross-arm problem means, and is not a paired rank-biserial effect.

## Newly executed sensitivity analyses

An independent Python analysis used exact rational means/ranks. A separately implemented JavaScript dynamic program reproduced its central results. The new JavaScript signed-rank calculation groups mathematically equivalent ties with a declared `1e-12` absolute tolerance. Genuineness p changes from **0.3125 to 0.296875**; novelty p is unchanged. This corrects numerical tie handling, not the underlying observations.

The finite bootstrap distribution was evaluated by integer convolution over **all 10^10 ordered problem resamples**. Its novelty 95% percentile interval is **[0.225, 1.213889]**. The original 10,000-draw interval remains the historical result. The new interval removes Monte Carlo error; it does not fix small-sample coverage, biased measurement, sampling limitations, or confounding. Every hypothetical missing-score combination still meets the original point-plus-positive-interval rule under this exhaustive calculation.

Leaving out each grader in turn gives novelty differences **+0.644444 to +0.777778**, positive exhaustive-bootstrap lower bounds, and signed-rank p **0.019531 to 0.046875**. This shows the recorded novelty direction is not driven by one labeled grader. It does not create independent judge families or validate human creativity.

The exact mean sign-flip sensitivity gives novelty p **0.033203125**. It is a separate post-hoc statistic under sign-exchangeability assumptions, not a replacement primary analysis. A two-sided sign test for 8/10 positive differences gives p **0.109375**; it discards effect magnitude and answers a different question. Leave-one-problem-out novelty differences remain positive, but six of ten corresponding signed-rank p values exceed .05.

## Fabrication counts and normalization

Wildcard has **0/120 positive judgments and 0/30 outputs with any flag**. Plain has **6/118 positive judgments across 2/30 outputs**: P-p01-r1 was flagged by two of four graders, and P-p36-r3 by all four. These are model-judge flags, not six independent factual errors and not independently adjudicated truth.

Spot inspection of P-p01-r1 confirms a raw-to-normalized change: the raw response names `REFRESH MATERIALIZED VIEW CONCURRENTLY` and separately “TimescaleDB's continuous aggregates”; the normalized response compresses these to “Postgres continuous aggregates,” losing that distinction. The flag therefore cannot automatically be attributed to the generator alone. The source files remain available for separate technical adjudication. This audit does not certify every factual assertion in every raw or normalized output.

Non-derailment agreement is negative (ordinal alpha about **−0.0655**); its numerical gain should not be promoted as an established benefit. Novelty alpha about **0.7845** concerns consistency among these judge runs, not their validity against human judgment. The Study 1 human-anchor correlations reproduce, including about **0.01 for novelty** on only fifteen selected outputs. Pooling different rubric dimensions into one correlation does not validate each dimension.

## Sampler and grader-order interpretation

Every recorded Study 3 treatment seed is 22 bytes and satisfies `modeIndex === lensIndex % 2`. Independently replaying 100,000 seeds padded to 22 bytes reaches 189/378 specialist leaves conditionally on automatic specialist mode and four/eight lenses for each mode. The marginal mode balance is exactly 50/50 in that probe. Marginal balance and shell/browser parity do not imply independent streams.

An additional probe of the historical `seededShuffle` over 100,000 six-byte seeds with tag `audit` reaches only **12/24 permutations for length four**, and **2,520/40,320 for length eight**; length three reaches all six. Equal-length tagged CRC values couple low bits of Fisher–Yates indices. This is a diagnostic of the implementation and seed strata, not a claim that the actual historical grader presentation orders are known.

The resulting Study 3 estimate applies to the complete recorded skill/prompt/legacy-sampler configuration against the specified plain prompt. It cannot isolate the causal effect of external cues, persona wording, structural mapping, removability, or a future independent sampler. The sign or size of sampler bias relative to a corrected treatment is unknown.

## Provenance boundary

The repository records requested subject `claude-sonnet-4-6`, normalizer `claude-haiku-4-5`, and grader `claude-opus-5` for Study 3. It does not contain returned model IDs, full request/response envelopes, sampling settings beyond a stated harness default, token/cost/latency receipts, exact grading prompts, or grader-order receipts. Four labeled runs of one requested grader model are not four independent human experts or cross-vendor replication.

Git shows preregistration commit `e387745` before collection-artifact commit `406af96`. That verifies repository order. It does not independently timestamp actual model execution. Arm IDs in saved filenames and the idmap do not prove graders saw those IDs; absence of actual request envelopes also prevents certifying blind exposure or isolation.

Study 1's entropy comparison reproduces, but compares canonicalized self-picked labels with externally sampled corpus labels. It measures the label-selection procedure, not useful action diversity, output semantic novelty, or inaccessible model knowledge.

## Reproduce and consume

```sh
node scripts/verify-history.mjs
node scripts/build-evidence.mjs --check
node --test research/lib/stats.test.mjs research/audit-2026-09/evidence.test.mjs
```

`history-manifest.json` pins every historical file; `verify-history.mjs` is read-only. `build-evidence.mjs` writes only `research/audit-2026-09/evidence.json`, `site/data/evidence.json`, and `site/js/evidence-data.js`. The browser module exports named and default `evidence`. Each public claim identifies units, denominators, source paths/hashes, and caveats.

`readStudy(root, studyId)` defaults to strict validation and rejects Studies 2 and 3. Reading preserved observations requires the explicit `legacy-available-case` mode, which still reports `confirmatoryEligible: false`. This mode never repairs or writes grades. Malformed scales, booleans, unknown identities, and invalid design cells fail even in legacy mode.

New statistics live in `research/lib/stats.mjs`: `mean`, `pairedBootstrap`, `signedRank`, `signFlip`, and `holm`. Exact signed-rank DP is bounded at 250 nonzero differences; exact sign-flip enumeration at 20 paired differences. Larger studies must use a separately specified supported method rather than silently changing statistical procedures. This exact bootstrap utility is restricted to at most twelve rational-grid problem differences.
