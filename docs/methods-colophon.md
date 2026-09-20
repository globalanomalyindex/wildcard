# Methods, authorship and the evidence boundary

This companion to the case study separates the recorded protocol from what the repository can independently establish. The historical studies are inspectable artifacts, not a guarantee that every collection safeguard worked as described.

## Authorship and assistance

Wildcard is presented by **christopher robin fiore**. It was developed with AI assistance across writing, design, implementation, review and evaluation. Historical notes describe agent-assisted orchestration, problem authoring, skill revision and model grading. Those notes do not establish a precise division of manual labor or time spent, and this colophon does not invent one.

Requested model names in committed protocols are metadata about the intended setup. Where returned provider model IDs and complete request/response envelopes are absent, they cannot establish the actual serving model. Avoid capability rankings or claims about a model family's internal architecture. In Study 3, the recorded requested subject is `claude-sonnet-4-6`, normalizer `claude-haiku-4-5`, and grader `claude-opus-5`; older public prose named a different grader. See the [dated audit](../research/audit-2026-09/README.md).

## Recorded design and verified chronology

The protocols describe separately prompted problem generation, selected problem subsets, repeated outputs, masked/normalized judge materials and multiple labeled judge runs. A prompt that omits the hypothesis reduces one route to bias; it does not prove neutral problem selection, perfect blindness or independent judgments.

Git records preregistration before collection-artifact commits. That verifies repository chronology. It does not independently timestamp model execution or recover missing collection logs. Saved arm labels do not prove that judges saw those labels; without actual request envelopes, blind exposure and cross-context isolation cannot be certified either way.

The new historical-file manifest pins 478 research/analyzer artifacts to audited commit `04ff0a546d4e55038fa75881ec245662ac5765e9`. The [read-only verifier](../scripts/verify-history.mjs) checks integrity. The three preserved analyzers reproduce their committed result objects. Reproduction establishes what those algorithms compute, not completeness or scientific validity.

## What the audit changed

| Study | Stored rows | Unique grader/output pairs | Scheduled pairs | Observed issue |
|---|---:|---:|---:|---|
| 1 | 360 | 360 | 360 | Complete grading matrix |
| 2 | 240 | 239 | 240 | One duplicated pair and one missing pair |
| 3 | 238 | 238 | 240 | Two missing pairs |

Study 2 duplicates `g3/out-35` and omits `g3/out-48`. Study 3 omits `g4/P-p48-r3` and `g3/P-p47-r2`. These observations remain unchanged. Separate sensitivity analyses describe the impact of explicit hypothetical treatments; they do not recover real missing judgments.

The legacy seeded sampler couples mode, cue index and lens. Every Study 3 treatment seed is 22 bytes; the fixed-length probe reaches only half of specialist entries conditionally on specialist mode and four of eight lenses per mode. The historical estimate therefore applies to its complete prompt/sampler configuration. The new SHA-256 sampler is a different configuration and has not inherited its creative-effect evidence.

Normalization also changed technical content in a flagged output. A raw PostgreSQL/TimescaleDB distinction became compressed in the normalized version. Judge flags cannot therefore be automatically attributed to the subject's original response. The audit has not fact-checked every assertion in every output.

## Interpreting the result

Study 3's original judged-novelty difference is +0.725 points across ten problem-level units, with paired bootstrap 95% interval [+0.2167, +1.2083] and signed-rank p=0.0371. It met its point-estimate/positive-interval rule. It did not establish a lower-bound benefit of +0.30. Usefulness and genuineness have negative point estimates; non-significance or an interval crossing zero is not evidence of equality.

Plain responses received six positive fabrication judgments across two of thirty outputs (6/118 observed judgments). Wildcard received none across thirty outputs (0/120). These are repeated model-judge flags, not six independent factual errors, adjudicated truth or a safety guarantee.

Four labeled runs of one requested grader model do not create four independent expert populations. Outputs, graders and suggestions are not extra independent task units. Study 1's fifteen-output human anchor had weak item-level association with model judgments, including novelty correlation near 0.01. The arm-recognition check identified 58/90 arms, above the 33.3% chance baseline. These findings constrain “blind” and “validated” language.

Different problem IDs within one agent-authored pool are not a broad out-of-sample guarantee. The studies do not establish better deployed artifacts, faster implementation, user satisfaction, cost efficiency, a neural mechanism or superiority over every prompting baseline. A bundled skill revision can support a comparison between versions; it does not isolate one causal instruction.

## Current and future work

The correctness release introduces versioned cue receipts, stronger corpus validation, safer display/copy behavior and source-linked claim presentation. These are engineering changes with their own tests. The [transfer-v1 protocol](../research/transfer-v1/protocol.md) separately proposes controlled tests of donor labels, relations and transfer boundaries. No new study result is asserted here.

Use the [audit resolution ledger](audit-resolution.md) for implementation status and remaining limitations. Read the [historical evidence audit](../research/audit-2026-09/README.md) for full denominators, primary decision rules, sensitivity analyses, source hashes and reproducible commands. Negative results and unresolved checks belong next to the favorable result, because they define what the tool is ready to support.
