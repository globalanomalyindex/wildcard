# Wildcard: Counterfactual Cue Transfer — protocol v1

**Author and public project attribution:** christopher robin fiore. **Project:** globalanomalyindex/wildcard. **Protocol authored:** 20 September 2026. **Status:** executable protocol; acquisition status and freeze timestamp are established by the run manifest and ledger, not by this document. This is a bounded preregistered synthetic benchmark, not a power-justified confirmatory population study.

## Question and claim boundary

When a source-backed relation and its transfer boundary are already supplied, does adding its explicit donor name increase the number of qualified mechanisms absent from an independently acquired strong-baseline bank? The single primary comparison is **LR minus R on QNM@4**.

This is a behavioral prompt intervention. It does not update model weights, identify training examples, observe internal representations, or establish a neural or human cognitive mechanism. A positive result is conditional on the specified tasks, cue library, prompts, requested model configuration, and observed acquisition environment. A null result is not equivalence. A new mechanism here means new **relative to the finite reference bank**, not historically unprecedented.

The protocol is a new intervention inspired by Wildcard. It does not reproduce the full historical skill: there is no persona, specialist/concept draw, lens, iterative search, live retrieval, or implementation step performed by a tool. Historical effect sizes are not inherited.

## Fixed materials

`tasks.json` contains 32 distinct synthetic main briefs, eight each in interaction/accessibility, software systems, operational workflows, and information/creative tooling. Four disjoint development briefs exercise transport and measurement. Main briefs contain a concrete objective, hard constraints, observable success criteria, and non-goals. They are heterogeneous designed cases, not minor paraphrases of a common template.

The authoring agent knew the research question and wrote the tasks before any subject or judge output. Task authorship is therefore **not blinded**. There is no claim of a probability sample of natural user work, and “32 tasks” does not mean 32 independent customer populations. Family membership is a fixed stratification device. Results describe this constructed benchmark and motivate later external validation.

`cards.json` contains 16 curated donor cards. Each has an explicit label, an authored relation abstraction, a transfer boundary, primary-source URLs, and a source-fact note. Sources were checked on 20 September 2026. The relation and boundary are hypotheses for transfer, not proof of efficacy in a target domain. Several relations are familiar control or information patterns; the library is not claimed to contain uniformly distant or equally unusual ideas.

Only `relation` and `boundary` are shown in R; LR additionally shows the correct `label`; XR shows a different card's label. Card IDs, sources, source facts, notes, and the treatment names are not shown to subjects. Source provenance remains public in the materials. Removing the explicit name does not guarantee that the relation's source is unguessable; the estimand is the effect of the explicit name, not the effect of all domain knowledge.

`diagnostics.json` contains eight separate pairs of invented known-answer cases. Their expected outcomes exist before acquisition. They do not enter the main score or provide independent evidence of creativity.

## Arms, bank, and fixed schedule

| Arm | Subject receives |
|---|---|
| S | Strong direct prompt asking for distinct, useful, executable, constraint-respecting actions with falsifiable checks. |
| R | S plus one optional relation and boundary. |
| LR | R plus the correct explicit donor label. |
| XR | R plus an experimentally mismatched donor label. |

`prompts.py` is the authoritative literal prompt source. The optional-cue wrapper requests transfer of relationships, allows ignoring an unhelpful cue, and says the donor is not evidence that an intervention works. R, LR, and XR use byte-identical relation and boundary strings. S is a credible comparator with the same final output requirements; it is not intentionally weakened by omitting basic quality instructions. The incremental cue bundle differs from S, so R−S does not isolate randomness or a single transfer instruction.

Before any main generation, acquire two separate S bank responses per task, with up to eight actions each. The two calls have identical templates and fresh contexts. They are independent acquisitions in the operational sense; the transport does not expose an inference RNG seed or prove provider-level stochastic independence. Freeze the resulting bank before main acquisition. Never show the bank to the main generator. The same bank is used for all arms, including S. Its realized size may be below sixteen if a valid response supplies fewer actions; report actual sizes.

