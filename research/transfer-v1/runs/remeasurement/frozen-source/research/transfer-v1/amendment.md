# Measurement amendment 1: constrained reference identities

christopher robin fiore · 20 September 2026

## Original primary status: halted

The original frozen protocol remains unchanged. Its 64-block judge panel contains 63 valid blocks and one invalid block, `i07-judge-2`. In that block, two `baseline_match` fields contain candidate ID `73e7cd8ccf86c466`, which is not one of the 15 reference-bank IDs. One is a self-reference. Transport completed successfully, so the protocol forbids retrying this response. All original requests, responses, attempts, timestamps and the failure status remain immutable under `runs/main/`. The original primary analysis is halted; it is not a completed preregistered test.

The 64 bank calls, 128 candidate-generation calls and 16 diagnostic calls completed without validation failures. Those generated samples will not be regenerated. No aggregate main effect estimates, confidence intervals or hypothesis tests were calculated before this amendment. The failed block was inspected to diagnose its schema violation; individual examples and raw diagnostics had also been inspected. This is not an outcome-blind amendment.

## One new measurement panel

Before the first amended judge call, publish this amendment, acquisition/analysis code and a manifest containing hashes of all original artifacts, unchanged judge requests and per-request schemas. Acquire exactly one new panel of all 64 judge blocks, in the original acquisition order, with three workers. The requested model aliases, reasoning setting, system instructions, prompt bytes, candidate order, reference bank, masking, rubric, task set, arms and scoring rules remain unchanged. Each new block has a structured-output schema restricting `id` to that block's candidate IDs and `baseline_match` to that block's reference-bank IDs or null. No numeric rating, mechanism label, explanation or hypothesis direction is forced by the schema.

All 64 blocks are reacquired; the valid 63 original blocks are not pooled with the new panel. Original and amended panels cannot be selected according to their results. Use only the amended panel for the amended primary estimate. Transport retry rules remain unchanged: at most two attempts for incomplete/failed transport, no regeneration of a delivered invalid response. Missing or invalid amended judge blocks halt the amended primary analysis. No additional panel is authorized by this amendment.

The acquisition remains same-provider model evaluation, not human validation or an independent generator replication. Model snapshots and decoding controls not exposed by the transport remain unknown. A constrained schema corrects identity handling, not semantic judge reliability.

## Analysis and reporting

Use the exact frozen QNM/QDM scoring, conservative within-task/judge bank-match propagation, task-level two-judge average, family-stratified 50,000-resample bootstrap, 100,000-draw paired mean sign-flip test, exact signed-rank sensitivity and two-comparison Holm correction. The main sample is the same 32 already acquired briefs. The result is explicitly labeled **amended measurement after an original instrument failure**, never an original completed preregistered primary or a second independent study.

Report acquisition ledgers for both panels, all invalid records, judge agreement and bank-match inconsistencies. Preserve the original halt in machine-readable provenance and public prose. The strict diagnostic score remains 6/8 pairs (12/16 variants); extra trace labels in x03/x04 are not rescored as passes.

A separate, explicitly labeled **post-hoc metric-invariance sensitivity** may enumerate hypothetical assignments of each invalid link to any valid bank ID or null, holding every other rating, qualification flag, and mechanism group fixed. These assignments are evaluated in memory; no corrected links are inserted into the original records. Other candidates in the same frozen mechanism group already carry a valid bank match, so the frozen global propagation rule may make QNM/QDM invariant to these assignments. This sensitivity does not validate semantic judgments, recover intended links, validate the invalid response, or reinstate the halted original primary. If calculated, publish every permitted assignment and label all original-panel estimates as post-hoc sensitivity results. It will not replace or select the new panel.

## Interpretation limits

This amendment was chosen after observing an instrument failure. It increases structured-output constraint strength and adds evaluation calls. New estimates describe this corrected measurement procedure on the original generated sample. They do not prove broad creativity, deployed usefulness, a neural mechanism or a unique first-ever invention. Both positive and inconclusive findings will be published under the same rules.
