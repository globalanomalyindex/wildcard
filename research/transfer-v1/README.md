# Wildcard: Counterfactual Cue Transfer

**christopher robin fiore**

**Question:** Does explicitly naming a donor domain add model-judged qualified mechanisms after its relation and transfer boundary are already supplied?

**Status:** The **original preregistered primary analysis is halted**. All 64 bank calls, 128 candidate-generation calls, and 16 diagnostic calls passed validation. One of 64 judge blocks failed because two bank-reference fields contained a candidate ID. The [measurement amendment](amendment.md) declares one new complete 64-block panel with constrained IDs; amended estimates remain pending. The original data and failure remain unchanged. Strict operational diagnostics passed **6/8 pairs (12/16 variants)**. Development outputs are excluded from the main estimate.

## The comparison

Thirty-two designed briefs cover interaction/accessibility, software systems, operational workflows, and information/creative tooling. Sixteen source-backed donor cards are each assigned to two briefs. Each brief receives one response of up to four actions in each condition:

| Condition | Input |
|---|---|
| S | Strong direct prompt with constraints, implementation steps, and observable checks |
| R | S plus an optional relation and transfer boundary |
| LR | The same relation and boundary, plus its correct donor name |
| XR | The same relation and boundary, plus a mismatched donor name |

The primary comparison is **LR−R on QNM@4**, the count of qualified distinct mechanism groups absent from a separately acquired finite direct-prompt bank. Two requested judge configurations assess masked, verbatim actions. A bank match anywhere in a task/judge mechanism group makes that group non-new in every arm. The task is the analysis unit, after averaging both judges. R−S and XR−LR are secondary comparisons with Holm correction.

This is a bounded synthetic benchmark, not a powered population study. Bank-relative newness is not historical originality, feasibility ratings are not implementation tests, and same-provider model judges are not human validation. The name intervention changes a model's prompt; it does not test whether displaying names improves an interface for people. The 16-card research set does not test the complete deployed skill with its 378 specialists and 461 concepts, or validate the sampler's creative benefit. Eight separate paired diagnostics test supplied operational relations, not general creativity. See the [protocol](protocol.md), [manuscript](paper.md), and [prior-work map](related-work.md).

## Registration and preserved development

