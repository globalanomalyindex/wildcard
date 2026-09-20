# Independent verification of the amended transfer study

**Verdict: the published amended results reproduce exactly. The original primary remains halted.**

The [independent Python verifier](verify_transfer_independent.py) imports no production analysis modules. It reconstructs the original bank and candidate actions, reads all 64 new judge blocks, independently scores qualification and globally propagated bank matches, and calculates the frozen statistical procedures using integer half-score units. Its [machine-readable audit](transfer-independent-audit.json) includes all 32 task score rows and hashes of the input manifests, published result, and verifier.

This verifies arithmetic and source consistency. It is not independent human adjudication of the model ratings.

## Numerical result

All differences below are mean task-level QNM@4 differences after averaging the two required judges. The interval is the frozen 50,000-resample bootstrap within four fixed task-family strata. The p-value is the two-sided 100,000-draw mean sign-flip procedure with the plus-one correction.

| Contrast | Difference | 95% interval | Raw p | Holm p |
|---|---:|---|---:|---:|
| **LR−R, amended primary** | **−0.015625** | **[−0.109375, 0.062500]** | **1.000000** | Separate primary |
| R−S, secondary | +0.125000 | [0.000000, 0.265625] | 0.139459 | 0.278917 |
| XR−LR, secondary | −0.015625 | [−0.109375, 0.062500] | 1.000000 | 1.000000 |

The frozen primary decision is **inconclusive**. None of the secondary contrasts passes its multiplicity-adjusted test. The amended interval and test conclusions agree; the R−S lower interval bound is exactly zero. Supplementary exact signed-rank p-values are 1, 0.140625, and 1, respectively; they do not replace the primary test.

The primary paired difference is zero on 29 of 32 tasks. Its three nonzero values are +1 on s02, −0.5 on s06, and −1 on o05. The judges' separate mean LR−R differences are 0 and −0.03125. Every candidate-generation request succeeded, so the prespecified complete-success sensitivity includes all 32 tasks and equals the main estimate.

| Arm | Mean QNM@4 | Mean QDM@4 | Tasks with zero judge-averaged QNM |
|---|---:|---:|---:|
| S | 0.046875 | 3.671875 | 30/32 |
| R | 0.171875 | 3.765625 | 25/32 |
| LR | 0.156250 | 3.750000 | 26/32 |
| XR | 0.140625 | 3.718750 | 27/32 |

Bank-relative newness is sparse despite high qualified-distinct-mechanism counts. This benchmark does not establish equivalence, prove that labels never help, or measure human interface usefulness. The finite bank, authored task set, cue library, and model matching judgments limit interpretation. The unexecuted restricted-bank sensitivity cannot be inferred from a single selected match ID.

## Integrity and measurement checks

- All 13 current and frozen amendment source files match the amendment manifest. Its 1,648-file inventory of the original run remains unchanged.
- The 64 new requests equal the original judge requests in their original order. New records use the amendment freeze clock; the unchanged bank and generation records use the original freeze clock.
- Reconstructing the original raw outputs yields exactly 448 bank actions and 478 candidate actions. All mask IDs, bank ordering, published card assignments, and explorer action fields match. Bank acquisition completed before candidate acquisition. Realized banks range from 10 to 16 actions per task.
- All 64 amended judge blocks are valid and contribute to the estimate. The original invalid i07-judge-2 remains invalid. There is no `runs/main/results.json`.
- The [run result](../../research/transfer-v1/runs/remeasurement/results.json), [research result](../../research/transfer-v1/results.json), and [site result](../../site/data/transfer-study.json) are equal as JSON data.

Qualification agrees on 476/478 candidate actions; feasibility and actionability each agree on all 478. Bank-newness classifications agree on 471/478. The judges agree on 3,334/3,373 within-task candidate co-clustering pairs; positive-link agreement is 1,120/1,159 = 0.966350. Candidate pairs are correlated, and these descriptive agreement rates do not establish truth. Mean absolute judge disagreement on the 128 task/arm QNM scores is 0.0546875.

One amended within-group matching contradiction occurs in i07/j2: one member has a valid bank match while another has null. The frozen global rule makes that group non-new in every arm without changing either raw annotation.

The separate diagnostics remain **6/8 passing pairs, 12/16 passing variants**. Actor/time prefixes in x03 and x04 fail the exact trace contract. No post-hoc text cleanup changes that score.

## Acquisition and usage accounting

There are **336 distinct study calls and 336 attempts**, excluding development and calibration: 64 bank, 128 candidate-generation, 16 diagnostic, 64 original judge, and 64 amended judge calls. Exactly one original judge response is invalid; all other 335 responses are valid. The additional judge panel is measurement on the same generated sample, not a second independent experiment.

The two published 272-entry ledgers share the 208 bank, generation, and diagnostic calls. The effective amended ledger uses those 208 calls plus 64 new judges; the original ledger uses them plus 64 original judges. Summing the ledger lengths would double-count the shared calls. Reused judge request IDs must be identified together with their panel/path.

The new panel ran from 20:43:26.859623 to 20:55:23.807490 UTC on 20 September 2026: 716.947867 seconds of wall time with three workers. Summed call latency is 2,136.863431 seconds, averaging 33.388491 seconds per new judge call. Summed latency is not wall time when calls overlap.

Across the 336 unique calls, the recorded totals are 9,373.437102 summed call-seconds, 2,756,273 `input_tokens`, and 292,147 `output_tokens`. Cache and reasoning fields remain separate emitted metadata; they are not added again to these totals. Subscription marginal dollar cost and provider-returned model snapshots are unavailable. Main-arm action-count and word budgets are matched; actual tokens are not matched.

## Original-panel sensitivity stays separate

The [256-completion proof](../../research/transfer-v1/runs/original-sensitivity/invariance-proof.json) holds all original qualification and group annotations fixed while enumerating legal bank-ID/null values for the two invalid links. Its [post-hoc result](../../research/transfer-v1/runs/original-sensitivity/results.json) does not repair the original response or reinstate its primary analysis.

That sensitivity gives LR−R −0.015625, interval [−0.093750, 0.031250], p = 1. Its R−S interval excludes zero while the sign-flip p = 0.093939 and Holm p = 0.187878 do not reject; this method disagreement is preserved. Agreement with the amended point estimate is not independent replication. The amended panel alone determines the amended primary result.

## Reproduce the audit

From the repository root, run:

```sh
python3 docs/verification/verify_transfer_independent.py
```

This reads the retained evidence and writes only the audit JSON in this directory. It never calls a model or modifies a research source, acquisition record, or published study result. To verify the separate original sensitivity without writing files:

```sh
python3 research/transfer-v1/original_sensitivity.py --check --aggregate --amendment-manifest research/transfer-v1/runs/remeasurement/manifest.json
```