For each task, acquire one main response per arm, with up to four actions each. Each action is at most 110 whitespace-delimited words across `action`, `mechanism`, `implementation`, `check`, and `risk`. The response contains only those structured action fields and an `abstention_reason`. A valid empty action list requires a reason; a nonempty list cannot also be labeled abstention. No selection or rewriting step follows generation.

`run.py` fixes the public schedule seed to `wildcard-transfer-2026-09-20-v1`. `stable_shuffle` sorts items by SHA-256 keys derived from canonical JSON containing the seed, a stream namespace, and the item. This is a specified deterministic ordering, not an inference seed or a claim of exact uniform semantic sampling. Card ordering uses the `card-order` namespace. In task-file order, task index `i` receives card `order[i mod 16]`; its XR label comes from `order[(i+8) mod 16]`. Thus each card is used twice on the main set and never receives its own label in XR. The explicit task/card/label assignments and every rendered request are stored in the manifest. Acquisition request order is separately shuffled by cohort namespace; bank acquisition finishes before the main phase.

The main sample is fixed at 32 tasks. No task, card, arm, or weak response is replaced because its content is inconvenient. There is no efficacy-based early stopping and no prompt tuning after main or bank outputs. If development requires a substantive prompt or rubric change, it must be completed and recorded before the main freeze.

## Acquisition and budgets

The requested generator is `gpt-6-astra`. Requested judges are `gpt-6-astra` and `gpt-5.5`. All use the `low` reasoning configuration through the locally authenticated Codex CLI. The actual provider-returned model snapshot is not exposed by this transport and is recorded as null; an alias is not reported as a verified immutable model version. Both judge configurations share OpenAI as provider, and one shares the requested generator alias. They are two measurement configurations, not independent organizations or human raters.

The CLI replaces system instructions with the frozen `system-instructions.txt`, ignores user configuration, uses ephemeral sessions in an empty working directory, and disables web search, shell tools, plugins, apps, memory, multi-agent behavior, and host skill discovery. The empty directory and event logs allow enforcement to be checked. CLI infrastructure can still introduce common overhead; this is not described as a raw API experiment with no wrapper.

The output budget is matched by action count and word limit. Input length differs because of the cue fields, and actual tokens can differ. Temperature, top-p, model sampling seed, and hard maximum output tokens are unavailable/unset and recorded as null. **Do not describe the study as token-matched or temperature-controlled.** Report observed input/output usage and latency where emitted. Subscription-based marginal dollar cost is unavailable; do not invent a zero cost or dollar estimate.

Planned main acquisition consists of 64 bank calls and 128 main calls. Judging adds 64 blocks, one per task per requested judge. Diagnostics add sixteen calls under their separate output contract. Development, calibration, technical failures, and retries are separately listed; the exact ledger is authoritative for the realized count.

Each transport call has a 240-second timeout and at most two attempts. A retry is allowed only for unsuccessful/incomplete transport, never because the action is weak, uncreative, empty, or poorly scored. A delivered response with invalid JSON, wrong fields, too many actions, or a word-limit violation is a validation failure and is not regenerated. Keep every attempt, event stream, stderr record, request, delivered response, status, timestamps, usage, request hash, and result hash. The first valid completed response is the logical output.

The collector records requested model, returned model null, provider, CLI version, reasoning setting, unknown decoding settings, attempt count, and request identity. A tool-policy violation stops that logical call and is not treated as harmless text. An interrupted call with existing partial attempts cannot silently restart; it requires a documented ledger resolution or a new run version. Completed immutable artifacts are never overwritten.

## Freeze and integrity

The main manifest must precede both bank and main generation. `prepare` stores source hashes, rendered request hashes, schema hashes, task statements, assignments, schedule, acquisition settings, and a UTC freeze time. Its source list includes tasks, cards, diagnostics, this protocol, prompts, collector, and system instructions. Preserve the source commit and uncommitted source hashes so the exact state is recoverable. Commit/timestamp the frozen materials before collecting main-cohort data; commit the run manifest before outcomes or use an equivalent append-only chronological record.