| Checkpoint | Recorded evidence |
|---|---|
| Reviewed materials | [6ca0d76](https://github.com/globalanomalyindex/wildcard/commit/6ca0d769575b2d2c80d12367810d661985e6f5ae), 20 September 2026, 19:54:23 UTC |
| Main manifest | [d93831e](https://github.com/globalanomalyindex/wildcard/commit/d93831ef15b28d89bed84b47ec1f190e861ee7f4), committed 19:54:40 UTC; [manifest](runs/main/manifest.json) frozen at 19:54:24 UTC |
| Reference bank checkpoint | [4757b5e](https://github.com/globalanomalyindex/wildcard/commit/4757b5ea105da8923f85ce7ffa14c3348fc3d140), committed 20:04:47 UTC, before candidate generation |
| Measurement amendment | [3d70e45](https://github.com/globalanomalyindex/wildcard/commit/3d70e454f4b8e8384e04e6f89051ca0cc8082cbc), committed 20:42:38 UTC, preserving the original halt |
| Amended panel manifest | [ca29d29](https://github.com/globalanomalyindex/wildcard/commit/ca29d2964e697418d8d823fa9c83176eff25761d), committed 20:42:59 UTC; [manifest](runs/remeasurement/manifest.json) frozen at 20:42:49 UTC, before new panel acquisition |

Materials and the manifest were pushed before the first main-cohort bank call. Git commits document repository chronology; recorded request times and hashes document acquisition. Neither provides an independent third-party timestamp of provider execution or a verified returned model snapshot.

All development versions remain available:

- [Prefreeze check](runs/development-prefreeze/README.md): eight successful bank calls, then stopped after source drift; no candidate or judge requests. Exact source snapshots and all calls were preserved.
- [First completed development pass](runs/development-v1/README.md): eight valid banks, eleven of sixteen valid candidate responses, and eight valid judge blocks. Five whole responses exceeded the unchanged 110-word action cap. None was repaired or substituted.
- [Final development pass](runs/development/README.md): one declared rerun after a common 60–80-word target and illustrative field budgets were added before main acquisition. All 32 calls passed. The reused four-brief set checks instrumentation and contributes no main observations.

No further generation-prompt tuning followed final development. Main failures retain zero scores, and missing required judgments prevent primary analysis. The complete rules, including unknown decoding settings and the single allowed transport retry, are in the frozen protocol.

## Original halt and measurement amendment

The original run completed 272 calls in 272 attempts. Its 64 bank calls produced 448 reference actions. The failed judge block, [i07-judge-2](runs/main/calls/i07-judge-2/record.json), returned all sixteen candidate ratings but used candidate ID `73e7cd8ccf86c466` for two bank matches, including a self-reference. The original schema allowed arbitrary strings; the subsequent validator correctly rejected them. A delivered invalid response cannot be regenerated under the frozen rule, and a missing valid block prevents the original primary analysis.

The [amendment](amendment.md) changes only the structured-output identity constraints and authorizes one full new panel. Bank and candidate texts, prompt bytes, order, requested judge configurations, rubric, and scoring remain fixed. All 64 blocks are remeasured; the valid original 63 are not pooled into the new panel. No additional panel or outcome-dependent selection is authorized. No aggregate effects were calculated before choosing this amendment, although individual outputs and the failure had been inspected. Its results are **amended measurement on the same generated sample**, not an independent replication or a completed original preregistered primary.

A separate [post-hoc metric-invariance proof](runs/original-sensitivity/invariance-proof.json) enumerates all 256 legal assignments to the two invalid fields. With all other original ratings and groups fixed, each assignment produces the same mechanism counts. No intended links are inferred or written into the data. [Original-panel aggregate sensitivities](runs/original-sensitivity/results.json) were computed only after the amended manifest was frozen. These limited sensitivities neither validate the remaining semantic judgments nor reinstate the original primary; they cannot replace or select the amended panel.

All sixteen operational diagnostic responses were structurally valid. Two pairs failed because their traces added actor or time labels, despite matching the expected operational decisions. The exact score remains 6/8 pairs. See the [diagnostic discussion](paper.md#54-strict-operational-diagnostics-six-of-eight-pairs).

## What each artifact establishes

| Artifact | What it records, and its limit |
|---|---|
| [Protocol](protocol.md), [prompts](prompts.py), [system instructions](system-instructions.txt) | Intended intervention, response contract, failure policy, and analysis decisions. A specification is not an empirical result. |
| [Tasks](tasks.json), [cards](cards.json), [diagnostics](diagnostics.json) | Fixed stimuli, donor-source links, and known-answer toy cases. Source facts do not prove target interventions work; task authorship was not blinded. |
| [Main manifest](runs/main/manifest.json), [frozen sources](runs/main/frozen-source/research/transfer-v1/) | Exact source/request hashes, assignments, settings, schemas, and source snapshots. Requested model aliases are recorded; returned model snapshots are unavailable. |
| [Call directories](runs/main/calls/) | Each request, raw response, attempt events/stderr, timestamps, usage, and validation status. They expose failures and retries; they do not establish provider-level stochastic independence. |
| [Judge manifest](runs/main/judge-manifest.json) and [mask map](runs/main/mask-map.json) | Exact original masked judge requests and reversible ID mapping. Content may still reveal its source; masking does not prove perfect blinding. |
| [Validator/scorer](analysis.py) and [statistical analysis](analyze.mjs) | Identity, source, event, schema, and coverage checks; global bank-match propagation; paired inference and declared sensitivities. They do not independently verify the truth of model judgments. |
| [Amendment](amendment.md), [remeasurement manifest](runs/remeasurement/manifest.json), [collector](remeasure.py), [amended analysis](amended_analysis.py) | The changed identity constraints, full-panel acquisition and validation, and reuse of the frozen statistical analysis. The amended manifest binds the original records and new source/schema hashes before new acquisition. |
| `runs/remeasurement/results.json`, `results.json`, and `site/data/transfer-study.json` | Produced only after complete amended validation: equivalent derived amended results for the run, research entry point, and website. They are pending. No original `runs/main/results.json` may be presented as a completed primary. |
| [Invariance proof](runs/original-sensitivity/invariance-proof.json) and [sensitivity implementation](original_sensitivity.py) | Exhaustive hypothetical identity completions holding all other original ratings fixed. Any aggregate original-panel sensitivity is separately labeled and cannot replace the amended estimate. |
| [Historical audit](../audit-2026-09/README.md) | New checks of preserved earlier studies. Its results are separate from this component experiment and the corrected live sampler. |

## Reproduce offline

Run from the repository root with Python 3 and Node.js 22 or newer. The commands below do not call a model or need network access. The study's Python validation commands were also exercised with Python 3.9.6; no third-party Python packages are required.

Check frozen current sources and validate the completed development records without rewriting them:

```sh
python3 research/transfer-v1/run.py verify --cohort main
python3 research/transfer-v1/analysis.py --cohort development --validate-only
```

Run the transport parsing, response validation, mechanism scoring, and statistical tests:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s research/transfer-v1 -p 'test_*.py'
node --test research/transfer-v1/test_analysis.mjs
```

Confirm the original analysis halt with the original validator. This command is **expected to exit unsuccessfully** with `Missing or invalid required judge block prevents primary analysis`. The retained `i07-judge-2` record identifies the specific error as `unknown reference-bank id`. Do not treat the halt as a request to repair or regenerate the response:

```sh
python3 research/transfer-v1/analysis.py --cohort main --validate-only
```

After the amended manifest is frozen, verify its original-record and source hashes. Once all 64 amended blocks are complete, require their validity and recompute the published analysis in memory:

```sh
python3 research/transfer-v1/remeasure.py verify
python3 research/transfer-v1/remeasure.py verify --require-complete
python3 research/transfer-v1/amended_analysis.py --validate-only
python3 scripts/check-transfer-results.py
```

Completion checks intentionally fail while the amended dataset or published result files are incomplete. `run.py verify` checks the original manifest and source hashes only; it is not a substitute for complete record validation. The published-result check also rejects an original `runs/main/results.json`, preserving the original halt.

To explicitly regenerate the three derived amended-result JSON files from complete retained records, then verify them:

```sh
python3 research/transfer-v1/amended_analysis.py
python3 scripts/check-transfer-results.py
```

The regeneration command writes only derived amended result files. It does not repair raw responses, rerun model calls, fill missing judgments, or change frozen materials. The separate identity-invariance proof can be regenerated with `python3 research/transfer-v1/original_sensitivity.py`; its default does not compute aggregate effects. Bootstrap and sign-flip streams are fixed by the frozen analysis, so the numerical result is reproducible from a complete dataset. Acquiring new responses is a different operation requiring the recorded transport and model access; these offline commands do not claim to reproduce the provider's hidden sampling state.
