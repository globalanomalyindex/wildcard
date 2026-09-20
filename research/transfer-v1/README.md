# Wildcard: Counterfactual Cue Transfer

**christopher robin fiore · globalanomalyindex**

**Question:** Does explicitly naming a donor domain add model-judged qualified mechanisms after its relation and transfer boundary are already supplied?

**Status:** Main acquisition is in progress. The reference bank is complete: **64 successful calls, 64 attempts, 448 realized actions**, committed before candidate generation. Main efficacy results, judge comparisons, and diagnostic scores remain pending. Development outputs are excluded from the main estimate.

## The comparison

Thirty-two designed briefs cover interaction/accessibility, software systems, operational workflows, and information/creative tooling. Sixteen source-backed donor cards are each assigned to two briefs. Each brief receives one response of up to four actions in each condition:

| Condition | Input |
|---|---|
| S | Strong direct prompt with constraints, implementation steps, and observable checks |
| R | S plus an optional relation and transfer boundary |
| LR | The same relation and boundary, plus its correct donor name |
| XR | The same relation and boundary, plus a mismatched donor name |

The primary comparison is **LR−R on QNM@4**, the count of qualified distinct mechanism groups absent from a separately acquired finite direct-prompt bank. Two requested judge configurations assess masked, verbatim actions. A bank match anywhere in a task/judge mechanism group makes that group non-new in every arm. The task is the analysis unit, after averaging both judges. R−S and XR−LR are secondary comparisons with Holm correction.

This is a bounded synthetic benchmark, not a powered population study. Bank-relative newness is not historical originality, feasibility ratings are not implementation tests, and same-provider model judges are not human validation. The name intervention changes a model's prompt; it does not test whether displaying names improves an interface for people. Eight separate paired diagnostics test supplied operational relations, not general creativity. See the [protocol](protocol.md), [manuscript](paper.md), and [prior-work map](related-work.md).

## Registration and preserved development

| Checkpoint | Recorded evidence |
|---|---|
| Reviewed materials | [6ca0d76](https://github.com/globalanomalyindex/wildcard/commit/6ca0d769575b2d2c80d12367810d661985e6f5ae), 20 September 2026, 19:54:23 UTC |
| Main manifest | [d93831e](https://github.com/globalanomalyindex/wildcard/commit/d93831ef15b28d89bed84b47ec1f190e861ee7f4), committed 19:54:40 UTC; [manifest](runs/main/manifest.json) frozen at 19:54:24 UTC |
| Reference bank checkpoint | [4757b5e](https://github.com/globalanomalyindex/wildcard/commit/4757b5ea105da8923f85ce7ffa14c3348fc3d140), committed 20:04:47 UTC, before candidate generation |

Materials and the manifest were pushed before the first main-cohort bank call. Git commits document repository chronology; recorded request times and hashes document acquisition. Neither provides an independent third-party timestamp of provider execution or a verified returned model snapshot.

All development versions remain available:

- [Prefreeze check](runs/development-prefreeze/README.md): eight successful bank calls, then stopped after source drift; no candidate or judge requests. Exact source snapshots and all calls were preserved.
- [First completed development pass](runs/development-v1/README.md): eight valid banks, eleven of sixteen valid candidate responses, and eight valid judge blocks. Five whole responses exceeded the unchanged 110-word action cap. None was repaired or substituted.
- [Final development pass](runs/development/README.md): one declared rerun after a common 60–80-word target and illustrative field budgets were added before main acquisition. All 32 calls passed. The reused four-brief set checks instrumentation and contributes no main observations.

No further prompt tuning followed final development. Main failures retain zero scores, and missing required judgments prevent primary analysis. The complete rules, including unknown decoding settings and the single allowed transport retry, are in the frozen protocol.

## What each artifact establishes

| Artifact | What it records, and its limit |
|---|---|
| [Protocol](protocol.md), [prompts](prompts.py), [system instructions](system-instructions.txt) | Intended intervention, response contract, failure policy, and analysis decisions. A specification is not an empirical result. |
| [Tasks](tasks.json), [cards](cards.json), [diagnostics](diagnostics.json) | Fixed stimuli, donor-source links, and known-answer toy cases. Source facts do not prove target interventions work; task authorship was not blinded. |
| [Main manifest](runs/main/manifest.json), [frozen sources](runs/main/frozen-source/research/transfer-v1/) | Exact source/request hashes, assignments, settings, schemas, and source snapshots. Requested model aliases are recorded; returned model snapshots are unavailable. |
| [Call directories](runs/main/calls/) | Each request, raw response, attempt events/stderr, timestamps, usage, and validation status. They expose failures and retries; they do not establish provider-level stochastic independence. |
| `judge-manifest.json` and `mask-map.json` | Added after generation: the exact masked judge requests and reversible ID mapping. Content may still reveal its source; masking does not prove perfect blinding. |
| [Validator/scorer](analysis.py) and [statistical analysis](analyze.mjs) | Identity, source, event, schema, and coverage checks; global bank-match propagation; paired inference and declared sensitivities. They do not independently verify the truth of model judgments. |
| `runs/main/results.json`, `results.json`, and `site/data/transfer-study.json` | Produced only after complete validation: equivalent derived results for the run, research entry point, and website. They are currently pending and must reproduce from the retained records. |
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

**After main acquisition, all required judging, and diagnostics are complete**, validate raw records and recompute the published analysis in memory:

```sh
python3 research/transfer-v1/analysis.py --cohort main --validate-only
python3 scripts/check-transfer-results.py
```

These checks intentionally fail while the main dataset or published result files are incomplete. `run.py verify` checks the manifest and source hashes only; it is not a substitute for complete record validation.

To explicitly regenerate the three derived main-result JSON files from complete retained records, then verify them:

```sh
python3 research/transfer-v1/analysis.py --cohort main
python3 scripts/check-transfer-results.py
```

The regeneration command writes only derived result files. It does not repair raw responses, rerun model calls, fill missing judgments, or change frozen materials. Bootstrap and sign-flip streams are fixed by the frozen analysis, so the numerical result is reproducible from a complete dataset. Acquiring new responses is a different operation requiring the recorded transport and model access; these offline commands do not claim to reproduce the provider's hidden sampling state.