The collector verifies frozen sources before continuing. A source change after the main freeze requires a new version or an explicit deviation; it must not silently resume against the previous manifest. Finalize and freeze `analysis.py`, `analyze.mjs`, and `../lib/stats.mjs` with the same main manifest before main-cohort acquisition. The frozen estimand and rules below govern their implementation.

All banks must have valid completed responses, including valid abstentions, before main acquisition. A malformed or failed bank blocks main acquisition: it is not silently replaced, shortened, or exempted. A run that cannot satisfy this gate must be reported as incomplete or superseded with an explicit version and reason. Main failures remain in the primary denominator and score zero. They are not missing-at-random observations.

## Masked judging and qualification

Judge blocks contain a task, its complete realized bank, and all candidate actions in a masked order. Source and treatment metadata are omitted. The original structured fields are carried verbatim; no model normalizer, paraphraser, or stylistic cleanup is used. The second judge sees the reverse of the first judge's candidate order. This counterbalances position but does not randomize every order independently or establish perfect blinding. Candidate content may still reveal its origin. Judges see several candidate sets together, which may create within-block context effects; report this limitation.

For every candidate ID the judge returns exactly: `constraint_valid`, `feasible`, `actionable`, `baseline_match`, `mechanism_group`, and a concise `reason`. IDs must match the provided candidates once each. A nonnull baseline match must name a real bank ID. No judge may browse, use tools, read source cues, or access other judges' results.

An action is **qualified** only when all three boolean flags are true:

1. `constraint_valid`: respects all explicit task constraints. An interesting idea does not excuse a violation.
2. `feasible`: has a plausible technical or operational route using the stated resources. An unsupported factual dependency fails this check. A proposed test or assumption must not be mistaken for a proven outcome.
3. `actionable`: specifies an implementable intervention and an observable check. A restated requirement, renamed concept, decorative analogy, or measurement with no action is insufficient.

`baseline_match` identifies the same causal/operational mechanism in the bank, including an imperfectly expressed bank action. Cosmetic names, parameter changes alone, different metaphor words, or a new feature title do not establish novelty. `mechanism_group` groups all candidates implementing the same mechanism, including across their presentation order. Different interventions may target the same outcome yet remain distinct when their causal routes differ.

Judge uncertainty must be conservative about feasibility and explained in the reason; it is not permission to reward speculation. The schema does not directly measure every factual claim or provide a separately adjudicated novelty-uncertainty flag. Qualification and matching are model judgments, not executable proof or human validation. Calibration uses known-answer examples before main freeze; all calibration records and any prefreeze changes remain separate from the main results.

## Scores and primary analysis

For each candidate set and judge:

- **QDM@4:** count unique mechanism groups containing at least one qualified action. Range 0–4.
- **QNM@4:** count those qualified groups only when no candidate anywhere in the same task/judge block's mechanism group has a nonnull bank match. Propagate a match globally across all four arms before scoring each set. A match on any member conservatively makes the group not new in every arm, even if another member has a null match. Range 0–4. Preserve raw judgments unchanged and report within-group matching contradictions rather than silently rewriting them.
- Also retain qualified-action count, total actions, constraint violations, and each qualification flag.

Average the two judges' scores for each task/arm. Each task contributes one paired primary difference `d_i = QNM(LR)_i - QNM(R)_i`. Do not count judges, actions, or groups as additional independent tasks. A main acquisition failure contributes zero to both QDM and QNM. A missing or invalid required judge block prevents primary analysis rather than silently changing measurement coverage. A valid zero-candidate task has known zero scores without fabricated ratings.

The primary point estimate is the mean of the 32 `d_i`. Report the entire paired table, arm means, primary difference, and a paired 95% percentile bootstrap interval using the 2.5th and 97.5th percentiles. The bootstrap uses 50,000 resamples, resampling tasks within each of the four fixed eight-task family strata and retaining all arm/judge scores for a sampled task together. Use the deterministic SHA-256-counter stream `wildcard-transfer-analysis-v1:bootstrap:<contrast>`, with contrast IDs `LR-R`, `R-S`, and `XR-LR`; the finalized frozen analysis code specifies counter encoding and unbiased integer sampling. Intervals condition on the fixed cue library; task-only resampling does not establish generalization over all possible cues or natural task populations.

The primary two-sided randomization test uses 100,000 independently sampled sign vectors on the paired task differences, compares absolute resampled mean with the observed absolute mean including ties, and reports `(1 + extreme_count) / (100000 + 1)`. This relies on a paired exchangeability/symmetry null and is not an exact test of all possible causal mechanisms. Use the separate deterministic SHA-256-counter stream `wildcard-transfer-analysis-v1:signflip:<contrast>` with the same contrast IDs. A supplementary signed-rank result, if reported, cannot replace the primary statistic.

Secondary inferential contrasts on QNM are **R−S** and **XR−LR**, each computed at the task level with the same method. Apply Holm correction to those two secondary p-values as one prespecified family. They do not replace a failed primary. QDM, valid-action rate, judge-specific effects, disagreements, realized bank sizes, invalid-output rates, usage and latency are descriptive secondary outcomes. Do not search among endpoints for a favorable headline.

Prespecified sensitivity views are: judge configuration separately; complete successful main outputs versus the primary acquisition-inclusive zeros; per-family effects; all realized bank actions versus bank replicate 1 only; and frequency of QDM=4 ceilings. The bank-size sensitivity must be **rejudged** against the restricted bank or supported by complete bank-match annotations. A single `baseline_match` ID cannot reliably recover all matches in the restricted bank, so no approximate bank-size result may be presented as a measured sensitivity. If not acquired, mark that sensitivity unexecuted rather than inventing it.

The primary evidence rule labels a positive or negative direction only when the mean has that sign, its two-sided primary p-value is at most 0.05, and the 95% interval excludes zero in the same direction. Otherwise the result is inconclusive; explicitly note disagreement between uncertainty methods if present. No minimum practical effect is claimed from statistical significance alone. Report the numerical effect and operational costs so a product decision can distinguish a detectable change from a useful change. A negative result is published with the same visibility as a positive result. No inference implies superiority to Verbalized Sampling, in-context regeneration, learned routing, the complete historical skill, or human designers, none of which is an arm here.

## Diagnostic analysis

Each of the eight fixtures holds target brief, constraints, output format, and synthetic label fixed while changing `relation_a` to `relation_b`. The separate response contains `decision`, `action`, `trace`, and `explanation`. The file defines apply/adapt/abstain and exact expected decisions and traces. In x05, the action field is additionally required to be the selected command token, which reverses when the control relation reverses.

For a fixture variant, decision and trace must match the frozen expected values exactly; x05 also must match the exact case-insensitive command after trimming whitespace. A pair passes only when both variants pass. Report every variant and all eight pair results, including acquisition/validation failures as failures. Qualitative action/explanation review is separate and cannot silently change these scores.

Several fixtures deliberately make literal transfer unsafe for the toy target: deleting queued drafts, admitting flow without recovery, attaching a note through an ambiguous marker, and reconstructing a message without enough evidence. These test respect for stated boundaries. The diagnostic score measures operational relation sensitivity on designed cases, not creativity, broad analogical ability, or the internal process responsible for the main outputs.

## Publication and interpretation

Publish a complete source/claim trail: protocol, exact prompts, frozen manifest, task/card schedule, source notes, raw responses, attempt ledger, masked judgments, analysis, paired task results, errors, disagreement and usage. Keep historical `experiment/`, `experiment/v2/`, and `experiment/v3/` artifacts immutable. Source-backed cards and experimental mismatch labels must be distinguishable in the example explorer.

The strongest allowed new empirical statement is a scoped comparison of the named configurations on this 32-task synthetic benchmark. The result may inform whether an exploration interface exposes donor labels or emphasizes relations and transfer limits. It does not establish human satisfaction, real-world implementation success, correctness of every suggestion, or safety guarantees. A subsequent implementation study would require a common candidate selector, fixed implementation budget, and held-out acceptance tests.
